<div align="center">
  <h1>Meeting Assistant</h1>
  <p>Live transcript, instant translation into your language and suggested answers for online meetings and interviews — on Windows.</p>

  [![CI](https://github.com/samaliyan/MeetingAssistant/actions/workflows/ci.yml/badge.svg)](https://github.com/samaliyan/MeetingAssistant/actions/workflows/ci.yml)
  [![Latest release](https://img.shields.io/github/v/release/samaliyan/MeetingAssistant)](https://github.com/samaliyan/MeetingAssistant/releases/latest)
  [![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
  [![Windows](https://img.shields.io/badge/Windows-10%20%7C%2011-0078D4.svg)](#requirements)

  [Download](https://github.com/samaliyan/MeetingAssistant/releases/latest) · [User guide](Guide-EN.md) · [راهنمای فارسی](README_FA.md) · [Report a bug](https://github.com/samaliyan/MeetingAssistant/issues/new?template=bug_report.yml)
</div>

## What it does

Meeting Assistant listens to your **microphone** and to your **computer's sound** (Zoom, Teams, Meet, …), writes a
live transcript with speaker labels, translates every line into **your own language**, and suggests what to say when
you are asked a question.

- Live transcript of both sides ("Me" / "Person 1"), with text appearing while people are still speaking
- Instant translation into the language you choose (34 languages; right-to-left languages supported)
- Suggested answers, in the language of the question or in a fixed language, with their meaning in your language
- Answers use only the facts you give about yourself and stay consistent when a question is asked again
- Select words in any line to get them explained, or to get an answer about them
- Stop and **continue** the same meeting later (Shift+F9), even after restarting the program
- Meeting summary, and transcription of recorded audio / video files
- Works with **Groq** (free API key), any **OpenAI-compatible** service, **Deepgram** live — or completely
  **offline**: a local Whisper model for speech to text and a local AI model (llama.cpp, `.gguf`) for translation
  and answers, both downloadable inside the program
- Tools: post-meeting feedback, "help me say", read the screen, search past meetings, export (Word, subtitles, PDF), glossary, speaker separation, CV from a file
- Optional **hide from screen sharing** (some companies forbid assistants in interviews — check the rules first)
- See what credit or free limit is left with each service (Setup › Services › Credit & limits)

## Requirements

- Windows 10 or 11 (the computer's sound is recorded with WASAPI loopback)
- Headphones are strongly recommended
- One of: a free [Groq API key](https://console.groq.com/keys), another OpenAI-compatible service, Deepgram — or the
  local models (speech to text and a local AI model; the AI model wants about 4 GB of free memory)

## Quick start

1. Download `MeetingAssistant.exe` from the [latest release](https://github.com/samaliyan/MeetingAssistant/releases/latest)
   and put it in its own folder.
2. Run it. Setup opens on first start. (Windows SmartScreen may warn about an unknown publisher — choose
   *More info › Run anyway*.)
3. **Setup › Services**: paste a Groq API key, or add another service, or download a local model.
4. **Setup › Meeting**: choose the meeting languages, your language and the answer language; write the topic.
5. **Setup › Answers › About you**: your background (your CV can go there).
6. Press **Start** (F9).

Everything the program saves (settings, meetings, log, models) stays in a `Data` folder next to the exe
(or in `%LOCALAPPDATA%\MeetingAssistant` when that folder is read-only).

## Run from source

Python 3.10–3.13 (3.12 recommended):

```bat
install.bat
run.bat
```

Build your own single-file exe (also copies your settings next to it):

```bat
build_exe.bat
```

## Languages

In **Setup › Meeting**:

| Setting | What it does |
|---|---|
| Languages spoken in the meeting | 1–6 languages. One language = recognition is told it (faster, more accurate). Several = each sentence is recognised as one of them. |
| My language (translations) | Translations, word explanations, the summary and the meaning of each answer are written in it. Lines already in this language are not translated. |
| Suggested answers in | "Same language as the question" (default) or a fixed language. |

## Services

| Task | Options |
|---|---|
| Speech to text | Groq Whisper, any OpenAI-compatible `/audio/transcriptions`, Deepgram (live streaming), local faster-whisper model |
| Translation / answers | Groq, OpenAI, OpenRouter, Google Gemini, Cerebras, Mistral, any OpenAI-compatible chat service, or a local AI model (`.gguf`, llama.cpp) |

Each task can use a different service; Groq can act as a backup when another service fails.

## Tips for good results

- **Use headphones.** Otherwise your microphone also hears the other side.
- A headset microphone close to your mouth keeps background noise out. In noisy places lower
  **Setup › Audio › Microphone sensitivity**.
- In **What is this meeting about?** keep the first line short (it also guides speech recognition); paste the job
  description or other details below it.
- Fill in **About you**. Answers use only those facts about you and write a placeholder like `[years]` for anything
  missing instead of inventing it.

## Privacy

- API keys and settings are stored only on your computer.
- Audio is sent only to the speech-to-text service you choose (nothing leaves the computer with the local model).
- The window is a local page served on `127.0.0.1` and protected by a random per-session key; only the window the
  program opens receives it.

See [SECURITY.md](SECURITY.md) for reporting security problems.

## Development

```
python -m pip install -r requirements-test.txt
python -m pytest tests
```

The tests need no audio device and run on any system. Every push to main and every pull request runs them on GitHub Actions and builds the exe;
a commit with `[release]` in its message publishes a release (see [CONTRIBUTING.md](CONTRIBUTING.md)).

```
app.py              the program (audio, services, local web server)
web/index.html      the window (one page)
web/Vazirmatn-*     bundled Persian/Arabic font (SIL Open Font License, see web/Vazirmatn-OFL.txt)
install.bat         creates a Python environment and installs the packages
run.bat             starts the program from source
build_exe.bat       builds MeetingAssistant.exe on your computer
tools/build.py      the same build, used by GitHub Actions
tests/              automated tests
Guide-EN.md         full user guide (English)
Guide-FA.md         full user guide (Persian)
CHANGELOG.md        what changed in each version
```

## License

MIT — see [LICENSE](LICENSE). The bundled Vazirmatn font is under the SIL Open Font License 1.1.
