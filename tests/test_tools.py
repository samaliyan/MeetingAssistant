"""Tests for the 6.2 features (no audio device, no network)."""
import datetime
import io
import json
import os
import struct
import sys
import time
import zipfile
import zlib


def _tiny_pdf(path, text):
    objs = ["<< /Type /Catalog /Pages 2 0 R >>", "<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
            "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 300 200] /Contents 4 0 R "
            "/Resources << /Font << /F1 5 0 R >> >> >>"]
    stream = f"BT /F1 14 Tf 20 100 Td ({text}) Tj ET"
    objs.append(f"<< /Length {len(stream)} >>\nstream\n{stream}\nendstream")
    objs.append("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    out, offs = b"%PDF-1.4\n", []
    for i, o in enumerate(objs, 1):
        offs.append(len(out))
        out += f"{i} 0 obj\n{o}\nendobj\n".encode()
    x = len(out)
    out += f"xref\n0 {len(objs) + 1}\n0000000000 65535 f \n".encode()
    out += "".join(f"{o:010d} 00000 n \n" for o in offs).encode()
    out += f"trailer\n<< /Size {len(objs) + 1} /Root 1 0 R >>\nstartxref\n{x}\n%%EOF".encode()
    with open(path, "wb") as f:
        f.write(out)


def _cfg(app, **kw):
    return app.sanitize(kw)


# ---- settings -----------------------------------------------------------------------------
def test_new_settings_are_checked(app):
    c = app.sanitize({})
    assert c["about_source"] == "text" and c["meeting_mode"] == "general" and c["search_days"] == "90"
    assert c["hide_from_share"] is False and c["diarize"] is False
    c = app.sanitize({"about_source": "file"})                       # no file chosen: the written text is used
    assert c["about_source"] == "text"
    c = app.sanitize({"about_source": "file", "about_file": "C:\\cv.docx"})
    assert c["about_source"] == "file" and c["about_file"] == "C:\\cv.docx"
    c = app.sanitize({"about_source": "file", "about_file": "\\\\server\\share\\cv.docx"})
    assert c["about_file"] == "" and c["about_source"] == "text"
    c = app.sanitize({"meeting_mode": "nope", "screen_delay": "9", "search_days": "5", "glossary": "x" * 9000,
                      "screen_provider": "../../evil"})
    assert c["meeting_mode"] == "general" and c["screen_delay"] == "3" and c["search_days"] == "90"
    assert len(c["glossary"]) == 3000 and c["screen_provider"] == ""
    assert "about_file" in app.INTERNAL_KEYS


# ---- About from a file --------------------------------------------------------------------------
def test_read_document_formats(app, tmp_path):
    d = str(tmp_path)
    p = os.path.join(d, "cv.txt")
    with open(p, "wb") as f:
        f.write("\ufeffJohn Doe\r\n\r\n\r\n\r\nNetwork engineer, 8 years. سلام".encode("utf-8"))
    t = app.read_document(p)
    assert t.startswith("John Doe") and "8 years" in t and "\r" not in t and "\n\n\n" not in t and "سلام" in t
    p = os.path.join(d, "cv.docx")
    with open(p, "wb") as f:
        f.write(app.docx_bytes([("title", "Jane Roe", None), ("p", "Skills: OSPF & <BGP>", None), ("p", "تجربه کاری", None)]))
    t = app.read_document(p)
    assert "Jane Roe" in t and "OSPF & <BGP>" in t and "تجربه کاری" in t
    try:
        import pypdf  # noqa: F401
    except ImportError:
        return
    p = os.path.join(d, "cv.pdf")
    _tiny_pdf(p, "Senior DBA at Example")
    assert "Senior DBA at Example" in app.read_document(p)


def test_read_document_errors(app, tmp_path):
    d = str(tmp_path)
    bad = app.DocError
    for path, why in (("", "No file"), (os.path.join(d, "missing.txt"), "not found"), ("\\\\srv\\x\\a.txt", "Network")):
        try:
            app.read_document(path)
            assert False, path
        except bad as e:
            assert why in str(e), (path, str(e))
    p = os.path.join(d, "a.exe")
    open(p, "wb").write(b"x")
    try:
        app.read_document(p)
        assert False
    except bad as e:
        assert ".docx" in str(e)
    p = os.path.join(d, "empty.txt")
    open(p, "w").write("  \n ")
    try:
        app.read_document(p)
        assert False
    except bad as e:
        assert "No text" in str(e)
    p = os.path.join(d, "broken.docx")
    open(p, "wb").write(b"not a zip")
    try:
        app.read_document(p)
        assert False
    except bad as e:
        assert "readable" in str(e)
    p = os.path.join(d, "broken.pdf")
    open(p, "wb").write(b"%PDF-1.4 nothing")
    try:
        app.read_document(p)
        assert False
    except bad:
        pass
    p = os.path.join(d, "long.txt")
    open(p, "w", encoding="utf-8").write("word " * 5000)
    assert len(app.read_document(p)) == app.ABOUT_MAX


def test_about_text_uses_file_and_falls_back(app, tmp_path):
    p = os.path.join(str(tmp_path), "me.txt")
    open(p, "w", encoding="utf-8").write("I am Siavash, 10 years in networking.")
    c = _cfg(app, about_me="written text", about_file=p, about_source="file")
    assert "Siavash" in app.about_text(c) and "written text" not in app.about_text(c)
    c["about_source"] = "text"
    assert app.about_text(c) == "written text"
    c["about_source"] = "file"
    os.remove(p)
    assert app.about_text(c) == "written text"                        # the file vanished: the written text is used
    info = app.about_info(c)
    assert info["file"] == "me.txt" and info["error"]


# ---- glossary and speakers -----------------------------------------------------------------------
def test_glossary_terms_and_spelling(app):
    c = _cfg(app, glossary="OSPF, RMAN\nkubectl; ospf ,  , k8s،Vlan 100")
    t = app.glossary_terms(c)
    assert t == ["OSPF", "RMAN", "kubectl", "k8s", "Vlan 100"]
    assert app.apply_glossary("we run ospf and rman, not Rmanager. kubectl get pods; K8S", t) == \
        "we run OSPF and RMAN, not Rmanager. kubectl get pods; k8s"
    assert app.glossary_terms(_cfg(app, glossary="")) == [] and app.glossary_note(_cfg(app)) == ""
    many = ",".join(f"t{i}" for i in range(200))
    assert len(app.glossary_terms(_cfg(app, glossary=many))) == app.GLOSSARY_MAX_TERMS


def test_glossary_reaches_the_prompts(app):
    class E(app.Engine):
        def __init__(self, cfg):
            self.cfg = cfg
    e = E(_cfg(app, glossary="OSPF, RMAN", context="Network job\nsecond line"))
    p = e._stt_prompt("them")
    assert p.startswith("Network job.") and "OSPF, RMAN" in p and len(p) <= 420
    assert E(_cfg(app, context="Network job\nx"))._stt_prompt("them") == "Network job"    # unchanged without a glossary


def test_speaker_label(app):
    assert app.speaker_label("Interviewer", None) == "Interviewer"
    assert app.speaker_label("Interviewer", 0) == "Interviewer"
    assert app.speaker_label("Interviewer", 1) == "Interviewer 2"
    assert app.speaker_label("Person 1", 2) == "Person 3"
    assert app.speaker_label("Person 1", True) == "Person 1"
    assert app.speaker_label("مصاحبه‌کننده", 1) == "مصاحبه‌کننده 2"


def test_deepgram_url_options(app):
    u = app.deepgram_url("nova-3", "en")
    assert "diarize" not in u and "keyterm" not in u
    u = app.deepgram_url("nova-3", "en", ["OSPF", "Vlan 100"], True)
    assert "diarize=true" in u and u.count("keyterm=") == 2 and "keyterm=Vlan+100" in u
    u = app.deepgram_url("nova-2", "en", ["OSPF"], False)
    assert "keywords=OSPF%3A2" in u and "keyterm" not in u


class _FakeWS:
    def __init__(self, msgs):
        self.msgs, self.closed = list(msgs), False

    def recv(self):
        if not self.msgs:
            self.closed = True
            return 0x8, b""
        return 0x1, json.dumps(self.msgs.pop(0)).encode()


def _dg_result(words, spk, final=True, speech_final=True):
    return {"type": "Results", "start": 1.0, "duration": 2.0, "is_final": final, "speech_final": speech_final,
            "channel": {"alternatives": [{"transcript": " ".join(w for w in words),
                                          "words": [{"word": w, "speaker": s} for w, s in zip(words, spk)]}]}}


def test_live_speaker_is_the_one_who_said_most_words(app):
    got = []
    lv = app.DeepgramLive("them", "k", "nova-3", "en", "", lambda *a: None, lambda *a: got.append(a), lambda e: None,
                          diarize=True)
    lv.stop_event.set()
    lv.ws = _FakeWS([_dg_result(["hello", "there", "all"], [1, 1, 0])])
    lv._receive()
    assert len(got) == 1 and got[0][3] == "hello there all" and got[0][4] == 1
    got.clear()
    lv2 = app.DeepgramLive("them", "k", "nova-3", "en", "", lambda *a: None, lambda *a: got.append(a), lambda e: None)
    lv2.stop_event.set()
    lv2.ws = _FakeWS([_dg_result(["hello", "there"], [1, 1])])
    lv2._receive()
    assert len(got) == 1 and len(got[0]) == 4                          # no speaker argument when it is switched off


def test_session_keeps_speaker_feedback_and_screens(app):
    c = _cfg(app, them_label="Interviewer")
    s = app.Session(c)
    a = s.add("them", 100.0, 102.0, "First question?", "en", [], 0)
    b = s.add("them", 103.0, 105.0, "Second person here", "en", [], 1)
    assert a["speaker"] is None and b["speaker"] == 1
    assert s.label(s.get(b["id"])) == "Interviewer 2" and s.label(s.get(a["id"])) == "Interviewer"
    s.set_feedback("## Overall\nGood.")
    s.add_screen("The screen shows a form.")
    s.save_if_dirty()
    md = open(s.path, encoding="utf-8").read()
    assert "Interviewer 2:** Second person here" in md and "## Feedback" in md and "## Screen" in md
    r = app.Session.load_last(c)
    assert r is not None and r.feedback == "## Overall\nGood." and r.screens[0]["text"] == "The screen shows a form."
    assert sorted(x["speaker"] or 0 for x in r.entries.values()) == [0, 1]


# ---- statistics ------------------------------------------------------------------------------------
def test_talk_stats(app):
    rows = [{"source": "them", "t0": 0, "t_end": 5, "text": "Tell me about OSPF please"},
            {"source": "me", "t0": 13, "t_end": 43, "text": "Um well " + "word " * 58 + "you know"},
            {"source": "them", "t0": 44, "t_end": 46, "text": "Thanks"},
            {"source": "me", "t0": 47, "t_end": 49, "text": "Sure"}]
    st = app.talk_stats(rows)
    assert st["me_words"] == 63 and st["them_words"] == 6 and st["me_share"] == 91
    assert st["wpm"] == 118 and st["fillers"] == 2 and st["long_pauses"] == 1 and st["answers"] == 2
    assert st["avg_delay"] == 4.5
    assert app.talk_stats([])["me_share"] == 0 and app.talk_stats([])["wpm"] is None


# ---- screen picture ----------------------------------------------------------------------------------
def _read_png(data):
    assert data[:8] == b"\x89PNG\r\n\x1a\n"
    pos, idat, ihdr = 8, b"", None
    while pos < len(data):
        n, kind = struct.unpack(">I4s", data[pos:pos + 8])
        body = data[pos + 8:pos + 8 + n]
        assert struct.unpack(">I", data[pos + 8 + n:pos + 12 + n])[0] == zlib.crc32(kind + body) & 0xFFFFFFFF
        if kind == b"IHDR":
            ihdr = struct.unpack(">IIBBBBB", body)
        elif kind == b"IDAT":
            idat += body
        pos += 12 + n
    w, h = ihdr[0], ihdr[1]
    raw = zlib.decompress(idat)
    assert len(raw) == h * (w * 3 + 1)
    return w, h, raw


def test_png_encoder_and_downscale(app):
    import numpy as np
    w, h = 300, 100
    px = np.zeros((h, w, 4), dtype=np.uint8)
    px[:, :, 0], px[:, :, 1], px[:, :, 2] = 10, 20, 200            # BGRA: blue 10, green 20, red 200
    ww, hh, raw = _read_png(app.encode_png(w, h, px.tobytes()))
    assert (ww, hh) == (300, 100) and list(raw[1:4]) == [200, 20, 10]
    big = np.zeros((1000, 4000, 4), dtype=np.uint8)
    big[:, :, 2] = 255
    ww, hh, raw = _read_png(app.encode_png(4000, 1000, big.tobytes(), 1920))
    assert (ww, hh) == (1920, 480) and list(raw[1:4]) == [255, 0, 0]


def test_vision_model_guess(app):
    assert app.guess_vision_model(["whisper-1", "text-embedding-3-small", "gpt-4o-mini", "gpt-4o"]) == "gpt-4o-mini"
    assert app.guess_vision_model(["llama-3.3-70b", "meta-llama/llama-4-scout-17b-16e-instruct"]) == \
        "meta-llama/llama-4-scout-17b-16e-instruct"
    assert app.guess_vision_model(["llama-3.3-70b", "whisper-large-v3"]) is None
    assert app.guess_vision_model([]) is None


def test_picture_messages_are_not_counted_as_text(app):
    m = {"role": "user", "content": [{"type": "text", "text": "abcd"},
                                     {"type": "image_url", "image_url": {"url": "data:image/png;base64," + "A" * 900000}}]}
    assert app._msg_chars(m) < 10000 and app._msg_chars({"content": "hello"}) == 5


# ---- old meetings ----------------------------------------------------------------------------------------
def _meeting(app, when, lines):
    s = app.Session(_cfg(app))
    s.started = when
    s.path = os.path.join(app.MEETINGS_DIR, when.strftime("meeting_%Y-%m-%d_%H-%M-%S.md"))
    t = when.timestamp()
    for i, (src, text, tr) in enumerate(lines):
        e = s.add(src, t + i * 10, t + i * 10 + 5, text, "en", [])
        s.update(e["id"], translation=tr)
    s.save_if_dirty()
    return s


def test_search_old_meetings_with_a_range(app):
    now = datetime.datetime(2026, 9, 29, 12, 0)
    _meeting(app, now - datetime.timedelta(days=3), [("them", "Tell me about OSPF areas", "درباره OSPF بگو"),
                                                     ("me", "Area zero is the backbone", "")])
    _meeting(app, now - datetime.timedelta(days=60), [("them", "What is BGP?", ""), ("me", "OSPF is not BGP", "")])
    _meeting(app, now - datetime.timedelta(days=400), [("them", "Old talk about OSPF", "")])
    hits, n = app.search_meetings(app.MEETINGS_DIR, "ospf", 7, now=now)
    assert n == 1 and len(hits) == 1 and hits[0]["date"] == "2026-09-26 12:00" and "درباره" in hits[0]["text"]
    hits, n = app.search_meetings(app.MEETINGS_DIR, "OSPF", 90, now=now)
    assert n == 2 and len(hits) == 2
    hits, n = app.search_meetings(app.MEETINGS_DIR, "OSPF", 0, now=now)
    assert n == 3 and len(hits) == 3
    hits, _ = app.search_meetings(app.MEETINGS_DIR, "backbone area", 0, now=now)     # all words must be in one line
    assert len(hits) == 1 and hits[0]["who"]
    hits, _ = app.search_meetings(app.MEETINGS_DIR, "backbone bananas", 0, now=now)   # half of the words is enough
    assert len(hits) == 1
    assert app.search_meetings(app.MEETINGS_DIR, "?", 0, now=now) == ([], 0)
    assert app.fold("كيك") == app.fold("کیک") and app.fold("Café") == "cafe"


def test_search_survives_odd_files(app):
    os.makedirs(app.MEETINGS_DIR, exist_ok=True)
    open(os.path.join(app.MEETINGS_DIR, "meeting_2026-09-01_10-00-00.md"), "wb").write(b"\xff\xfe**[10:00:00] Me:** bad bytes ospf\n")
    open(os.path.join(app.MEETINGS_DIR, "notes.md"), "w").write("ospf")
    open(os.path.join(app.MEETINGS_DIR, "meeting_broken.md"), "w").write("ospf")
    hits, n = app.search_meetings(app.MEETINGS_DIR, "ospf", 0, now=datetime.datetime(2026, 9, 29))
    assert n == 1


# ---- export ---------------------------------------------------------------------------------------------
def _sample_session(app):
    c = _cfg(app, context="Interview", them_label="Interviewer")
    s = app.Session(c)
    t = s.started.timestamp()
    e = s.add("them", t + 5, t + 8, "What is <OSPF> & why?", "en", [])
    s.update(e["id"], translation="OSPF چیست؟", answer="It is a link-state protocol.", answer_fa="یک پروتکل است.")
    s.add("me", t + 12, t + 14, "Let me explain.", "en", [])
    s.set_summary("## Summary\n- one\n- two")
    return s


def test_export_docx_is_a_valid_word_file(app):
    s = _sample_session(app)
    data = app.export_bytes(s, "docx")
    z = zipfile.ZipFile(io.BytesIO(data))
    assert z.testzip() is None and "word/document.xml" in z.namelist()
    import xml.dom.minidom
    xml.dom.minidom.parseString(z.read("word/document.xml"))
    try:
        import docx
    except ImportError:
        return
    d = docx.Document(io.BytesIO(data))
    text = "\n".join(p.text for p in d.paragraphs)
    assert "What is <OSPF> & why?" in text and "OSPF چیست؟" in text and "• one" in text
    assert "Interviewer:" in text
    rtl = [p for p in d.paragraphs if "چیست" in p.text][0]
    assert rtl._p.pPr.find("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}bidi") is not None


def test_export_srt_txt_json(app):
    s = _sample_session(app)
    srt = app.export_bytes(s, "srt").decode("utf-8")
    assert srt.startswith("1\n00:00:05,000 --> 00:00:08,000\nInterviewer: What is <OSPF> & why?\nOSPF چیست؟\n")
    assert "2\n00:00:12,000 --> 00:00:14,000\n" in srt
    txt = app.export_bytes(s, "txt").decode("utf-8")
    assert "Interviewer: What is" in txt and "== Summary ==" in txt
    assert json.loads(app.export_bytes(s, "json"))["entries"][0]["text"].startswith("What is")
    assert app.srt_time(3661.5) == "01:01:01,500" and app.srt_time(-4) == "00:00:00,000"


# ---- hidden window -----------------------------------------------------------------------------------------
class _Stop:
    """A stop flag whose wait() also advances a fake clock, so the keeper loop can be run without sleeping."""
    def __init__(self, ticks):
        self.ticks = ticks
        self.flag = False

    def is_set(self):
        return self.flag

    def wait(self, t=None):
        self.ticks -= 1
        if self.ticks <= 0:
            self.flag = True
        return self.flag


def test_hiding_is_set_and_reported(app):
    log = []
    state = {"aff": 0}
    set_aff = lambda h, f: state.update(aff=f) or True
    ok = app.keep_hidden(lambda: 77, set_aff, lambda h: state["aff"], lambda *a: log.append(a), _Stop(3), interval=0)
    assert ok and log[0] == (True, "exclude", "") and state["aff"] == 0x11


def test_hiding_falls_back_to_black_and_notices_a_loss(app):
    log = []
    state = {"aff": 0, "refuse_exclude": True, "sets": 0}

    def set_aff(h, f):
        state["sets"] += 1
        if f == 0x11 and state["refuse_exclude"]:
            return False
        state["aff"] = f
        return True

    class Stop(_Stop):
        def wait(self, t=None):
            if self.ticks == 3:
                state["aff"] = 0                        # something removed the flag
            return super().wait(t)
    ok = app.keep_hidden(lambda: 5, set_aff, lambda h: state["aff"], lambda *a: log.append(a), Stop(4), interval=0)
    assert ok and log[0] == (True, "black", "")
    assert state["aff"] == 1                             # it was put back
    assert log[-1][0] is True


def test_hiding_failure_is_reported_not_hidden(app):
    log = []
    assert not app.keep_hidden(lambda: 5, lambda h, f: False, lambda h: 0, lambda *a: log.append(a), _Stop(3), interval=0)
    assert log[-1][0] is False and "refused" in log[-1][2]
    log.clear()
    assert not app.keep_hidden(lambda: None, lambda h, f: True, lambda h: 0, lambda *a: log.append(a), _Stop(1), first_wait=0)
    assert log[-1][0] is False and "not be found" in log[-1][2]


def test_hide_status_file(app, tmp_path):
    p = os.path.join(str(tmp_path), "hide.json")
    assert app.read_hide_status(p) is None
    app.write_hide_status(p, True, "exclude", "")
    assert app.read_hide_status(p) == {"active": True, "mode": "exclude", "error": ""}
    open(p, "w").write("{broken")
    assert app.read_hide_status(p) is None
    open(p, "w").write("[1]")
    assert app.read_hide_status(p) is None


def test_hide_setting_is_read_from_the_settings_file(app):
    assert app.hide_wanted() is False
    with open(app.CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump({"hide_from_share": True}, f)
    assert app.hide_wanted() is True
    with open(app.CONFIG_PATH, "w", encoding="utf-8") as f:
        f.write("not json")
    assert app.hide_wanted() is False
    if sys.platform != "win32":
        assert app.hidden_window_possible() is False
    else:
        assert isinstance(app.hidden_window_possible(), bool)   # true when pywebview is installed


def test_glossary_short_mixed_case_left_alone(app):
    assert app.apply_glossary("let's go now", ["Go"]) == "let's go now"
    assert app.apply_glossary("use ospf", ["OSPF"]) == "use OSPF"


def test_search_question_style_and_order(app, tmp_path):
    import pathlib; tmp_path = pathlib.Path(tmp_path)
    import datetime
    (tmp_path / "meeting_2026-01-05_10-00-00.md").write_text("**[00:00:01] Interviewer:** we discussed kubernetes rollout\n", encoding="utf-8")
    (tmp_path / "recording_x_2025-12-01_10-00-00.md").write_text("**[00:00:01] Interviewer:** unrelated\n", encoding="utf-8")
    hits, n = app.search_meetings(str(tmp_path), "what did we say about kubernetes?", days=0)
    assert n == 2 and len(hits) == 1 and hits[0]["file"].startswith("meeting_")


def test_srt_base_for_recording(app):
    import datetime
    d = datetime.datetime(2026, 1, 5, 15, 30)
    base = datetime.datetime.combine(d.date(), datetime.time()).timestamp()
    rows = [{"text": "hi", "t0": base + 5, "t_end": base + 7}]
    out = app.srt_text(rows, base, lambda r: "X")
    assert "00:00:05,000 --> 00:00:07,000" in out


def test_decode_text_encodings(app):
    assert app._decode_text("café".encode("cp1252")) == "café"
    fa = "سلام دنيا اين يك متن است"
    assert app._decode_text(fa.encode("cp1256")) == fa
    assert app._decode_text(fa.encode("utf-16")) == fa
    assert app._decode_text(fa.encode("utf-8")) == fa


def test_glossary_two_letter_terms(app):
    assert app.apply_glossary("I think it is fine", ["IT", "AI"]) == "I think it is fine"


def test_docx_text_no_duplicates(app, tmp_path):
    import zipfile, os
    W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
    x = (f'<w:document xmlns:w="{W}"><w:body><w:p><w:r><w:t>Hello</w:t></w:r></w:p>'
         f'<w:p><w:r><w:txbxContent><w:p><w:r><w:t>Box</w:t></w:r></w:p></w:txbxContent></w:r></w:p></w:body></w:document>')
    p = os.path.join(tmp_path, "a.docx")
    with zipfile.ZipFile(p, "w") as z:
        z.writestr("word/document.xml", x)
    assert app._docx_text(p).split("\n") == ["Hello", "Box"]


def test_model_info_and_picks(app):
    raw = [{"id": "whisper-large-v3", "active": True}, {"id": "old-model", "active": False},
           {"id": "qwen/qwen3.8-27b", "active": True, "input_modalities": ["text", "image"]},
           {"id": "openai/gpt-oss-120b", "active": True}, {"id": "llama-guard", "active": True},
           {"id": "text-embedding-3", "active": True}]
    infos = app.model_infos(raw)
    by = {i["id"]: i for i in infos}
    assert by["whisper-large-v3"]["stt"] and not by["whisper-large-v3"]["chat"]
    assert not by["old-model"]["alive"]
    assert by["qwen/qwen3.8-27b"]["vision"] and by["qwen/qwen3.8-27b"]["sure"]
    assert not by["llama-guard"]["chat"] and not by["text-embedding-3"]["chat"]
    assert app.pick_vision(infos) == "qwen/qwen3.8-27b"
    assert app.pick_vision([{"id": "x", "vision": True, "alive": False, "sure": True, "chat": True, "stt": False}]) is None
    assert app.pick_chat(infos)[0] == "openai/gpt-oss-120b"
    # a model the service says cannot read pictures is not chosen even if its name looks like one
    assert app.model_info({"id": "gpt-4o-audio", "input_modalities": ["text"]})["vision"] is False
    # the id is kept exactly as the service writes it (it is what requests use)
    assert app.model_info({"id": "models/gemini-2.5-flash"})["id"] == "models/gemini-2.5-flash"
    assert not app.model_info({"id": "flux", "type": "image"})["chat"]
    assert not app.model_info({"id": "x-old", "deprecation": "2026-01-01"})["alive"]
    assert app.pick_chat(app.model_infos([{"id": "openai/gpt-oss-120b"}, {"id": "acme-128b-x"}, {"id": "groq/compound"}]))[0] == "openai/gpt-oss-120b"


def test_custom_item_and_needs(app):
    it = app.custom_item("llm", "unsloth/gemma-3-4b-it-GGUF", "gemma-3-4b-it-Q4_K_M.gguf", 2490)
    assert it["file"].endswith(".gguf") and "/" not in it["id"] and it["id"].startswith("hf-")
    it2 = app.custom_item("stt", "Systran/faster-whisper-small", "", 484)
    assert "file" not in it2
    for bad in (("llm", "../x/y", "a.gguf", 5), ("llm", "a/b", "../a.gguf", 5), ("llm", "a/b", "a.bin", 5), ("stt", "a/b", "", 0), ("stt", "bad", "", 5)):
        try:
            app.custom_item(*bad); assert False, bad
        except ValueError:
            pass
    n = app.model_needs("llm", 2490)
    assert n["ram_mb"] > 2490 and "cores" in n["cpu"]
    assert app.model_fit(2000, 16000) == "ok" and app.model_fit(10000, 16000) == "tight" and app.model_fit(15000, 16000) == "no"
    pick = app._hf_pick_file([{"rfilename": "m-Q8_0.gguf", "size": 8_000_000_000}, {"rfilename": "m-Q4_K_M.gguf", "size": 4_000_000_000},
                              {"rfilename": "m-00001-of-00002.gguf", "size": 1}, {"rfilename": "mmproj-x.gguf", "size": 5}])
    assert pick == ("m-Q4_K_M.gguf", 4000)


def test_decode_partial_utf8_and_srt_blank_lines(app):
    fa = "سلام دنیا " * 50
    raw = (fa * 3000).encode("utf-8")[:1_500_001]        # cut in the middle of a character
    assert app._decode_text(raw).startswith("سلام دنیا")
    rows = [{"text": "a\n\nb", "translation": "x\n\n\ny", "t0": 1, "t_end": 3}, {"text": "c", "t0": 4, "t_end": 5}]
    blocks = app.srt_text(rows, 0, lambda r: "L").strip().split("\n\n")
    assert len(blocks) == 2 and blocks[0].count("\n") == 5      # index, time, 4 text lines: no blank line inside a cue



def test_sanitize_float_choice_and_hf_search(app):
    import httpx, json
    cfg = app.sanitize({"search_days": 30.0, "screen_delay": 2.0})
    assert cfg["search_days"] == "30" and cfg["screen_delay"] == "2"
    a = app.custom_item("llm", "Org/Model", "m-Q4_K_M.gguf", 100)
    b = app.custom_item("llm", "org/model", "m-q4_k_m.gguf", 100)
    c = app.custom_item("llm", "Org/Model", "m-Q8_0.gguf", 100)
    assert a["id"] == b["id"] and a["id"] != c["id"] and len(a["id"]) < 60      # same folder only for the same file

    real = httpx.Client

    def make(handler):
        app.httpx.Client = lambda **kw: real(transport=httpx.MockTransport(handler), **{k: v for k, v in kw.items() if k != "proxy"})
    make(lambda req: httpx.Response(200, json={"error": "nope"}))
    try:
        app.hf_search("llm", "popular", ""); assert False
    except app.APIError:
        pass

    def h(req):
        if req.url.path == "/api/models":
            return httpx.Response(200, json=[{"id": "a/b-Instruct-GGUF", "downloads": "x"}, "junk",
                                             {"modelId": "a/c-Instruct-GGUF", "downloads": 5000}])
        return httpx.Response(200, json={"siblings": ["bad", {"rfilename": "c-Q4_K_M.gguf", "size": "not-a-number"},
                                                      {"rfilename": "c-Q5_K_M.gguf", "size": 5_000_000_000}]})
    make(h)
    res = app.hf_search("llm", "popular", "")
    assert [i["file"] for i in res["items"]] == ["c-Q5_K_M.gguf"] and res["items"][0]["mb"] == 5000
    try:
        make(lambda req: httpx.Response(200, json=[{"id": "a/c-Instruct-GGUF", "downloads": 5000}]) if req.url.path == "/api/models" else httpx.Response(429))
        try:
            app.hf_search("llm", "popular", ""); assert False
        except app.APIError as e:
            assert "429" in str(e)
    finally:
        app.httpx.Client = real


def test_hide_status_stale_and_ping_empty(app, tmp_path):
    import json, os, time
    p = os.path.join(tmp_path, "h.json")
    json.dump({"active": True, "mode": "exclude", "error": "", "t": time.time() - 500}, open(p, "w"))
    st = app.read_hide_status(p)
    assert st["active"] is False and "stopped" in st["error"]
    json.dump({"active": True, "mode": "exclude", "error": "", "t": time.time()}, open(p, "w"))
    assert app.read_hide_status(p)["active"] is True
    # an empty or odd model list is not an error (6.1 behaviour)
    import httpx
    api = app.GroqAPI.__new__(app.GroqAPI)
    for body in ({"data": []}, [], ["gpt-a", "gpt-b"], {"models": [{"id": "m1"}]}):
        api.request = lambda *a, _b=body, **k: httpx.Response(200, json=_b, request=httpx.Request("GET", "http://x/models"))
        ms, ids = api.ping()
        assert isinstance(ids, list)
    assert ids == ["m1"]


def _speech_events(app, sens, level, seconds=1.0, gain=1.0):
    """Feeds a steady tone of the given loudness to a Segmenter and returns what it reported."""
    import numpy as np
    events = []
    seg = app.Segmenter("me", 16000, sens, lambda kind, *a, **k: events.append(kind))
    n = int(16000 * app.FRAME_SEC)
    t = np.arange(n) / 16000.0
    frame = (np.sin(2 * np.pi * 220 * t) * level * 1.414 * gain).astype("float32")
    silent = np.zeros(n, dtype="float32")
    room = (np.random.RandomState(2).randn(n) * 0.0004).astype("float32")
    for _ in range(int(3.0 / app.FRAME_SEC)):                 # a quiet room first (sets the noise floor)
        seg.feed(room)
    for _ in range(int(seconds / app.FRAME_SEC)):
        seg.feed(frame)
    for _ in range(int(2.0 / app.FRAME_SEC)):
        seg.feed(silent)
    return events


def test_low_sensitivity_ignores_small_sounds(app):
    assert "segment" in _speech_events(app, 6, 0.02)          # normal speech level: heard at the default
    assert "segment" not in _speech_events(app, 1, 0.02)      # the same sound is ignored at the lowest setting
    assert "segment" in _speech_events(app, 1, 0.12)          # loud speech is still heard
    assert "segment" not in _speech_events(app, 2, 0.05, seconds=0.2)   # a short click is ignored


def test_sensitivity_scale_is_ordered(app):
    lv = []
    for s in range(1, 11):
        seg = app.Segmenter("me", 16000, s, lambda *a, **k: None)
        lv.append(seg.min_level)
    assert lv == sorted(lv, reverse=True)
    assert abs(lv[5] - 0.0056) < 0.0005                        # the default is unchanged


def test_mic_gain_is_limited_and_only_for_me(app):
    me = app.AudioCapture(None, {}, "me", 6, lambda *a, **k: None)
    them = app.AudioCapture(None, {}, "them", 6, lambda *a, **k: None)
    me.set_gain(1000)
    them.set_gain(300)
    assert me.gain == 3.0 and them.gain == 1.0
    me.set_gain(1)
    assert me.gain == 0.25
    assert app.sanitize({"mic_gain": 5000})["mic_gain"] == 300


def test_live_service_hears_the_mic_only_during_speech(app):
    import numpy as np
    got = []
    cap = app.AudioCapture(None, {}, "me", 1, lambda *a, **k: None)
    cap.seg = app.Segmenter("me", 16000, 1, lambda *a, **k: None)
    cap.tap = lambda x, rate: got.append(float(np.abs(x).max()) if x is not None else 0.0)
    quiet = (np.random.RandomState(1).randn(480) * 0.004).astype("float32")
    for _ in range(20):
        cap._got(quiet, 16000)
    assert got and max(got) == 0.0                              # a quiet room is sent as silence


def test_looks_askable(app):
    ask = ["Tell me about yourself.", "Walk me through your last project", "How does BGP choose a path",
           "and why?", "Can you give an example", "Describe how you would design a backup plan.",
           "Erzählen Sie mir von Ihrer Erfahrung", "Was ist der Unterschied zwischen TCP und UDP"]
    quiet = ["We are a company founded in 2010 in Berlin.", "Great, thank you.", "Our team has twelve people and we ship monthly."]
    for s in ask:
        assert app.looks_askable(s, "en"), s
    for s in quiet:
        assert not app.looks_askable(s, "en"), s
    assert app.looks_askable("Please introduce yourself", "en") and app.looks_askable("Walk us through your CV", "en")
    assert app.looks_askable("سلام معرفی کنید", "")                # unknown language, not plain English: never dropped
    assert app.looks_askable("سلام خوش آمدید", "fa")           # other languages: always yes


class _Hub:
    def publish(self, *a, **k): pass
    def toast(self, *a, **k): pass


class _FakeApp:
    def __init__(self, app):
        self.cfg = app.sanitize({})
        self.hub = _Hub()
        self.stats = app.Stats()
        self.captures = []
        self.running = False
        self.engine = None
    def provider(self, pid): return None


def _engine(app):
    fa = _FakeApp(app)
    sess = app.Session(fa.cfg)
    eng = app.Engine(fa, sess, workers=False)
    calls = []
    eng._answer = lambda eid, force=False, question=None, _retry=0: calls.append((eid, force, question))
    eng._submit_tr = lambda eid: True
    return eng, sess, calls


def _say(app, eng, text, when=None):
    now = when or __import__("time").time()
    eng.accept_text("them", text, "en", now - 2, now - 0.1, [next(app._seg_counter)],
                    {"pause": 0.0, "queue": 0.0, "stt": 0.0, "service": "x", "model": "x"})


def test_question_in_pieces_gets_one_answer(app):
    import time
    eng, sess, calls = _engine(app)
    try:
        _say(app, eng, "Tell me about a time")
        time.sleep(0.4)
        _say(app, eng, "when you led a team through an outage")
        time.sleep(1.8)
        assert len(calls) == 1, calls
        assert "Tell me about a time" in calls[0][2] and "outage" in calls[0][2]
        first = sess.ordered()[0]
        assert first["ans_state"] == "none"                     # the first piece was merged into the second
    finally:
        eng.stop_event.set()


def test_statements_and_old_lines_are_not_answered(app):
    import time
    eng, sess, calls = _engine(app)
    try:
        _say(app, eng, "We are a company founded in 2010 in Berlin.")
        _say(app, eng, "Great, thank you.")
        eng.accept_text("them", "How would you monitor a database?", "en", time.time() - 200, time.time() - 199, [next(app._seg_counter)],
                        {"pause": 0.0, "queue": 0.0, "stt": 0.0, "service": "x", "model": "x"})
        time.sleep(1.6)
        assert calls == []
    finally:
        eng.stop_event.set()


def test_question_mark_is_answered_quickly(app):
    import time
    eng, sess, calls = _engine(app)
    try:
        _say(app, eng, "How would you monitor a database?")
        time.sleep(0.7)
        assert len(calls) == 1 and calls[0][2] is None
    finally:
        eng.stop_event.set()


def test_answer_button_cancels_a_waiting_automatic_answer(app):
    import time
    eng, sess, calls = _engine(app)
    try:
        _say(app, eng, "Explain how OSPF elects a DR")
        eng.answer_now()
        time.sleep(1.6)
        assert [c[1] for c in calls] == [True]                  # only the forced one
    finally:
        eng.stop_event.set()


def test_stopped_meeting_leaves_no_answer_writing(app):
    import time
    eng, sess, calls = _engine(app)
    _say(app, eng, "Explain how OSPF elects a DR")
    eng.stop_event.set()                                        # the meeting ends during the short wait
    time.sleep(1.6)
    assert calls == []
    assert sess.ordered()[0]["ans_state"] == "none"


def test_retry_does_not_override_a_forced_answer(app):
    eng, sess, calls = _engine(app)
    try:
        _say(app, eng, "How would you monitor a database?")
        eid = sess.ordered()[0]["id"]
        eng.ans_gen[eid] += 1                                   # the user pressed F2 meanwhile (a newer request)
        eng._retry_answer(eid, None, 1, 0)                      # the old retry wakes up
        assert calls == []
    finally:
        eng.stop_event.set()


def test_repeated_question_is_found(app):
    import time
    eng, sess, calls = _engine(app)
    now = time.time()
    a = sess.add("them", now - 200, now - 195, "How would you design a backup strategy for a large Oracle database?", "en", [], None)
    sess.add("me", now - 190, now - 150, "I would use RMAN and take backups every night, that is it.", "en", [], None)
    b = sess.add("them", now - 20, now - 15, "So how would you design a backup strategy for a big Oracle database?", "en", [], None)
    n, prev, said = eng.find_repeats(b, None)
    assert n == 1 and prev["id"] == a["id"] and "RMAN" in said
    c = sess.add("them", now - 5, now - 2, "Tell me about your experience with OSPF and BGP routing", "en", [], None)
    assert eng.find_repeats(c, None)[0] == 0
    # the same question in two pieces (no answer between) is not "asked again"
    d1 = sess.add("them", now + 1, now + 3, "How would you monitor replication lag on a standby", "en", [], None)
    d2 = sess.add("them", now + 4, now + 6, "How would you monitor replication lag on a standby database", "en", [], None)
    assert eng.find_repeats(d2, None)[0] == 0


def test_repeat_is_never_skipped_and_reaches_the_prompt(app):
    import time
    eng, sess, calls = _engine(app)
    eng.__dict__.pop("_answer", None)                            # use the real _answer
    seen = {}

    def fake_chat(chain, messages, max_tokens, temperature, on_text):
        seen["user"] = messages[-1]["content"]
        seen["system"] = messages[0]["content"]
        return "NO_REPLY"
    eng.run_chat = fake_chat
    eng.chat_targets = lambda task: [("groq", "m", None)]
    now = time.time()
    sess.add("them", now - 200, now - 195, "How would you design a backup strategy for a large Oracle database?", "en", [], None)
    sess.add("me", now - 190, now - 150, "I would use RMAN nightly.", "en", [], None)
    b = sess.add("them", now - 20, now - 15, "How would you design a backup strategy for a large Oracle database?", "en", [], None)
    eng._answer(b["id"])
    assert "REPEATED QUESTION" in seen["user"] and "RMAN nightly" in seen["user"]
    assert sess.get(b["id"])["repeat"] == 1
    assert sess.get(b["id"])["ans_state"] == "done"              # NO_REPLY is not accepted for an asked-again question


def test_situation_card_reads_the_model_answer(app):
    eng, sess, calls = _engine(app)
    import time
    now = time.time()
    sess.add("them", now - 50, now - 45, "Tell me about yourself", "en", [], None)
    sess.add("me", now - 40, now - 20, "I am a network engineer.", "en", [], None)
    sess.add("them", now - 10, now - 5, "How does OSPF elect a designated router", "en", [], None)
    published = []
    eng.hub = type("H", (), {"publish": lambda self, *a, **k: published.append((a, k)), "toast": lambda *a, **k: None})()
    eng.chat_targets = lambda task: [("groq", "m", None)]
    eng.run_chat = lambda *a, **k: 'Sure: {"phase": "technical", "topic": "OSPF DR election", "difficulty": 7, "trend": "up", "signal": "meh", "tip": "Answer directly."}'
    eng._coach_run()
    st = eng.coach_state
    assert st["phase"] == "technical" and st["difficulty"] == 5 and st["trend"] == "up" and st["signal"] == "neutral"
    assert published and published[0][0][0] == "coach"
    eng.run_chat = lambda *a, **k: "not json at all"
    eng._coach_run()                                             # a bad reply changes nothing and raises nothing
    assert eng.coach_state is st


def test_similar_frames_are_not_repeats(app):
    sim = app.Engine._sim
    assert sim("How would you back up the production database?", "How would you restore the production database?") < app.REPEAT_SIM
    assert sim("Tell me about your experience with Oracle", "Tell me about your experience with Kubernetes") < app.REPEAT_SIM
    assert sim("Can you walk me through how you would design the backup?", "Can you walk me through how you would test the backup?") < app.REPEAT_SIM
    assert sim("How would you design a backup strategy for a large Oracle database?",
               "So how would you design a backup strategy for a big Oracle database?") >= app.REPEAT_SIM
    assert sim("Why did you leave your last job", "Why did you leave your last job") >= app.REPEAT_SIM


def test_coach_reply_parsing_is_forgiving(app):
    import time
    eng, sess, calls = _engine(app)
    now = time.time()
    sess.add("them", now - 50, now - 45, "Tell me about yourself", "en", [], None)
    sess.add("them", now - 10, now - 5, "How does OSPF elect a designated router", "en", [], None)
    eng.chat_targets = lambda task: [("groq", "a", None), ("groq", "b", None)]
    used = []
    eng.hub = type("H", (), {"publish": lambda *a, **k: None, "toast": lambda *a, **k: None})()

    def chat(chain, *a, **k):
        used.append(chain)
        return '```json\n{"phase": "intro", "topic": "x", "difficulty": 2} trailing } text\n```'
    eng.run_chat = chat
    eng._coach_run()
    assert eng.coach_state["phase"] == "intro"
    assert used[0] == [("groq", "b", None)]                     # its own model, not the first one the answers use
    eng.run_chat = lambda *a, **k: "[1, 2]"
    eng._coach_run()                                             # a list is not a situation
    assert eng.coach_state["phase"] == "intro"


def test_question_types_and_targets(app):
    cases = {"Tell me about yourself": "intro", "Tell me about a time you disagreed with your manager": "behavioural",
             "How would you design a backup strategy for a large database?": "design",
             "What would you do if the database suddenly becomes slow?": "troubleshoot",
             "What is the difference between TCP and UDP?": "concept",
             "Do you have any questions for us?": "candidate_q", "What are your salary expectations?": "salary",
             "What is your notice period?": "availability", "What is your greatest weakness?": "weakness",
             "Have you worked with Oracle Data Guard?": "experience", "Can you write a function that reverses a list?": "coding",
             "Why do you want to work here?": "motivation", "Do you know Linux?": "yesno"}
    for text, want in cases.items():
        got = app.classify_question(text)[0]
        assert got == want, (text, got, want)
    assert app.classify_question("We are a company founded in 2010")[0] == ""
    name, lo, hi = app.classify_question("Tell me about yourself")
    assert (lo, hi) == (60, 90) and app.qtype_hint("intro", "fa") and app.qtype_hint("intro", "en") != app.qtype_hint("intro", "fa")


def _rows(app, spec):
    """spec: [(source, t0, t_end, text, extra)] -> entries with ids"""
    out = []
    for i, (src, a, b, text, extra) in enumerate(spec, 1):
        out.append({"id": i, "source": src, "t0": a, "t_end": b, "text": text, **extra})
    return out


def test_reply_check_flags(app):
    q = {"id": 1, "source": "them", "t0": 0, "t_end": 3, "text": "Tell me about a time you led a team", "qtype": "behavioural", "qmin": 90, "qmax": 120}
    long_text = "I think maybe it was kind of a hard project and I guess we probably did some things, you know. " * 6
    rows = [q, {"id": 2, "source": "me", "t0": 5, "t_end": 45, "text": long_text, "extra": 1}]
    rows += [{"id": 3, "source": "me", "t0": 46, "t_end": 86, "text": long_text, "extra": 1},
             {"id": 4, "source": "me", "t0": 87, "t_end": 127, "text": long_text, "extra": 1},
             {"id": 5, "source": "me", "t0": 128, "t_end": 168, "text": long_text, "extra": 1}]
    c = app.check_answer(rows, q)
    assert "long" in c["flags"] and "hedging" in c["flags"] and "no_example" in c["flags"], c
    good = [q, {"id": 2, "source": "me", "t0": 5, "t_end": 60,
                "text": "At my last company I led a team of six during a migration. We moved forty databases in three months and reduced downtime by 90 percent, "
                        "which the management noticed. I set the plan, split the work and reviewed every cutover with the team.", }]
    c = app.check_answer(good, q)
    assert c["flags"] == ["good"], c
    assert app.check_answer([q], q) is None


def test_notes_are_cleaned(app):
    n = app.clean_notes({"me_facts": ["8 years OSPF", "", 5, {"x": 1}], "topics": "not a list", "brief": {"key_messages": ["a", "b"], "junk": 1},
                         "commitments": ["send the report on Friday"] * 30})
    assert n["me_facts"] == ["8 years OSPF", "5"] and "topics" not in n
    assert len(n["commitments"]) == 8 and n["brief"] == {"key_messages": ["a", "b"]}
    assert app.clean_notes("x") == {} and app.clean_notes(None) == {}


def test_coach_writes_notes_and_alert(app):
    import time
    eng, sess, calls = _engine(app)
    now = time.time()
    sess.add("them", now - 90, now - 85, "How many years of OSPF experience do you have", "en", [], None)
    sess.add("me", now - 80, now - 70, "I have five years of OSPF experience", "en", [], None)
    sess.add("them", now - 30, now - 25, "And how long did you work with BGP", "en", [], None)
    sess.add("me", now - 20, now - 10, "Eight years of OSPF and BGP", "en", [], None)
    published = []
    eng.hub = type("H", (), {"publish": lambda self, *a, **k: published.append((a[0], k)), "toast": lambda *a, **k: None})()
    eng.chat_targets = lambda task: [("groq", "a", None), ("groq", "b", None)]
    seen = {}

    def chat(chain, messages, *a, **k):
        seen["sys"], seen["user"] = messages[0]["content"], messages[1]["content"]
        return ('{"phase": "technical", "topic": "OSPF", "difficulty": 3, "trend": "same", "signal": "neutral", '
                '"tip": "Clarify: five or eight years?", "alert": "You said 5 years, then 8 years of OSPF", '
                '"notes": {"me_facts": ["5 years OSPF (said first)", "8 years OSPF and BGP (said later)"], "topics": ["OSPF", "BGP"]}}')
    eng.run_chat = chat
    eng._coach_run()
    assert eng.coach_state["alert"].startswith("You said 5 years")
    assert sess.coach_notes["me_facts"][0].startswith("5 years") and "coach_notes" in [p[0] for p in published]
    assert "interview" in seen["sys"].lower() or "meeting" in seen["sys"].lower()
    assert "Tips already shown" not in seen["user"]
    # (second run shows the earlier tip so it is not repeated)
    eng.coach_last = 0
    eng._coach_run()
    assert "Clarify: five or eight years?" in seen["user"]
    assert "5 years OSPF" in eng.notes_text()


def test_coach_help_and_brief(app):
    import time
    eng, sess, calls = _engine(app)
    eng.cfg["about_me"] = "Network engineer, 8 years OSPF and BGP, Oracle DBA."
    eng.chat_targets = lambda task: [("groq", "a", None), ("groq", "b", None)]
    got = {}

    def chat(chain, messages, *a, **k):
        got["chain"], got["user"] = chain, messages[-1]["content"]
        if "prepare a user" in messages[0]["content"]:
            return '{"key_messages": ["Show OSPF depth"], "strengths": ["8 years"], "risks": ["No cloud: say what you learn"], "ask_them": ["What does success look like?"]}'
        return "  Say the direct answer first, then one example.  "
    eng.run_chat = chat
    eng.coach_brief()
    assert sess.coach_notes["brief"]["key_messages"] == ["Show OSPF depth"]
    assert "8 years OSPF" in got["user"]
    now = time.time()
    sess.add("them", now - 10, now - 5, "Explain OSPF areas", "en", [], None)
    out = eng.coach_help("what now?")
    assert out == "Say the direct answer first, then one example."
    assert len(got["chain"]) == 2 and "what now?" in got["user"]         # the help key uses the whole chain
    eng.stop_event.set()


def test_question_types_negatives_and_german(app):
    not_behavioural = ["Have you ever used Terraform?", "Can you give me an example of an index?", "How do you resolve a merge conflict in git?",
                       "What happens on a node failure in a cluster?", "How does RMAN handle a block failure?"]
    for t in not_behavioural:
        assert app.classify_question(t)[0] != "behavioural", t
    assert app.classify_question("Have you ever used Terraform?")[0] == "experience"
    assert app.classify_question("How much do you know about our company?")[0] != "salary"
    assert app.classify_question("How much do you expect to earn?")[0] == "salary"
    assert app.classify_question("What design patterns do you know?")[0] != "design"
    assert app.classify_question("How would you tune a slow SQL query?")[0] not in ("coding", "behavioural")
    assert app.classify_question("Have you ever had a conflict with a colleague?")[0] == "behavioural"
    assert app.classify_question("Wie gehen Sie mit Konflikten um?")[0] == "behavioural"
    assert app.classify_question("Wie viel Gehalt erwarten Sie?")[0] == "salary"
    assert app.classify_question("Stellen Sie sich bitte kurz vor")[0] == "intro"
    assert app.classify_question("Haben Sie noch Fragen an uns?")[0] == "candidate_q"


def test_reply_check_scope_and_speed(app):
    q1 = {"id": 1, "source": "them", "t0": 0, "t_end": 3, "text": "Tell me about a time you led a team", "qtype": "behavioural", "qmin": 90, "qmax": 120}
    ans = "At my last job I led six people and we cut the downtime by 90 percent in three months. " * 5
    q2 = {"id": 3, "source": "them", "t0": 200, "t_end": 204, "text": "Where are you based at the moment please"}
    late = {"id": 4, "source": "me", "t0": 206, "t_end": 209, "text": "I am in Berlin now, close to the office."}
    rows = [q1, {"id": 2, "source": "me", "t0": 5, "t_end": 65, "text": ans}, q2, late]
    c = app.check_answer(rows, q1)
    assert c["secs"] == 60 and "long" not in c["flags"], c                # the later short reply is not added to the first answer
    c2 = app.check_answer(rows, q2)
    assert c2["words"] < 12 and c2["qid"] == 3
    one = [q1, {"id": 2, "source": "me", "t0": 5, "t_end": 95, "text": "word " * 150}]
    c = app.check_answer(one, q1)
    assert c["secs"] == 90 and c["wpm"] == 100 and "fast" not in c["flags"], c   # a long single line keeps its real duration
    de = [q1, {"id": 2, "source": "me", "t0": 5, "t_end": 60, "lang": "de", "text": "Ich habe sechs Leute geführt und wir haben das Projekt pünktlich abgeschlossen. " * 3}]
    assert "no_example" not in app.check_answer(de, q1)["flags"]         # English word lists: no verdict on German


def test_notes_merge_and_stale_check(app):
    import time
    eng, sess, calls = _engine(app)
    now = time.time()
    sess.add("them", now - 90, now - 85, "How many years of OSPF experience do you have", "en", [], None)
    sess.add("them", now - 60, now - 55, "And how long did you work with BGP", "en", [], None)
    sess.coach_notes = {"me_facts": ["8 years OSPF"], "topics": ["OSPF"], "brief": {"key_messages": ["x"]}}
    eng.hub = type("H", (), {"publish": lambda self, *a, **k: None, "toast": lambda *a, **k: None})()
    eng.chat_targets = lambda task: [("groq", "a", None)]
    eng.run_chat = lambda *a, **k: '{"phase": "technical", "difficulty": 1e999, "alert": "None", "notes": {"topics": ["BGP"]}}'
    eng._coach_run()
    assert sess.coach_notes["me_facts"] == ["8 years OSPF"] and sess.coach_notes["topics"] == ["BGP"]   # an omitted list is kept
    assert sess.coach_notes["brief"]["key_messages"] == ["x"] and eng.coach_state["alert"] == ""
    eng.last_check = {"qid": 1, "secs": 10, "words": 20, "wpm": None, "flags": []}
    assert eng.current_check() is None                                    # it belongs to an older question
    eng.chat_targets = lambda task: [("llm", "local", None), ("groq", "a", None)]
    assert eng.coach_chain() == [("llm", "local", None)]                  # the background text stays on the local model
    eng.chat_targets = lambda task: []
    assert eng.coach_chain() == []


def test_help_key_is_single_flight(app):
    eng, sess, calls = _engine(app)
    class A: pass
    a = app.App.__new__(app.App)
    a.engine = eng
    eng.cfg["coach"] = True
    assert eng._help_lock.acquire(blocking=False)
    r = a.api_coach_help("x")
    assert not r["ok"] and "still" in r["error"]
    eng._help_lock.release()
    eng.cfg["coach"] = False
    assert "off" in a.api_coach_help("x")["error"]


def test_exam_mode_and_describe_questions(app):
    assert "exam" in app.MODES and "client" in app.MODES and app.CHOICES["meeting_mode"] == tuple(app.MODES)
    assert "IELTS" in app.MODES["exam"]["name"] and "level" in app.MODES["exam"]["answer"]
    assert app.classify_question("Describe a place you like to visit")[0] == "describe"
    assert app.classify_question("You should say where it is and why you like it")[0] == "describe"
    assert app.classify_question("Describe a time you failed at work")[0] == "behavioural"
    for t in ("Now I'd like you to talk about your hometown.", "Do you agree or disagree with this statement", "Let's move to part two"):
        assert app.looks_askable(t, "en"), t
    assert "speaking-test" in app.COACH_ROLES["exam"] and "negotiation" in app.COACH_ROLES["client"]


def test_overlay_api_off_windows(app):
    a = app.App.__new__(app.App)
    a.cfg = dict(app.DEFAULTS)
    a.hub = type("H", (), {"publish": lambda self, *x, **k: None})()
    a.url = "http://127.0.0.1:1/?t=x"
    a.closing = __import__("threading").Event()
    a.overlay = app.Overlay(a)
    real = app.sys.platform
    app.sys.platform = "linux"                                  # never open a real window from a test, also on Windows
    try:
        r = a.api_overlay()
        assert r["ok"] is False and "Windows" in r["error"] and r["on"] is False
        assert a.api_overlay(False)["ok"] is True
    finally:
        app.sys.platform = real
    assert app.DEFAULTS["overlay_alpha"] == 65 and app.DEFAULTS["overlay_hide"] is True and app.CHOICES["overlay_pos"] == ("top", "bottom")


def _chat_returns(eng, text, seen=None):
    eng.chat_targets = lambda task: [("groq", "a", None)]
    def chat(chain, messages, *a, **k):
        if seen is not None:
            seen.append(messages)
        return text
    eng.run_chat = chat


def test_scores_clean_and_saved(app, tmp_path):
    sc = app.clean_scores({"clarity": 4, "structure": "3", "depth": 9, "signals": 0, "follow_up": 2.6, "fixes": ["a", "", 5, {"x": 1}, "b", "c", "d"], "best": " ok "})
    assert sc["clarity"] == 4 and sc["structure"] == 3 and sc["depth"] == 5 and "signals" not in sc and sc["follow_up"] == 3
    assert sc["fixes"] == ["a", "5", "b"] and sc["best"] == "ok" and sc["overall"] == round((4 + 3 + 5 + 3) / 4, 1)
    assert app.clean_scores({"clarity": 4}) == {} and app.clean_scores("x") == {} and app.clean_scores({"clarity": float("inf"), "structure": 1, "depth": 1}) == {}
    eng, sess, calls = _engine(app)
    import time
    now = time.time()
    for i, (src, t) in enumerate([("them", "Explain OSPF areas to me please"), ("me", "OSPF areas split the network so that routers keep small tables"),
                                  ("them", "And what is a stub area exactly"), ("me", "A stub area blocks external routes and uses a default route")]):
        sess.add(src, now - 100 + i * 10, now - 95 + i * 10, t, "en", [], None)
    _chat_returns(eng, 'Here: {"clarity": 4, "structure": 3, "depth": 4, "signals": 2, "follow_up": 3, "fixes": ["Add a number"], "best": "OSPF answer"}')
    got = eng.debrief_scores(sess.ordered(), {})
    assert got["overall"] == 3.2 and got["fixes"] == ["Add a number"]
    sess.set_scores(got)
    assert sess.state()["scores"]["clarity"] == 4
    sess.set_feedback("new review")
    assert sess.scores == {}                                   # the old scores do not belong to a new review


def test_job_prep_and_note(app):
    eng, sess, calls = _engine(app)
    eng.cfg["job_ad"] = "Senior Oracle DBA. RMAN, Data Guard, Linux, 5+ years. " * 3
    assert "Senior Oracle DBA" in app.job_note(eng.cfg) and app.job_note({"job_ad": ""}) == ""
    assert "Senior Oracle DBA" in eng.coach_background(1000)
    seen = []
    _chat_returns(eng, "## What they look for\n- RMAN", seen)
    out = eng.job_prep(eng.cfg["job_ad"])
    assert out.startswith("## What they look for") and "Job advert" in seen[0][1]["content"]
    a = app.App.__new__(app.App)
    a.engine = None
    a.cfg = {"job_ad": ""}
    a.tool_eng = None
    assert a.api_job_prep("short")["ok"] is False


def test_practice_questions_grade_and_finish(app, tmp_path):
    import time
    app.PRACTICE_PATH = str(__import__("pathlib").Path(tmp_path) / "practice.json")
    eng, sess, calls = _engine(app)
    _chat_returns(eng, 'Sure: ["Tell me about yourself", "Why this job?", "Tell me about yourself", 5, ""]')
    qs = eng.practice_questions("general", 5)
    assert [q["q"] for q in qs] == ["Tell me about yourself", "Why this job?"] and qs[0]["type"] == "intro"
    _chat_returns(eng, "1. What is RMAN?\n2. Explain Data Guard\nnot a question")
    assert [q["q"] for q in eng.practice_questions("technical", 3)] == ["What is RMAN?", "Explain Data Guard"]
    app.save_practice({"weak": [{"q": "Old weak question?", "t": 1, "type": ""}], "history": []})
    _chat_returns(eng, '["New one?"]')
    q = eng.practice_questions("redrill", 3)
    assert q[0]["q"] == "Old weak question?" and q[1]["q"] == "New one?"
    # grading
    good = ("At my last company I migrated forty databases to a new RMAN scheme in three months and cut the restore time by half. " * 2)
    _chat_returns(eng, '{"clarity": 4, "structure": 4, "depth": 3, "signals": 5, "tips": ["Shorter"], "better": "Say it in one line.", "follow_up": "How did you test it?"}')
    r = eng.practice_grade("Tell me about a time you improved backups", good, "behavioural", 45)
    assert r["avg"] == 4.0 and r["follow_up"].startswith("How") and r["scores"]["signals"] == 5 and not r["empty"]
    assert eng.practice_grade("Why this job?", "um", "general", 3)["empty"] is True      # no model call for no answer
    _chat_returns(eng, "no json here")
    try:
        eng.practice_grade("Why this job?", good, "general", 40)
        assert False
    except app.APIError:
        pass
    _chat_returns(eng, '{"clarity": 4, "structure": 4, "depth": 3, "signals": 5, "language": 0}')
    r = eng.practice_grade("Describe a place", good, "english", 40)    # one missing score gets the average of the others
    assert r["scores"]["language"] == 4
    _chat_returns(eng, '{"clarity": 4, "structure": 0, "depth": 0, "signals": 5}')
    try:
        eng.practice_grade("Describe a place", good, "english", 40)     # too many missing scores are not accepted
        assert False
    except app.APIError:
        pass
    # finish: good answers leave the weak list, bad ones and empty ones enter it
    a = app.App.__new__(app.App)
    a.practice_until = time.time() + 100
    out = a.api_practice_finish("general", [{"q": "Old weak question?", "avg": 4.2}, {"q": "Bad one?", "avg": 2.0}, {"q": "Skipped?", "avg": None},
                                            {"q": 5}, "x", {"q": "Bool?", "avg": True}])
    st = app.load_practice()
    assert out["avg"] == 2.7 or out["avg"] == 3.1
    assert {w["q"] for w in st["weak"]} == {"Bad one?", "Skipped?", "Bool?"} and a.practice_until == 0.0
    assert st["history"][-1]["kind"] == "general"


def test_practice_mutes_answers_and_coach(app):
    import time
    eng, sess, calls = _engine(app)
    eng.app.practice_until = time.time() + 60
    try:
        _say(app, eng, "Tell me about a time you led a team through an outage?")
        time.sleep(0.6)
        assert calls == [] and eng.plan is None
        eng.app.practice_until = 0.0
        _say(app, eng, "Tell me about a time you led a team through another outage?")
        time.sleep(0.8)
        assert len(calls) == 1
    finally:
        eng.stop_event.set()


def test_overlay_keys_and_new_defaults(app):
    for k in ("toggle", "more", "less", "screen", "answer", "coach", "up", "down", "prev", "next"):
        assert k in app.OV_KEYS
    assert app.DEFAULTS["auto_screen"] is False and app.DEFAULTS["debrief_scores"] is True and app.DEFAULTS["job_ad"] == ""


def test_second_piece_after_the_first_was_answered(app):
    import time
    eng, sess, calls = _engine(app)
    try:
        _say(app, eng, "Tell me about a time")
        time.sleep(1.5)                                          # the first piece is answered already (no plan is waiting)
        assert len(calls) == 1
        _say(app, eng, "when you led a team through an outage")  # used to raise TypeError (old plan is None)
        time.sleep(1.8)
        assert len(calls) == 2 and "outage" in calls[1][2] and "Tell me about a time" in calls[1][2]
    finally:
        eng.stop_event.set()


def test_json_from_and_clip_and_practice_file(app, tmp_path):
    assert app.json_from('Scores {see} {"a": 1}') == {"a": 1}
    assert app.json_from('[1] refs ["q?"]', list) == ["q?"]                # a stray [1] is skipped
    assert app.json_from("no json") is None and app.json_from(None) is None and app.json_from('{"a": ', dict) is None
    assert app.clip("", 10) == "" and app.clip(None, 10) == "" and app.clip("a  b", 10) == "a b" and app.clip("x" * 20, 5) == "xxxxx…"
    sc = app.clean_scores({"clarity": 4, "structure": 4, "depth": 4})
    assert sc["best"] == "" and sc["fixes"] == []                          # a missing text stays empty (never the word "str")
    assert app.score_int(True) == 0 and app.score_int(0) == 0 and app.score_int(8) == 5 and app.score_int("x") == 0
    path = __import__("pathlib").Path(tmp_path) / "practice.json"
    app.PRACTICE_PATH = str(path)
    path.write_text('{"weak": [{"q": "Ok?", "t": "bad"}, {"q": 5}, "x"], "history": [{"t": "x", "avg": "y", "n": "z"}, 5]}', encoding="utf-8")
    st = app.load_practice()
    assert st["weak"] == [{"q": "Ok?", "t": 0.0, "type": ""}] and st["history"][0]["avg"] is None
    a = app.App.__new__(app.App)
    a.practice_until = 0.0
    out = a.api_practice_finish("general", [{"q": "N?", "avg": float("nan")}, {"q": "I?", "avg": float("inf")}, {"q": "Fine?", "avg": 9}])
    assert out["ok"] and out["avg"] == 5.0                                 # only usable numbers count, and never above 5
    path.write_text("not json", encoding="utf-8")
    assert app.load_practice() == {"weak": [], "history": []}


def test_practice_mute_leaves_no_thinking_line(app):
    import time
    eng, sess, calls = _engine(app)
    eng.app.practice_until = time.time() + 60
    try:
        _say(app, eng, "Tell me about a time you led a team through an outage?")
        time.sleep(0.5)
        row = [r for r in sess.ordered() if r["source"] == "them"][0]
        assert row.get("ans_state") == "none" and calls == []
    finally:
        eng.stop_event.set()


def test_job_ad_is_capped(app):
    assert len(app.sanitize({"job_ad": "x" * 20000})["job_ad"]) == 8000


def test_round2_fixes(app):
    assert app.score_int("4/5") == 4 and app.score_int(" 3 / 5") == 3
    assert app.reply_numbers("hello there", float("inf"))["secs"] == 0
    a = app.App() if hasattr(app, "App") else None
    if a is not None:
        assert a.api_practice_questions(kind=["x"], n=float("inf"))["ok"] is False
        assert a.api_practice_grade(question="Q?", answer="a", kind={"a": 1}, secs=float("inf")).get("ok") in (True, False)
        a.running, a.started_at = True, __import__("time").time()
        assert a.api_practice_mode(on=True).get("ignored") is True and a.practice_until == 0.0


def test_selfcheck_and_new_fixes(app):
    a = app.App()
    r = a.api_selfcheck()
    assert r["ok"] and any(i["name"] == "Program" for i in r["items"]) and "Program" in r["report"]
    assert all(i["state"] in ("ok", "warn", "bad", "info") for i in r["items"])
    assert a.api_selfcheck(overlay_live=True)["ok"]                          # off Windows: skipped, no window
    assert app.clean_key(" “gsk_abc‏123” \n") == "gsk_abc123" and app.clean_key("گ") == ""
    assert app.sanitize({"api_key": "gsk_‏x y"})["api_key"] == "gsk_xy"


def test_blank_reply_tries_next_model_and_preview_is_soft(app):
    eng, sess, calls = _engine(app)
    eng.app.get_api = lambda pid=None: object()
    eng.app.note_request = lambda: None
    outs = iter(["", "second model text"])
    orig = app.chat_compat
    app.chat_compat = lambda *a, **k: next(outs)
    try:
        chain = [("groq", "m1", None), ("groq", "m2", None)]
        assert eng.run_chat(chain, [], 10, 0.1, lambda t: None) == "second model text"
        eng.models.cooldown("groq|m1", 60)
        try:
            eng.run_chat(chain, [], 10, 0.1, lambda t: None, soft=True)      # a preview does not use a resting model
            assert False
        except app.APIError:
            pass
        assert not eng.models.ok("groq|m1") and eng.models.ok("groq|m2")
    finally:
        app.chat_compat = orig
        eng.stop_event.set()


def test_session_save_survives_odd_text_and_tells(app, tmp_path):
    told = []
    app.save_alert = lambda kind, msg: told.append((kind, msg))
    eng, sess, calls = _engine(app)
    sess.add("them", 1.0, 2.0, "hello \ud83d there", "en", [1])
    sess.dirty = True
    sess._save()                                                              # a lone surrogate does not lose the file
    assert os.path.isfile(sess.path)
    eng.stop_event.set()
