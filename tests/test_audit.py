"""Tests for the fixes of the 6.35 strict review (no audio device, no network)."""
import json
import os
import threading
import time
import types

from test_tools import _RecHub, _engine


def _job(np, seg, source, t0, dur=1.0, **kw):
    return {"segs": [seg], "source": source, "audio": np.zeros(int(16000 * dur), np.float32), "t0": t0,
            "t_end": t0 + dur, "dur": dur, "tries": 0, "t_queued": time.time(), **kw}


# ---- Stop: the last sentences are not thrown away silently ----------------------------------------------------
def test_stop_waits_while_the_last_sentences_are_still_being_written(app):
    np = app.np
    eng, sess, _ = _engine(app)
    eng.cfg["api_key"] = "gsk_test"                       # a service exists: the sentence can still be written
    told = []
    with eng.cv:
        eng.pending.append(_job(np, 1, "them", time.time() - 3))

    def worker():                                         # the service answers only after the first wait
        time.sleep(0.8)
        with eng.cv:
            job = eng.pending.pop()
            eng._mark_done(job["segs"])
            eng.cv.notify_all()
    threading.Thread(target=worker, daemon=True).start()
    lost = eng.finish(timeout=0.3, patient=10, on_wait=told.append)
    assert lost == (0, 0.0) and told == [1] and not eng.pending


def test_stop_reports_what_could_not_be_written(app):
    np = app.np
    eng, sess, _ = _engine(app)
    eng.cfg["api_key"] = ""                               # no service could ever take it: no long wait
    with eng.cv:
        eng.pending.append(_job(np, 1, "them", time.time() - 3, dur=2.5))
    t = time.time()
    lost = eng.finish(timeout=0.2, patient=30)
    assert time.time() - t < 3
    assert lost == (1, 2.5)


def test_a_dropped_sentence_is_counted_but_a_say_sentence_is_not(app):
    np = app.np
    eng, sess, _ = _engine(app)
    try:
        eng._drop(_job(np, 1, "them", time.time(), dur=2.0))
        eng._drop(_job(np, 2, "me", time.time(), dur=1.0, say=True))
        assert eng.dropped == [1, 2.0]
    finally:
        eng.stop_event.set()


# ---- sentences are never left waiting for a service that does not exist -----------------------------------------
def test_a_sentence_nobody_can_write_is_not_queued(app):
    np = app.np
    eng, sess, _ = _engine(app)
    hub = _RecHub()
    eng.hub = hub
    try:
        eng.cfg["api_key"] = ""                           # e.g. only a live service, which is reopening right now
        eng.on_audio("segment", "them", 5, audio=np.zeros(16000, np.float32), t0=time.time() - 1, t_end=time.time(), dur=1.0)
        assert eng.pending == [] and 5 in eng.done_segs
        assert any(k == "speaking" and e.get("phase") == "discard" for k, e in hub.events)
    finally:
        eng.stop_event.set()


# ---- sentences are joined only when they belong together --------------------------------------------------------
def test_waiting_pieces_are_joined_only_when_they_follow_each_other(app):
    np = app.np
    eng, sess, _ = _engine(app)
    eng.cfg["api_key"] = "gsk_test"
    now = time.time()
    try:
        with eng.cv:                                       # the other side: 20 s apart, with my line in between
            eng.pending[:] = [_job(np, 1, "them", now - 40), _job(np, 2, "them", now - 20),
                              _job(np, 3, "me", now - 30)]
        job, model = eng._take_job()
        assert job["segs"] == [1]                           # not joined across 20 s and my reply
        with eng.cv:
            eng.pending[:] = [_job(np, 4, "them", now - 10), _job(np, 5, "them", now - 8.5)]
        job, model = eng._take_job()
        assert job["segs"] == [4, 5]                        # 0.5 s apart, same speaker: one request
        eng.cfg["work_mode"] = "inperson"                   # in person: the microphone hears different people
        with eng.cv:
            eng.pending[:] = [_job(np, 6, "me", now - 6), _job(np, 7, "me", now - 4.8)]
        job, model = eng._take_job()
        assert job["segs"] == [6]
    finally:
        eng.stop_event.set()


# ---- "Continue last" always means the newest meeting ------------------------------------------------------------
def test_a_late_save_of_an_older_meeting_never_replaces_the_last_meeting(app):
    cfg = app.sanitize({})
    a = app.Session(cfg)
    a.started = a.started.replace(year=a.started.year - 1)          # meeting A: older
    t = time.time()
    a.add("them", t, t + 2, "Question of meeting A?", "en", [1])
    a.save_if_dirty(final=True)
    b = app.Session(cfg)
    b.add("them", t, t + 2, "Question of meeting B?", "en", [2])
    b.save_if_dirty(final=True)
    assert app.Session.load_last(cfg).ordered()[0]["text"] == "Question of meeting B?"
    a.set_summary("A late summary of meeting A")
    a.save_if_dirty(final=True)                                              # e.g. its summary arrived later
    assert app.Session.load_last(cfg).ordered()[0]["text"] == "Question of meeting B?"


# ---- answers have their own threads -----------------------------------------------------------------------------
def test_answers_do_not_wait_behind_translations(app):
    fa = types.SimpleNamespace(cfg=app.sanitize({}), hub=_RecHub(), stats=app.Stats(), captures=[], running=False,
                               engine=None, provider=lambda pid: None)
    eng = app.Engine(fa, app.Session(fa.cfg), workers=False)
    seen = []
    try:
        eng.pool.submit = lambda fn, *a: seen.append(("pool", fn.__name__))
        eng.ans_pool.submit = lambda fn, *a: seen.append(("ans", fn.__name__))
        eng._submit(eng._answer, 1, False, None)
        eng._submit(eng._translate, 1, 1)
        assert seen == [("ans", "_answer"), ("pool", "_translate")]
    finally:
        eng.stop_event.set()


# ---- a broken live stream: the words already heard are written once -----------------------------------------------
def test_a_live_line_counts_as_heard_at_once(app):
    eng, sess, _ = _engine(app)
    try:
        eng.live_pool.submit = lambda *a: None             # (the line itself is written later on its own thread)
        eng._submit_live("them", "Lthem1_0", 100.0, 104.0, "hello there")
        assert eng.live_heard["them"] == 104.0             # a failure right after does not hand it to the backup too
    finally:
        eng.stop_event.set()


# ---- a long break in the kept meeting sound ------------------------------------------------------------------------
def test_a_long_break_starts_a_new_sound_part_instead_of_hours_of_silence(app, tmp_path):
    np = app.np
    path = os.path.join(str(tmp_path), "meeting_gap.md")
    rec = app.MeetingAudio(path)
    now = time.time()
    rec._write_now("them", np.full(16000, 0.2, np.float32), 16000, now)
    t = time.time()
    rec._write_now("them", np.full(16000, 0.2, np.float32), 16000, now + 3 * 3600)   # the PC slept 3 hours
    assert time.time() - t < 1.0                                    # no 3 hours of silence written
    rec.close()
    parts = app.load_audio_index(os.path.join(str(tmp_path), "meeting_gap.audio.json"))
    assert len(parts) == 2 and parts[1]["t0"] - parts[0]["t0"] > 3 * 3600 - 5 and all(p["dur"] < 2 for p in parts)


# ---- changing who said a line -------------------------------------------------------------------------------------
def test_marking_a_line_as_mine_stops_its_answer(app):
    a = app.App()
    try:
        s = app.Session(a.cfg)
        t = time.time()
        e = s.add("them", t, t + 2, "My own words that were taken for theirs", "en", [1])
        s.update(e["id"], ans_state="streaming", answer="half an answer")
        eng = app.Engine(a, s, workers=False)
        a.review = eng
        a.last_session = s
        a._shown_session = lambda: s
        before = eng.ans_gen[e["id"]]
        r = a.api_line_who(entry_id=e["id"], who="me")
        assert r["ok"] and r["entry"]["source"] == "me" and r["entry"]["ans_state"] == "off"
        assert r["entry"]["answer"] == "" and eng.ans_gen[e["id"]] == before + 1
        eng.stop_event.set()
    finally:
        a.closing.set()


# ---- settings ------------------------------------------------------------------------------------------------------
def test_the_coach_has_one_switch_and_the_old_one_is_carried_over(app):
    with open(app.CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump({"config_version": app.CONFIG_VERSION, "coach": False}, f)
    cfg = app.load_config()
    assert cfg["features"].get("coach") is False and cfg["coach"] is True and not app.coach_on(cfg)
    cfg["features"] = {}
    assert app.coach_on(cfg)


def test_start_needs_only_the_services_used_during_the_meeting(app):
    a = app.App()
    try:
        a.cfg["features"] = {"answers": False, "coach": False, "screen": False, "say": False}
        assert a.needed_tasks(at_start=True) == ("stt", "tr")       # prep, review and notes ask later
        assert "ans" in a.needed_tasks()                            # Setup still shows them as used
    finally:
        a.closing.set()


def test_plain_keys_from_an_older_version_are_written_encrypted_at_once(app):
    fake = lambda data, protect: bytes(reversed(data))
    old = app.SECRET_CODEC[0]
    app.SECRET_CODEC[0] = fake
    try:
        for p in (app.CONFIG_PATH, app.CONFIG_PATH + ".bak"):
            with open(p, "w", encoding="utf-8") as f:
                json.dump({"config_version": app.CONFIG_VERSION, "api_key": "gsk_plain_key"}, f)
        cfg = app.load_config()
        assert cfg["api_key"] == "gsk_plain_key" and app.reseal_secrets(cfg)
        for p in (app.CONFIG_PATH, app.CONFIG_PATH + ".bak"):
            text = open(p, encoding="utf-8").read()
            assert "gsk_plain_key" not in text and app.SECRET_TAG in text, p
        assert app.load_config()["api_key"] == "gsk_plain_key"
        assert not app.reseal_secrets(app.load_config())          # nothing plain any more: no extra save
    finally:
        app.SECRET_CODEC[0] = old


def test_changing_only_the_proxy_port_keeps_its_password(app):
    a = app.App.__new__(app.App)
    a.cfg = {"proxy": "http://bob:s3cret@10.0.0.1:8080"}
    shown = app.mask_proxy(a.cfg["proxy"])
    assert a._real_proxy(shown) == "http://bob:s3cret@10.0.0.1:8080"
    assert a._real_proxy("http://bob:***@10.0.0.1:8081") == "http://bob:s3cret@10.0.0.1:8081"
    assert a._real_proxy("http://alice:***@10.0.0.1:8081") == "http://alice:***@10.0.0.1:8081"   # another user
    assert a._real_proxy("http://bob:new@10.0.0.1:8081") == "http://bob:new@10.0.0.1:8081"
    assert a._real_proxy("") == ""


def test_proxy_lookup_is_asked_for_each_service_address(app):
    seen = []
    old = app._detect_proxy
    app._detect_proxy = lambda manual, url=app.PAC_GROQ: (seen.append(url), ("", ""))[1]
    app._proxy_cache.clear()
    try:
        app.detect_proxy("", app.PAC_DEEPGRAM)
        app.detect_proxy("", app.pac_url("https://api.openai.com/v1"))
        app.detect_proxy("")
        assert seen == ["https://api.deepgram.com/", "https://api.openai.com/", "https://api.groq.com/"]
        app._detect_proxy = lambda manual, url=app.PAC_GROQ: ("", "pending")
        app._proxy_cache.clear()
        assert app.detect_proxy("") == ("", "") and not app._proxy_cache    # not found yet: never kept as "direct"
    finally:
        app._detect_proxy = old
        app._proxy_cache.clear()


def test_a_web_page_is_never_kept_as_a_model_file(app, tmp_path):
    good = os.path.join(str(tmp_path), "model.bin")
    with open(good, "wb") as f:
        f.write(b"\x00\x01binary model")
    page = os.path.join(str(tmp_path), "config.json")
    with open(page, "w", encoding="utf-8") as f:
        f.write("<!DOCTYPE html><html><body>Blocked</body></html>")
    real_json = os.path.join(str(tmp_path), "tokenizer.json")
    with open(real_json, "w", encoding="utf-8") as f:
        f.write('{"a": 1}')
    assert app.download_looks_real(good) and app.download_looks_real(real_json)
    assert not app.download_looks_real(page)
