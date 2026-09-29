# Changelog

All notable changes. The full user guide is in [Guide-EN.md](Guide-EN.md) and [Guide-FA.md](Guide-FA.md).

## [6.2]

New tools. Nothing that worked before changes; every new part is optional and off until you use it.

- **About you from a file**: in Setup, Answers, choose "Use a file (CV)" and pick your CV (`.txt`, `.md`, `.docx`, `.pdf`);
  or keep writing the About text yourself. The file is read again when it changes.
- **Ready-made modes** (Setup, Meeting, "Type of meeting"): General, Technical interview, HR / behavioural interview, Work meeting, Lecture / class. A mode only fills in a suggested
  style; you can still change every setting.
- **Glossary** (Setup, Meeting): technical words (OSPF, RMAN, kubectl). They help speech recognition (Whisper prompt,
  Deepgram keywords) and the spelling of capital / digit words in the transcript, translations and answers.
- **Speaker separation** (Deepgram live): several people on the computer's sound become "Person 1", "Person 2".
- **Tools menu** in the meeting window:
  - "How did I do?": talking time, speed, filler words and an AI review, saved in the meeting file.
  - "Help me say": type what you mean in your own words and get a good sentence in the meeting language.
  - "Read my screen": sends a picture of the screen to a picture-reading model (needs a model that can read pictures).
  - "Search past meetings": choose how far back (7 days to all time), optionally ask the AI a question about them.
  - "Export": Word (`.docx`), subtitles (`.srt`), text, JSON, PDF (print), or copy the summary.
- **Hide from screen sharing** (Setup, Display): the window is drawn black / invisible to screen sharing.
  Needs the optional `pywebview` package (WebView2); the program shows a red "NOT hidden" mark when it could not do it.
  **Warning:** some companies forbid using an assistant in interviews. You are responsible for following their rules.
- **Easier to follow while you answer**: lines of the same person that follow each other are grouped as one turn (the
  name is shown once), your own lines have a colour of their own, and when your new lines push the other side's last
  question out of view, a bar at the top of the transcript keeps showing what they said (with its translation).
  Press the bar to read all of it, press again to jump to the line, or close it with the cross.
- **Check models** (Setup, Services): asks every service which models it has now and shows only the ones that exist and
  are not marked old (speech to text, translation and answers, picture reading). It tells you which of your chosen models
  is gone and what to try instead. Groq's built-in choices are checked while you work; if they disappear, current Groq
  models are used instead.
- **Find more models** (Setup, Services, Local model and Local AI model): searches Hugging Face for speech-to-text
  (faster-whisper) and chat (.gguf) models, most used or newest. Every model shows its download size, the memory and
  processor it needs, and whether it fits this computer's memory. The built-in download lists show the same facts.
- **Reading the screen** picks its model from what the service says about its models (input types, capabilities);
  you can still type your own. A model name typed for one service is no longer sent to another.
- Build: the exe build no longer excludes `distutils` (it broke the build when the hidden-window support was included).
- Build and tests: `pypdf` is in the requirements; `pywebview` is installed by the build scripts when available; 56 automated tests.

## [6.1]

Fixes only, from a full independent code review (eight separate reviewers, then a second review of the fixes).
Nothing changes in how the program is used.

- "Continue last meeting" could miss the last lines, answers or the summary when the meeting ended right after a
  regular save; the final save now always writes it.
- Live service (Deepgram): speech the service never answered is sent to the next service instead of being lost;
  audio still queued at Stop is sent before closing; a failed connection is closed properly.
- Settings: a settings file that could not be read at start is never overwritten with defaults; odd values
  (text instead of numbers or yes/no, huge numbers, a version written as text) are corrected instead of resetting
  everything; a failed save leaves no half-written file.
- Services: a 403 that is not about the key no longer marks the key as wrong; wait times from the service are
  limited (an odd header can no longer park a model for hours); "no credit" is recognised.
- Downloads: a wrong piece sent by the site is not stitched onto the file.
- Security: the window page and its live updates need the window's key; the page cannot be embedded in other
  sites; proxy passwords with unusual characters are hidden; network folders are not opened.
- Window: settings typed while a save was running are kept; failed saves show a message; a removed service
  cannot come back through a late save; no double action from a held function key.
- Quitting waits for the last translations; a free-plan request of a dropped sentence is given back; many smaller
  race conditions and error paths.
- Build and tests: the build checks that every engine really imports; release notes must exist before a release;
  more automated tests.

## [6.0]

- **Local AI model for translation and answers** (Setup › Services › Local AI model): download a model inside the
  program (Gemma 3 4B recommended, Qwen 2.5 1.5B / 3B, Gemma 3 12B) or choose any `.gguf` chat model, then use it
  for translation, answers or both — no internet, no key, no limits. Runs with llama.cpp; the engine is optional
  (the program works without it). Speech to text can already run locally, so the whole program can now work offline.
- The window's key is no longer handed out to anyone who asks for the page: the program opens its window with the
  key, a reload uses a cookie, and the key is not in the address or in the live-updates address any more. A window
  left over from an earlier start shows "This window is out of date".
- Install and build scripts no longer tell everyone to turn on a VPN.
- Fixes from a fourth code review: rejected requests close their connection (no mixed-up follow-up request);
  free-plan requests of sentences that are dropped are given back; a superseded model load stops before reading the
  file; live-service callbacks can no longer break the connection; "NO REPLY" variants are recognised; rows no
  longer stay on "writing…" after Stop; a stream that dies in callback mode is reopened; odd rate-limit headers,
  sample rate 0, 416 with unknown size, and more.
- Suggestions adopted: build options in one place (`tools/build.py`, used by `build_exe.bat` and GitHub),
  proxy test only probes local proxies, proxy passwords never reach the window, API-level tests, at most three
  damaged-settings backups kept, quicker retry after a connection hiccup.

## [5.9]

- **Version shown** in the status bar, in Setup and in the window title.
- **Choosing a model folder or a recording** now opens a browser inside the window (the Windows dialog often opened
  behind the program). Model folders are marked; quick places for Models, Downloads, Desktop and drives.
- **Credit & limits** (Setup › Services): shows what is left with each service — the real balance for Deepgram and
  OpenRouter, the free-plan limits for Groq (requests today, tokens this minute) and for services that report them,
  with a link to the service's account page otherwise.
- Proxies with a user name and password now work for live speech (HTTP CONNECT and SOCKS5); passwords are hidden
  on screen and in the log.
- Fixes from a third code review: live service that stops answering without closing is detected after 25 s and
  the program falls back; a live stream is retried after a device change; quota is refunded by handle (exact
  request), also for previews and for the language retry; model switching waits for a running transcription;
  broken requests to the local server are answered with 400 instead of being run; the answer panel shows when an
  answer failed; settings that could not be saved are retried; quitting mid-meeting waits for the last sentences;
  log writing moved off the audio and speech threads; a dozen smaller race conditions and edge cases.
- Project: GitHub Actions for tests and for building the exe and the release, `requirements-test.txt`,
  Python version check in `install.bat` / `build_exe.bat`, more tests.

## [5.8]

- **Continue last meeting** (Shift+F9): go on with the same transcript and meeting file, also after a restart.
- Answers remember the last 10 questions answered in the meeting and stay consistent when a question is repeated.
- Stricter answer rules: personal facts only from "About you" (placeholders otherwise), no guessed technical details.
- "What is this meeting about?" can hold a long text (only its first line guides speech recognition).
- English user guide; automated tests.
- Fixes: pausing a live (Deepgram) stream no longer sends queued audio; falls back to the local model when the live
  service fails; quota not charged for requests that never arrived; 413 for oversized requests; and more.

## [5.7]

- **Languages are selectable**: meeting languages (1–6 of 34), your language for translations, explanations and
  the summary, and the language of suggested answers. Right-to-left languages are shown right-to-left.
- README, license and `.gitignore` for publishing.
- Fixes from a code review: thread-safe Groq quota, no permanent downgrade after one refused transcription request,
  local model wait limited to 3 minutes, download recovery, engine threads released after each meeting, and more.

## [5.6]

- Everything the program writes lives in one `Data` folder next to it; older files are moved there automatically.
- Your own lines are translated by default.

## [5.5]

- Speed (Windows no longer slows the program down as a background process; faster local model), stability (device
  changes, microphone reopen, 2-minute network outages, window crash recovery, settings backup, single instance)
  and a clearer window.

## [5.4] and earlier

- 5.4: reorganised Services, Groq optional, faster local model, clear log.
- 5.3: calmer live text, explain / answer selected words, edit a line, pause, summary, transcribe recordings.
- 5.2: local speech-to-text model (faster-whisper), downloadable inside the program.
- 5.1: per-service capability tests, live vs. preview modes, usage counters.
- 5.0: new window and services.
