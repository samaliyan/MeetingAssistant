"""OpenAI live speech to text: session settings, 24 kHz audio, the stream against a local fake of the
service (HTTP for the session key + WebSocket for the audio), and how it is wired into the program."""
import base64
import hashlib
import json
import socket
import struct
import threading
import time

import numpy as np
import pytest


# ---- a tiny fake of OpenAI's live service -------------------------------------------------------
class FakeOpenAILive:
    """POST /v1/realtime/client_secrets -> a session key; GET /v1/realtime (WebSocket) -> a transcription
    session that answers with speech events once enough audio has arrived."""

    def __init__(self, sentences=(("hello there", 1.0),), secret="ek_test", fail_secret=None, error_event=None):
        self.sentences = list(sentences)       # (text, seconds of audio before it is "spoken")
        self.secret = secret
        self.fail_secret = fail_secret
        self.error_event = error_event
        self.session = None
        self.secret_session = None
        self.auth = None
        self.audio_bytes = 0
        self.commits = 0
        self.pings = 0
        self.sock = socket.socket()
        self.sock.bind(("127.0.0.1", 0))
        self.sock.listen(5)
        self.port = self.sock.getsockname()[1]
        threading.Thread(target=self._serve, daemon=True).start()

    @property
    def base_url(self):
        return f"http://127.0.0.1:{self.port}/v1"

    def _serve(self):
        while True:
            try:
                conn, _ = self.sock.accept()
            except OSError:
                return
            threading.Thread(target=self._client, args=(conn,), daemon=True).start()

    @staticmethod
    def _read_request(conn):
        data = b""
        while b"\r\n\r\n" not in data:
            chunk = conn.recv(4096)
            if not chunk:
                return None, {}, b""
            data += chunk
        head, _, rest = data.partition(b"\r\n\r\n")
        lines = head.decode("latin-1").split("\r\n")
        headers = {k.strip().lower(): v.strip() for k, _, v in (ln.partition(":") for ln in lines[1:])}
        n = int(headers.get("content-length") or 0)
        while len(rest) < n:
            rest += conn.recv(4096)
        return lines[0], headers, rest

    def _client(self, conn):
        try:
            line, headers, body = self._read_request(conn)
            if line is None:
                return
            if line.startswith("POST") and "/realtime/client_secrets" in line:
                if self.fail_secret:
                    payload = json.dumps({"error": {"message": self.fail_secret}}).encode()
                    conn.sendall(b"HTTP/1.1 401 Unauthorized\r\nContent-Type: application/json\r\n"
                                 b"Content-Length: " + str(len(payload)).encode() + b"\r\nConnection: close\r\n\r\n"
                                 + payload)
                    return
                self.secret_session = json.loads(body)["session"]
                payload = json.dumps({"value": self.secret, "session": {"type": "transcription"}}).encode()
                conn.sendall(b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: "
                             + str(len(payload)).encode() + b"\r\nConnection: close\r\n\r\n" + payload)
                return
            if line.startswith("GET") and "/realtime" in line and headers.get("upgrade", "").lower() == "websocket":
                self.auth = headers.get("authorization")
                accept = base64.b64encode(hashlib.sha1((headers["sec-websocket-key"] +
                                                         "258EAFA5-E914-47DA-95CA-C5AB0DC85B11").encode()).digest())
                conn.sendall(b"HTTP/1.1 101 Switching Protocols\r\nUpgrade: websocket\r\nConnection: Upgrade\r\n"
                             b"Sec-WebSocket-Accept: " + accept + b"\r\n\r\n")
                self._session_loop(conn)
        except OSError:
            pass
        finally:
            conn.close()

    @staticmethod
    def _recv_frame(conn):
        def exact(n):
            buf = b""
            while len(buf) < n:
                chunk = conn.recv(n - len(buf))
                if not chunk:
                    raise OSError("closed")
                buf += chunk
            return buf
        b1, b2 = exact(2)
        n = b2 & 0x7F
        if n == 126:
            n = struct.unpack(">H", exact(2))[0]
        elif n == 127:
            n = struct.unpack(">Q", exact(8))[0]
        mask = exact(4)
        data = bytes(b ^ mask[i % 4] for i, b in enumerate(exact(n)))
        return b1 & 0x0F, data

    @staticmethod
    def _send(conn, event):
        data = json.dumps(event).encode()
        head = bytes([0x81]) + (bytes([len(data)]) if len(data) < 126 else bytes([126]) + struct.pack(">H", len(data)))
        conn.sendall(head + data)

    def _session_loop(self, conn):
        spoken = 0
        while True:
            op, data = self._recv_frame(conn)
            if op == 0x8:
                return
            if op == 0x9:                                    # ping -> pong
                self.pings += 1
                conn.sendall(bytes([0x8A, len(data)]) + data)
                continue
            event = json.loads(data)
            if event["type"] == "session.update":
                self.session = event["session"]
                self._send(conn, {"type": "session.updated", "session": {"type": "transcription"}})
                if self.error_event:
                    self._send(conn, {"type": "error", "error": self.error_event})
            elif event["type"] == "input_audio_buffer.append":
                self.audio_bytes += len(base64.b64decode(event["audio"]))
                seconds = self.audio_bytes / 48000                       # 24 kHz, 16-bit
                while spoken < len(self.sentences) and seconds >= self.sentences[spoken][1]:
                    text, at = self.sentences[spoken]
                    item = f"item_{spoken}"
                    start_ms = int(max(0.0, at - 0.8) * 1000)
                    self._send(conn, {"type": "input_audio_buffer.speech_started", "item_id": item,
                                      "audio_start_ms": start_ms})
                    words = text.split()
                    for i, w in enumerate(words):
                        self._send(conn, {"type": "conversation.item.input_audio_transcription.delta",
                                          "item_id": item, "delta": (" " if i else "") + w})
                    self._send(conn, {"type": "input_audio_buffer.speech_stopped", "item_id": item,
                                      "audio_end_ms": int(at * 1000)})
                    self._send(conn, {"type": "conversation.item.input_audio_transcription.completed",
                                      "item_id": item, "transcript": text + "."})
                    spoken += 1
            elif event["type"] == "input_audio_buffer.commit":
                self.commits += 1
                self._send(conn, {"type": "error", "error": {"code": "input_audio_buffer_commit_empty",
                                                             "message": "buffer too small"}})

    def close(self):
        self.sock.close()


def tone(seconds, freq=220.0):
    t = np.arange(int(16000 * seconds)) / 16000
    return (0.2 * np.sin(2 * np.pi * freq * t)).astype(np.float32)


# ---- settings ---------------------------------------------------------------------------------------
def test_session_for_the_live_model_and_for_the_gpt4o_models(app):
    s = app.openai_live_session("gpt-live-transcribe", "de", ["OSPF"])
    inp = s["audio"]["input"]
    assert s["type"] == "transcription"
    assert inp["format"] == {"type": "audio/pcm", "rate": 24000}
    assert inp["transcription"] == {"model": "gpt-live-transcribe", "delay": "low", "languages": ["de"], "keywords": ["OSPF"]}
    assert inp["turn_detection"]["type"] == "server_vad"
    s = app.openai_live_session("gpt-4o-mini-transcribe", "en", ["OSPF", "RMAN"])
    assert s["audio"]["input"]["transcription"] == {"model": "gpt-4o-mini-transcribe", "language": "en",
                                                    "prompt": "OSPF, RMAN"}
    assert app.openai_live_session("", None)["audio"]["input"]["transcription"] == {"model": "gpt-live-transcribe",
                                                                                   "delay": "low"}


def test_stream_address_follows_the_service_address(app):
    assert app.openai_live_url("https://api.openai.com/v1") == "wss://api.openai.com/v1/realtime"
    assert app.openai_live_url("") == "wss://api.openai.com/v1/realtime"
    assert app.openai_live_url("http://127.0.0.1:8080/v1/") == "ws://127.0.0.1:8080/v1/realtime"


def test_upsampling_to_24k_is_seamless_across_pieces(app):
    t = np.arange(16000) / 16000
    pcm = (np.sin(2 * np.pi * 440 * t) * 12000).astype("<i2").tobytes()
    whole = np.frombuffer(app.Upsample24k()(pcm), dtype="<i2").astype(float)
    up = app.Upsample24k()
    pieces = np.frombuffer(b"".join(up(pcm[i:i + 962]) for i in range(0, len(pcm), 962)), dtype="<i2").astype(float)
    assert abs(len(whole) - 24000) <= 2 and abs(len(pieces) - len(whole)) <= 1
    n = min(len(whole), len(pieces))
    assert np.max(np.abs(whole[:n] - pieces[:n])) <= 1
    spectrum = np.abs(np.fft.rfft(pieces))
    assert abs(np.argmax(spectrum) * 24000 / len(pieces) - 440) < 2
    assert up(b"") == b""


def test_models_of_each_live_service(app):
    dg = {"preset": "deepgram", "kind": "live"}
    oa = {"preset": "openai-live", "kind": "live"}
    assert app.live_model(dg, "") == "nova-3" and app.live_model(dg, "nova-2") == "nova-2"
    assert app.live_model(dg, "gpt-live-transcribe") == "nova-3"          # never a model of the other service
    assert app.live_model(oa, "nova-3") == "gpt-live-transcribe"
    assert app.live_model(oa, "gpt-4o-transcribe") == "gpt-4o-transcribe"
    assert app.live_service({"kind": "live"})["models"][0] == "nova-3"      # saved before there were others
    assert app.live_service(oa)["pac"] == app.PAC_OPENAI


def test_saved_openai_live_service_is_a_live_one(app):
    provs = app.clean_providers([{"id": "openailive", "preset": "openai-live", "name": "OpenAI live",
                                  "base_url": "https://api.openai.com/v1", "api_key": "sk-x"}])
    assert provs[0]["kind"] == "live" and provs[0]["preset"] == "openai-live"
    assert app.PRESETS["openai-live"]["kind"] == "live"
    assert app.BILLING_PAGES["openai-live"].startswith("https://platform.openai.com/")


# ---- the stream against the fake service ------------------------------------------------------------
def _open(app, server, model="gpt-live-transcribe", language="en", terms=None):
    interim, final, failed = [], [], []
    lv = app.OpenAILive("them", "sk-real", model, language, "", lambda *a: interim.append(a),
                        lambda *a: final.append(a), lambda e: failed.append(e), terms=terms,
                        base_url=server.base_url)
    return lv, interim, final, failed


def _wait(cond, timeout=8.0):
    end = time.time() + timeout
    while time.time() < end:
        if cond():
            return True
        time.sleep(0.02)
    return cond()


def test_words_arrive_while_spoken_and_sentences_are_finished(app):
    server = FakeOpenAILive(sentences=[("hello there", 1.0), ("how are you today", 2.0)])
    lv, interim, final, failed = _open(app, server, terms=["OSPF"])
    try:
        start = time.time()
        for _ in range(25):                              # 2.5 s of sound in 100 ms pieces
            lv.feed(tone(0.1), 16000)
        assert _wait(lambda: len(final) == 2), (final, failed)
        assert not failed
        # the real key only went to the HTTP request; the stream used the session key
        assert server.auth == "Bearer ek_test"
        assert server.secret_session == server.session
        assert server.session["audio"]["input"]["transcription"]["languages"] == ["en"]
        texts = [f[3] for f in final]
        assert texts == ["hello there.", "how are you today."]
        assert [i[2] for i in interim][:2] == ["hello", "hello there"]   # word by word
        assert final[0][0] != final[1][0]                                 # each sentence its own key
        assert final[0][0] == interim[0][0]                               # interim and final share it
        for key, t0, t1, _ in final:                 # on the wall clock (the sound was fed faster than real time)
            assert start - 1 < t0 <= t1 < start + 3.5
        assert abs(server.audio_bytes / 48000 - 2.5) < 0.1                # 24 kHz audio, nothing lost
    finally:
        lv.stop()
        server.close()


def test_silence_is_not_sent_after_two_seconds(app):
    server = FakeOpenAILive(sentences=[])
    lv, _, _, failed = _open(app, server)
    try:
        lv.feed(tone(0.5), 16000)
        for _ in range(60):                                  # 6 s of silence
            lv.feed(np.zeros(1600, np.float32), 16000)
        assert _wait(lambda: server.audio_bytes / 48000 >= 2.35)
        time.sleep(0.5)
        assert 2.35 <= server.audio_bytes / 48000 <= 2.55     # the sound + about 2 s of silence, not the other 4 s
        assert not failed
    finally:
        lv.stop()
        server.close()


def test_stop_finishes_quietly_and_commits_the_last_words(app):
    server = FakeOpenAILive(sentences=[])
    lv, _, _, failed = _open(app, server)
    lv.feed(tone(0.3), 16000)
    assert _wait(lambda: server.audio_bytes > 0)
    lv.stop()
    assert _wait(lambda: not lv.thread.is_alive(), 8)
    assert server.commits == 1                       # (the empty-buffer answer is harmless)
    assert not failed
    server.close()


def test_a_quiet_line_is_kept_alive_with_pings(app):
    server = FakeOpenAILive(sentences=[])
    lv, _, _, failed = _open(app, server)
    try:
        lv.feed(tone(0.2), 16000)
        assert _wait(lambda: server.pings >= 1, 10)   # nothing to send for 4 s: a ping goes out
        assert not lv._idle_check(30) and lv._idle_check(46)
        assert not failed and lv.ok
    finally:
        lv.stop()
        server.close()


def test_a_rejected_key_fails_with_its_reason(app):
    server = FakeOpenAILive(fail_secret="Incorrect API key provided")
    lv, _, _, failed = _open(app, server)
    try:
        assert _wait(lambda: failed)
        assert isinstance(failed[0], app.AuthError)
        assert not lv.ok
    finally:
        server.close()


def test_a_service_error_during_the_session_fails_the_stream(app):
    server = FakeOpenAILive(error_event={"code": "invalid_value", "message": "Unsupported model"})
    lv, _, _, failed = _open(app, server)
    try:
        lv.feed(tone(0.2), 16000)
        assert _wait(lambda: failed)
        assert "Unsupported model" in str(failed[0])
    finally:
        server.close()


def test_open_words_are_kept_when_the_connection_breaks(app):
    final = []
    lv = app.OpenAILive.__new__(app.OpenAILive)
    lv.__dict__.update(source="them", sid=1, utt=0, sent=3.0, t_audio0=1000.0, break_pos=[0.0], break_off=[0.0],
                       items=app.collections.OrderedDict(), on_final=lambda *a: final.append(a),
                       on_interim=lambda *a: None, speaking=False, ready=threading.Event(),
                       done=app.collections.deque(maxlen=200))
    lv._handle({"type": "input_audio_buffer.speech_started", "item_id": "a", "audio_start_ms": 1000})
    lv._handle({"type": "conversation.item.input_audio_transcription.delta", "item_id": "a", "delta": "half a"})
    lv._flush()
    assert final and final[0][3] == "half a" and final[0][1] == 1001.0
    lv._handle({"type": "error", "error": {"code": "input_audio_buffer_commit_empty"}})   # harmless: ignored
    with pytest.raises(app.AuthError):
        lv._handle({"type": "error", "error": {"message": "You exceeded your current quota"}})
    with pytest.raises(app.AuthError):                   # a setting it does not take: not retried every minute
        lv._handle({"type": "error", "error": {"code": "invalid_value", "message": "Unsupported model"}})
    with pytest.raises(app.Transient):
        lv._handle({"type": "error", "error": {"code": "server_error", "message": "try again"}})


def test_repeated_or_late_events_never_write_a_sentence_twice(app):
    final, interim = [], []
    lv = app.OpenAILive.__new__(app.OpenAILive)
    lv.__dict__.update(source="them", sid=1, utt=0, sent=3.0, t_audio0=1000.0, break_pos=[0.0], break_off=[0.0],
                       items=app.collections.OrderedDict(), on_final=lambda *a: final.append(a),
                       on_interim=lambda *a: interim.append(a), speaking=False, ready=threading.Event(),
                       done=app.collections.deque(maxlen=200))
    done = {"type": "conversation.item.input_audio_transcription.completed", "item_id": "x", "transcript": "Hi."}
    lv._handle(done)                                   # (no speech_started seen for it)
    lv._handle(done)                                   # the same event again
    lv._handle({"type": "conversation.item.input_audio_transcription.delta", "item_id": "x", "delta": "late"})
    lv._handle({"type": "input_audio_buffer.speech_started", "item_id": "y", "audio_start_ms": 500})
    lv._handle({"type": "conversation.item.input_audio_transcription.delta", "item_id": "y", "delta": "next"})
    lv._flush()
    assert [f[3] for f in final] == ["Hi.", "next"]
    assert final[0][0] != final[1][0]                  # each sentence its own key
    assert [i[2] for i in interim] == ["next"]


def test_check_reports_the_time_to_a_ready_session(app):
    server = FakeOpenAILive(sentences=[])
    try:
        secs = app.openai_live_check("sk", "", "gpt-4o-transcribe", "auto", server.base_url)
        assert 0 <= secs < 5
        assert server.session["audio"]["input"]["transcription"] == {"model": "gpt-4o-transcribe"}
        prov = {"preset": "openai-live", "api_key": "sk", "base_url": server.base_url}
        assert app.live_check(prov, "", "nova-3") >= 0                      # a Deepgram model is not sent
        assert server.session["audio"]["input"]["transcription"]["model"] == "gpt-live-transcribe"
    finally:
        server.close()


# ---- wiring ------------------------------------------------------------------------------------------
def test_the_engine_opens_the_live_class_of_the_chosen_service(app):
    from test_tools import _engine
    eng, sess, calls = _engine(app)
    made = []

    class Lv:
        def __init__(self, *a, **k):
            made.append((self.kind, a, k))
            self.ok = True
            self.stop_event = threading.Event()

        def feed(self, *a):
            pass

        def pause(self, on):
            pass

    class Dg(Lv):
        kind = "deepgram"

    class Oa(Lv):
        kind = "openai"

    old = app.DeepgramLive, app.OpenAILive
    app.DeepgramLive, app.OpenAILive = Dg, Oa
    try:
        eng.speech_mode = lambda: {}
        eng.cfg["stt_model"] = "nova-3"                    # left over from Deepgram
        eng.app.provider = lambda pid: {"kind": "live", "preset": "openai-live", "api_key": "k", "name": "OpenAI live",
                                        "use_proxy": False, "base_url": "https://api.openai.com/v1"}
        cap = app.types.SimpleNamespace(source="them", tap=None, preview_every=1.0, seg=None)
        eng.start_live([cap])
        kind, args, kw = made[-1]
        assert kind == "openai" and args[2] == "gpt-live-transcribe"
        assert kw["base_url"] == "https://api.openai.com/v1"
        assert cap.tap is not None and cap.preview_every == 0.0
    finally:
        app.DeepgramLive, app.OpenAILive = old
