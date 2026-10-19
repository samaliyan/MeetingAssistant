"""6.37: every key can be changed (Setup › Keys), Read my screen offers a choice first, and during a meeting a question
read from the screen becomes a line of the transcript with its translation and answer (the answer panel shows it)."""
import time

import numpy as np
import pytest


# ---- keys -----------------------------------------------------------------------------------------------------
def test_combo_spelling(app):
    assert app.parse_combo("ctrl + alt + s") == "Ctrl+Alt+S"
    assert app.parse_combo("Shift+Ctrl+F3") == "Ctrl+Shift+F3"            # one fixed order
    assert app.parse_combo("alt+pgup") == "Alt+PageUp" and app.parse_combo("Ctrl+←") == "Ctrl+Left"
    assert app.parse_combo("f12") == "F12" and app.parse_combo("space") == "Space"
    for bad in ("", "Ctrl+", "Ctrl+Ctrl+S", "Win+S", "Ctrl+Alt+Tab", "Ctrl+Escape", "Hyper+X", "Ctrl+ü"):
        assert app.parse_combo(bad) is None, bad
    assert app.combo_vk("Ctrl+Alt+S") == (0x3, 0x53) and app.combo_vk("Shift+F3") == (0x4, 0x72)
    assert app.combo_vk("Ctrl+Alt+Shift+PageDown") == (0x7, 0x22)


def test_which_keys_are_allowed(app):
    ok = lambda a, c: app.combo_problem(a, c) == ""
    assert ok("g_screen", "Ctrl+Alt+S") and ok("g_area", "Shift+F3") and ok("g_area", "F11")
    assert not ok("g_screen", "S") and not ok("g_screen", "Shift+S")      # would steal typing from every program
    assert not ok("g_screen", "Alt+F4") and not ok("g_move", "Ctrl+Alt+Shift+Left")
    assert ok("screen", "F3") and ok("waiting", "Space") and ok("prev", "Ctrl+Left") and ok("answer", "Alt+A")
    assert not ok("screen", "A") and not ok("screen", "Shift+A")          # could not be typed in the text boxes
    assert not ok("answer", "Ctrl+C") and not ok("answer", "Ctrl+V") and not ok("answer", "F5")
    assert not ok("waiting", "Ctrl+Space")


def test_defaults_and_cleaning(app):
    k = app.clean_keys({})
    assert set(k) == set(app.KEY_IDS) and k["start"] == "F9" and k["g_area"] == "Ctrl+Alt+D"
    assert len([v for v in k.values() if v]) == len(set(v for v in k.values() if v))   # no key twice
    k = app.clean_keys({"screen": "garbage", "answer": "", "pause": "Ctrl+C", "coach": "F9"})
    assert k["screen"] == "F3"                     # damaged: the default
    assert k["answer"] == ""                       # no key on purpose
    assert k["pause"] == "F8"                      # not allowed: the default
    assert k["coach"] == ""                        # F9 is taken by Start (earlier in the list): none
    k = app.clean_keys({"area": "Shift+F3", "g_area": "Shift+F3"})
    assert k["area"] == k["g_area"] == "Shift+F3"  # twins may share one key


def test_set_key_api(app):
    a = app.App()
    try:
        r = a.api_set_key(action="g_area", key="shift + f3")
        assert r["ok"] and a.cfg["keys"]["g_area"] == "Shift+F3" and r["config"]["keys"]["g_area"] == "Shift+F3"
        assert app.load_config()["keys"]["g_area"] == "Shift+F3"            # kept in the settings file
        r = a.api_set_key(action="g_screen", key="F9")
        assert not r["ok"] and "Start the meeting" in r["error"]
        r = a.api_set_key(action="g_screen", key="Q")
        assert not r["ok"] and "Ctrl or Alt" in r["error"]
        r = a.api_set_key(action="g_screen", key="Ctrl+Hyper+Q")
        assert not r["ok"] and "cannot be used" in r["error"]
        assert not a.api_set_key(action="nope", key="F2")["ok"]
        assert a.api_set_key(action="focus", key="")["ok"] and a.cfg["keys"]["focus"] == ""
        assert a.api_reset_keys()["ok"] and a.cfg["keys"]["focus"] == "F10" and a.cfg["keys"]["g_area"] == "Ctrl+Alt+D"
        pc = a.public_config()
        assert {x["id"] for x in pc["key_actions"]} == set(app.KEY_IDS)
        assert all({"scope", "default", "text", "part", "when"} <= set(x) for x in pc["key_actions"])
    finally:
        a.closing.set()


def test_keys_from_any_program_follow_the_settings(app):
    a = app.App()
    try:
        ov = a.overlay
        a.running, ov.on = False, False
        w = ov.wanted_keys()
        assert w == {"g_overlay": "Ctrl+Alt+O", "g_screen": "Ctrl+Alt+S", "g_area": "Ctrl+Alt+D"}   # always there
        a.running = True
        assert {"g_mark", "g_say"} <= set(ov.wanted_keys()) and "g_answer" not in ov.wanted_keys()
        ov.on = True
        assert {"g_answer", "g_coach", "g_prev", "g_more", "g_subs"} <= set(ov.wanted_keys())
        assert "g_move" not in ov.wanted_keys()                 # (the see-through window holds that one itself)
        a.cfg["features"] = {"screen": False}
        assert "g_screen" not in ov.wanted_keys() and "g_area" not in ov.wanted_keys()
        a.cfg["features"] = {}
        a.cfg["keys"] = dict(a.cfg["keys"], g_area="")
        assert "g_area" not in ov.wanted_keys()
        a.api_keys_pause(on=True)
        assert ov.wanted_keys() == {}                           # the page is taking a new key
        a.api_keys_pause(on=False)
        assert ov.wanted_keys()
        a.cfg["hotkeys"] = "off"
        assert ov.wanted_keys() == {}
    finally:
        a.running = False
        a.closing.set()


def test_key_names_in_messages(app):
    c = app.sanitize({})
    assert app.key_label(c, "answer") == "F2" and app.key_label(c, "g_say") == "Ctrl+Alt+J"
    c["hotkeys"] = "off"
    assert app.key_label(c, "g_say") == "" and app.key_label(c, "say") == "F6"
    c["keys"]["say"] = ""
    assert app.key_label(c, "say") == ""


def test_page_takes_keys_from_the_settings(app):
    import os
    page = open(os.path.join(app.WEB_DIR, "index.html"), encoding="utf-8").read()
    assert 'data-pane="keys"' in page and 'data-tab="keys"' in page and "function startKeyCap" in page
    assert "function winAction" in page and "function comboOf" in page and 'api("keys_pause"' in page
    # no key is written into the page any more: they come from the settings
    for old in ("<kbd>F9</kbd>", "<kbd>F2</kbd>", "<kbd>F3</kbd>", "(F7)", "(F8)", "Ctrl+Alt+O to", "F6 ends"):
        assert old not in page, old
    assert 'ev.key === "F9"' not in page and 'ev.key === "F3"' not in page


# ---- screen answers in parts ----------------------------------------------------------------------------------
def test_parse_screen_reply(app):
    p = app.parse_screen("@@QUESTION\nWhat is 6x7?\nA) 41\nB) 42\n@@TRANSLATION\nشش ضرب در هفت؟\n@@ANSWER\n**B) 42**\n"
                         "چون ۶×۷=۴۲\n@@MEANING\nگزینه‌ی ب")
    assert p["question"] == "What is 6x7?\nA) 41\nB) 42" and p["translation"] == "شش ضرب در هفت؟"
    assert p["answer"] == "**B) 42**\nچون ۶×۷=۴۲" and p["meaning"] == "گزینه‌ی ب" and p["notes"] == ""
    assert app.parse_screen("Just an answer")["answer"] == "Just an answer"          # no markers: all answer
    half = app.parse_screen("@@QUESTION\nWhat is\n@@ANS")
    assert half["question"] == "What is" and half["answer"] == ""                    # still being written
    assert app.parse_screen("**@@ANSWER:**\nyes")["answer"] == "yes"                 # a marker in bold / with colon
    n = app.parse_screen("@@NOTES\nA slide about OSPF\n- area 0")
    assert n["notes"].startswith("A slide") and n["answer"] == ""
    md = app.screen_markdown(app.parse_screen("@@QUESTION\nQ\n@@TRANSLATION\nT\n@@ANSWER\nA\n@@MEANING\nM"), "Persian")
    assert md == "## Question\nQ\nT\n## Answer\nA\n## Meaning in Persian\nM"
    assert app.screen_markdown(n, "Persian") == n["notes"]


def test_screen_line_in_the_session_and_file(app):
    s = app.Session(app.sanitize({}))
    e = s.add("screen", time.time(), time.time(), "Reading…", "", [], tr_state="off", ans_state="thinking", forced=True)
    assert e["tr_state"] == "off" and e["ans_state"] == "thinking" and e["forced"] is True
    s.update(e["id"], text="What is 6x7?", answer="**B) 42**", ans_state="done")
    assert s.label(s.get(e["id"])) == "Screen"
    s.save_if_dirty()
    txt = open(s.path, encoding="utf-8").read()
    assert "Screen:** What is 6x7?" in txt and "💡 **B) 42**" in txt
    st = app.talk_stats(s.ordered())
    assert st["them_words"] == 0                                    # a screen line is nobody's speech


@pytest.fixture
def meeting(app, monkeypatch):
    a = app.App()
    eng = a.tool_engine()                                           # an engine with a session, as in a meeting
    events, entries = [], []
    monkeypatch.setattr(app, "SCREEN_CAPTURE", True)
    monkeypatch.setattr(app, "win_rects", lambda: {"virtual": (0, 0, 1920, 1080), "front_monitor": (0, 0, 1920, 1080),
                                                   "cursor_monitor": (0, 0, 1920, 1080), "front_window": None})
    monkeypatch.setattr(app, "grab_rect", lambda r: np.zeros((r[3], r[2], 4), dtype=np.uint8).tobytes())
    monkeypatch.setattr(app, "pick_area", lambda *x, **k: (10, 10, 300, 200))
    monkeypatch.setattr(a, "vision_target", lambda quick=False: ("groq", "" if quick else "vision-x"))
    monkeypatch.setattr(a, "live_engine", lambda: eng)

    def pub(kind, **kw):
        if kind == "screen":
            events.append(kw)
        elif kind == "entry":
            entries.append(dict(kw["entry"]))
    monkeypatch.setattr(a.hub, "publish", pub)
    a.cfg["screen_delay"] = "0"
    yield a, eng, events, entries
    a.closing.set()


def test_screen_answer_goes_into_the_meeting(meeting):
    a, eng, events, entries = meeting

    def fake_read(png, pid, model, on_text=None):
        on_text("@@QUESTION\nWhat is 6x7?\n@@ANSWER\n**B")
        return ("@@QUESTION\nWhat is 6x7?\nA) 41\nB) 42\n@@TRANSLATION\nشش ضرب در هفت؟\n@@ANSWER\n**B) 42**\n"
                "@@MEANING\nگزینه‌ی ب")
    eng.read_screen = fake_read
    a._screen_job(what="area")
    rows = [r for r in eng.session.ordered() if r["source"] == "screen"]
    assert len(rows) == 1
    r = rows[0]
    assert r["text"] == "What is 6x7?\nA) 41\nB) 42" and r["translation"] == "شش ضرب در هفت؟"
    assert r["answer"] == "**B) 42**" and r["answer_fa"] == "گزینه‌ی ب" and r["ans_state"] == "done" and r["forced"]
    states = [e.get("state") for e in events]
    assert "meeting" in states and states[-1] == "done" and events[-1].get("meeting") is True
    assert entries[0]["ans_state"] == "thinking" and entries[0]["text"].startswith("Reading the area you drew")
    assert any(e["ans_state"] == "streaming" and e["answer"] == "**B" for e in entries)   # it fills in as it is written
    assert not eng.session.screens                                 # (the line is in the transcript, not a note)
    assert not a.screen_busy


def test_screen_failure_in_the_meeting_is_said_on_the_line(meeting, app):
    a, eng, events, entries = meeting

    def fail(png, pid, model, on_text=None):
        raise app.APIError("The service is busy")
    eng.read_screen = fail
    a._screen_job()
    r = [r for r in eng.session.ordered() if r["source"] == "screen"][0]
    assert r["ans_state"] == "error" and r["text"] == "Reading the screen failed"
    assert events[-1]["state"] == "error" and events[-1]["meeting"] is True and "busy" in events[-1]["note"]


def test_screen_without_a_meeting_is_a_text_in_parts(app, monkeypatch):
    a = app.App()
    try:
        events = []
        monkeypatch.setattr(app, "SCREEN_CAPTURE", True)
        monkeypatch.setattr(app, "win_rects", lambda: {"virtual": (0, 0, 800, 600), "front_monitor": (0, 0, 800, 600),
                                                       "cursor_monitor": (0, 0, 800, 600), "front_window": None})
        monkeypatch.setattr(app, "grab_rect", lambda r: np.zeros((r[3], r[2], 4), dtype=np.uint8).tobytes())
        monkeypatch.setattr(a, "vision_target", lambda quick=False: ("groq", "v"))
        monkeypatch.setattr(a, "helper", lambda: None)
        shown = []
        monkeypatch.setattr(a.overlay, "show_main", lambda: shown.append(1))

        class Eng:
            def read_screen(self, png, pid, model, on_text=None):
                return "@@QUESTION\nQ?\n@@ANSWER\nYes."
        monkeypatch.setattr(a, "tool_engine", lambda: Eng())
        monkeypatch.setattr(a.hub, "publish", lambda kind, **kw: events.append(kw) if kind == "screen" else None)
        a.cfg["screen_delay"] = "0"
        a._screen_job(what="screen")
        assert events[-1]["state"] == "done" and events[-1]["text"] == "## Question\nQ?\n## Answer\nYes."
        assert shown == []                                       # asked in this window: it is already in front
        a._screen_job(now=True, from_key=True)
        assert shown == [1]                                      # asked from another program: the window comes up
    finally:
        a.closing.set()


def test_the_window_steps_aside_only_when_asked_from_it(app, monkeypatch):
    a = app.App()
    try:
        calls = []
        monkeypatch.setattr(app, "SCREEN_CAPTURE", True)
        monkeypatch.setattr(app, "win_rects", lambda: {"virtual": (0, 0, 800, 600), "front_monitor": (0, 0, 800, 600),
                                                       "cursor_monitor": (0, 0, 800, 600), "front_window": None})
        monkeypatch.setattr(app, "grab_rect", lambda r: (calls.append("grab"), np.zeros((r[3], r[2], 4), dtype=np.uint8).tobytes())[1])
        monkeypatch.setattr(a, "vision_target", lambda quick=False: ("groq", "v"))
        monkeypatch.setattr(a, "helper", lambda: None)
        monkeypatch.setattr(a.overlay, "show_main", lambda: None)

        def own(show=None):
            calls.append("back" if show is not None else "aside")
            return [] if show is not None else [111]
        monkeypatch.setattr(a, "_own_windows", own)

        class Eng:
            def read_screen(self, png, pid, model, on_text=None):
                calls.append("read")
                return "@@ANSWER\nok"
        monkeypatch.setattr(a, "tool_engine", lambda: Eng())
        a.cfg["screen_delay"] = "0"
        a._screen_job()
        assert calls == ["aside", "grab", "back", "read"]          # back before the (slow) reading
        calls.clear()
        a._screen_job(now=True, from_key=True)
        assert calls == ["grab", "read"]
    finally:
        a.closing.set()


def test_what_choice_and_where_a_drawn_area_is_kept(meeting):
    a, eng, events, entries = meeting
    eng.read_screen = lambda png, pid, model, on_text=None: "@@ANSWER\nok"
    a.cfg["screen_area_mode"] = "screen"
    a._screen_job(what="area")                                     # the "Draw an area" button: drawn, not kept
    assert a.cfg["screen_area"] == ""
    a._screen_job(what="same")                                     # "Same area again" without one: drawn and kept
    assert a.cfg["screen_area"] == "10,10,300,200"
    a.cfg["screen_area_mode"] = "same"
    a.cfg["screen_area"] = ""
    a._screen_job(new_area=True)                                   # the area key with "same" chosen: kept
    assert a.cfg["screen_area"] == "10,10,300,200"
