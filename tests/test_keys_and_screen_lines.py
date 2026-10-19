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
    assert k["coach"] == "F9" and k["start"] == ""  # a key chosen on purpose wins over a first key (a file edited by hand)
    k = app.clean_keys({"screen": "F11", "area": "F3", "start": "F9"})
    assert k["screen"] == "F11" and k["area"] == "F3"
    k = app.clean_keys({"screen": 5, "area": None, "mark": True})
    assert k["screen"] == "F3" and k["area"] == "Shift+F3" and k["mark"] == "F7"   # damaged values: the first keys
    k = app.clean_keys({"area": "F3", "screen": "garbage"})
    assert k["area"] == "F3" and k["screen"] == ""                 # a damaged value never takes a chosen key
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
        assert not r["ok"] and "needs Alt" in r["error"]
        assert not a.api_set_key(action="g_mark", key="Ctrl+S")["ok"]       # one modifier: not from any program
        assert not a.api_set_key(action="g_mark", key="Ctrl+Alt+Shift+M")["ok"]   # the overlay's spare move key
        assert not a.api_set_key(action="answer", key="Alt+Space")["ok"]
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
        assert ov.wanted_keys() == {"g_overlay": "Ctrl+Alt+O"}       # (AltGr keyboards: the others only when needed)
        a.running = True
        assert {"g_mark", "g_say", "g_screen", "g_area"} <= set(ov.wanted_keys()) and "g_answer" not in ov.wanted_keys()
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


def test_old_ctrl_alt_shift_settings_are_kept_and_stable(app):
    c1 = app.sanitize({"hotkeys": "ctrl_alt_shift"})
    assert c1["keys"]["g_screen"] == "Ctrl+Alt+Shift+S" and c1["keys"]["g_prev"] == "Ctrl+Alt+Left"   # (Shift+arrows move the overlay)
    assert app.sanitize(c1)["keys"] == c1["keys"]                      # the same after every save
    for a, k in c1["keys"].items():
        assert not k or app.combo_problem(a, k) == "", (a, k)
    assert app.clean_keys(app.clean_keys({}, True)) == app.clean_keys({}, True)


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
        monkeypatch.setattr(a.overlay, "show_main", lambda since=None: shown.append(1))

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
        monkeypatch.setattr(a.overlay, "show_main", lambda since=None: None)

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


def test_odd_replies_are_read_well(app):
    P = app.parse_screen
    assert P("@@QUESTION: What is 2+2?\n@@ANSWER: **4**") == dict(P(""), question="What is 2+2?", answer="**4**")
    assert P("## @@QUESTION\nWhat?\n## @@ANSWER\nThis.")["answer"] == "This."
    code = "Fix:\n```diff\n@@ -1,2 +1,2 @@\n-a\n+b\n```"
    assert P(code)["answer"] == code                                   # no marker of ours: all of it
    two = P("@@QUESTION\n1. Q one\n@@ANSWER\nA one\n@@QUESTION\n2. Q two\n@@ANSWER\nA two")
    assert two["question"] == "1. Q one\n\n2. Q two" and two["answer"] == "A one\n\nA two"   # one block per question
    for partial in ("@", "**", "@@ANS"):
        assert not any(P(partial).values()), partial
    assert P("**@@QUESTION**\nQ?\n**")["question"] == "Q?"
    assert P("```\n@@QUESTION\nQ\n@@ANSWER\nA\n```")["answer"] == "A"   # the whole reply in a code block
    assert P("@@EXPLANATION\nfoo\n@@ANSWER\nbar")["answer"] == "bar"
    assert P("**@@ANSWER:** **B) 42**")["answer"] == "**B) 42**"
    f = app.Engine.screen_fields(P("@@ANSWER\n```python\nprint(1)\n```"), True)
    assert f["text"] == "Question on the screen" and f["ans_state"] == "done"
    f = app.Engine.screen_fields(P("@@NOTES\nA slide about OSPF\n- area 0\n- LSAs"), True)
    assert f["text"] == "A slide about OSPF" and f["answer"] == "- area 0\n- LSAs"


def test_screen_lines_are_not_speech(app):
    s = app.Session(app.sanitize({}))
    t = time.time()
    q = s.add("them", t, t + 2, "Tell me about OSPF", "en", [])
    sc = s.add("screen", t + 3, t + 3, "Q\n" + "x" * 900, "", [], ans_state="done", answer="A", tr_state="off")
    s.add("screen", t + 4, t + 4, "Reading the whole screen…", "", [], ans_state="thinking", tr_state="off")
    h = s.history(t + 10, 10)
    assert [n for n, _ in h] == ["Person 1", "Screen"] and len(h[1][1]) <= 300   # short, and not one still being read
    srt = app.srt_text(s.ordered(), t, s.label)
    assert "Screen" not in srt and "OSPF" in srt
    eng = app.App().tool_engine()
    eng.session = s
    assert eng.edit(sc["id"], "changed") is False and eng.answer_now(sc["id"]) is False
    s.save_if_dirty()
    rows = app.parse_meeting_md(open(s.path, encoding="utf-8").read())
    assert [r for r in rows if r[0] == "line" and r[2] == "Screen"][0][3].startswith("Q\nx")   # rows kept in one line


def test_sql_variables_and_code_blocks_survive(app):
    P = app.parse_screen
    r = P("@@QUESTION\nWhat does it return?\n@@ANSWER\n@@ROWCOUNT returns the number of rows affected.\nUse it after DML.")
    assert r["answer"] == "@@ROWCOUNT returns the number of rows affected.\nUse it after DML."
    assert P("@@ANSWER\nThe function is\n@@IDENTITY")["answer"] == "The function is\n@@IDENTITY"
    assert P("@@ANSWER\n@@global.sql_mode shows the mode")["answer"] == "@@global.sql_mode shows the mode"
    assert P("```\n@@QUESTION\nQ\n@@ANSWER\nPara one.\n\nPara two.\n```")["answer"] == "Para one.\n\nPara two."
    two = P("```python\nx=1\n```\n@@ANSWER\nfoo\n```js\nbar\n```")
    assert two["answer"] == "foo\n```js\nbar\n```"                       # (not one block around the whole reply)
    assert P("@@QUESTION\nQ\n@@ANS")["question"] == "Q" and P("@@ANSWER\nThe options are:")["answer"] == "The options are:"


def test_screen_lines_in_prompts_are_short_and_finished(app):
    rows = [{"source": "them", "text": "x" * 500, "ans_state": "none"},
            {"source": "screen", "text": "y" * 900, "ans_state": "done"},
            {"source": "screen", "text": "Reading the whole screen…", "ans_state": "thinking"}]
    out = app.for_prompt(rows)
    assert len(out) == 2 and len(out[0]["text"]) == 500 and len(out[1]["text"]) <= 300 and rows[1]["text"] == "y" * 900


def test_global_keys_need_alt(app):
    assert app.combo_problem("g_mark", "Ctrl+Shift+M") != ""            # (Teams' mute)
    assert app.combo_problem("g_mark", "Alt+Shift+M") == "" and app.combo_problem("g_mark", "Ctrl+F4") != ""
    assert app.combo_types_text("Ctrl+Alt+S") is False                  # (not on Windows here: never)
