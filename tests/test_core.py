"""Tests for the parts that need no audio device and no network: pytest tests/"""
import json
import os
import time


# ---- settings -----------------------------------------------------------------------------
def test_defaults_are_valid(app):
    c = app.sanitize({})
    assert c["languages"] == ["en", "de"] and c["my_language"] == "fa" and c["answer_language"] == "same"
    assert c["config_version"] == app.CONFIG_VERSION


def test_bad_values_are_fixed(app):
    c = app.sanitize({"languages": ["EN", "xx", "fr", "fr"], "my_language": "zz", "answer_language": "??",
                      "sensitivity": 99, "theme": "neon", "stt_provider": "missing"})
    assert c["languages"] == ["en", "fr"]
    assert c["my_language"] == "fa" and c["answer_language"] == "same"
    assert c["sensitivity"] == 10 and c["theme"] == "system" and c["stt_provider"] == "groq"


def test_legacy_single_language_key_is_converted(app):
    with open(app.CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump({"config_version": app.CONFIG_VERSION, "language": "de", "api_key": " gsk_x "}, f)
    c = app.load_config()
    assert c["languages"] == ["de"] and c["api_key"] == "gsk_x" and "language" not in c


# ---- languages ----------------------------------------------------------------------------
def test_language_rules(app):
    c = app.sanitize({"languages": ["en"], "my_language": "de"})
    assert app.fixed_lang(c) == "en"
    assert "German" in app.translate_system(c)
    assert "same language as the NEW line (English)" in app.answer_lang_rule(c)
    assert "German" in app.meaning_rule(c, "en")          # answer in English -> its meaning in German
    c["answer_language"] = "de"
    assert app.meaning_rule(c, "en") == ""                # the answer is already in my language


def test_reply_language_check(app):
    assert app.in_language("سلام، حالت چطوره؟", "fa")
    assert not app.in_language("Hello there", "fa")
    assert app.in_language("Hallo zusammen", "de")        # Latin letters are not checked
    assert app.LANG_CODES["english"] == "en" and app.LANG_CODES["castilian"] == "es"


# ---- small helpers ----------------------------------------------------------------------------
def test_token_check_never_raises(app):
    assert app.token_ok("abc", "abc")
    assert not app.token_ok("é", "abc") and not app.token_ok(None, "abc") and not app.token_ok("", "abc")


def test_split_answer(app):
    assert app.split_answer("Sure, I can.\n###\nحتماً.") == ("Sure, I can.", "حتماً.")
    assert app.split_answer("Only English") == ("Only English", "")


def test_filler(app):
    assert app.is_filler("Okay, great.")
    assert not app.is_filler("What is the difference between OSPF and EIGRP?")


# ---- free-plan limits ------------------------------------------------------------------------
def test_quota_record_and_refund(app):
    q = app.SttQuota("m")
    now = time.time()
    handles = []
    for i in range(app.STT_RPM):
        assert q.can_send(now, 3)
        handles.append(q.record(now - 50 + i, 3 + i * 0.1))
    assert not q.can_send(now, 3)                         # requests per minute used up
    total = q.billed_sum
    q.refund(handles[0])                                  # an older request: exactly that one is taken back
    assert q.can_send(now, 3) and q.recent() == app.STT_RPM - 1
    assert abs(q.billed_sum - (total - max(app.MIN_BILLED, 3))) < 1e-9
    q.refund(handles[0])                                  # twice does nothing
    assert q.recent() == app.STT_RPM - 1


# ---- meetings --------------------------------------------------------------------------------
def test_meeting_is_kept_for_continue(app):
    cfg = app.sanitize({})
    s = app.Session(cfg)
    e = s.add("them", time.time(), time.time() + 2, "Can you introduce yourself?", "en", [1])
    s.update(e["id"], translation="خودت را معرفی کن", tr_state="done", answer="Sure.", ans_state="done")
    s.save_if_dirty()
    assert os.path.isfile(s.path) and os.path.isfile(app.LAST_MEETING)
    back = app.Session.load_last(cfg)
    rows = back.ordered()
    assert back.path == s.path and len(rows) == 1 and rows[0]["answer"] == "Sure."
    assert back.answered_before(time.time() + 10, 5) == [("Can you introduce yourself?", "Sure.")]
    back.resumes.append(time.time() + 5)
    back.add("them", time.time() + 6, time.time() + 7, "Thanks.", "en", [2])
    back.save_if_dirty()
    with open(s.path, encoding="utf-8") as f:
        assert "continued at" in f.read()


def test_strip_think(app):
    assert app.strip_think("<think>a <think>b</think> c</think> answer") == "answer"
    assert app.strip_think("text <think>still thinking") == "text "
    assert app.strip_think("plain") == "plain"


def test_proxy_password_is_hidden(app):
    assert app.mask_proxy("http://user:secret@127.0.0.1:8080") == "http://user:***@127.0.0.1:8080"
    assert app.mask_proxy("socks5://127.0.0.1:1080") == "socks5://127.0.0.1:1080"


def test_limits_are_readable(app):
    h = {"x-ratelimit-limit-requests": "14400", "x-ratelimit-remaining-requests": "14390",
         "x-ratelimit-limit-tokens": "6000", "x-ratelimit-remaining-tokens": "5990",
         "x-ratelimit-reset-requests": "2m59.56s"}
    lines = app.describe_limits(h, groq=True)
    assert "14,390 of 14,400 requests today left (full again in 3 min)" in lines
    assert any("tokens this minute" in x for x in lines)


# ---- the local web server (what the window talks to) -------------------------------------------
def test_http_api_needs_the_key(app):
    import threading
    import httpx
    a = app.App()
    app.Handler.app = a
    srv = app.ThreadingHTTPServer(("127.0.0.1", 0), app.Handler)
    srv.daemon_threads = True
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{srv.server_address[1]}"
    try:
        with httpx.Client(trust_env=False, timeout=10) as c:
            assert c.get(base + "/").status_code == 403                        # no key: no page, no key inside
            r = c.get(base + "/?t=" + a.token)
            assert r.status_code == 200 and a.token in r.text and "ma_key" in r.headers.get("set-cookie", "")
            assert c.get(base + "/").status_code == 200                        # a reload works with the cookie
            with httpx.Client(trust_env=False, timeout=10) as other:
                assert other.post(base + "/api/devices", json={}).status_code == 403
                assert other.post(base + "/api/devices", json={}, headers={"X-Token": "wrong"}).status_code == 403
            h = {"X-Token": a.token}
            r = c.post(base + "/api/save_config?x=1", json={"languages": ["fr", "en"], "my_language": "de"}, headers=h)
            cfg = r.json()["config"]
            assert cfg["languages"] == ["fr", "en"] and cfg["my_language"] == "de" and "api_key" not in cfg
            bad = c.post(base + "/api/save_config", content=b'{"languages": [', headers={**h, "Content-Type": "application/json"})
            assert bad.status_code == 400                                       # half a request is never acted on
            r = c.post(base + "/api/save_config", json={"llm_model": "C:/x.gguf", "local_bench": {"quick": "x"}},
                       headers=h).json()
            assert r["config"]["llm_model"] == "" and r["config"]["local_bench"] == {}   # only their own actions set these
            assert c.get(base + "/?t=" + a.token).headers.get("x-frame-options") == "DENY"
            assert c.post(base + "/api/nothing_like_this", json={}, headers=h).json()["ok"] is False
    finally:
        srv.shutdown()
        a.closing.set()


def test_local_ai_is_a_service(app):
    c = app.sanitize({"tr_provider": "llm", "ans_provider": "llm", "tr_model": "x", "llm_model": "/m.gguf"})
    assert c["tr_provider"] == "llm" and c["tr_model"] == ""
    c2 = app.sanitize({"stt_provider": "llm"})
    assert c2["stt_provider"] == "groq"                                          # it cannot do speech to text
    assert app.clean_providers([{"id": "llm"}, {"id": "local"}, {"id": "ok", "models": "gpt-4"}]) == [
        {**app.clean_providers([{"id": "ok"}])[0]}]


# ---- audit round: odd files and inputs never stop the program ----------------------------------
def test_odd_settings_file_is_survived(app):
    with open(app.CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump({"config_version": "5", "sensitivity": 1e400, "transcribe_me": "false", "tr_provider": "My Service",
                   "providers": [{"id": "My Service", "name": "X", "caps": {"chat": "odd"}}]}, f)
    c = app.load_config()
    assert c["transcribe_me"] is False and c["sensitivity"] == app.DEFAULTS["sensitivity"]
    assert c["tr_provider"] == "myservice" and c["providers"][0]["caps"] == {}


def test_damaged_last_meeting_is_ignored(app):
    for bad in ('{"path": 5}', '[]', '{"path": "x.md", "entries": {"a": 1}}', '{"entries": [1, 2]}', "not json"):
        with open(app.LAST_MEETING, "w", encoding="utf-8") as f:
            f.write(bad)
        assert app.Session.load_last(app.sanitize({})) is None
    s = app.Session(app.sanitize({}))
    s.add("them", time.time(), time.time() + 1, "Hello", "en", [1])
    s.save_if_dirty()
    with open(app.LAST_MEETING, encoding="utf-8") as f:
        d = json.load(f)
    d["entries"].append({"t0": None, "text": 5})              # a damaged line is skipped, the rest is kept
    d["resumes"] = "abc"
    with open(app.LAST_MEETING, "w", encoding="utf-8") as f:
        json.dump(d, f)
    back = app.Session.load_last(app.sanitize({}))
    assert back is not None and len(back.ordered()) == 1 and back.resumes == []


def test_proxy_password_with_odd_characters_is_hidden(app):
    assert app.mask_proxy("http://u:p/ss@1.2.3.4:8080") == "http://u:***@1.2.3.4:8080"
    assert "ss@" not in app.mask_proxy("socks5://u:p@ss@h:1")


def test_network_paths_are_refused(app):
    assert app.is_network_path(r"\\server\share\a.mp3") and app.is_network_path("//server/x")
    assert not app.is_network_path(r"C:\Users\a.mp3")


def test_retry_after_forms(app):
    class R:
        def __init__(self, h):
            self.headers = h
    assert app.retry_after_seconds(R({"retry-after": "12"})) == 12
    assert app.retry_after_seconds(R({"x-ratelimit-reset-requests": "45s"})) == 45
    assert app.retry_after_seconds(R({"x-ratelimit-reset-requests": "2h0m0s"})) == 60
    assert app.retry_after_seconds(R({"retry-after": "inf"})) == 5.0
    assert app.retry_after_seconds(R({})) == 5.0


def test_quota_is_given_back_when_a_sentence_is_dropped(app):
    eng_q = app.SttQuota("whisper-large-v3-turbo")
    h = eng_q.record(time.time(), 4)
    eng_q.refund(h)
    assert eng_q.recent() == 0 and eng_q.billed_sum == 0


def test_continue_copy_is_written_at_the_end(app):
    """A regular save during the meeting may skip the 'Continue' copy; the final save must still write it."""
    cfg = app.sanitize({})
    s = app.Session(cfg)
    e = s.add("them", time.time(), time.time() + 2, "First question?", "en", [1])
    s.save_if_dirty()                                   # writes both files
    s.update(e["id"], answer="Late answer.", ans_state="done")
    s.save_if_dirty(final=False)                        # within 20 s: the 'Continue' copy is skipped
    s.save_if_dirty()                                   # nothing new, but the copy is still behind
    back = app.Session.load_last(cfg)
    assert back.ordered()[0]["answer"] == "Late answer."
