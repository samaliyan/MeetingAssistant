"""Real Windows check of the overlay in the EXE, the way a user uses it (not run by pytest).

    python tests/win_overlay_exe_check.py MeetingAssistant.exe OUTDIR

Two set-ups: (A) "hide from screen sharing" on for the window and the overlay (as most users have it), (B) both off.
In each: starts the exe, presses the real keys (Ctrl+Alt+O on, Ctrl+Alt+PageUp, Ctrl+Alt+T, Ctrl+Alt+O off), checks the
window flags, that the main window is minimized and comes back, and takes pictures of what the overlay really shows
(PrintWindow, which also works when it is hidden from screen capture) and of the whole screen. A picture that is one flat
colour means the overlay shows nothing. Prints one line per check (also as GitHub annotations); exit 1 on a hard failure."""
import ctypes
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request
from ctypes import wintypes as wt

from PIL import Image

u, g = ctypes.windll.user32, ctypes.windll.gdi32
u.GetWindowLongPtrW.argtypes = [wt.HWND, ctypes.c_int]
u.GetWindowLongPtrW.restype = ctypes.c_ssize_t
u.FindWindowW.argtypes = [wt.LPCWSTR, wt.LPCWSTR]
u.FindWindowW.restype = wt.HWND
u.GetWindowRect.argtypes = [wt.HWND, ctypes.POINTER(wt.RECT)]
u.GetWindowDisplayAffinity.argtypes = [wt.HWND, ctypes.POINTER(wt.DWORD)]
u.IsIconic.argtypes = [wt.HWND]
u.IsWindowVisible.argtypes = [wt.HWND]
u.GetWindowTextW.argtypes = [wt.HWND, wt.LPWSTR, ctypes.c_int]
u.PrintWindow.argtypes = [wt.HWND, wt.HDC, wt.UINT]
u.GetDC.argtypes = [wt.HWND]
u.GetDC.restype = wt.HDC
u.ReleaseDC.argtypes = [wt.HWND, wt.HDC]
g.CreateCompatibleDC.argtypes = [wt.HDC]
g.CreateCompatibleDC.restype = wt.HDC
g.CreateCompatibleBitmap.argtypes = [wt.HDC, ctypes.c_int, ctypes.c_int]
g.CreateCompatibleBitmap.restype = wt.HBITMAP
g.SelectObject.argtypes = [wt.HDC, wt.HGDIOBJ]
g.SelectObject.restype = wt.HGDIOBJ
g.BitBlt.argtypes = [wt.HDC, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, wt.HDC, ctypes.c_int, ctypes.c_int, wt.DWORD]
g.GetDIBits.argtypes = [wt.HDC, wt.HBITMAP, wt.UINT, wt.UINT, ctypes.c_void_p, ctypes.c_void_p, wt.UINT]
g.DeleteObject.argtypes = [wt.HGDIOBJ]
g.DeleteDC.argtypes = [wt.HDC]
PROTO = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)
FAILS, LINES = [], []


def check(name, ok, detail="", hard=True):
    line = f"[{'OK' if ok else ('FAIL' if hard else 'WARN')}] {name}" + (f": {detail}" if detail else "")
    LINES.append(line)
    print(line, flush=True)
    if os.environ.get("GITHUB_ACTIONS"):
        print(("::notice" if ok else "::warning") + " title=Overlay::" + line.replace("%", "%25").replace("\n", " "), flush=True)
    if not ok and hard:
        FAILS.append(name)


def call(port, key, name, body=None, timeout=60):
    req = urllib.request.Request(f"http://127.0.0.1:{port}/api/{name}", data=json.dumps(body or {}).encode(),
                                 headers={"X-Token": key, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def keys(*vks):
    for vk in vks:
        u.keybd_event(vk, 0, 0, 0)
    time.sleep(0.12)
    for vk in reversed(vks):
        u.keybd_event(vk, 0, 2, 0)


CTRL, ALT = 0x11, 0x12


def rect(h):
    r = wt.RECT()
    u.GetWindowRect(h, ctypes.byref(r))
    return r.left, r.top, r.right - r.left, r.bottom - r.top


def windows_titled(prefix):
    out = []

    def cb(h, _):
        if u.IsWindowVisible(h) or u.IsIconic(h):
            buf = ctypes.create_unicode_buffer(300)
            u.GetWindowTextW(h, buf, 300)
            if buf.value.startswith(prefix) or (prefix == "Meeting Assistant" and buf.value == "Notes"):
                out.append(h)
        return True
    u.EnumWindows(PROTO(cb), 0)
    return out


def grab(draw, w, h):
    hdc = u.GetDC(None)
    mdc = g.CreateCompatibleDC(hdc)
    bmp = g.CreateCompatibleBitmap(hdc, w, h)
    old = g.SelectObject(mdc, bmp)
    try:
        if not draw(mdc):
            return None
        g.SelectObject(mdc, old)
        old = None

        class BMIH(ctypes.Structure):
            _fields_ = [("biSize", wt.DWORD), ("biWidth", ctypes.c_long), ("biHeight", ctypes.c_long), ("biPlanes", wt.WORD),
                        ("biBitCount", wt.WORD), ("biCompression", wt.DWORD), ("biSizeImage", wt.DWORD),
                        ("biXPelsPerMeter", ctypes.c_long), ("biYPelsPerMeter", ctypes.c_long), ("biClrUsed", wt.DWORD),
                        ("biClrImportant", wt.DWORD)]
        bi = BMIH()
        bi.biSize, bi.biWidth, bi.biHeight, bi.biPlanes, bi.biBitCount = ctypes.sizeof(BMIH), w, -h, 1, 32
        buf = ctypes.create_string_buffer(w * h * 4)
        if not g.GetDIBits(hdc, bmp, 0, h, buf, ctypes.byref(bi), 0):
            return None
        return Image.frombuffer("RGBA", (w, h), buf.raw, "raw", "BGRA", 0, 1).convert("RGB")
    finally:
        if old:
            g.SelectObject(mdc, old)
        g.DeleteObject(bmp)
        g.DeleteDC(mdc)
        u.ReleaseDC(None, hdc)


def shot_window(h, path):
    x, y, w, hh = rect(h)
    img = grab(lambda mdc: bool(u.PrintWindow(h, mdc, 2)), w, hh)
    if img:
        img.save(path)
    return img


def shot_screen(path):
    w, h = u.GetSystemMetrics(0), u.GetSystemMetrics(1)

    def draw(mdc):
        sdc = u.GetDC(None)
        try:
            return bool(g.BitBlt(mdc, 0, 0, w, h, sdc, 0, 0, 0x00CC0020 | 0x40000000))
        finally:
            u.ReleaseDC(None, sdc)
    img = grab(draw, w, h)
    if img:
        img.save(path)
    return img


def ink(img):
    """How much of the picture is not the background colour: 0 = one flat colour (the overlay shows nothing)."""
    if img is None:
        return -1.0
    small = img.resize((min(400, img.width), min(160, img.height)))
    px = list(small.getdata())
    bg = max(set(px), key=px.count)
    far = sum(1 for p in px if abs(p[0] - bg[0]) + abs(p[1] - bg[1]) + abs(p[2] - bg[2]) > 60)
    return 100.0 * far / len(px)


def read_cfg(data):
    try:
        with open(os.path.join(data, "config.json"), encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def scenario(name, exe, out, cfg):
    print(f"\n=== {name} ===", flush=True)
    work = tempfile.mkdtemp(prefix="ma_ov_")
    dst = os.path.join(work, "MeetingAssistant.exe")
    shutil.copy2(exe, dst)
    data = os.path.join(work, "Data")
    os.makedirs(data)
    with open(os.path.join(data, "config.json"), "w", encoding="utf-8") as f:
        json.dump(cfg, f)
    proc = subprocess.Popen([dst], cwd=work)
    try:
        port = key = None
        for _ in range(90):
            try:
                with open(os.path.join(data, ".port"), encoding="utf-8") as f:
                    a = f.read().split()
                port, key = int(a[0]), a[1]
                break
            except (OSError, ValueError, IndexError):
                time.sleep(0.5)
        check(f"{name}: program started", bool(port))
        if not port:
            return
        mains = []
        for _ in range(60):
            mains = windows_titled("Meeting Assistant")
            if mains:
                break
            time.sleep(0.5)
        check(f"{name}: main window open", bool(mains), f"{len(mains)} window(s)")
        time.sleep(6)                                            # let the page load and the program settle
        shot_screen(os.path.join(out, f"{name}-0-screen-before.png"))
        # Ctrl+Alt+O: the overlay comes, the main window goes down
        t0 = time.time()
        keys(CTRL, ALT, 0x4F)
        h = None
        for _ in range(80):
            h = u.FindWindowW(None, "MA-Overlay")
            if h:
                break
            time.sleep(0.25)
        check(f"{name}: Ctrl+Alt+O opens the overlay", bool(h), f"after {time.time() - t0:.1f} s" if h else "no window in 20 s")
        if not h:
            try:
                print("   log tail:", open(os.path.join(data, "app.log"), encoding="utf-8", errors="replace").read()[-1500:], flush=True)
            except OSError:
                pass
            return
        time.sleep(5)                                            # the page inside it loads
        ex = u.GetWindowLongPtrW(h, -20)
        check(f"{name}: click-through, see-through, on top", bool(ex & 0x20) and bool(ex & 0x80000) and bool(ex & 0x8), hex(ex))
        aff = wt.DWORD(0)
        u.GetWindowDisplayAffinity(h, ctypes.byref(aff))
        want_hidden = cfg.get("overlay_hide", True)
        check(f"{name}: hidden from screen capture = {want_hidden}", (aff.value in (0x11, 0x1)) == bool(want_hidden), hex(aff.value))
        x, y, w, hh = rect(h)
        check(f"{name}: size and place on the screen", w >= 300 and hh >= 100 and -50 < x < u.GetSystemMetrics(0) and -50 < y < u.GetSystemMetrics(1), f"{w}x{hh} at {x},{y}")
        mins = [m for m in windows_titled("Meeting Assistant")]
        check(f"{name}: main window minimized", bool(mins) and all(u.IsIconic(m) for m in mins), f"{[bool(u.IsIconic(m)) for m in mins]}", hard=False)
        img = shot_window(h, os.path.join(out, f"{name}-1-overlay.png"))
        shot_screen(os.path.join(out, f"{name}-2-screen-with-overlay.png"))
        k = ink(img)
        check(f"{name}: the overlay shows something (not one flat colour)", k > 0.3, f"{k:.2f}% of the picture is text/shapes")
        # Ctrl+Alt+PageUp: more solid
        a0 = int(read_cfg(data).get("overlay_alpha", 65))
        keys(CTRL, ALT, 0x21)
        time.sleep(1.5)
        a1 = int(read_cfg(data).get("overlay_alpha", 65))
        check(f"{name}: Ctrl+Alt+PageUp makes it more solid", a1 == min(100, a0 + 5), f"{a0} -> {a1}")
        # Ctrl+Alt+T: subtitle mode on, the overlay shows the subtitle line
        keys(CTRL, ALT, 0x54)
        time.sleep(2.5)
        s1 = read_cfg(data).get("subtitles")
        check(f"{name}: Ctrl+Alt+T turns subtitle mode on", s1 is True, str(s1))
        img2 = shot_window(h, os.path.join(out, f"{name}-3-overlay-subtitles.png"))
        check(f"{name}: overlay changed to subtitles", img2 is not None and img is not None and list(img2.resize((60, 20)).getdata()) != list(img.resize((60, 20)).getdata()), f"ink {ink(img2):.2f}%")
        keys(CTRL, ALT, 0x54)
        time.sleep(2)
        check(f"{name}: Ctrl+Alt+T again turns it off", read_cfg(data).get("subtitles") is False)
        # Ctrl+Alt+O: the overlay goes, the main window comes back
        keys(CTRL, ALT, 0x4F)
        gone = False
        for _ in range(40):
            if not u.FindWindowW(None, "MA-Overlay"):
                gone = True
                break
            time.sleep(0.25)
        check(f"{name}: Ctrl+Alt+O again closes it", gone)
        time.sleep(1.5)
        mains = windows_titled("Meeting Assistant")
        check(f"{name}: main window back", bool(mains) and not all(u.IsIconic(m) for m in mains), f"{[bool(u.IsIconic(m)) for m in mains]}", hard=False)
        shot_screen(os.path.join(out, f"{name}-4-screen-after.png"))
        # the overlay button path (API) as well
        r = call(port, key, "overlay", {"on": True})
        check(f"{name}: Overlay button opens it", r.get("ok") is True and r.get("on") is True, str(r)[:150])
        time.sleep(3)
        h = u.FindWindowW(None, "MA-Overlay")
        if h:
            shot_window(h, os.path.join(out, f"{name}-5-overlay-from-button.png"))
        call(port, key, "overlay", {"on": False})
        try:
            log = open(os.path.join(data, "app.log"), encoding="utf-8", errors="replace").read()
            bad = [ln for ln in log.splitlines() if "[error]" in ln or ("[warn]" in ln and any(w in ln.lower() for w in ("overlay", "see-through", "page", "helper")))]
            check(f"{name}: no overlay errors in the log", not bad, " | ".join(bad[-3:])[:400], hard=False)
            with open(os.path.join(out, f"{name}-app.log"), "w", encoding="utf-8") as f:
                f.write(log[-20000:])
        except OSError:
            pass
    finally:
        subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)], capture_output=True)
        subprocess.run(["taskkill", "/F", "/IM", "MeetingAssistant.exe"], capture_output=True)
        time.sleep(2)
        shutil.rmtree(work, ignore_errors=True)


def main():
    exe, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    scenario("A-hidden", exe, out, {"hide_from_share": True, "overlay_hide": True})
    scenario("B-visible", exe, out, {"hide_from_share": False, "overlay_hide": False})
    print("\n" + "\n".join(LINES), flush=True)
    print("RESULT: " + ("OK" if not FAILS else "FAILED - " + "; ".join(FAILS)), flush=True)
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
