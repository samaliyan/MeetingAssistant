# Changelog

All notable changes. The full user guide is in [Guide-EN.md](Guide-EN.md) and [Guide-FA.md](Guide-FA.md).

## [6.8]

The see-through answer window (Overlay) is now quiet, movable and hidden from screen sharing.

- **Almost no extra text**: only what they said, its translation, the answer and its meaning, and one short line from the coach (the time you have used and the tip, or an alert). Soft grey-blue colours, easy to read but not loud.
- **Hidden from screen sharing** (Setup › Display, on by default): the window is now opened by a small helper of the program, so Windows can hide it from a shared screen. If the helper cannot start, a simpler window opens and a message says it cannot be hidden.
- **Adjustable**: how see-through the window is and how strong the words are (Setup › Display); Ctrl+Alt+PageUp / PageDown change it while it is on.
- **Movable**: Ctrl+Alt+M = move mode (drag with the mouse, press again to lock), or Ctrl+Alt+Shift + arrows; Ctrl+Alt+Shift+Home / End = bigger / smaller. The place is remembered.
- Everything below it still works with the mouse and keyboard as if it were not there. 83 automated tests.

## [6.7]

A see-through answer window, and more kinds of meetings.

- **See-through answer window (Overlay)**: one button (or the key **Ctrl+Alt+O**, which works from any program) minimizes the program and shows a rectangle that stays on top of everything and shows only what they said (with its translation) and the answer to say. It is see-through, and the mouse and keyboard work on the program below it as if it were not there. Press the same key again to come back to the normal window. While it is on: Ctrl+Alt+Up/Down scroll a long answer, Ctrl+Alt+Left/Right show an earlier or newer answer. Setup › Display: how see-through it is, and top or bottom of the screen. It is an Edge window, so screen sharing can see it.
- **New meeting type "Language or oral exam (IELTS, TOEFL, level test)"**: answers are made for speaking a test at the level you set in Answer style (B2 if empty): answer first, then a reason and a short example, linking phrases, and a simple frame for "Describe..." talks. The coach watches length and fluency, and the review judges fluency, structure, vocabulary and grammar clues.
- **New meeting type "Client, sales or negotiation call"**: short confident answers, objections, prices, deadlines, next steps.
- New question kind "Describe / talk" (for example "Describe a place you like", "You should say...") with a 1-2 minute guide. Test phrases such as "I'd like you to talk about...", "Do you agree or disagree", "cue card" are answered.
- 83 automated tests.

## [6.6]

A real coach next to you: it knows the kind of question, how long to speak, what you said before, and it helps until the last minute.

- **Kind of question and how to answer it**: the card shows the kind (introduction, salary, behavioural, coding, design, troubleshooting, experience, concept, opinion, yes/no, your questions to them ...), one line on how to answer that kind, and a time guide with a bar that fills while you speak, so you know when to stop.
- **Your reply is checked** after you speak, from the transcript only: too long, too short, no example or number, too fast, too many soft words ("maybe", "I think"), or good. Only the lines between this question and the next one count. For non-English replies only the length and speed are judged.
- **The coach remembers**: facts you said (so you do not contradict yourself), topics, promises and to-dos, people, what went well, what is still open. It warns you when you contradict something you said earlier. Notes are saved with the meeting and come back when you resume it. Open them from the tools menu, "Coach notes".
- **Preparation at Start**: from your CV and the meeting text, a short card with key messages, strengths to show, risks, and questions to ask them.
- **F4 = ask the coach** ("what should I do or say now?"), or click "Ask coach" and type your own question. Only one request runs at a time.
- **It fits the meeting type**: an interview coach, a work-meeting coach (decisions, action items), or a lecture coach.
- The review after the meeting uses the coach notes and the repeated questions.
- Cost care: about one small request every 45 seconds, only when idle; it uses one model of its own. If your main model is the local one, the coach and its background text stay on the local model.
- Fixes found by an independent review: better question-type rules (for example "Have you ever used Terraform?" is an experience question, not a story question), German questions, a stale check is never shown for a new question, notes are merged instead of replaced, the "None" alert is ignored, F4 with Alt or Ctrl does nothing, the notes window keeps its scroll position, and a small window keeps room for the answer.
- 81 automated tests.

## [6.5]

The program now knows what is happening in the interview.

- **Interview situation card** above the suggested answer: what is happening now (they are asking / you are answering with a timer / the answer is being written / your turn), the stage of the interview (introduction, technical, behavioural, coding, ...), the topic, how demanding the questions are (level 1-5 with an arrow up or down), a "Going well / Steady / Needs care" sign, and one short tip in your language.
- **A question asked again is noticed.** If the other side asks the same question again after you answered, the transcript shows "Asked again", and the new suggested answer is written to fix what was probably missing: it sees the earlier suggestion and what you actually said, and starts with the direct answer and one example. A question asked again is never skipped.
- The situation analysis is one small request about every 30 seconds, only when the program is idle, and it uses its own model so it does not take the limits of the answers. Turn it off in Setup, Meeting, "Interview situation card".
- 72 automated tests.

## [6.4]

Made for an interview where you only press Start.

- **One answer per question**: a question spoken in pieces (short pauses) is answered once, from all its pieces. A line that ends with "?" is answered almost at once; others wait about one second for the rest.
- **Free limits are kept for real questions**: statements (a company introduction, thanks, small talk) are not sent to the AI. Requests such as "Tell me about yourself" or "Walk me through..." are always answered. "Answer this" and F2 still work for any line.
- **Old questions are not answered late**: after a network break, lines that arrive very late, or a question you have already answered yourself, are skipped.
- **Answers retry by themselves** (twice) after a short network or service problem, instead of failing at once.
- **Live text (Deepgram) reconnects by itself** after a network break or sleep, and the audio is reopened after the PC wakes up or a reader stops.
- **Check before Start**: the program tests the services and the key first. A wrong key, no internet or a missing computer-sound device is reported before the interview begins; pressing Start again starts anyway.
- **Mentioning the screen** ("look at this code", "on the screen") shows a hint to press F3.
- A new answer opens at its top, not in the middle of the previous one.
- 67 automated tests.

## [6.3.1]

- **You are speaking, a new question arrives**: the answer you are reading stays on screen. A yellow bar "New question" shows the new question; when you stop speaking (about 2.5 seconds of quiet) the new answer comes up by itself, or click the bar to see it at once.

## [6.3]

- **Hands-free answers**: the answer panel follows the newest question by itself (no click on "Show suggested answer"). Ctrl+Left / Ctrl+Right move between answers, Ctrl+Up / Ctrl+Down scroll a long answer, and a "2 / 5" counter shows where you are.
- **Microphone sensitivity now works**: the lowest settings ignore small sounds, clicks and coughs; the change also applies to Deepgram live text. A red line in the audio test shows the limit.
- **Microphone volume** slider (25-300 %) in Setup, Audio.
- 60 automated tests.

## [6.2.1]

Same as 6.2 plus the last fixes: the conversation view while you answer (turns grouped, your own lines in a different colour, a "They said" bar), the exe build fix, and the Windows test fix. This release exists because the tag v6.2 had already been published.

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
