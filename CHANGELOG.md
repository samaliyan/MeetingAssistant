# Changelog

All notable changes. The full user guide is in [Guide-EN.md](Guide-EN.md) and [Guide-FA.md](Guide-FA.md).

## [6.23]

**A clear message when a model is in the wrong place, and .gguf speech models now work.** A downloaded Whisper model (a `.gguf` file) put in **Local AI model** failed with the unhelpful *"Failed to load model from file"*. That box is for a chat model (translation and answers), such as gemma3-4b; a Whisper model is for speech to text. Now the program reads what is inside the `.gguf` file and knows which kind it is: a Whisper model placed under Local AI model is refused with a message pointing to **Setup › Audio**, and a chat model placed under speech to text is pointed back to **Local AI model**. The speech-to-text box also accepts a Whisper model in `.gguf` form now, not only the older `ggml-….bin` files. 143 automated tests.

## [6.22]

**No translation for a meeting in your own language.** When the meeting language (Setup › Meeting) is only your own language (Setup › Meeting › My language), nothing is translated any more — also not the live translation shown while someone is still speaking, which before was still sent (it used the service's limits for nothing and could show the same sentence twice). Finished lines in your language were already left untranslated. To turn translation off completely, use Setup › Features › Translation. 142 automated tests.

## [6.21]

**"Test it now" fixed.** The **Test it now** button for "Hide from screen sharing" said *"The hidden window could not be found"* even when the window was open and really hidden. The exe (and the Python version started from `venv`) runs the hidden window in a second, inner process, and the test was looking for the window in the outer one, which has no window. The hidden window now reports which process it really is, and the test looks there. Hiding itself was not affected — only the test. 141 automated tests.

## [6.20]

**A test fixed, nothing in the program changed.** One of the 141 automated tests for "Hide from screen sharing" wrongly assumed the Windows version number is always 0 (true only when the test runs outside Windows). On the GitHub check that runs on a real Windows machine, the version number is real (for example 26100), so the test failed there even though the program itself was correct. The test now checks the real number on Windows and the placeholder number everywhere else. 141 automated tests.

## [6.19]

**Eight new helpers for meetings.** Each one has its own switch in Setup › Features.

- **Say it in my language (F6).** Press F6 (or Ctrl+Alt+J from any program, during a meeting), mute yourself in Teams or Zoom, and speak in your own language. Your words are not written in the transcript; a card shows the sentence to say in the meeting language, with its meaning. F6 again turns it off.
- **Mark a moment (F7).** F7 (or Ctrl+Alt+K) marks the newest line as important; the flag next to any line marks or unmarks it. Marked lines are in the summary, the meeting file, Word, text and PDF export, with ★.
- **My notes.** A notes box under the answer panel, saved while you type. After the meeting **Make full notes** (or Tools › Full notes) completes your notes from the transcript.
- **Decisions and action items** in the summary (who — what — by when), and **Copy as message**: the summary as plain text for an email, Teams or Slack (without the interview questions).
- **Technical words from the job advert and the CV**: Setup › Meeting › **Fill from job advert and CV** adds the new ones to the list.
- **Meeting reminder**: when a Zoom, Teams or Google Meet meeting window opens, a message offers **Start** (once; only the window titles are read).
- **Speaker names**: click "Person 1" on a line and type a name (for example Interviewer or John); every line, the summary and the export use it.
- **How did I do?** lists the filler words you used ("um", "you know", "like," …) per minute and says if your pace was slow, easy to follow or fast.
- Someone who used the program without the answers service (answers and "after the meeting" off) keeps it that way: the two new parts that need it start off.
- **Hide from screen sharing — now honest and checkable.** The program reads the real Windows version (RtlGetVersion); on Windows older than version 2004, where the window can only be shown as a black box, it says so in advance instead of surprising you mid-meeting, and offers the three choices (keep it, turn it off, or share a single window). A **Test it now** button checks on your own computer whether the window is really invisible, a black box, or visible — by capturing it the way a screen share would and comparing. The overlay reports the black-box case too. (A phone photo of the screen or a hardware capture card can still show it — this is a Windows limit, not something any program can remove.)
- 141 automated tests.

## [6.18]

**Use only what you need: Setup › Features.** Eight switches, one per part of the program:

- **Translation**, **Suggested answers**, **Coach**, **Overlay**, **Screen reading**, **Interview prep** (job advert, practice), **After the meeting** (summary, How did I do?), **Files and links**. Speech to text is always on.
- A part that is off is **hidden** (its buttons, its menu items, its panel — with answers and coach off, the transcript takes the whole width), **sends nothing**, and **needs no service**: Start only asks for the services of the parts that are on.
- Three ready choices: **Text only**, **Text + translation**, **Full interview help** (everything, as before — the default).
- Under each switch: which service it uses, or "Needs a service for …" with a **Set it up** button. A key for a part that is off (F2, F3, F4, Ctrl+Alt+O …) says "… is turned off. Turn it on in Setup › Features." Turning the overlay off closes it.
- Services shows a task only the switched-off parts need as "not used".
- 128 automated tests.

## [6.17]

A full independent check of the whole program (seven reviewers: threads, error paths, security, network, the window, settings and build, and the look and the buttons), and the fixes.

- **The local model never runs twice in memory.** A whisper.cpp model that was replaced or turned off could start itself again in the background; now it stays closed. A whisper.cpp model that takes too long is started afresh (it no longer makes every next sentence wait). Stop on a recording ends a long whisper.cpp step at once.
- **Stop on a recording**: ffmpeg is always ended (also when Stop is pressed in the first seconds), and no time is spent on the speaker step after Stop. A short problem in fast file mode is tried again (up to 3 times) instead of ending the recording; if a recording stops on an error, the lines already written are kept and saved.
- **Downloads** (models, Vosk, NVIDIA): a blocked site always gets the advice "needs a VPN or proxy"; the useful error (for example "start your VPN") is shown instead of the last one; a part of a file that does not fit is never stitched on; the Vosk engine file is checked with its SHA-256; a web page saved instead of a model is recognised.
- **Links**: "too many requests / busy" is no longer reported as "video removed"; the link box is off when this copy cannot download links; the address is kept out of the log after the "?".
- **The window**: a setting changed during a meeting is never undone by a message from an earlier change; a line still playing stops when a meeting starts; the screen is redrawn when an unfinished line is removed; the first second before the program answers shows a spinner, not "undefined"; the file window starts clean; Setup › Services shows Test all parts, Check this computer and New models, and the rest under **More checks**; the Local model card is shorter (one Speed choice, Test, then Open models folder / Delete).
- **Words**: "Tell the people apart" and **Person 1, Person 2** in recordings too (as in meetings); the Vosk warning has a one-click **Download the … Vosk model** button; the health check marks what needs action and gives NVIDIA advice that matches the NVIDIA box.
- **Settings**: if config.json is missing, the backup is used and the message says "missing" (to start fresh, delete both files). The proxy password is never sent to the window.
- **Security**: deleting a model never touches a network path; network paths written with mixed slashes are recognised.
- **Build**: build_exe.bat and install.bat now add onnxruntime and yt-dlp too (optional); the release warns when a part is missing.
- The guides use the real button names (**Use Groq as a backup**, **Test**).
- 126 automated tests.

## [6.16]

**NVIDIA graphics card with one button.** When the computer has an NVIDIA card, Setup › Services › Local model shows **Use the NVIDIA graphics card**.

- One download, about 560 MB, only when you press it: NVIDIA's official cuBLAS files from pypi.org, checked with their SHA-256. Only the two files the engine needs are kept. Nothing else to install (no CUDA Toolkit).
- Then the local model loads on the graphics card by itself: several times faster, and the larger, more accurate models become usable. If the card cannot be used, the model runs on the processor and the status line says why (driver too old, too little graphics memory, card too old).
- The download continues after a break, can be stopped, and can be removed again (**Remove NVIDIA support**).
- The local model engine is now always CTranslate2 4.6.3 or newer (it needs only cuBLAS, not cuDNN).
- 124 automated tests.
- Also in this version if you skipped 6.15: the very light Vosk models (see 6.15 below).

## [6.15]

**A very light local model (Vosk), as a choice.** For weak computers, or when the internet is bad.

- Setup › Services › Local model › the download list has a new group, **Vosk**: English, German, French, Spanish, Italian, Dutch, Russian, Turkish and Persian, each about 35–55 MB.
- The first time, the Vosk engine (about 15 MB, from github.com) is downloaded with the model. **The program file does not get bigger.**
- Vosk is very fast on any processor (in the test: 11 seconds of speech in about 1.5 seconds, with no graphics card), but it is less accurate than Whisper, writes no punctuation, and understands only the one language of its model. The status line says so when the meeting has other languages.
- It works for live meetings, for recorded files and for links.
- The models come from alphacephei.com (the makers of Vosk); from Iran a VPN may be needed.
- 122 automated tests.


## [6.14]

Six ideas from the open-source program Buzz, built into this program.

- **Recorded files are much faster with the local model.** When a file is transcribed with the local model (faster-whisper), the program skips the silent parts and works on many pieces at once (batched mode), so it is several times faster, most of all on an NVIDIA graphics card. The language is found once for the whole file.
- **Who said what in a recording.** In the "Transcribe a file…" window choose **Separate the speakers** (or the number of people). After the text is ready, each line is labelled Speaker 1, Speaker 2 … The voice model (27 MB) is downloaded the first time.
- **whisper.cpp engine for Intel and AMD graphics.** Three new models in Setup › Services › Local model: cpp-base, cpp-small and cpp-large-v3-turbo. They run on any graphics card that supports Vulkan (Intel Iris / Arc, AMD Radeon, NVIDIA) and on the processor otherwise. A ggml-….bin file you downloaded yourself can be chosen too.
- **Better subtitles (.srt / .vtt).** A long sentence becomes several short subtitles: at most two lines of 42 characters and 7 seconds each; the translation is cut in the same places, at a comma when there is one. The speaker name is shown only when there is more than one speaker.
- **A link to text.** Paste a YouTube link (or any page with audio or video) in the "Transcribe a file…" window and press **Transcribe the link**. It is downloaded into the "downloads" folder, then transcribed and translated like a file. Needs ffmpeg (the window tells you how to install it).
- **Hear a line again.** Setup › Audio › **Keep the sound of meetings** (off by default) keeps the sound next to the meeting file. After the meeting (and for every recorded file) the ▶ button on a line plays exactly that part.
- Fixes from an independent review of these parts: very long words (links) no longer stop the subtitle export; subtitles never overlap; a cancelled download no longer shows an error; reopening a recording keeps the speaker names; the sound link expires after an hour; keeping the sound never slows the microphone (it is written by its own thread); while the meeting is paused, silence is kept instead of the sound; a slow whisper.cpp no longer ends a recording with an error (what was read is kept).
- **ffmpeg help everywhere**: opening an m4a / mp4 file (not only a link) without ffmpeg opens a window with the one line to type in cmd (`winget install Gyan.FFmpeg`) and a **Try again** button; ffmpeg installed by winget is found at once, without restarting; Check this computer finds it in every place the program looks and has a **How to install ffmpeg** button. Both guides have the steps.
- **A strict UX review** (three independent reviewers, with screenshots), and the fixes:
  - Speaker 1 / 2 / 3 are shown on every line where the speaker changes (consecutive lines of different people were grouped under the first name).
  - The ▶ button never sits on the text; it is shown only when that meeting really has its sound; a clear message when the sound is missing (file moved, meeting held before the option was on).
  - "Transcribe a file or a link" window: who is speaking first, clearer choices ("Separate the speakers (count them by itself)"), a note that it takes a little longer, the link, then the files. The option is off when this copy cannot separate speakers.
  - The waiting text matches the step (downloading the link / reading / adding speaker names); the bar shows the speaker step's own progress.
  - Stop works at once while a link is being looked at; plain messages for private videos, "not a robot" checks, no connection (with the VPN / proxy place), and "Download stopped.".
  - whisper.cpp: if the graphics card cannot be used, it runs on the processor by itself and says so; Intel / AMD computers are offered cpp-small first; the model list is grouped by engine; a downloaded model is chosen at once.
  - Messages no longer cover the Setup panel; the overlay shows "▼ more · Ctrl+Alt+↓" when the answer continues; a pasted part of a key gets a warning; the Groq help says a VPN is needed from Iran.
- 119 automated tests.

## [6.13.1]

Two small things learned from the open-source program Buzz:

- **The computer stays awake** while a meeting or a recording runs: Windows no longer sleeps or turns the screen off in the middle of a long interview where you only listen (that used to stop the sound capture).
- **Web subtitles (.vtt)** in Export, next to .srt.
- 104 automated tests.

## [6.13]

**New models** (Setup › Services › New models): the program looks in three public lists, with no key needed — models.dev (models sold by OpenAI, Google, Mistral, Groq, xAI, DeepSeek, Azure and many others, with prices and release dates), OpenRouter (hundreds of models behind one key, many of them free) and Hugging Face (new speech-to-text models).

- One line per model, newest first: what it is for (translation and answers, or speech to text), when it came out, every service that sells it with its price per million tokens, or "free", and whether this program can use it there.
- Filters: kind, free / paid, the last 30 days / 3 months / 1 year, only the ones this program can use, and a search box. Models that appeared since your last look are marked NEW; once a day (never during a meeting) the program checks quietly and shows the number on the button.
- After you buy a key: **Add this service** adds it to Setup with the right address (or opens the one you already added), you paste the key and press Test, and then **Use for answers / translation / speech to text** sets that model. Speech to text is offered only where the service really does it in this program (OpenAI, Groq, Mistral); a new local model from Hugging Face opens the local model download.
- The list is kept for 12 hours; if a site cannot be reached, the last list stays usable and the screen says which site did not answer. Links and service addresses from the lists are used only when they are plain https.
- 103 automated tests.

## [6.12]

Easier to read at a glance (a strict review of the screens, the text sizes and the colours by independent reviewers).

- **The answer gets the room.** While an answer is on screen, the coach card shrinks to one status line and the tip; **Details** opens the rest. The question block is smaller (the English question is two lines, click it for all; the Persian meaning stays). On a 1366×768 laptop the answer now starts about 200 pixels higher and fits without scrolling.
- **Start speaking after one glance**: the first sentence of the answer is bold (a long first sentence only up to its first comma); answers are now written so that the first sentence answers the question on its own. The rest is slightly lighter. Lines are at most about 66 characters, so the eyes do not travel across a wide screen.
- **The Persian meaning of the answer** is larger (0.9 of the answer size instead of 0.8).
- **Text sizes**: no information text is smaller than 12 px (keys, badges) or 13 px (hints, chips, times); the coach text is larger; Persian text in the interface uses the Persian font.
- **Colours**: grey hints, green, orange and red texts are darker, so they pass the usual contrast rule; clearer keyboard focus.
- **See-through window**: words never fade below 60% and get a soft shadow, so they stay readable over a bright video; the coach line is larger; in a very small window the English question is hidden and the Persian meaning stays.
- **Small**: the Tools button keeps its name on laptops; the review shows labels and Persian text on separate lines and no empty number tiles; clearer error messages (what to do next); "Answer engine" is now "Answer speed"; the practice note is two short lines.
- 99 automated tests.

## [6.11]

A smarter coach, and room for its words in the see-through window.

- **The coach sees the moment, not only the transcript**: which question is open, how long ago it was asked, whether you have started answering (it listens to your microphone, even before any text exists), how long you have talked, whether they asked again, and the suggested answer already on your screen (so it adds what is missing instead of repeating it).
- **It acts in the situations that matter**, in this order: you are silent after a question (about 7 s, or 14 s when an answer is already shown) - it gives a first sentence to start with, once per question; you contradicted yourself - an alert; you talk too long - a closing sentence; they asked again - what to give this time; known kinds of questions (pay, weakness, why are you leaving, why us, a career gap, start date or visa, tell me about yourself, your questions for us, closing) - the move an expert would make.
- **It looks right after a real question** (not only every 45 s), never more than once every 25 s, and always after the suggested answer is written, so it does not compete with the answers for the free limits. In a class or a work meeting it never says "you are stuck".
- **Help (Ask coach, Ctrl+Alt+H)** gets the same picture: if you did not understand the question it explains it and gives a clarifying question; if you do not know the answer it gives an honest bridge; then the exact words to say.
- **See-through window**: the coach text is never cut any more. The coach line takes up to 45% of the window (65% while help is shown) and scrolls; Ctrl+Alt+Up/Down scroll the coach text first and then the answer. Help stays on screen for 75 s.
- 99 automated tests.

## [6.10.2]

The coach now gives the exact words to say. Its tip stays short and in your language; when the tip is about saying something, a separate line shows the sentence in the language of the meeting (for example English), also in the see-through window. Help from the coach (Ctrl+Alt+H or Ask coach) does the same: advice first, then the sentence to speak. 97 automated tests.

## [6.10.1]

Small hardening from a checklist review: the sound buffer of a microphone or of the computer sound is capped, so a stuck reader can never grow the memory without end. Nothing else changes.

## [6.10]

A full independent audit, a health check button, and a real Windows check of the overlay.

- **Check this computer** (Setup › Services): looks at Windows version, WebView2, the overlay keys, microphone and computer sound, services, proxy and ffmpeg, and says in plain words what is wrong. **Try the overlay (5 s)** opens the see-through window for a few seconds and reports whether it opened, how fast, and whether it is hidden from screen sharing. **Copy the report** puts the result on the clipboard.
- **Overlay**: the window now uses real pixels at 125% / 150% screen scaling (positions and sizes no longer disagree), works on more than one monitor, closes by itself if the program ends or crashes, starts faster (the helper no longer tidies files or writes a second log), and the hotkeys never repeat while held.
- **Speed**: a page with thousands of lines is built about 4 times faster after a reconnect or a resumed meeting, and streaming text no longer re-checks the whole page for every word. Live word-by-word translation never uses up a model's rate limit any more (it waits its turn), so real translations and answers are not blocked by previews. An empty reply from a model makes the next model try.
- **Safer**: a meeting file that cannot be saved now shows a message (and another when it works again); a strange character can no longer lose the file; a Deepgram live stream is closed when Start fails; an API key pasted with hidden characters or quotes is cleaned; a failed key save is shown; the same page error is reported once a minute.
- **Small**: the see-through window keeps `?overlay=1` on reload; selecting text in a window and releasing the mouse outside no longer closes it; the desktop shortcut works with Persian folder names.
- New in the project: `TESTING.md` (what is tested how, and what only a real Windows machine can confirm) and a GitHub check that really opens the overlay on Windows (`.github/workflows/windows-check.yml`). 96 automated tests.

## [6.9.1]

Fix: the see-through window could not be moved with the mouse in move mode (Ctrl+Alt+M). Now the program follows the mouse itself: hold the left button and drag to move, hold the right button and drag to resize. The keys (Ctrl+Alt+Shift + arrows, Home / End) still work.

## [6.9]

Practice interview, job-ad preparation, scores in the review. Everything is an option; nothing that worked before changes.

- **Practice interview** (Tools › Practice interview): the coach asks questions one by one (general, behavioural, technical, English level test, or your weak spots again). You type or speak the answer; you get scores (clarity, structure, depth, proof, and language for the English test), the real numbers (seconds, words, pace), tips, a stronger answer and the follow-up an interviewer would ask. Weak questions are saved and can be re-drilled. Suggested answers and the coach stay quiet while you practise.
- **Prepare for the job** (Tools › Prepare for the job): paste the job advert in Setup (or here) and get what they look for and likely questions. The advert is also used for answers and by the coach (capped at 8000 characters).
- **Scores in the review** (Setup › Review, option "Scores in the review", on by default): after the written review, one small extra request gives clarity, structure, depth, proof and follow-up as bars, with the most useful fixes. Needs at least 4 lines.
- **Read the screen by itself** (option, off by default): when they say "look at this code" or "on my screen", the screen is read after the picture delay.
- **Overlay keys**: Ctrl+Alt+S read the screen, Ctrl+Alt+A answer now, Ctrl+Alt+H ask the coach; the screen result and coach help show inside the overlay. These keys are taken only while the overlay is on.
- Longer time limits for the slow requests, a practice window left open never keeps a real meeting quiet, and several small robustness fixes. 93 automated tests.

## [6.8.1]

Fix: an automatic test opened a real window on Windows and failed the release check. No change for users; everything in 6.8 is included.

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
