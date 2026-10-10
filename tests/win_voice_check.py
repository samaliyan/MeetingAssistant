"""Real Windows check of "Learn my voice" in the exe (run by .github/workflows/ci.yml, not by pytest).

    python tests/win_voice_check.py NEW.exe OUTDIR

The runner has no microphone, so Windows' own speech voices read sentences into WAV files and the program is told
(MA_TEST_MIC_WAV) to use one of them in place of the microphone. Checks, with the real exe:
  - "Learn my voice" downloads the voice model, learns the voice and keeps it (Data/voiceprint.json);
  - another recording of the same voice is taken as "me", a different voice as "them".
Prints one line per check (also as GitHub annotations); exit 1 when one fails."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request

EXE, OUT = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
os.makedirs(OUT, exist_ok=True)
results = []


def check(name, ok, detail=""):
    results.append(bool(ok))
    line = f"[{'OK' if ok else 'FAIL'}] {name}" + (f": {detail}" if detail else "")
    print(line, flush=True)
    if os.environ.get("GITHUB_ACTIONS"):
        print(("::notice" if ok else "::error") + " title=Voice::" + line.replace("%", "%25").replace("\n", "%0A"), flush=True)


TEXTS = {
    "a1": "Today I am trying the program so it learns my voice. I speak normally, as in a work meeting. "
          "We moved our main database to the new data centre last month, and the switchover took less than five minutes.",
    "a2": "Thank you for having me. In my last role I led a team of thirty people and planned the backups for every system.",
    "b1": "Could you tell me about a project you led recently, and what you would do differently next time?",
}


def speak(voice, text, path):
    ps = ("Add-Type -AssemblyName System.Speech; $s = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
          f"$s.SelectVoice('{voice}'); "
          "$f = New-Object System.Speech.AudioFormat.SpeechAudioFormatInfo(16000, [System.Speech.AudioFormat.AudioBitsPerSample]::Sixteen, [System.Speech.AudioFormat.AudioChannel]::Mono); "
          f"$s.SetOutputToWaveFile('{path}', $f); $s.Speak('{text}'); $s.Dispose()")
    subprocess.run(["powershell", "-NoProfile", "-Command", ps], check=True, timeout=120)


voices = subprocess.run(["powershell", "-NoProfile", "-Command",
                         "Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer)"
                         ".GetInstalledVoices() | ForEach-Object { $_.VoiceInfo.Name + '|' + $_.VoiceInfo.Gender }"],
                        capture_output=True, text=True, timeout=120).stdout.split("\n")
voices = [v.strip().split("|") for v in voices if "|" in v]
print("speech voices on this machine:", voices, flush=True)
male = next((v[0] for v in voices if v[1] == "Male"), None)
female = next((v[0] for v in voices if v[1] == "Female"), None)
check("Windows has two different speech voices", male and female, str(voices))
if not (male and female):
    sys.exit(1)
wav = {}
for k, text in TEXTS.items():
    wav[k] = os.path.join(OUT, k + ".wav")
    speak(male if k.startswith("a") else female, text, wav[k])

work = tempfile.mkdtemp(prefix="ma_voice_")
shutil.copy2(EXE, os.path.join(work, "MeetingAssistant.exe"))
data = os.path.join(work, "Data")
os.makedirs(data)
with open(os.path.join(data, "config.json"), "w", encoding="utf-8") as f:
    json.dump({"hide_from_share": False, "work_mode": "inperson"}, f)
env = dict(os.environ, MA_NO_BROWSER="1", MA_TEST_MIC_WAV=wav["a1"])
proc = subprocess.Popen([os.path.join(work, "MeetingAssistant.exe")], cwd=work, env=env)


def call(name, body=None, timeout=60):
    req = urllib.request.Request(f"http://127.0.0.1:{port}/api/{name}", data=json.dumps(body or {}).encode(),
                                 headers={"X-Token": key, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


try:
    end = time.time() + 120
    while time.time() < end and not os.path.exists(os.path.join(data, ".port")):
        time.sleep(0.2)
    port, key = open(os.path.join(data, ".port"), encoding="utf-8").read().split()[:2]
    st = call("voice_status")
    check("before: nothing learned", st.get("learned") is False, json.dumps(st))
    r = call("voice_learn", {"seconds": 10})
    check("Learn my voice starts", r.get("ok"), json.dumps(r))
    t0, seen, last = time.time(), [], {}
    while time.time() - t0 < 300:
        st = call("voice_status")
        last = st.get("learning") or {}
        if not seen or seen[-1] != last.get("state"):
            seen.append(last.get("state"))
        if last.get("state") in ("done", "error"):
            break
        time.sleep(0.5)
    check("learning finishes", last.get("state") == "done",
          f"after {time.time() - t0:.0f} s, states {seen}, last {json.dumps(last)}")
    st = call("voice_status")
    check("the voice is learned and kept", st.get("learned") and os.path.isfile(os.path.join(data, "voiceprint.json")), json.dumps(st))
    same = call("voice_try", {"path": wav["a2"]})
    check("the same voice, other words: me", same.get("who") == "me", json.dumps(same))
    other = call("voice_try", {"path": wav["b1"]})
    check("another voice: not me", other.get("who") == "them", json.dumps(other))
    log = os.path.join(data, "app.log")
    if os.path.isfile(log):
        for ln in open(log, encoding="utf-8", errors="replace").read().splitlines()[-12:]:
            print("log:", ln[:220], flush=True)
finally:
    subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)], capture_output=True)
    time.sleep(2)
    shutil.rmtree(work, ignore_errors=True)

ok = all(results)
print("RESULT:", "OK" if ok else "FAILED", flush=True)
sys.exit(0 if ok else 1)
