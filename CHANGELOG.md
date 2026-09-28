# Changelog

All notable changes. The full user guide is in [Guide-EN.md](Guide-EN.md) and [Guide-FA.md](Guide-FA.md).

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
