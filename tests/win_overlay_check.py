"""Real Windows check of the see-through window (run by .github/workflows/windows-check.yml, not by pytest).

It starts the program, opens the overlay through its own API and looks at the real window: styles, hidden from screen
sharing, position, mouse drag in move mode, and that the helper process ends with the program. It prints one line per
check and exits 1 if a hard check failed."""
import ctypes
import json
import os
import subprocess
import sys
import time
import urllib.request
from ctypes import wintypes as wt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
u = ctypes.windll.user32
u.GetWindowLongPtrW.argtypes = [wt.HWND, ctypes.c_int]
u.GetWindowLongPtrW.restype = ctypes.c_ssize_t
u.FindWindowW.argtypes = [wt.LPCWSTR, wt.LPCWSTR]
u.FindWindowW.restype = wt.HWND
u.GetWindowRect.argtypes = [wt.HWND, ctypes.POINTER(wt.RECT)]
u.GetWindowDisplayAffinity.argtypes = [wt.HWND, ctypes.POINTER(wt.DWORD)]
u.SetCursorPos.argtypes = [ctypes.c_int, ctypes.c_int]
FAILS, LINES = [], []


def check(name, ok, detail="", hard=True):
    LINES.append(f"[{'OK' if ok else ('FAIL' if hard else 'WARN')}] {name}: {detail}")
    print(LINES[-1], flush=True)
    if not ok and hard:
        FAILS.append(name)


def call(port, key, name, body=None):
    req = urllib.request.Request(f"http://127.0.0.1:{port}/api/{name}", data=json.dumps(body or {}).encode(),
                                 headers={"X-Token": key, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.loads(r.read())


def find_overlay(timeout=40):
    end = time.time() + timeout
    while time.time() < end:
        h = u.FindWindowW(None, "MA-Overlay")
        if h:
            return h
        time.sleep(0.5)
    return None


def rect(h):
    r = wt.RECT()
    u.GetWindowRect(h, ctypes.byref(r))
    return r.left, r.top, r.right - r.left, r.bottom - r.top


def key_combo(vks):
    for vk in vks:
        u.keybd_event(vk, 0, 0, 0)
    time.sleep(0.15)
    for vk in reversed(vks):
        u.keybd_event(vk, 0, 2, 0)
    time.sleep(0.6)


def main():
    env = dict(os.environ, MA_NO_BROWSER="1", MA_PORT="17699")
    proc = subprocess.Popen([sys.executable, "app.py"], cwd=ROOT, env=env)
    try:
        port = key = None
        for _ in range(60):
            try:
                with open(os.path.join(ROOT, "Data", ".port")) as f:
                    a = f.read().split()
                port, key = int(a[0]), a[1]
                break
            except (OSError, ValueError, IndexError):
                time.sleep(1)
        check("program started", bool(port), f"port {port}")
        if not port:
            return
        try:
            sc = call(port, key, "selfcheck")
            for i in sc.get("items", []):
                print(f"   selfcheck {i['state']:>4} {i['name']}: {i['detail']}", flush=True)
        except Exception as e:
            check("selfcheck answered", False, str(e)[:200], hard=False)
        r = call(port, key, "overlay", {"on": True})
        check("overlay API says on", r.get("ok") is True and r.get("on") is True, str(r))
        h = find_overlay()
        check("overlay window found", bool(h), "title MA-Overlay")
        if not h:
            return
        time.sleep(3)
        ex = u.GetWindowLongPtrW(h, -20)
        check("click-through (WS_EX_TRANSPARENT)", bool(ex & 0x20), hex(ex))
        check("layered + topmost + tool window", (ex & 0x80000) and (ex & 0x8) and (ex & 0x80), hex(ex))
        aff = wt.DWORD(0)
        u.GetWindowDisplayAffinity(h, ctypes.byref(aff))
        check("hidden from screen capture", aff.value in (0x11, 0x1), f"affinity {hex(aff.value)}", hard=False)
        x0, y0, w0, h0 = rect(h)
        check("window has a real size", w0 >= 300 and h0 >= 100, f"{w0}x{h0} at {x0},{y0}")
        # move mode with the keys
        key_combo([0x11, 0x12, 0x4D])                       # Ctrl+Alt+M
        ex2 = u.GetWindowLongPtrW(h, -20)
        check("move mode removes click-through", not (ex2 & 0x20), hex(ex2), hard=False)
        # mouse drag with the left button
        cx, cy = x0 + w0 // 2, y0 + h0 // 2
        u.SetCursorPos(cx, cy)
        time.sleep(0.3)
        u.mouse_event(0x0002, 0, 0, 0, 0)                   # left down
        for step in range(1, 11):
            u.SetCursorPos(cx + 12 * step, cy + 6 * step)
            time.sleep(0.05)
        u.mouse_event(0x0004, 0, 0, 0, 0)                   # left up
        time.sleep(0.5)
        x1, y1, w1, h1 = rect(h)
        check("mouse drag moves the window", abs(x1 - x0) > 40 or abs(y1 - y0) > 20, f"{x0},{y0} -> {x1},{y1}", hard=False)
        key_combo([0x11, 0x12, 0x4D])                       # lock again
        ex3 = u.GetWindowLongPtrW(h, -20)
        check("locked again: click-through back", bool(ex3 & 0x20), hex(ex3), hard=False)
        r = call(port, key, "overlay", {"on": False})
        time.sleep(2)
        check("overlay closes", not u.FindWindowW(None, "MA-Overlay"), str(r))
        call(port, key, "overlay", {"on": True})            # left on: the program ends while it is open
        check("overlay opens again", bool(find_overlay()), "")
    finally:
        proc.terminate()
        time.sleep(2)
        # the helper must not be left behind when the program ends
        time.sleep(3)
        check("no overlay window left after the program ended", not u.FindWindowW(None, "MA-Overlay"), "", hard=False)
        if proc.poll() is None:
            proc.kill()
    print("\n".join(LINES))
    if FAILS:
        print("FAILED:", ", ".join(FAILS))
        sys.exit(1)


if __name__ == "__main__":
    main()
