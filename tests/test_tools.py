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
