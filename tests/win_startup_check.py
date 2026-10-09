"""Real Windows check of how fast the exe starts (run by .github/workflows/ci.yml, not by pytest).

    python tests/win_startup_check.py NEW.exe [OLD.exe]

For each exe, a few times, in a fresh folder with "hide from screen sharing" on:
  - starts the exe and times: the program running (Data/.port written) and its window open and hidden (Data/.hide.json);
  - counts how many times the one-file exe was unpacked into the temp folder (_MEI... folders) - each one costs time;
  - opens and closes the see-through window (overlay) through the program's own API and times the opening;
  - closes the window the way a user does and checks the program then quits by itself and leaves no temp folder.
Prints a table and exits 1 when the NEW exe does not start, does not open its window, does not quit cleanly or leaves
its temp folder behind (a hard failure). Being slower than OLD is only reported (machines differ from run to run)."""
import ctypes
import glob
import json
import os
import shutil
import statistics
import subprocess
import sys
import tempfile
import time
import urllib.request
from ctypes import wintypes as wt

RUNS = int(os.environ.get("MA_STARTUP_RUNS") or 3)
TMP = tempfile.gettempdir()
u = ctypes.windll.user32
PROTO = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)
u.GetWindowThreadProcessId.argtypes = [wt.HWND, ctypes.POINTER(wt.DWORD)]
u.IsWindowVisible.argtypes = [wt.HWND]
u.PostMessageW.argtypes = [wt.HWND, wt.UINT, wt.WPARAM, wt.LPARAM]


def meis():
    return set(glob.glob(os.path.join(TMP, "_MEI*")))


def read_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def windows_of(pid):
    found = []

    def cb(hwnd, _lp):
        p = wt.DWORD()
        u.GetWindowThreadProcessId(hwnd, ctypes.byref(p))
        if p.value == pid and u.IsWindowVisible(hwnd):
            found.append(hwnd)
        return True
    u.EnumWindows(PROTO(cb), 0)
    return found


def call(port, key, name, body=None, timeout=90):
    req = urllib.request.Request(f"http://127.0.0.1:{port}/api/{name}", data=json.dumps(body or {}).encode(),
                                 headers={"X-Token": key, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def why_still_running(data, port, key):
    """Evidence for a program that did not quit: what it wrote last, its windows and its processes."""
    out = []
    try:
        with open(os.path.join(data, "app.log"), encoding="utf-8", errors="replace") as f:
            out += ["log: " + ln.rstrip()[:220] for ln in f.readlines()[-14:]]
    except OSError as e:
        out.append(f"log: not readable ({e})")
    try:
        res = call(port, key, "debug_clients", timeout=5)
        out.append("pages connected: " + json.dumps(res)[:300])
    except Exception as e:
        out.append("pages connected: no answer (" + str(e)[:80] + ")")
    pids = []
    for pid_s in subprocess.run(["powershell", "-NoProfile", "-Command",
                                 "(Get-Process MeetingAssistant -ErrorAction SilentlyContinue).Id"],
                                capture_output=True, text=True, timeout=60).stdout.split():
        pids.append(int(pid_s))
    for pid in pids:                                         # every top-level window of the program, shown or not
        wins = []

        def cb(hwnd, _lp, pid=pid, wins=wins):
            p = wt.DWORD()
            u.GetWindowThreadProcessId(hwnd, ctypes.byref(p))
            if p.value == pid:
                buf = ctypes.create_unicode_buffer(120)
                u.GetWindowTextW(hwnd, buf, 120)
                if buf.value or u.IsWindowVisible(hwnd):
                    wins.append(f"{'visible' if u.IsWindowVisible(hwnd) else 'hidden'} '{buf.value}'")
            return True
        u.EnumWindows(PROTO(cb), 0)
        out.append(f"windows of {pid}: " + (", ".join(wins[:8]) or "none"))
    ps = subprocess.run(["powershell", "-NoProfile", "-Command",
                         "Get-CimInstance Win32_Process | Where-Object { $_.Name -match 'MeetingAssistant|msedgewebview2' } | "
                         "ForEach-Object { \"$($_.ProcessId) $($_.ParentProcessId) $($_.Name) $($_.CommandLine)\" }"],
                        capture_output=True, text=True, timeout=60)
    out += ["proc: " + ln[:200] for ln in ps.stdout.splitlines()[:12]]
    return out


def kill_all():
    subprocess.run(["taskkill", "/F", "/T", "/IM", "MeetingAssistant.exe"], capture_output=True)
    time.sleep(2)


def run_once(exe, early_close=False):
    """early_close: the window is closed the moment it appears (its page may still be loading)."""
    r = {"port": None, "window": None, "unpacked": None, "overlay": None, "exit": None, "left_temp": None, "error": "", "why": None}
    work = tempfile.mkdtemp(prefix="ma_start_")
    dst = os.path.join(work, "MeetingAssistant.exe")
    shutil.copy2(exe, dst)
    data = os.path.join(work, "Data")
    os.makedirs(data)
    with open(os.path.join(data, "config.json"), "w", encoding="utf-8") as f:
        json.dump({"hide_from_share": True}, f)
    before = meis()
    t0 = time.perf_counter()
    proc = subprocess.Popen([dst], cwd=work)
    try:
        end = t0 + 150
        while time.perf_counter() < end:
            now = time.perf_counter() - t0
            if r["port"] is None and os.path.exists(os.path.join(data, ".port")):
                r["port"] = now
            st = read_json(os.path.join(data, ".hide.json"))
            if st is not None:
                if st.get("active"):
                    r["window"] = now
                    break
                if st.get("error"):
                    r["error"] = "hidden window: " + str(st["error"])[:160]
                    break
            if proc.poll() is not None:
                r["error"] = f"the program ended at once (code {proc.returncode})"
                break
            time.sleep(0.05)
        r["unpacked"] = len(meis() - before)
        if r["window"] is None:
            if not r["error"]:
                r["error"] = "the window did not open in 150 s"
            return r
        port, key = open(os.path.join(data, ".port"), encoding="utf-8").read().split()[:2]
        if not early_close:
            # the see-through window (overlay): opened and closed through the program's own API
            try:
                t1 = time.perf_counter()
                res = call(port, key, "overlay", {"on": True})
                if res.get("ok") and res.get("on"):
                    r["overlay"] = time.perf_counter() - t1
                else:
                    r["error"] = "overlay: " + str(res.get("error"))[:160]
                call(port, key, "overlay", {"on": False})
            except Exception as e:
                r["error"] = "overlay: " + str(e)[:160]
        # close the window like a user: the program must then quit by itself and clean its temp folder
        st = read_json(os.path.join(data, ".hide.json")) or {}
        pid = int(st.get("pid") or 0)
        wins = windows_of(pid) if pid else []
        if not wins:
            r["error"] = (r["error"] + "; " if r["error"] else "") + "could not find the window to close"
            return r
        for h in wins:
            u.PostMessageW(h, 0x0010, 0, 0)                       # WM_CLOSE
        t2 = time.perf_counter()
        try:
            proc.wait(90)                                          # quits about 12 s after its window is gone
            r["exit"] = time.perf_counter() - t2
        except subprocess.TimeoutExpired:
            r["error"] = (r["error"] + "; " if r["error"] else "") + \
                "did not quit within 90 s after its window was closed (a warning box may be open)"
            r["why"] = why_still_running(data, port, key)
            return r
        time.sleep(1.5)
        r["left_temp"] = len(meis() - before)
        return r
    finally:
        if proc.poll() is None or r["exit"] is None:
            kill_all()
        for d in meis() - before:
            shutil.rmtree(d, ignore_errors=True)
        shutil.rmtree(work, ignore_errors=True)


def note(line):
    """Also shown on the GitHub page of the run (an annotation), where it can be read without the log."""
    print(line, flush=True)
    if os.environ.get("GITHUB_ACTIONS"):
        print("::notice title=Startup::" + line.replace("%", "%25").replace("\n", "%0A"), flush=True)


def fmt(v, unit="s"):
    return "-" if v is None else (f"{v:.1f} {unit}" if isinstance(v, float) else f"{v}")


def med(rs, k):
    vals = [x[k] for x in rs if isinstance(x[k], (int, float))]
    return statistics.median(vals) if vals else None


def main():
    exes = [("NEW", sys.argv[1])]
    if len(sys.argv) > 2 and os.path.isfile(sys.argv[2]):
        exes.append(("OLD", sys.argv[2]))
    for label, exe in exes:
        print(f"{label}: {exe} ({os.path.getsize(exe) / 1e6:.0f} MB)", flush=True)
    kill_all()
    results = {label: [] for label, _ in exes}
    for i in range(RUNS):
        for label, exe in exes:
            r = run_once(exe)
            results[label].append(r)
            (note if r["error"] and label == "NEW" else print)(f"run {i + 1} {label}: running after {fmt(r['port'])}, window after {fmt(r['window'])}, "
                  f"unpacked {fmt(r['unpacked'], '')}x, overlay {fmt(r['overlay'])}, quit {fmt(r['exit'])} after "
                  f"closing, temp folders left {fmt(r['left_temp'], '')}" + (f"  !! {r['error']}" if r["error"] else ""),
                 )
            if r.get("why") and label == "NEW":
                note(f"run {i + 1} NEW, why it is still running:\n" + "\n".join(r["why"]))
    # closed at once, while its page may still be loading: it must quit by itself too (before 6.29 it could wait
    # for that page for ever, invisible)
    early = {label: [] for label, _ in exes}
    for i in range(2):
        for label, exe in exes:
            r = run_once(exe, early_close=True)
            early[label].append(r)
            (note if r["error"] and label == "NEW" else print)(f"closed at once {i + 1} {label}: window after {fmt(r['window'])}, quit {fmt(r['exit'])} after closing, "
                 f"temp folders left {fmt(r['left_temp'], '')}" + (f"  !! {r['error']}" if r["error"] else ""))
            if r.get("why") and label == "NEW":
                note(f"closed at once {i + 1} NEW, why it is still running:\n" + "\n".join(r["why"]))
    print("\nmedian of the runs:")
    for label, _ in exes:
        rs = results[label]
        note(f"{label} median: running {fmt(med(rs, 'port'))} · window {fmt(med(rs, 'window'))} · "
              f"unpacked {fmt(med(rs, 'unpacked'), '')}x · overlay {fmt(med(rs, 'overlay'))}")
    fails = []
    new = results["NEW"]
    if not all(r["port"] for r in new):
        fails.append("the new exe did not start every time")
    if not all(r["window"] for r in new):
        fails.append("the new exe did not open its hidden window every time")
    if not all(r["exit"] is not None for r in new):
        fails.append("the new exe did not quit cleanly after its window was closed")
    if not all(r["exit"] is not None for r in early["NEW"]):
        fails.append("the new exe did not quit when its window was closed at once")
    if any(r["left_temp"] for r in new):
        fails.append("the new exe left its temp folder behind")
    old = results.get("OLD")
    if old and all(r["overlay"] for r in old) and not all(r["overlay"] for r in new):
        fails.append("the overlay opened with the old exe but not with the new one")
    if old and med(new, "window") and med(old, "window") and med(new, "window") > med(old, "window") * 1.15:
        print("WARNING: the new exe opened its window more slowly than the old one")
    note("RESULT: " + ("OK" if not fails else "FAILED - " + "; ".join(fails)))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
