"""Real Windows check that keys are kept encrypted (DPAPI) by the exe, and that a PAC proxy is read
(run by .github/workflows/ci.yml, not pytest).

    python tests/win_secrets_check.py NEW.exe

Starts the exe (no window), saves a Groq key and a proxy with a password through its own API, checks that
Data/config.json and its backup do not contain them, starts the exe again and checks the key is still there
(read back by Windows). Then sets a proxy setup script (PAC) for this Windows user, served from here, and checks the
exe uses the proxy it names. Exit 1 when one check fails."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request

EXE = os.path.abspath(sys.argv[1])
results = []
KEY = "gsk_" + "TestKey1234567890abcdefghijklmnopqrstuvWXYZ"
PROXY = "http://someone:VerySecret99@127.0.0.1:3128"


def check(name, ok, detail=""):
    results.append(bool(ok))
    line = f"[{'OK' if ok else 'FAIL'}] {name}" + (f": {detail}" if detail else "")
    print(line, flush=True)
    if os.environ.get("GITHUB_ACTIONS"):
        print(("::notice" if ok else "::error") + " title=Keys::" + line.replace("%", "%25").replace("\n", "%0A"), flush=True)


def place_program(exe, work):
    """The one-file exe, or (installed-style) the whole folder with its _internal files."""
    src = os.path.dirname(os.path.abspath(exe))
    if os.path.isdir(os.path.join(src, "_internal")):
        shutil.copytree(src, work, dirs_exist_ok=True, ignore=shutil.ignore_patterns("Data"))
    else:
        shutil.copy2(exe, os.path.join(work, "MeetingAssistant.exe"))


work = tempfile.mkdtemp(prefix="ma_keys_")
place_program(EXE, work)
data = os.path.join(work, "Data")
os.makedirs(data)
with open(os.path.join(data, "config.json"), "w", encoding="utf-8") as f:
    json.dump({"hide_from_share": False}, f)


def start():
    try:
        os.remove(os.path.join(data, ".port"))
    except OSError:
        pass
    p = subprocess.Popen([os.path.join(work, "MeetingAssistant.exe")], cwd=work, env=dict(os.environ, MA_NO_BROWSER="1"))
    end = time.time() + 120
    while time.time() < end and not os.path.exists(os.path.join(data, ".port")):
        time.sleep(0.2)
    port, key = open(os.path.join(data, ".port"), encoding="utf-8").read().split()[:2]

    def call(name, body=None):
        req = urllib.request.Request(f"http://127.0.0.1:{port}/api/{name}", data=json.dumps(body or {}).encode(),
                                     headers={"X-Token": key, "Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read())
    return p, call


def stop(p):
    subprocess.run(["taskkill", "/F", "/T", "/PID", str(p.pid)], capture_output=True)
    time.sleep(2)


try:
    p, call = start()
    r = call("save_config", {"api_key": KEY, "proxy": PROXY})
    check("the key and proxy are saved", r.get("ok"), json.dumps({k: r.get(k) for k in ("ok", "error")}))
    r = call("save_config", {"answer_size": 26})                   # a second save: the backup copy is made
    raw = open(os.path.join(data, "config.json"), encoding="utf-8").read()
    bak = open(os.path.join(data, "config.json.bak"), encoding="utf-8").read() if os.path.exists(os.path.join(data, "config.json.bak")) else ""
    check("config.json does not contain the key or the proxy password", KEY not in raw and "VerySecret99" not in raw
          and "dpapi:" in raw, raw[:300].replace("\n", " "))
    check("the backup copy does not contain them either", KEY not in bak and "VerySecret99" not in bak, f"{len(bak)} bytes")
    stop(p)
    p, call = start()                                              # a new start reads them back (Windows decrypts)
    st = call("save_config", {})
    cfg = st.get("config") or {}
    check("after a new start the key is still there", cfg.get("has_key") and cfg.get("key_hint") == "…" + KEY[-4:],
          json.dumps({k: cfg.get(k) for k in ("has_key", "key_hint")}))
    stop(p)

    # a Windows proxy set by a setup script (PAC): served here, set in the user's Internet settings, read by WinHTTP
    import http.server
    import threading
    import winreg

    class Pac(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            body = b"function FindProxyForURL(url, host) { return 'PROXY 127.0.0.1:3999; DIRECT'; }"
            self.send_response(200)
            self.send_header("Content-Type", "application/x-ns-proxy-autoconfig")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *a):
            pass
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Pac)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    path = r"Software\Microsoft\Windows\CurrentVersion\Internet Settings"
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, path, 0, winreg.KEY_ALL_ACCESS) as k:
        try:
            old = winreg.QueryValueEx(k, "AutoConfigURL")[0]
        except OSError:
            old = None
        winreg.SetValueEx(k, "AutoConfigURL", 0, winreg.REG_SZ, f"http://127.0.0.1:{srv.server_address[1]}/proxy.pac")
    try:
        with open(os.path.join(data, "config.json"), "w", encoding="utf-8") as f:
            json.dump({"hide_from_share": False}, f)
        p, call = start()
        st = call("proxy_status")
        check("a Windows proxy from a setup script (PAC) is used", st.get("proxy") == "http://127.0.0.1:3999"
              and "PAC" in str(st.get("source")), json.dumps(st))
        stop(p)
    finally:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, path, 0, winreg.KEY_ALL_ACCESS) as k:
            if old is None:
                try:
                    winreg.DeleteValue(k, "AutoConfigURL")
                except OSError:
                    pass
            else:
                winreg.SetValueEx(k, "AutoConfigURL", 0, winreg.REG_SZ, old)
        srv.shutdown()
finally:
    shutil.rmtree(work, ignore_errors=True)

ok = all(results)
print("RESULT:", "OK" if ok else "FAILED", flush=True)
sys.exit(0 if ok else 1)
