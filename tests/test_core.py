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
