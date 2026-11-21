"""6.42 screen mode: nothing is listened to; every question comes from a picture of the screen."""
import os
import time

import numpy as np
import pytest


def _wait(cond, secs=10):
    end = time.time() + secs
    while time.time() < end:
        if cond():
            return True
        time.sleep(0.05)
    return False


def test_screen_mode_rules(app):
    c = app.sanitize({"work_mode": "screen", "features": {"answers": False, "screen": False, "coach": True}})
    assert c["work_mode"] == "screen" and c["subtitles"] is False
    assert app.screen_only(c) and not app.use_mic(c) and not app.use_loop(c)
    assert app.feat(c, "screen") and app.feat(c, "answers")          # always on there, whatever was turned off
    for part in ("coach", "say", "detect", "prep", "files"):
        assert not app.feat(c, part)
    back = dict(c, work_mode="meeting")
    assert not app.feat(back, "answers") and app.feat(back, "coach")  # the user's own choices apply again


def test_page_and_program_agree_on_screen_mode(app):
    page = open(os.path.join(app.WEB_DIR, "index.html"), encoding="utf-8").read()
    assert 'data-mode="screen"' in page and 'id="mbArea"' in page
    assert 'SCREEN_ON = ["screen", "answers"]' in page
    assert 'SCREEN_OFF = ["coach", "say", "detect", "prep", "files"]' in page
    assert app.SCREEN_ON == ("screen", "answers") and app.SCREEN_OFF == ("coach", "say", "detect", "prep", "files")


@pytest.fixture
def screen_app(app, monkeypatch):
    a = app.App()
    a.cfg.update(app.sanitize(dict(a.cfg, work_mode="screen", api_key="gsk_" + "s" * 40,
                                   context="CCNA practice exam, multiple choice")))
    monkeypatch.setattr(app, "pyaudio", None)                         # screen mode needs no audio library at all
    monkeypatch.setattr(a, "preflight", lambda: "")
    monkeypatch.setattr(app, "SCREEN_CAPTURE", True)
    monkeypatch.setattr(app, "win_rects", lambda: {"virtual": (0, 0, 1920, 1080), "front_monitor": (0, 0, 1920, 1080),
                                                   "cursor_monitor": (0, 0, 1920, 1080), "front_window": None})
    monkeypatch.setattr(app, "grab_rect", lambda r: np.zeros((r[3], r[2], 4), dtype=np.uint8).tobytes())
    monkeypatch.setattr(app, "pick_area", lambda *x, **k: (10, 10, 300, 200))
    monkeypatch.setattr(a, "vision_target", lambda quick=False: ("groq", "" if quick else "vision-x"))
    monkeypatch.setattr(a, "_own_windows", lambda show=None: [])
    yield a
    if a.running:
        a.api_stop()
        _wait(lambda: not a.stopping)


def test_screen_mode_starts_without_sound_and_numbers_each_question(app, screen_app, monkeypatch):
    a = screen_app
    assert a.needed_tasks(at_start=True) == ("ans",)                  # no speech to text, no translation service
    r = a.api_start()
    assert r == {"ok": True}, r
    assert a.running and a.captures == [] and a.audio_rec is None
    seen = []

    def fake_chat(targets, messages, max_tokens, temperature, on_text=None, **k):
        seen.append(messages)
        n = len(seen)
        text = f"@@QUESTION\nQuestion {n}?\n@@TRANSLATION\nسؤال {n}\n@@ANSWER\n**B) answer {n}**\n@@MEANING\nمعنی {n}"
        if on_text:
            on_text(text)
        return text
    monkeypatch.setattr(a.engine, "run_chat", fake_chat)
    for n in (1, 2):
        assert a.api_screen(new_area=True, now=True)["ok"]
        assert _wait(lambda: not a.screen_busy), "the screen job did not finish"
        rows = a.session.ordered()
        assert len(rows) == n and rows[-1]["source"] == "screen"
        assert rows[-1]["text"] == f"Question {n}?" and rows[-1]["answer"] == f"**B) answer {n}**"
        assert rows[-1]["ans_state"] == "done" and rows[-1]["translation"] == f"سؤال {n}"
    assert "CCNA practice exam" in seen[0][0]["content"]              # what the questions are about goes with each picture
    # the mode cannot change to one that listens while this session runs
    a.api_save_config(work_mode="meeting")
    assert a.cfg["work_mode"] == "screen"
    path = a.session.path
    assert a.api_stop()["ok"]
    assert _wait(lambda: not a.stopping and not a.running)
    txt = open(path, encoding="utf-8").read()
    assert "Question 1?" in txt and "answer 2" in txt


def test_screen_mode_says_at_start_when_no_service_reads_pictures(app, screen_app, monkeypatch):
    a = screen_app

    def none(quick=False):
        raise app.APIError("Reading the screen needs an online AI service")
    monkeypatch.setattr(a, "vision_target", none)
    r = a.api_start()
    assert r["ok"] is False and "Reading the screen" in r["error"] and not a.running


def test_meeting_mode_still_needs_the_audio_library(app, screen_app, monkeypatch):
    a = screen_app
    a.cfg["work_mode"] = "meeting"
    r = a.api_start()
    assert r["ok"] is False and "audio library" in r["error"]
