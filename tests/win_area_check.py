"""Real Windows check of 'Read my screen' areas (6.36), run by .github/workflows/area-check.yml (not by pytest).

On a real Windows desktop it shows a test window with known colours and checks: the picture of a rectangle has the
right pixels, the window in front is found, the darkened screen for drawing a box appears (bright inside the box,
darker outside, the hint at the top), the box drawn with the mouse comes back in screen pixels, Esc / right click /
time out cancel, a plain click does not end it, the window is gone afterwards, hiding from screen sharing works,
nothing leaks, and the whole 'Read my screen' job reads exactly the drawn area (with a fake AI service).
Pictures of each step are written to the folder given as the first argument. Exit 1 if a hard check failed."""
import ctypes
import importlib.util
import os
import shutil
import struct
import sys
import tempfile
import threading
import time
import zlib
from ctypes import wintypes as wt

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if len(sys.argv) > 2 and sys.argv[1] == "--notes":         # the small pictures as notes on the CI run
    import base64
    folder = sys.argv[2]
    for n in sorted(os.listdir(folder) if os.path.isdir(folder) else []):
        if n.startswith("small-") and n.endswith(".png"):
            b = base64.b64encode(open(os.path.join(folder, n), "rb").read()).decode()
            print(f"::notice title={n}::" + (b if len(b) < 60000 else f"too big ({len(b)} characters)"))
    sys.exit(0)
OUT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else "area-shots")
os.makedirs(OUT, exist_ok=True)
u = ctypes.windll.user32
u.PostMessageW.argtypes = [wt.HWND, wt.UINT, wt.WPARAM, wt.LPARAM]
u.IsWindow.argtypes = [wt.HWND]
u.GetWindowDisplayAffinity.argtypes = [wt.HWND, ctypes.POINTER(wt.DWORD)]
u.GetWindowRect.argtypes = [wt.HWND, ctypes.POINTER(wt.RECT)]
u.GetWindowLongPtrW.argtypes = [wt.HWND, ctypes.c_int]
u.GetWindowLongPtrW.restype = ctypes.c_ssize_t
k = ctypes.windll.kernel32
k.GetCurrentProcess.restype = wt.HANDLE
u.GetGuiResources.argtypes = [wt.HANDLE, wt.DWORD]
FAILS, LINES = [], []


def check(name, ok, detail="", hard=True):
    LINES.append(f"[{'OK' if ok else ('FAIL' if hard else 'WARN')}] {name}: {detail}")
    print(LINES[-1], flush=True)
    if not ok and hard:
        FAILS.append(name)


# the program, from a copy in a temporary folder (it keeps its data next to app.py)
TMP = tempfile.mkdtemp(prefix="ma-area-")
shutil.copy(os.path.join(ROOT, "app.py"), os.path.join(TMP, "app.py"))
shutil.copytree(os.path.join(ROOT, "web"), os.path.join(TMP, "web"))
os.environ["MA_NO_BROWSER"] = "1"
spec = importlib.util.spec_from_file_location("ma_app", os.path.join(TMP, "app.py"))
app = importlib.util.module_from_spec(spec)
sys.modules["ma_app"] = app
spec.loader.exec_module(app)
app.make_dpi_aware()

# a test window with known colours, without a frame, always on top: red left half, green right half, a blue square
import tkinter as tk                                      # noqa: E402
TX, TY, TW, TH = 200, 150, 600, 400
root = tk.Tk()
root.overrideredirect(True)
root.attributes("-topmost", True)
root.geometry(f"{TW}x{TH}+{TX}+{TY}")
cv = tk.Canvas(root, width=TW, height=TH, highlightthickness=0, bd=0)
cv.pack(fill="both", expand=True)
cv.create_rectangle(0, 0, TW // 2, TH, fill="#ff0000", outline="")
cv.create_rectangle(TW // 2, 0, TW, TH, fill="#00ff00", outline="")
cv.create_rectangle(320, 100, 520, 300, fill="#0000ff", outline="")
BLUE = (TX + 320, TY + 100, 200, 200)
ESC_SEEN = []
root.bind_all("<Escape>", lambda e: ESC_SEEN.append(time.time()))


def pump(sec):
    end = time.time() + sec
    while time.time() < end:
        root.update()
        time.sleep(0.01)


pump(1.0)
root.focus_force()
pump(0.5)


def px(raw, full, x, y):
    """(R, G, B) of the screen pixel x, y inside a picture of the rectangle full."""
    i = ((y - full[1]) * full[2] + (x - full[0])) * 4
    return raw[i + 2], raw[i + 1], raw[i]


def near(c, want, tol=12):
    return all(abs(int(a) - b) <= tol for a, b in zip(c, want))


def save(name, raw, full, crop=None):
    w, h, data = app.crop_bgra(raw, full, crop) if crop else (full[2], full[3], raw)
    with open(os.path.join(OUT, name + ".png"), "wb") as f:
        f.write(app.encode_png(w, h, data, max_width=4000))
    with open(os.path.join(OUT, "small-" + name + ".png"), "wb") as f:
        f.write(app.encode_png(w, h, data, max_width=280))


def png_rgb(data):
    w, h = struct.unpack(">II", data[16:24])
    pos, idat = 8, b""
    while pos < len(data):
        n, kind = struct.unpack(">I4s", data[pos:pos + 8])
        if kind == b"IDAT":
            idat += data[pos + 8:pos + 8 + n]
        pos += 12 + n
    return np.frombuffer(zlib.decompress(idat), dtype=np.uint8).reshape(h, w * 3 + 1)[:, 1:].reshape(h, w, 3)


def lp(x, y):
    return (y & 0xFFFF) << 16 | (x & 0xFFFF)


def run_picker(full, raw, hide=False, timeout=60.0, steps=None):
    """Opens the box window in a thread; steps(hwnd) acts on it from here. Returns (result, seconds, error)."""
    box = {}

    def ready(h):
        box["hwnd"] = h

    def go():
        t = time.time()
        try:
            with app._DpiAwareThread():
                box["result"] = app.pick_area(raw, full, rects["cursor_monitor"], hide=hide, timeout=timeout,
                                              on_ready=ready)
        except Exception as e:
            box["error"] = e
        box["secs"] = time.time() - t
    th = threading.Thread(target=go, daemon=True)
    th.start()
    end = time.time() + 10
    while "hwnd" not in box and "error" not in box and time.time() < end:
        pump(0.05)
    if "hwnd" in box and steps:
        steps(box["hwnd"])
    end = time.time() + timeout + 10
    while th.is_alive() and time.time() < end:
        pump(0.05)
    return box.get("result", "still open" if th.is_alive() else None), box.get("secs"), box.get("error"), box.get("hwnd")


try:
    # 1. a picture of a rectangle has the right pixels
    with app._DpiAwareThread():
        rects = app.win_rects()
        raw = app.grab_rect((TX, TY, TW, TH))
    full_t = (TX, TY, TW, TH)
    check("picture of a rectangle: red, green and blue where they are",
          near(px(raw, full_t, TX + 20, TY + 20), (255, 0, 0)) and near(px(raw, full_t, TX + TW - 20, TY + 20), (0, 255, 0))
          and near(px(raw, full_t, TX + 400, TY + 200), (0, 0, 255)),
          f"{px(raw, full_t, TX + 20, TY + 20)} {px(raw, full_t, TX + TW - 20, TY + 20)} {px(raw, full_t, TX + 400, TY + 200)}")
    check("desktop and monitors found", rects["virtual"][2] > 0 and rects["cursor_monitor"][2] > 0
          and rects["front_monitor"][2] > 0, str(rects))
    check("the window in front is the test window", rects["front_window"] is not None and
          all(abs(a - b) <= 2 for a, b in zip(rects["front_window"], (TX, TY, TW, TH))), str(rects["front_window"]), hard=False)

    virt = rects["virtual"]
    with app._DpiAwareThread():
        before = app.grab_rect(virt)
    save("0-screen-before", before, virt)
    fx, fy = virt[0], virt[1]
    gdi0 = u.GetGuiResources(k.GetCurrentProcess(), 0)

    # 2. draw a box with mouse messages: darker outside, bright inside, the hint, the result in screen pixels
    seen = {}

    def drag(h):
        x0, y0, x1, y1 = TX + 50 - fx, TY + 60 - fy, TX + 450 - fx, TY + 260 - fy
        pump(0.4)
        with app._DpiAwareThread():
            seen["start"] = app.grab_rect(virt)
        st = ctypes.c_int()
        u.PostMessageW(h, 0x0201, 1, lp(x0, y0))
        u.PostMessageW(h, 0x0200, 1, lp((x0 + x1) // 2, (y0 + y1) // 2))
        u.PostMessageW(h, 0x0200, 1, lp(x1, y1))
        pump(0.5)
        with app._DpiAwareThread():
            seen["drawing"] = app.grab_rect(virt)
        aff = wt.DWORD()
        u.GetWindowDisplayAffinity(h, ctypes.byref(aff))
        seen["aff"] = aff.value
        seen["ex"] = u.GetWindowLongPtrW(h, -20)
        r = wt.RECT()
        u.GetWindowRect(h, ctypes.byref(r))
        seen["rect"] = (r.left, r.top, r.right - r.left, r.bottom - r.top)
        u.PostMessageW(h, 0x0202, 0, lp(x1, y1))
    res, secs, err, hwnd = run_picker(virt, before, steps=drag)
    check("box drawn with the mouse comes back in screen pixels", res == (TX + 50, TY + 60, 400, 200), f"{res} {err or ''}")
    check("the box window covers all screens, on top, not in the taskbar",
          seen.get("rect") == tuple(virt) and seen.get("ex", 0) & 0x08000088 == 0x08000088,
          f"{seen.get('rect')} ex={hex(seen.get('ex', 0))} (topmost, tool window, never activated)")
    check("not hidden from capture when hiding is off", seen.get("aff") == 0, hex(seen.get("aff", -1)))
    if "drawing" in seen:
        d = seen["drawing"]
        save("1-start-dark-with-hint", seen["start"], virt, rects["cursor_monitor"])
        save("2-box-being-drawn", d, virt, rects["cursor_monitor"])
        inside, outside = px(d, virt, TX + 100, TY + 100), px(d, virt, TX + 20, TY + 350)
        check("inside the box the screen is bright", near(inside, (255, 0, 0)), str(inside))
        check("outside the box the screen is darker (3/8)", near(outside, (96, 0, 0), 6), str(outside))
        border = px(d, virt, TX + 50 - 1, TY + 150)
        check("a blue border around the box", near(border, (0x30, 0xA0, 0xF0), 8), str(border))
        cm = rects["cursor_monitor"]
        s = seen["start"]
        fs = max(16, min(40, cm[3] // 45))
        hint_px = [px(s, virt, cm[0] + cm[2] // 2 + dx, cm[1] + fs + int(fs * 2.2) // 2 + dy)
                   for dx in range(-220, 220, 3) for dy in (-3, 0, 3)]
        check("the hint is shown at the top (panel and white text)",
              any(near(p, (0x28, 0x28, 0x30), 3) for p in hint_px) and any(min(p) > 200 for p in hint_px),
              f"{len(hint_px)} pixels looked at")
    pump(0.4)
    with app._DpiAwareThread():
        after = app.grab_rect(virt)
    check("the box window is gone afterwards", hwnd and not u.IsWindow(hwnd) and near(px(after, virt, TX + 20, TY + 350), (255, 0, 0)),
          str(px(after, virt, TX + 20, TY + 350)))

    # 3. ways to cancel
    res, secs, err, _ = run_picker(virt, before, steps=lambda h: (pump(0.3), u.PostMessageW(h, 0x0100, 0x1B, 0)))
    check("Esc cancels", res is None and err is None and secs < 5, f"{res} {secs and round(secs, 2)}s {err or ''}")
    res, secs, err, _ = run_picker(virt, before, steps=lambda h: (pump(0.3), u.PostMessageW(h, 0x0204, 2, lp(10, 10)),
                                                                  pump(0.3), seen.__setitem__("open_after_rdown", bool(u.IsWindow(h))),
                                                                  u.PostMessageW(h, 0x0205, 0, lp(10, 10))))
    check("a right click cancels when the button comes up", res is None and err is None and seen.get("open_after_rdown"),
          f"{res} {err or ''}")
    res, secs, err, _ = run_picker(virt, before, timeout=1.5)
    check("nothing drawn: it ends by itself", res is None and err is None and 1.3 < secs < 4, f"{res} {secs and round(secs, 2)}s")

    def click_then_drag(h):
        pump(0.3)
        u.PostMessageW(h, 0x0201, 1, lp(TX + 10 - fx, TY + 10 - fy))
        u.PostMessageW(h, 0x0202, 0, lp(TX + 12 - fx, TY + 11 - fy))     # a click, not a box
        pump(0.6)
        seen["after_click_open"] = bool(u.IsWindow(h))
        u.PostMessageW(h, 0x0201, 1, lp(BLUE[0] + BLUE[2] - fx, BLUE[1] + BLUE[3] - fy))   # dragged up-left
        u.PostMessageW(h, 0x0200, 1, lp(BLUE[0] - fx, BLUE[1] - fy))
        u.PostMessageW(h, 0x0202, 0, lp(BLUE[0] - fx, BLUE[1] - fy))
    res, secs, err, _ = run_picker(virt, before, steps=click_then_drag)
    check("a plain click does not end it; a box dragged up-left does", seen.get("after_click_open") and res == BLUE, f"{res}")

    def past_the_edge(h):                                 # dragged beyond the left / top edge: cut at the edge
        pump(0.3)
        u.PostMessageW(h, 0x0201, 1, lp(TX + 100 - fx, TY + 100 - fy))
        u.PostMessageW(h, 0x0200, 1, lp(-60, -40))
        u.PostMessageW(h, 0x0202, 0, lp(-60, -40))
    res, secs, err, _ = run_picker(virt, before, steps=past_the_edge)
    check("a box dragged past the edge stays inside the picture", res == (fx, fy, TX + 100 - fx, TY + 100 - fy), f"{res}")

    def lost_up(h):                                       # the button came up where the box window did not see it
        pump(0.3)
        u.PostMessageW(h, 0x0201, 1, lp(TX + 10 - fx, TY + 10 - fy))
        u.PostMessageW(h, 0x0200, 1, lp(TX + 110 - fx, TY + 60 - fy))
        u.PostMessageW(h, 0x0200, 0, lp(TX + 120 - fx, TY + 70 - fy))   # moved with no button held
    res, secs, err, _ = run_picker(virt, before, steps=lost_up)
    check("a lost button-up ends the box where the mouse is", res == (TX + 10, TY + 10, 110, 60), f"{res}")

    # 4. the real mouse and the real Esc key (best effort: the runner's desktop may not take input)
    def real_mouse(h):
        pump(0.3)
        u.SetCursorPos(TX + 100, TY + 100)
        u.mouse_event(0x0002, 0, 0, 0, 0)
        for i in range(1, 11):
            pump(0.03)
            u.SetCursorPos(TX + 100 + 20 * i, TY + 100 + 10 * i)
        u.mouse_event(0x0004, 0, 0, 0, 0)
    res, secs, err, _ = run_picker(virt, before, timeout=6, steps=real_mouse)
    check("real mouse drag", res == (TX + 100, TY + 100, 200, 100), f"{res}", hard=False)

    u.GetForegroundWindow.restype = wt.HWND
    root.focus_force()
    pump(0.4)
    fg_before = u.GetForegroundWindow()

    def tap_esc():
        u.keybd_event(0x1B, 0, 0, 0)
        pump(0.1)
        u.keybd_event(0x1B, 0, 2, 0)
        pump(0.4)
    ESC_SEEN.clear()
    tap_esc()
    esc_reaches_test_window = bool(ESC_SEEN)              # (the control: without a box, Esc reaches the test window)
    ESC_SEEN.clear()

    def real_esc(h):
        pump(0.3)
        seen["fg_during"] = u.GetForegroundWindow()
        u.keybd_event(0x1B, 0, 0, 0)
        pump(0.15)
        u.keybd_event(0x1B, 0, 2, 0)
    res, secs, err, _ = run_picker(virt, before, timeout=6, steps=real_esc)
    pump(0.3)
    check("real Esc key (also without the keyboard focus)", res is None and secs is not None and secs < 4,
          f"{res} {secs and round(secs, 2)}s", hard=False)
    esc_during = len(ESC_SEEN)
    ESC_SEEN.clear()
    tap_esc()
    esc_after = bool(ESC_SEEN)
    check("the box window does not take the focus from the program in front",
          bool(fg_before) and seen.get("fg_during") == fg_before, f"{seen.get('fg_during')} vs {fg_before}", hard=False)
    check("Esc does not reach the program below (and does again after the box)",
          esc_reaches_test_window and esc_during == 0 and esc_after,
          f"before {esc_reaches_test_window}, during {esc_during}, after {esc_after}", hard=False)

    # 5. hidden from screen sharing: the other side keeps seeing the real screen
    if app.capture_hide_supported():
        def hidden(h):
            pump(0.5)
            aff = wt.DWORD()
            u.GetWindowDisplayAffinity(h, ctypes.byref(aff))
            seen["aff_hidden"] = aff.value
            with app._DpiAwareThread():
                seen["shot_hidden"] = app.grab_rect(virt)
            u.PostMessageW(h, 0x0100, 0x1B, 0)
        run_picker(virt, before, hide=True, steps=hidden)
        check("hidden from capture when hiding is on (affinity)", seen.get("aff_hidden") == 0x11, hex(seen.get("aff_hidden", -1)))
        if "shot_hidden" in seen:
            save("3-hidden-picker-as-others-see-it", seen["shot_hidden"], virt, rects["cursor_monitor"])
            p = px(seen["shot_hidden"], virt, TX + 20, TY + 350)
            check("a screen picture does not show the darkened screen", near(p, (255, 0, 0)), str(p), hard=False)
    else:
        check("hiding from capture", True, "this Windows is too old - not checked")

    # 6. nothing leaks (GDI objects) after many boxes
    for _ in range(6):
        run_picker(virt, before, steps=lambda h: (pump(0.1), u.PostMessageW(h, 0x0100, 0x1B, 0)))
    gdi1 = u.GetGuiResources(k.GetCurrentProcess(), 0)
    check("no GDI objects left over", gdi1 - gdi0 <= 4, f"{gdi0} -> {gdi1}")

    # 7. the whole job: 'Read my screen' reads exactly the drawn area, then the same area again
    a = app.App()
    got, events = [], []

    class Eng:
        def read_screen(self, png, pid, model, on_text=None):
            got.append(png)
            return "@@QUESTION\nWhat is 6x7?\n@@ANSWER\n**B) 42**"
    a.vision_target = lambda quick=False: ("groq", "fake-vision")
    a.helper = lambda: None
    a.tool_engine = lambda: Eng()
    a.hub.publish = lambda kind, **kw: events.append(kw) if kind == "screen" else None
    real_pick = app.pick_area

    def pick_with_drag(raw, full, hint_mon, **kw):
        def ready(h):
            def act():
                time.sleep(0.4)
                fx_, fy_ = full[0], full[1]
                u.PostMessageW(h, 0x0201, 1, lp(BLUE[0] + 20 - fx_, BLUE[1] + 20 - fy_))
                u.PostMessageW(h, 0x0200, 1, lp(BLUE[0] + 180 - fx_, BLUE[1] + 120 - fy_))
                u.PostMessageW(h, 0x0202, 0, lp(BLUE[0] + 180 - fx_, BLUE[1] + 120 - fy_))
            threading.Thread(target=act, daemon=True).start()
        return real_pick(raw, full, hint_mon, on_ready=ready, **{x: y for x, y in kw.items() if x != "on_ready"})
    app.pick_area = pick_with_drag
    a.cfg["screen_area_mode"] = "same"

    def job(**kw):
        th = threading.Thread(target=a._screen_job, kwargs=kw, daemon=True)
        th.start()
        while th.is_alive():
            pump(0.05)
    job(now=True, from_key=True)
    ok = bool(got)
    if ok:
        rgb = png_rgb(got[-1])
        with open(os.path.join(OUT, "4-area-sent-to-the-model.png"), "wb") as f:
            f.write(got[-1])
        ok = rgb.shape[:2] == (200, 320) and (np.abs(rgb.astype(int) - (0, 0, 255)) <= 12).all()   # 160x100, sent 2x
    check("the job reads exactly the drawn area (all blue, sent twice as big)", ok,
          f"{got and png_rgb(got[-1]).shape} last={events and events[-1].get('state')} {events and events[-1].get('note', '')}")
    check("the area is kept for next time", a.cfg["screen_area"] == f"{BLUE[0] + 20},{BLUE[1] + 20},160,100", a.cfg["screen_area"])
    app.pick_area = lambda *x, **y: (_ for _ in ()).throw(AssertionError("must not draw again"))
    job(now=True, from_key=True)
    check("the same area is read again without drawing", len(got) == 2 and (np.abs(png_rgb(got[-1]).astype(int) - (0, 0, 255)) <= 12).all(),
          f"{len(got)} {events and events[-1].get('state')}")
    a.cfg["screen_area_mode"] = "window"
    root.focus_force()
    pump(0.5)
    job(now=True, from_key=True)
    check("the window in front is read (sent twice as big: it is small)", len(got) == 3 and png_rgb(got[-1]).shape[:2] == (2 * TH, 2 * TW),
          f"{got and png_rgb(got[-1]).shape}", hard=False)
    check("the result is in parts", events and events[-1].get("state") == "done"
          and events[-1].get("text") == "## Question\nWhat is 6x7?\n## Answer\n**B) 42**", str(events and events[-1]))

    # 8. asked from this program's window: its window steps aside for the picture and comes back
    notes = tk.Toplevel(root)
    notes.title("Notes")
    notes.geometry("300x200+850+150")
    pump(0.8)
    u.FindWindowW.argtypes = [wt.LPCWSTR, wt.LPCWSTR]
    u.FindWindowW.restype = wt.HWND
    u.IsIconic.argtypes = [wt.HWND]
    nh = u.FindWindowW(None, "Notes")
    seen_iconic = []
    real_grab = app.grab_rect
    app.grab_rect = lambda r: (seen_iconic.append(bool(u.IsIconic(nh))), real_grab(r))[1]
    a.cfg["screen_area_mode"] = "screen"
    a.overlay.show_main = lambda since=None: None
    job()
    pump(0.8)
    check("its own window is minimized while the picture is taken", bool(nh) and seen_iconic == [True], f"{nh} {seen_iconic}")
    check("and comes back afterwards", bool(nh) and not u.IsIconic(nh), str(bool(nh and u.IsIconic(nh))))
    seen_iconic.clear()
    job(now=True, from_key=True)
    check("from another program it stays where it is", seen_iconic == [False], str(seen_iconic))
    app.grab_rect = real_grab
    notes.destroy()

    # 9. keys from any program: the keys of Setup › Keys can be held (and given back)
    u.RegisterHotKey.argtypes = [wt.HWND, ctypes.c_int, wt.UINT, wt.UINT]
    u.UnregisterHotKey.argtypes = [wt.HWND, ctypes.c_int]
    held = []
    for i, combo in enumerate(("Ctrl+Alt+D", "Shift+F3", "Ctrl+Alt+Shift+S", "Alt+F11"), 7700):
        mods, vk = app.combo_vk(combo)
        if u.RegisterHotKey(None, i, mods | 0x4000, vk):
            held.append(combo)
            u.UnregisterHotKey(None, i)
    check("keys of Setup › Keys can be held from any program", len(held) == 4, ", ".join(held))
    a.closing.set()
except Exception as e:
    import traceback
    check("no crash", False, traceback.format_exc())
finally:
    try:
        root.destroy()
    except Exception:
        pass

print()
print(f"{len(LINES) - len(FAILS)} of {len(LINES)} checks passed" + (f"; failed: {', '.join(FAILS)}" if FAILS else ""))
with open(os.path.join(OUT, "report.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(LINES) + "\n")
sys.exit(1 if FAILS else 0)
