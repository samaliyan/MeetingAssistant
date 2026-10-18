"""6.36: what 'Read my screen' reads (whole screen, window in front, an area drawn with the mouse, the same area
again) and the layout of the answer (the question in my language, the answer, what it means).

The Windows parts (taking the picture, the window where the box is drawn) are replaced by fakes here; they are
checked on a real Windows machine by tests/win_area_check.py."""
import struct
import zlib

import numpy as np
import pytest


def _png_size(data):
    assert data[:8] == b"\x89PNG\r\n\x1a\n"
    w, h = struct.unpack(">II", data[16:24])
    return w, h


def _png_pixels(data):
    pos, idat = 8, b""
    w, h = _png_size(data)
    while pos < len(data):
        n, kind = struct.unpack(">I4s", data[pos:pos + 8])
        if kind == b"IDAT":
            idat += data[pos + 8:pos + 8 + n]
        pos += 12 + n
    raw = np.frombuffer(zlib.decompress(idat), dtype=np.uint8).reshape(h, w * 3 + 1)
    return raw[:, 1:].reshape(h, w, 3)                          # RGB


# ---- small pieces ---------------------------------------------------------------------------------------------
def test_area_text_round_trip_and_bad_values(app):
    assert app.parse_area("10,-20,300,200") == (10, -20, 300, 200)
    assert app.parse_area(" -1920 , 0 , 800 , 600 ") == (-1920, 0, 800, 600)
    assert app.area_text((10, -20, 300, 200)) == "10,-20,300,200"
    for bad in ("", None, "1,2,3", "a,b,c,d", "0,0,4,100", "0,0,100,4", "0,0,99999999,10", "1,2,3,4,5", "0,0,-5,10"):
        assert app.parse_area(bad) is None, bad


def test_rectangles(app):
    assert app.drag_rect(300, 200, 100, 50) == (100, 50, 200, 150)            # dragged up and to the left
    assert app.drag_rect(5, 5, 5, 5) == (5, 5, 0, 0)
    assert app.clip_rect((-100, -100, 300, 300), (0, 0, 1920, 1080)) == (0, 0, 200, 200)
    assert app.clip_rect((1915, 0, 300, 300), (0, 0, 1920, 1080)) is None     # (almost) off the screen
    assert app.clip_rect((3000, 0, 300, 300), (0, 0, 1920, 1080)) is None
    assert app._overlap((0, 0, 10, 10), (9, 9, 5, 5)) == (9, 9, 1, 1)
    assert app._overlap((0, 0, 10, 10), (10, 0, 5, 5)) is None


def test_crop_takes_the_right_pixels_from_a_desktop_that_starts_left_of_zero(app):
    full = (-1920, 0, 3840, 1080)                                       # second monitor on the left
    a = np.zeros((1080, 3840, 4), dtype=np.uint8)
    a[100:150, 2000:2100] = (10, 20, 200, 255)                         # a red patch at screen x 80..180, y 100..150
    w, h, raw = app.crop_bgra(a.tobytes(), full, (80, 100, 100, 50))
    assert (w, h) == (100, 50)
    px = np.frombuffer(raw, dtype=np.uint8).reshape(h, w, 4)
    assert (px[:, :, 2] == 200).all() and (px[:, :, 0] == 10).all()


def test_small_area_is_sent_bigger_and_big_screen_smaller(app):
    a = np.zeros((40, 60, 4), dtype=np.uint8)
    a[:, :, 2] = 255
    a[0, 0] = (0, 255, 0, 255)                                          # one green pixel in the corner
    png = app.screen_png(60, 40, a.tobytes())
    assert _png_size(png) == (120, 80)                                  # twice as big: small letters read better
    rgb = _png_pixels(png)
    assert list(rgb[0, 0]) == [0, 255, 0] and list(rgb[1, 1]) == [0, 255, 0] and list(rgb[2, 2]) == [255, 0, 0]
    big = np.zeros((1080, 1920, 4), dtype=np.uint8)
    assert _png_size(app.screen_png(1920, 1080, big.tobytes())) == (1920, 1080)
    huge = np.zeros((2160, 3840, 4), dtype=np.uint8)
    assert _png_size(app.screen_png(3840, 2160, huge.tobytes()))[0] == 1920
    noisy = np.random.default_rng(1).integers(0, 255, (1440, 2560, 4), dtype=np.uint8)
    png = app.screen_png(2560, 1440, noisy.tobytes())                   # does not compress: made smaller until it fits
    assert len(png) * 4 // 3 <= 3_200_000 or _png_size(png)[0] == 960


# ---- settings ---------------------------------------------------------------------------------------------------
def test_settings_for_what_is_read(app):
    c = app.sanitize({})
    assert c["screen_area_mode"] == "screen" and c["screen_area"] == ""      # unchanged behaviour by default
    c = app.sanitize({"screen_area_mode": "same", "screen_area": " 5, 6 ,700,80"})
    assert c["screen_area_mode"] == "same" and c["screen_area"] == "5,6,700,80"
    c = app.sanitize({"screen_area_mode": "everything", "screen_area": "evil"})
    assert c["screen_area_mode"] == "screen" and c["screen_area"] == ""
    a = app.App()
    try:
        a.cfg["screen_area"] = "1,2,300,400"
        a.api_save_config(screen_area="9,9,900,900", screen_area_mode="window")
        assert a.cfg["screen_area"] == "1,2,300,400"                   # set only by drawing, never by the page
        assert a.cfg["screen_area_mode"] == "window"
    finally:
        a.closing.set()


# ---- the answer's layout ----------------------------------------------------------------------------------------
def test_screen_prompt_layout(app):
    c = app.sanitize({"my_language": "fa", "languages": ["en"], "answer_language": "same", "answer_fa": True})
    p = app.screen_prompt(c)
    assert "Persian (Farsi)" in p
    for part in ("## The question", "## The answer", "## What the answer means"):
        assert part in p
    assert "Multiple choice" in p and "letter or number of the right option" in p and "**B) 42**" in p
    assert "in the language of the question on the screen (English)" in p
    assert "several questions" in p and "cut off or unreadable" in p and "[your name]" in p
    c2 = dict(c, answer_fa=False, answer_language="de")
    p2 = app.screen_prompt(c2)
    assert "What the answer means" not in p2 and "in German" in p2


def test_read_screen_sends_the_layout_and_the_picture(app):
    a = app.App()
    try:
        eng = a.tool_engine()
        sent = {}

        def fake_chat(targets, messages, max_tokens, temp, on_text):
            sent.update(targets=targets, messages=messages, max_tokens=max_tokens)
            on_text("## The question\nx")
            return "## The question\nx\n## The answer\n**B) 42**"
        eng.run_chat = fake_chat
        out = eng.read_screen(b"\x89PNG-fake", "groq", "some-vision-model")
        assert out.endswith("**B) 42**")
        assert sent["targets"] == [("groq", "some-vision-model", None)] and sent["max_tokens"] >= 3000
        system, user = sent["messages"]
        assert "## The answer" in system["content"]
        assert user["content"][1]["image_url"]["url"].startswith("data:image/png;base64,")
    finally:
        a.closing.set()


# ---- the screen job with the Windows parts replaced -------------------------------------------------------------
VIRT = (-1920, 0, 3840, 1080)
FRONT_MON = (0, 0, 1920, 1080)
CURSOR_MON = (-1920, 0, 1920, 1080)
FRONT_WIN = (100, 50, 1200, 800)


@pytest.fixture
def job(app, monkeypatch):
    a = app.App()
    calls = {"grab": [], "pick": [], "read": [], "events": []}
    front = {"win": FRONT_WIN}

    def fake_grab(r):
        calls["grab"].append(tuple(r))
        return np.zeros((r[3], r[2], 4), dtype=np.uint8).tobytes()

    def fake_pick(raw, full, hint_mon, hide=False, timeout=60.0, stop=None, on_ready=None):
        calls["pick"].append({"full": full, "hint": hint_mon, "hide": hide, "len": len(raw)})
        return calls.get("pick_result", (-1500, 200, 400, 300))

    class Eng:
        def read_screen(self, png, pid, model):
            calls["read"].append((_png_size(png), pid, model))
            return "## The answer\n**B) 42**"
    monkeypatch.setattr(app, "SCREEN_CAPTURE", True)
    monkeypatch.setattr(app, "win_rects", lambda: {"virtual": VIRT, "front_monitor": FRONT_MON,
                                                   "cursor_monitor": CURSOR_MON, "front_window": front["win"]})
    monkeypatch.setattr(app, "grab_rect", fake_grab)
    monkeypatch.setattr(app, "pick_area", fake_pick)
    monkeypatch.setattr(a, "vision_target", lambda quick=False: ("groq", "" if quick else "vision-x"))
    monkeypatch.setattr(a, "helper", lambda: None)
    monkeypatch.setattr(a, "tool_engine", lambda: Eng())
    monkeypatch.setattr(a.hub, "publish", lambda kind, **kw: calls["events"].append((kind, kw)) if kind == "screen" else None)
    a.cfg["screen_delay"] = "0"
    calls["front"] = front
    yield a, calls
    a.closing.set()


def _states(calls):
    return [kw.get("state") for k, kw in calls["events"]]


def test_whole_screen_is_the_default(job):
    a, calls = job
    a._screen_job()
    assert calls["grab"] == [FRONT_MON] and calls["pick"] == []
    assert calls["read"][0][0] == (1920, 1080) and calls["read"][0][1:] == ("groq", "vision-x")
    assert _states(calls)[-1] == "done" and not a.screen_busy
    assert "the whole screen" in " ".join(kw.get("note", "") for k, kw in calls["events"])


def test_window_in_front(job):
    a, calls = job
    a.cfg["screen_area_mode"] = "window"
    a._screen_job()
    assert calls["grab"] == [FRONT_WIN] and calls["read"][0][0] == (1200, 800)
    calls["grab"].clear()
    calls["front"]["win"] = None                                       # desktop or taskbar in front: the whole screen
    a._screen_job()
    assert calls["grab"] == [FRONT_MON]


def test_area_drawn_each_time(job):
    a, calls = job
    a.cfg["screen_area_mode"] = "area"
    a.cfg["hide_from_share"] = False
    a.cfg["overlay_hide"] = False
    a._screen_job()
    assert calls["grab"] == [VIRT]                                     # one picture of all screens, the box is cut from it
    p = calls["pick"][0]
    assert p["full"] == VIRT and p["hint"] == CURSOR_MON and p["hide"] is False and p["len"] == 3840 * 1080 * 4
    assert calls["read"][0][0] == (800, 600)                           # 400x300 drawn: sent twice as big
    assert a.cfg["screen_area"] == ""                                  # "each time": nothing kept
    assert any("Draw a box" in kw.get("note", "") for k, kw in calls["events"])
    a._screen_job()
    assert len(calls["pick"]) == 2                                     # drawn again


def test_same_area_is_drawn_once_then_reused(job, app):
    a, calls = job
    a.cfg["screen_area_mode"] = "same"
    a._screen_job()
    assert len(calls["pick"]) == 1 and a.cfg["screen_area"] == "-1500,200,400,300"
    assert app.load_config()["screen_area"] == "-1500,200,400,300"    # kept in the settings file (after a restart too)
    calls["grab"].clear()
    a._screen_job()
    assert len(calls["pick"]) == 1 and calls["grab"] == [(-1500, 200, 400, 300)]   # no drawing, the same area
    a._screen_job(new_area=True)                                       # Shift+F3 / "New area"
    assert len(calls["pick"]) == 2


def test_same_area_that_is_no_longer_on_a_screen_is_drawn_again(job):
    a, calls = job
    a.cfg["screen_area_mode"] = "same"
    a.cfg["screen_area"] = "5000,0,400,300"                            # that monitor was unplugged
    a._screen_job()
    assert len(calls["pick"]) == 1 and a.cfg["screen_area"] == "-1500,200,400,300"


def test_drawing_cancelled_reads_nothing(job):
    a, calls = job
    a.cfg["screen_area_mode"] = "area"
    calls["pick_result"] = None                                        # Esc, right click or 60 s without a box
    a._screen_job()
    assert calls["read"] == [] and _states(calls)[-1] == "cancelled" and not a.screen_busy
    assert a.cfg["screen_area"] == ""


def test_new_area_also_works_when_the_whole_screen_is_chosen(job):
    a, calls = job
    a._screen_job(new_area=True)
    assert len(calls["pick"]) == 1 and calls["read"][0][0] == (800, 600)
    assert a.cfg["screen_area"] == ""                                  # only "same" keeps the area


def test_hidden_from_sharing_follows_the_settings(job, app, monkeypatch):
    a, calls = job
    a.cfg["screen_area_mode"] = "area"
    a.cfg["overlay_hide"] = True
    monkeypatch.setattr(app, "capture_hide_supported", lambda: True)
    a._screen_job()
    assert calls["pick"][-1]["hide"] is True
    monkeypatch.setattr(app, "capture_hide_supported", lambda: False)  # old Windows: hiding would show a black box
    a._screen_job()
    assert calls["pick"][-1]["hide"] is False


def test_countdown_only_for_the_button_not_for_the_global_key(job, monkeypatch, app):
    a, calls = job
    a.cfg["screen_delay"] = "2"
    slept = []
    monkeypatch.setattr(app.time, "sleep", lambda s: slept.append(s))
    a._screen_job(now=True)
    assert slept == [] and calls["read"]
    a._screen_job()
    assert slept == [1, 1]
    a.cfg["screen_area_mode"] = "area"
    calls["events"].clear()
    a._screen_job()
    assert any("you draw a box" in kw.get("note", "") for k, kw in calls["events"])


def test_no_picture_service_is_said_before_the_countdown(job, app, monkeypatch):
    a, calls = job

    def no_service(quick=False):
        raise app.APIError("Reading the screen needs an online AI service with an API key")
    monkeypatch.setattr(a, "vision_target", no_service)
    a.cfg["screen_area_mode"] = "area"
    a._screen_job()
    assert calls["pick"] == [] and calls["grab"] == [] and _states(calls)[-1] == "error"


def test_api_screen_passes_the_choices(job, monkeypatch):
    a, calls = job
    got = []
    monkeypatch.setattr(a, "_screen_job", lambda new_area=False, now=False: got.append((new_area, now)))
    assert a.call("screen", {"new_area": True})["ok"]
    import time
    for _ in range(50):
        if got:
            break
        time.sleep(0.02)
    assert got == [(True, False)]


def test_page_has_the_new_controls():
    import os
    page = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "web", "index.html"),
                encoding="utf-8").read()
    assert 'data-key="screen_area_mode"' in page
    for v in ("screen", "window", "area", "same"):
        assert f'<option value="{v}">' in page
    assert "readScreen(ev.shiftKey)" in page and "New area" in page and '"cancelled"' in page
    assert "function lineDir(" in page and "mdLite(m.text, true)" in page


# ---- after the review ----------------------------------------------------------------------------------------
def test_tall_narrow_picture_is_made_smaller_too(app):
    noisy = np.random.default_rng(2).integers(0, 255, (4000, 900, 4), dtype=np.uint8)
    png = app.screen_png(900, 4000, noisy.tobytes())
    assert len(png) * 4 // 3 <= 3_200_000 and _png_size(png)[1] < 4000


def test_box_outside_the_picture_is_cut_to_it(job, app):
    a, calls = job
    a.cfg["screen_area_mode"] = "same"
    calls["pick_result"] = (-2500, 100, 1000, 200)              # dragged past the left edge of the desktop
    a._screen_job()
    assert calls["read"][0][0] == (840, 400)                          # 420x200 left inside the desktop, sent 2x
    assert a.cfg["screen_area"] == "-1920,100,420,200"


def test_closing_during_the_countdown_ends_the_job(job, app, monkeypatch):
    a, calls = job
    a.cfg["screen_delay"] = "3"
    monkeypatch.setattr(app.time, "sleep", lambda s: a.leaving.set())
    a._screen_job()
    assert calls["grab"] == [] and _states(calls)[-1] == "cancelled" and not a.screen_busy


def test_area_picker_stops_when_the_program_leaves(job, app):
    a, calls = job
    a.cfg["screen_area_mode"] = "area"
    seen = {}
    real = app.pick_area

    def pick(raw, full, hint_mon, **kw):
        seen["stop"] = kw.get("stop")
        return (0, 0, 100, 100)
    app.pick_area = pick
    try:
        a._screen_job()
    finally:
        app.pick_area = real
    assert seen["stop"] is a.leaving


def test_api_screen_resets_busy_after_an_error(job, app, monkeypatch):
    a, calls = job
    monkeypatch.setattr(app, "grab_rect", lambda r: (_ for _ in ()).throw(app.APIError("The screen could not be captured.")))
    assert a.api_screen()["ok"]
    import time
    for _ in range(100):
        if not a.screen_busy:
            break
        time.sleep(0.02)
    assert not a.screen_busy and _states(calls)[-1] == "error"
    assert "could not be captured" in calls["events"][-1][1]["note"]


def test_prompt_after_review(app):
    c = app.sanitize({"my_language": "fa", "languages": ["en"], "answer_language": "fa", "answer_fa": True})
    assert "What the answer means" not in app.screen_prompt(c)          # the answer is already in my language
    c = app.sanitize({"my_language": "fa", "languages": ["en"], "meeting_mode": "lecture"})
    assert "NO_REPLY" not in app.screen_prompt(c)
    p = app.screen_prompt(app.sanitize({"my_language": "fa", "languages": ["en"]}))
    assert "translated too" in p and "option texts" not in p
