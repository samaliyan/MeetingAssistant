# Meeting Assistant — User Guide (version 6.25)

## Version 6.25: subtitles

- **Subtitles (only the translation)**: press the **Subtitles** button at the top. Each line shows only its translation, like film subtitles. The see-through window (overlay) shows the last two lines in large letters at the bottom instead of the answer; a sentence still being spoken is translated there as it comes.
- Turn it on and off any time: the same button, **Ctrl+Alt+T** while the overlay is on, or Setup › Display › **Subtitles: only the translation**.
- A line that is not translated (for example it is already in your language) shows what was said. The original is kept: it comes back when subtitles are off, and it is in the meeting file.
- To also get no suggested answers: Setup › Features › **Text + translation**.

## Version 6.19: eight new helpers

- **Say it in your language**: during a meeting press **F6**, mute yourself in Teams or Zoom, and speak in your language. The sentence to say appears on the right (and in the overlay). Press F6 again to stop. From another program: Ctrl+Alt+J.
- **Mark a moment**: **F7** (or Ctrl+Alt+K) marks the newest line; the flag next to a line marks or unmarks it. Marks go into the summary and the export.
- **My notes**: the box under the answer panel. After the meeting press **Make full notes**.
- **Summary**: now with decisions and action items, and **Copy as message**.
- **Technical words**: Setup › Meeting › **Fill from job advert and CV**.
- **Meeting reminder**: when Zoom, Teams or Meet opens, press **Start** in the message.
- **Names**: click "Person 1" on a line and type a name.
- **How did I do?**: filler words and speaking pace.
- Every one can be turned off in Setup › Features.

### Hide from screen sharing — check it works

- Setup › Display › **Hide this window from screen sharing**.
- On Windows older than version 2004 the window cannot be made invisible — the other side sees a black box. The program tells you this in advance.
- After you turn it on and restart, press **Test it now** to check on your own computer whether it is really invisible.
- A photo of the screen with a phone, or a hardware capture card, can still show it. No program can prevent that.

## Version 6.18: use only what you need

- **Setup › Features**: turn parts off (translation, answers, coach, overlay, screen reading, interview prep, after the meeting, files). What is off is hidden, sends nothing and needs no service.
- Ready choices: **Text only**, **Text + translation**, **Full interview help**.

## Version 6.16: NVIDIA graphics card with one button

- Setup › Services › Local model: press **Use the NVIDIA graphics card** (one download of about 560 MB). The local model then runs several times faster.

## Version 6.15: a very light local model (Vosk)

- Setup › Services › Local model: in the download list, the **Vosk** group has small models (35–55 MB) for one language each.
- Very fast on a weak computer, but less accurate than Whisper and with no punctuation. Use it only when Whisper is too slow.

## Version 6.14: files, speakers, links, subtitles, sound

- **Faster files with the local model**: silent parts are skipped and many pieces are read at once.
- **Who said what**: in the "Transcribe a file…" window choose **Tell the people apart** (or 2–5 people). Lines are labelled Person 1, Person 2 …
- **Intel and AMD graphics**: Setup › Services › Local model › download **cpp-small** (whisper.cpp engine).
- **Better subtitles**: short cues of two lines; the translation is cut at the same places.
- **A link to text**: paste a YouTube link in the "Transcribe a file…" window and press **Transcribe the link** (needs ffmpeg).
- **Hear a line again**: Setup › Audio › **Keep the sound of meetings**; after the meeting press ▶ on a line.

## Version 6.13: find new models

- **Setup › Services › New models** lists new models from public lists (free and paid), the services that sell them and their prices.
- After you buy a key: **Add this service**, paste the key, press **Test**, then **Use for answers** (or translation / speech to text).

## Version 6.12: easier to read

- While an answer is on screen the coach card is one line; press **Details** for the rest.
- The first sentence of the answer is **bold**: start with it.
- Bigger, clearer text and colours; the overlay text stays readable over a bright video.

## Version 6.11: a smarter coach

- The coach watches the moment: the open question, your silence, your length, repeated questions, the answer on screen.
- Silent after a question? It gives you a first sentence to start with. Talking too long? A closing sentence. Pay, weakness, "why are you leaving", "any questions for us"? The expert move, with the words to say.
- In the overlay the coach text is never cut: it takes up to half of the window and scrolls with **Ctrl+Alt+↑ / ↓**.

## Version 6.10.2

- **The coach gives the words to say.** Besides the short tip in your language, a line below it shows the exact sentence to speak in the language of the meeting. The same when you press Ask coach or Ctrl+Alt+H.

## Version 6.10: health check

- **Setup › Services › Check this computer**: shows what works and what does not (Windows version, WebView2, keys, microphone, computer sound, services). **Copy the report** and send it if you need help.
- **Try the overlay (5 s)**: opens the see-through window for a few seconds and tells you if it opened, how fast, and if it is hidden from screen sharing.
- The overlay now works at 125% / 150% scaling and on several monitors, and closes by itself if the program ends.

## Version 6.9.1

- **Move the overlay with the mouse**: press **Ctrl+Alt+M**, hold the **left** mouse button on the window and drag to move it, hold the **right** button and drag to resize. Press **Ctrl+Alt+M** again to lock.

## Version 6.9: practice, job advert, scores

- **Practice interview**: Tools › Practice interview. Choose the kind (general, behavioural, technical, English level test, weak spots) and how many questions. The coach asks one question at a time (it can read it aloud). Type the answer, or press Start (F9) and speak, then press "Done answering" (or Ctrl+Enter). You get scores, seconds, words and pace, tips, a stronger answer and the likely follow-up. "Re-drill my weak spots" asks the weak ones again.
- While you practise, suggested answers and the coach are muted. If a meeting is running, the practice lines are also in its transcript, so stop the meeting when you finish.
- **Prepare for the job**: paste the job advert in Setup › "Job advert" (or Tools › Prepare for the job). You get what they look for and likely questions. The advert is also used in answers and by the coach.
- **Scores in the review**: bars for clarity, structure, depth, proof and follow-up, and the most useful fixes. Turn off with Setup › "Scores in the review".
- **Read the screen by itself** (off by default): Setup › "Read the screen by itself".
- **Overlay**: Ctrl+Alt+S read the screen, Ctrl+Alt+A answer now, Ctrl+Alt+H ask the coach.

## Version 6.8: quieter, movable, hidden overlay

- The overlay shows only the other side's words (with translation), the answer, and one short coach line (time used and a tip). Soft colours: readable, not loud.
- **Hidden from screen sharing**: on by default (Setup › Display › "Hide the overlay from screen sharing"). Needs Windows 10 version 2004 or newer.
- **Ctrl+Alt+PageUp / PageDown**: more / less solid. Setup › Display also has a slider for how strong the words are.
- **Move it**: **Ctrl+Alt+M**, drag with the mouse, press **Ctrl+Alt+M** again to lock. Or **Ctrl+Alt+Shift** with the arrow keys; **Home / End** = bigger / smaller. It remembers the place.
- **Ctrl+Alt+O** on / off, **Ctrl+Alt+↑↓** scroll, **Ctrl+Alt+←→** earlier / newer answer.

## Version 6.7: see-through answer window, exams

- **Overlay**: press the **Overlay** button or **Ctrl+Alt+O** (from any program). The program minimizes and a see-through rectangle stays on top of everything with only the other side's words (with translation) and the answer. The mouse and keyboard work on the program under it as if it were not there. Press **Ctrl+Alt+O** again to come back.
- While it is on: **Ctrl+Alt+↑ / ↓** scroll a long answer, **Ctrl+Alt+← / →** earlier or newer answer.
- Setup › Display: how see-through it is and whether it sits at the top or the bottom of the screen.
- The overlay is an Edge window, so screen sharing can see it. If the key is used by another program, use the button.
- **Type of meeting › Language or oral exam (IELTS, TOEFL, level test)**: suggested answers at your level (write it in Answer style, for example "B2"), answer first, then reason and example. The coach watches length and fluency.
- **Type of meeting › Client, sales or negotiation call.**

## Version 6.6: a real coach next to you

- **Kind of question**: the coach card shows what kind of question it is (introduction, salary, behavioural, coding, design, troubleshooting, experience, concept, opinion, yes/no, "your questions to us"), one line on how to answer it, and a time guide. While you speak a bar fills; when it turns red, finish with one closing sentence.
- **Your reply is checked** when you stop speaking (only from the transcript): too long, too short, no example or number, too fast, too many soft words, or good.
- **The coach remembers** the meeting: facts you said, topics, promises, people, what went well, what is open. If you contradict something you said before, a warning appears. Open the notes: tools menu › **Coach notes**. They are saved with the meeting.
- **Preparation**: when you press Start, the coach reads your CV and the meeting text and writes key messages, strengths, risks and questions to ask them (in Coach notes).
- **F4** = "what should I do or say now?". Or click **Ask coach** and type your own question. F4 with Alt or Ctrl does nothing.
- The coach changes with the meeting type (interview, work meeting, lecture). Turn it off in Setup › Meeting.
- Cost: one small request about every 45 seconds, only when nothing else is being written.

## Version 6.5: the program knows what is happening

- **Interview situation card** (above the suggested answer): the live state (they are asking, you are answering with a timer, the answer is being written, your turn), the stage of the interview, the topic, the level of the questions (1-5, with an arrow if it goes up or down), a sign "Going well / Steady / Needs care", and one short tip in your language.
- **Question asked again**: if they ask the same question again after your answer, the line shows "Asked again" and the new suggested answer is written to fix the earlier one (direct answer first, then one example). It also sees what you said the first time.
- The card costs one small request about every 30 seconds and only when nothing else is being written. Turn it off in Setup › Meeting.

## Version 6.4: an interview with only Start

- **Just press Start** (F9). Before it starts, the program checks the internet, the key and the sound device of the other side, and tells you at once if something is wrong. Pressing Start a second time starts anyway.
- **One answer for each question.** If the interviewer says a question in pieces, the program waits about one second and answers once for the whole question. A line that ends with a question mark is answered almost immediately.
- **No wasted answers.** Statements such as "We are a company founded in 2010" or "Thank you" are not sent to the AI, so the free limits last for the real questions. Requests like "Tell me about yourself" are answered. For any other line use "Answer this" or F2.
- **No late answers.** After a network break, old lines and questions you have already answered are skipped.
- **Recovery by itself**: answers are tried again twice after a short problem; live text (Deepgram) reconnects; the audio reopens after the PC wakes up.
- If they mention the screen ("look at this code"), a hint tells you to press F3.

## Version 6.3

### Hands-free answers
- While you are speaking, a new question from the other side does not replace the answer you are reading. A yellow "New question" bar appears; when you stop speaking the new answer opens by itself (or click the bar).
- The answer panel now follows the conversation by itself: the newest answer is always shown, with no click on "Show suggested answer". An answer you choose on purpose (arrow keys or a click) stays until a newer question is answered.
- **Ctrl + Left / Ctrl + Right**: earlier / newer answer. **Ctrl + Up / Ctrl + Down**: scroll a long answer. **F2**: answer the last thing they said. **F3**: read the screen. **F8**: pause. Nothing needs the mouse during an interview.
- Above the "Answer now" button a small "2 / 5" counter shows which answer you are looking at (orange = not the newest).

### Microphone: sensitivity and volume (Setup, Audio)
- **Sensitivity** now really ignores small sounds. At the lowest setting only clearly loud speech counts; short clicks and coughs are dropped. It also works when Deepgram (live) writes your microphone: quiet rooms are sent as silence.
- In "Test for 30 seconds" a **red line** on the Microphone bar shows the limit: sound below it is ignored.
- New **Microphone volume** slider (25 % - 300 %) makes your voice louder or quieter inside the program. Changes are live.

## Version 6.2

New optional tools. Nothing that worked before changes.

### About you from a file
1. Open Setup, then the Answers tab.
2. In "About you" choose **Use a file (CV)**, then pick your CV (`.txt`, `.md`, `.docx` or `.pdf`).
3. Or choose **Write it here** and write it yourself. Only the first 8,000 characters are used.

### Modes and glossary (Setup, Meeting tab)
1. Pick a **Type of meeting** (General, Technical interview, HR / behavioural interview, Work meeting, Lecture / class) to fill in a good style. You can still change everything.
2. In **Glossary** write one technical word per line (up to 60). They help speech recognition and are spelled
   correctly in the transcript. Words of one or two letters, and words that are all lower case, are left alone.

### Speaker separation
With Deepgram live, turn on "Tell the other speakers apart" (Setup, Meeting tab). Names follow the "Person 1" label you chose. People on the computer's sound become "Person 1", "Person 2", …

### Tools menu (in the meeting window)
- **How did I do?** — talking time, speed, filler words, and a written review. Saved in the meeting file.
- **Help me say** — write what you mean, get a good sentence in the meeting language.
- **Read my screen** — a picture of the screen goes to a model that can read pictures. Set the model in Setup, Services, "Reading the screen"
  if the automatic choice fails. The picture is not saved.
- **Search past meetings** — choose the range (7 days … all time). Tick "Also answer my question from what was said" for a written answer.
- **Export** — Word, subtitles (`.srt`), text, JSON, PDF (opens the print window: choose "Save as PDF"), copy summary.

### Following the conversation while you answer
1. Lines of the same person that follow each other are shown as one turn, with the name once.
2. Your own lines have a green colour and a green edge, so they are easy to tell from theirs.
3. When you speak for a while and their last question scrolls out of view, a bar at the top shows "They said" with its translation.
4. Press the bar once to read all of it, press again to jump to the line, or press the cross to hide it for that line.

### Check models
1. Open Setup, then the Services tab.
2. Press **Check models**.
3. Read the list: green = exists now, red = gone (the line says what to try instead).
4. Only models that exist and are not marked old are shown, and the menus use this fresh list.
5. Leave a model box empty to let the program choose. For "Reading the screen" it chooses from what the service reports, and you can type another name.

### Find more models to download
1. Open Setup, then the Services tab, then "Local model" or "Local AI model".
2. Under the download list you see the download size, the memory and the processor the chosen model needs.
3. Press **Find more…** to search Hugging Face. Choose "Most used" or "Newest".
4. Each line shows size, memory needed, processor, and "Fits this computer" or "Too big".
5. Press **Download** on the one you want, then **Test on this computer**.
6. The numbers are estimates. Check the licence on the model's Hugging Face page.

### Hide from screen sharing
1. Install the optional package: `pip install pywebview` (the exe build includes it when it is installed).
2. Setup, Display tab: turn on **Hide this window from screen sharing**, then restart the program.
3. Look at the pill at the top: the pill "Hidden from screen sharing" means it worked; red "NOT hidden" means it did not.
4. Test with a real share (for example a second Zoom meeting) before you rely on it.

> **Warning:** some companies forbid using an assistant in interviews. Check the rules first; you are responsible.
> The taskbar button may still be visible in a full-screen share.


## What changed in version 6.0

### Local AI model for translation and answers

Translation and answers can now also run on the computer itself, like speech to text. No internet, key or quota is needed. If you also turn on the local speech model, the whole app works offline.

**Important:** the local model is slower than online services, especially for long answers. Always test it before an important meeting.

1. Open this section:

```
Setup
```

```
Services
```

```
Local AI model
```

2. Choose a model from the list and click Download. This model is recommended to start with (about 2.5 GB, good translation in many languages, needs about 4 GB of free memory):

```
gemma3-4b
```

If your computer is weak, this model is smaller and faster (but its translation is weaker):

```
qwen2.5-1.5b
```

3. If you already downloaded a model with the gguf extension, click this button and choose its file:

```
Choose file…
```

4. Click this button to measure its speed on this computer:

```
Test on this computer
```

5. Under this heading, choose which task the local model does:

```
Use it for
```

It has two options:

```
Translation
```

```
Answers
```

You can turn on both, or only one. For example translation with the local model and answers with Groq.

6. With the local model, the translation appears after each sentence ends (not while someone is still speaking), because live translation is too heavy for the computer.

**Building the exe:** build_exe.bat adds the engine for this model by itself. At the end it says whether it was added.

### Window security

Only the window that the app opens itself can use the app. If you closed and reopened the app and an old window is still open, it says that it is out of date. Close that window — the app has already opened a new one.

### Install and build files

The install and build files no longer say that a VPN must be on. They only say that an internet connection is needed.

### Bug fixes

The fourth report of the bug-finding program was reviewed and its correct items were fixed. Some important ones:

1. Sentences that are not written no longer use up the Groq free quota.

2. If another model is chosen while one is loading, the first one no longer fills the memory for nothing.

3. After stopping a meeting, no line stays on "writing".

4. If the AI's reply comes as "NO REPLY", it is no longer shown as an answer.

5. Several other small items in connection, audio and downloads.


## What changed in version 5.9

### Version number

The version number is shown in three places: the bottom right corner of the window, the top of the settings panel (next to the word Setup), and the window title.

### Choosing a model folder or a recording

The Windows file dialog sometimes opened behind the app and could not be seen. Now the choice is made inside the app window.

1. In the local model section, click this button:

```
Choose folder…
```

2. A window opens. At the top there are shortcuts (the app's models folder, Downloads, Desktop and the drives).

3. Click folders until you reach the model folder. A folder that is a model has a green model label.

4. When you are inside the model folder, click this button:

```
Use this model
```

The same window opens for a recorded file. Only audio and video files are shown, and clicking a file starts the conversion.

You can also type or paste a path in the box at the top of the window and click Open.

### Credit and limits of the services

1. Open this section:

```
Setup
```

```
Services
```

2. Click this button:

```
Credit & limits
```

3. For every service that has a key, what is left is shown:

- **Deepgram and OpenRouter:** the real account balance (in dollars).
- **Groq:** there is no credit, only a free quota. The requests left today and the tokens left this minute are shown. This quota refills by itself.
- **Other services:** if the service sends numbers they are shown; otherwise a link to the service's account page.

To get these numbers, one very small request (one word) is sent to the service.

### Proxy with user name and password

Proxies that need a user name and password now also work for the live service (Deepgram). The proxy password is not shown on screen or in the log.

### Bug fixes

The third report of the bug-finding program was reviewed and its correct items were fixed. The most important:

1. If the live service silently stops working (without the connection closing), this is detected after 25 seconds and the app continues with another service.

2. If the live service has stopped, it is tried again after the audio device changes.

3. If an answer cannot be written, a message is shown in the answer column (before, only in the transcript column).

4. If saving the settings fails once, it is tried again, and what you typed is not lost.

5. If you close the app in the middle of a meeting, it waits for the last sentences to be written.

6. The Groq quota accounting is more exact.

7. Several other small items in preview, local model, connection and appearance.


## What changed in version 5.8

### Continue the previous meeting

If you stopped a meeting and later want to continue it, you no longer need to start a new meeting. Next to the start button, you will see this button:

```
Continue last
```

1. Click it, or press these keys together:

```
Shift + F9
```

2. The previous text stays on the screen, and new sentences are written below it, in the same meeting file.

3. In the meeting file, the point where the meeting continued is marked with a line (for example "continued at 14:32").

4. This also works after you close the app and open it again.

5. The normal start button (the F9 key) always starts a new meeting. The previous meeting is not deleted; it stays saved in its own file.

### Memory of previous questions

1. For each answer, the last 8 sentences of the conversation are given to the AI.

2. Now the last 10 questions that were answered in the same meeting are also sent, together with their answers.

3. If the same question is asked again in different words, the answer stays consistent with the previous answer, and numbers and facts do not change.

### More accurate answers, without empty talk

The rules for answers are now stricter:

1. Personal information (name, age, education, companies, years of experience, projects, numbers, certificates, salary) is taken only from the About you section. If it is not there, a blank placeholder such as [your name] is written instead.

2. In a technical answer, only things that are correct are said. If a number, version or command is not certain, it is described in general terms and not guessed.

3. The answer stays on the topic of the meeting and the job, with no general or unrelated talk.

### Where to write which information

1. Write your own information here. You can write as much as you want, even your whole CV:

```
Setup
```

```
Answers
```

```
About you
```

For example: your name, age, field of study and university, current job and years of experience, important projects with numbers, certificates, tools you know, and your salary expectation.

2. Write the meeting information here:

```
Setup
```

```
Meeting
```

```
What is this meeting about?
```

Keep the first line short (for example the job title and the technical topics). This line also helps technical terms get written correctly. From the second line on, you can paste the full job description, the company name and their expectations. Answers are written based on all of it.

### Bug fixes

The second report from the bug-finding program was also reviewed and fixed:

1. When the live service (Deepgram) is on and you press pause, audio that was still waiting in the send queue is no longer sent.

2. If the live service disconnects, the app continues with the local model if it is ready, otherwise with Groq. If neither is available, it shows a correct, clear message.

3. Requests that did not reach Groq because of an internet outage no longer count against the free quota.

4. The delay numbers at the bottom of the window start from zero for each new meeting.

5. If removing the local model does not finish completely, the app shows an error message.

6. A proxy address with a username and password (like the example below) is now tested correctly:

```
http://user:pass@127.0.0.1:10809
```

7. Switching the local model no longer keeps two large models in memory at the same time.

8. If the internet is too slow for the live service and audio falls behind, this is written in the log.


## What changed in version 5.7

### Choosing languages

Now anyone, with any language, can use the app. There are three new options in this part of the settings:

```
Setup
```

```
Meeting
```

1. Meeting languages. This option:

```
Languages spoken in the meeting
```

Add one or more languages (up to 6). To add one, choose from this list:

```
+ Add a language…
```

To remove one, click the cross next to the language name. If only one language is selected, speed and accuracy are a little higher. If there are several languages, each sentence is recognized as one of these languages, and other languages are ignored.

2. Your own language. This option:

```
My language (translations)
```

Line translations, word explanations, the meeting summary and the meaning of answers are written in this language. The default is Persian. If a sentence is already in your language, it is not translated.

3. Language of the suggested answer. This option:

```
Suggested answers in
```

The default is this (the same language as the question):

```
Same language as the question
```

You can also choose a fixed language. If the answer is in your own language, its meaning is not repeated below it.

The old "meeting language" setting is moved automatically to the new option.

### Bug fixes

The report from the bug-finding program was reviewed. The real issues were fixed, including:

1. The Groq free-quota counter is now fully safe when several tasks run at the same time.

2. If a service rejects a full request once, the app no longer switches to the simpler mode forever. It does so only after two rejections in a row, and it tries again from time to time. This keeps the quality of the "imaginary text" filter.

3. If the local model gets stuck, the app waits at most 3 minutes and then shows an error, instead of freezing forever.

4. If a model download gets stuck on a bad, half-finished file, that file is downloaded again from the start.

5. After several meetings in a row, extra processing threads no longer stay in memory.

6. If the app window stayed open with an old key (for example after closing and reopening the app), it refreshes the page by itself.

7. If the Windows default audio device is disconnected at that very moment, the device check no longer gives an error.

8. A few other small items in connection, live preview and moving old files.


## What changed in version 5.6

1. All files the app creates (settings, meetings, log, models and window memory) are now in only one folder next to the app:

```
Data
```

Next to the exe file you see only this one folder. Files from previous versions are moved to this folder automatically on the first run. The model you had selected is moved with them, and you do not need to select it again.

2. Building the exe no longer creates a log file.

3. Your own lines are also translated by default. In practice mode (when you ask the questions yourself) they are always translated. This option is in this part of the settings:

```
Setup
```

```
Answers
```

```
Translate my own lines too
```

4. Several problems were fixed: while an answer is being written, you can now select text and scroll. "Stop" for converting a recorded file works immediately. If starting a meeting gives an error, no half-finished file is left behind. And a few other small items.

## What changed in version 5.5

This version is the result of three rounds of strict review of the whole app (speed, stability, appearance).

**Speed**

1. Windows treats programs that do not have their own window as "background" and lowers their processor speed. This was turned off for our app. This was probably the main reason the local model was slow.

2. Local model: the number of cores is set correctly (on new laptops, fast and slow cores are counted separately). Live text is built with a shorter window and is about 3 times faster, but only if the speed test shows that it writes the text correctly.

3. When the other person pauses, the local model writes the whole sentence at that moment. If the sentence is really finished, this is the final text, and it no longer waits for a second pass.

4. If the local model is slow on a computer, live text automatically goes back to Groq, and the local model is tried again every 20 seconds.

**Stability**

1. If headphones or Bluetooth are connected or disconnected in the middle of a meeting, the app switches to the new Windows device by itself (when the Windows default option is selected in the audio settings).

2. If the microphone disconnects for a moment, it is opened again.

3. If the internet or your VPN drops for up to 2 minutes, sentences are not lost; they are written after the connection comes back.

4. If the window is closed or crashes in the middle of a meeting, the app does not stop the meeting and opens the window again.

5. The settings file has a backup copy, and if it gets damaged, your keys are not lost.

6. Opening the app twice does not create two separate apps.

7. A real "Thank you" or "Vielen Dank" is no longer removed. If you repeat the other person's sentence, it is no longer wrongly removed as an echo.

**Appearance**

1. The Persian font (Vazirmatn) is built into the app and does not need the internet. Persian text is larger and easier to read.

2. The answer column is wider. When the other person asks a question, "listening to the question" and then "writing" are shown, and the new answer is highlighted for a moment.

3. The status bar at the top shows problems (for example a lost connection). The bottom of the window is less crowded during a meeting.

4. There is a question-mark button at the top of the window that shows keyboard shortcuts and tips.

## What was added in version 5.4

1. The services section is reorganized: overall status at the top, then three numbered steps, and optional sections collapsed at the bottom. Each service has a colored status label.

2. Groq is no longer required. If another service does all the tasks, the app works without a Groq key too.

3. The local model is faster (the number of processing threads is set correctly, and live text and sentences are built with fast search). The speed test also had a bug that showed the live text number as worse than it really was.

4. If the local model is slow, the test result names a smaller model and shows its download button.

5. A button to clear the log was added in the log section.

## What was added in version 5.3

These features were taken from the Transcribe program and improved for your work. Each one is fully explained in the "During the meeting" and "After the meeting" sections.

1. Live text is calmer: words that will no longer change are shown in bold, and the end of the sentence, which may still change, is shown faded.

2. Selecting several words with the mouse: get an answer about those words, or an explanation of their meaning in your language.

3. Manually correcting a sentence that was heard wrong; the translation (and the answer) is created again.

4. Pause: in the middle of a meeting, nothing is written or sent for a while.

5. A meeting summary in your language, which is also saved at the end of the meeting file.

6. Converting a recorded audio or video file into text and a translation (in your language).

7. Copying the whole meeting text with one click.

8. Answers, explanations and the summary also work after the meeting has ended.

9. The exe build file waits longer on slow internet, and at the end it says whether the local model engine is included in the app or not.

## What was added in version 5.2

1. The app can now turn speech into text on the computer itself (local model), without internet and without a quota.

2. The model is not inside the exe file. You either download it from inside the app, or download it yourself from the website and select it in the app.

3. There is a test button that measures, on that same computer, how fast the model is and whether it hears the text correctly.

4. The full explanation is in the "Local model" section below.

## What was added in version 5.1

1. After testing each service, the app actually tries which tasks that service can do: speech to text, translation, and answers. The result is shown with a green tick or a red cross.

2. For each service, it says whether it writes text word by word (LIVE) or once every few seconds (PREVIEW).

3. With one button you can choose that service for the tasks it can do.

4. You choose how often the preview updates (every few seconds), and how often the live translation updates (every few words). The longer the interval, the fewer tokens are used.

5. The bottom of the window shows how many requests, how many tokens and how many minutes of audio were used in this meeting.

## Changes in version 5.0

1. Speed is higher. Translations and answers are written word by word and do not wait until they are complete.

2. The look of the app has completely changed. The app window is built with the Windows Edge browser engine, but it looks like a normal program.

3. Before a meeting you can test the audio and choose the microphone and speaker yourself.

4. If you do not have headphones and the microphone also hears the other person's voice, the app removes the duplicate lines by itself.

5. The window no longer always stays on top of other windows.

---

## Building the exe file (once and for all)

This turns the whole app into a single exe file, and it no longer needs Python.

1. Put all the files from the zip into the app's current folder and replace the old ones.

2. If services are blocked in your country, turn on your VPN.

3. Double-click this file:

```
build_exe.bat
```

4. Wait until you see this message. It takes about 3 to 5 minutes:

```
DONE.
```

5. The folder that contains the exe file opens by itself, with the file selected:

```
dist\MeetingAssistant.exe
```

6. From now on, the desktop icon opens this file. Your keys, settings and previous meeting texts are copied automatically to the Data folder next to it.

You can move the exe file anywhere, but take the Data folder next to it with it (settings, meetings, log and models are inside it). Put the app somewhere Windows allows writing. For example on the desktop or drive D, but not inside this folder:

```
Program Files
```

Opening the app takes about 2 to 4 seconds, because the exe unpacks itself each time. The speed of the meeting itself is not affected at all.

**First run:** Windows may show a blue window with this title, because the file has no digital signature:

```
Windows protected your PC
```

1. Click this text:

```
More info
```

2. Then click this button:

```
Run anyway
```

At the end of the build, one of these two lines is also written:

```
Local model engine: included.
```

This means the local model engine is included in the app.

```
Local model engine: NOT included
```

This means it was not installed because of slow internet. The app works fully without the local model. To add it, run the build file again later.

If building the exe gives an error, send me these two files (whichever exists):

```
build_log.txt
```

```
pip_log.txt
```

---

## Upgrading from the previous version

Your Groq key, meeting topic and all other previous settings are kept.

1. Close the previous app.

2. Open the zip file.

3. Copy all the files inside this folder:

```
MeetingAssistant
```

4. Put them in the app's previous folder. When Windows asks, choose this option:

```
Replace the files in the destination
```

5. If services are blocked in your country, turn on your VPN.

6. Double-click this file:

```
install.bat
```

7. Wait until you see this message:

```
Done. Open "Meeting Assistant" from your desktop
```

8. A purple icon with this name has been created on the desktop:

```
Meeting Assistant
```

From now on, always open the app with this icon.

---

## Installing on a new computer

If Python is already installed, skip this section.

1. Go to this address:

```
https://www.python.org/downloads/windows/
```

2. Download this version:

```
Python 3.12 — Windows installer (64-bit)
```

3. Run the file. On the first screen, make sure to tick this option:

```
Add python.exe to PATH
```

4. Click this button:

```
Install Now
```

5. Then do steps 2 to 8 of the "Upgrading" section. The difference is that you open the zip in a new folder. For example:

```
C:\MeetingAssistant
```

---

## First run

If no service has been set up yet, the services section opens by itself. The simplest way: paste your free Groq key into the Groq card, in this box:

```
API key
```

The key is saved automatically and the connection is tested automatically. When the box at the top of the page turns green and you see this text, the app is ready:

```
Ready — every task has a service
```

Instead of Groq, you can also add any other service (section four).

---

## Settings

Click this button at the top of the window:

```
Setup
```

All changes are saved automatically, and no save button is needed. The settings have five sections.

### Section one

```
Meeting
```

1. In the first box, write the meeting topic. You can also click one of the ready-made examples below it. Keep the first line short; from the second line on, you can paste the job description and company information.

2. Choose the languages spoken in the meeting. If there is only one language, speech recognition is a little faster and more accurate.

3. Choose your own language (the translation, word explanations and summary are in this language).

4. Choose the language of the suggested answer. Usually the same language as the question is best.

Details of these three options are in the "What changed in version 5.7" section of this guide.

### Section two

```
Answers
```

1. Write the style of the answers, or click one of the examples.

2. In the box below, write your background in English. As much as you want, even your whole CV. Answers use only this information about you:

```
About you
```

3. Choose the answer engine:

```
Fastest
```

This is the fastest mode and is recommended.

```
Deeper
```

This is better for hard technical questions, but about half a second slower.

4. This option is for practicing alone:

```
Test mode
```

When it is on, the app also answers questions you ask yourself into the microphone. While it is on, a blue label with this name is shown at the top of the window. Turn it off in a real meeting.

### Section three

```
Audio
```

1. Choose your microphone and headphones. If the Windows default option is correct, leave it.

2. Click this button:

```
Test for 30 seconds
```

3. Speak and play a video. Both bars should move.

### Section four

```
Services
```

This section is organized and is read from top to bottom.

#### Overall status (top of the page)

A box shows which service does each of the three tasks (speech to text, translation, answers):

- Green means it is ready.
- Orange means that task does not have a service yet, and the reason is written right there.

Until all rows are green, the meeting does not start, and the app tells you exactly what is missing.

#### Step 1: Your services

At least one service is needed. **Groq is not required.** If another service does all the tasks, you do not need a Groq key.

Each service has a card. Click the top of the card to open or close it. At the top of each card, a colored label shows its status:

```
Key needed
```

No key has been entered.

```
Not tested
```

It has not been tested yet.

```
Does everything
```

It does all three tasks.

```
Speech to text only
```

```
Translation & answers
```

It does only part of the work.

```
Not working
```

It does not work.

Below the name of each service, it also says which tasks it is used for.

**Adding a service (paid, free, or local to your country):**

1. In the dashed box, choose the service from the list. For a service that is not in the list, choose this option:

```
Another service (type its address)
```

2. Click this button:

```
Add service
```

3. Paste the service key into the box below:

```
API key
```

4. If the service was not in the list, write its address in this box (it usually ends with /v1):

```
Address (base URL)
```

5. For services inside your own country that are not blocked, turn this option off. For foreign services, leave it on:

```
Connect through the VPN / proxy
```

6. Click this button:

```
Test
```

For about 10 to 20 seconds, the app really translates a sentence with that service and turns a short audio clip into text. Then it shows which tasks it can do, and whether it writes text live (LIVE) or every few seconds (PREVIEW).

7. If it is useful, click a button like the one below so it is chosen for the tasks it can do:

```
Use it for everything
```

To remove a service, open its card and click this button:

```
Remove
```

#### Step 2: Who does what

For each task, choose the service from the list. For Groq, set the model box to automatic mode. For other services, the "Use it for…" button fills in the model by itself.

Next to each row there is a green tick or an orange mark.

If you have also entered a Groq key, leave this option on. If another service gives an error or runs out of credit, Groq continues:

```
Use Groq as a backup
```

#### Check everything

The button below is in the same status box at the top of the page. Click it before an important meeting. All three tasks are actually run once:

```
Test all parts
```

#### Optional sections (bottom of the page)

There are three collapsed boxes that open with a click:

```
Local model
```

The local model (full explanation in the "Local model" section).

```
Speed and token use
```

How often the live text and translation update.

```
Network (VPN / proxy)
```

The proxy. Usually leave it empty. The app finds the Windows proxy by itself.

### Section five

```
Display
```

Light or dark theme, and text size.

---

## Text while people are speaking

The app has two methods. It chooses the method by itself based on the speech-to-text service, and shows it on the screen.

### LIVE method (word by word)

When you have chosen this service for "speech to text":

```
Deepgram
```

Each word is written a fraction of a second after it is spoken. The translation updates every few words. Next to the line, a red label with this text is shown:

```
LIVE
```

Setup:

1. Sign up on the website below. It gives 200 dollars of free credit and does not need a bank card:

```
https://console.deepgram.com
```

2. On that website, create a key and copy it.

3. In the app, in the services section, choose this option from the list and click the add button:

```
Deepgram — LIVE speech to text
```

4. Paste the key and click the test button.

5. In the speech-to-text row, choose this service:

```
Deepgram — LIVE
```

### Preview method (for Groq and other services)

When the other person speaks, a temporary text and translation are shown about every 2 seconds. When the sentence is finished, the final version replaces it. Next to these lines there is a small red label with this text:

```
live
```

Each time, the audio is sent from the start of the sentence. So a word spoken between two sends is not cut in half. Previews use only Groq's extra quota. If the quota runs low, they stop by themselves so the final text never has to wait.

### Setting speed and token use

In the services section, you see these two rows. Any change is applied immediately, even in the middle of a meeting.

1. The first row is for Groq and services that are not LIVE:

```
Preview while speaking
```

Options:

```
Off
```

```
1.5 s
```

```
2 s
```

```
3 s
```

```
5 s
```

A lower number means the temporary text updates sooner, but more requests and tokens are used. With the off option, text appears only after the sentence is finished, and it uses the least. Suggestion: 2 seconds for free Groq, 3 or 5 seconds for a paid service.

2. The second row is for LIVE services such as Deepgram:

```
Live translation refresh
```

Options:

```
3 words
```

```
5 words
```

```
8 words
```

```
Sentence end
```

This means the translation (in your language) is rebuilt after a certain number of new words. A lower number means a more live translation, but more tokens. With the last option, the translation is built only once, at the end of the sentence. English or German text always arrives word by word, in every mode.

**Note:** In German sentences, the main verb usually comes at the end of the sentence. That is why the temporary translation sometimes changes until the end of the sentence. The final translation is always built from the whole sentence.

If Deepgram disconnects or runs out of credit, the app continues by itself with the Groq preview and shows a message.

---

## Local model (speech to text on the computer itself)

With the local model, audio is not sent to the internet; it is turned into text right there on the computer. That is why the text is written very fast and word by word, and there is no quota. Translations and answers still come from Groq (or the other service you chose), so they still need the internet — and, if services are blocked in your country, your VPN.

This is in this part of the settings:

```
Setup
```

```
Services
```

```
Local model
```

### Option one: download the model from inside the app

1. In the drop-down list under this text, choose a model:

```
Or download one here
```

The models, from small to large:

```
tiny
```

About 75 MB. Only for very weak computers. Its accuracy is low.

```
base
```

About 145 MB. Very fast. Good for clear English, weak for German.

```
small
```

About 485 MB. My suggestion to start with. Fast, and good for English and German.

```
medium
```

About 1.5 GB. More accurate, but needs a strong processor.

```
large-v3-turbo
```

About 1.6 GB. The most accurate. Needs a strong processor or an NVIDIA graphics card.

2. Click this button:

```
Download
```

3. A progress bar and the download speed are shown. If services are blocked in your country, your VPN must be on. If the first route does not connect, the app also tries a second site (mirror) and a connection without the VPN by itself.

4. If the download stops, click the download button again. It continues from where it stopped. After the download, all files are checked to make sure they are intact.

5. The model is saved in the folder below, inside the Data folder next to the app. To see that folder, click the next button:

```
models
```

```
Open models folder
```

### Option two: download the model from the website and select it in the app

1. In your browser, go to one of these addresses (for the small model):

```
https://huggingface.co/Systran/faster-whisper-small/tree/main
```

For other models, put the model name instead of small (for example base or medium). The large-v3-turbo model has this address:

```
https://huggingface.co/mobiuslabsgmbh/faster-whisper-large-v3-turbo/tree/main
```

2. Download these files and put them all in one folder:

```
model.bin
```

```
config.json
```

```
tokenizer.json
```

If these files are also on the page, download them too (depending on the model, one of the two vocabulary files is there):

```
vocabulary.txt
```

```
vocabulary.json
```


```
preprocessor_config.json
```

3. In the app, click this button:

```
Choose folder…
```

4. In the window that opens inside the app, go to that same folder (the folder that contains this file and has a green model label):

```
model.bin
```

5. Inside that folder, click this button:

```
Use this model
```

**Important:** Two kinds of model work:

- a faster-whisper model: a folder with model.bin, config.json and tokenizer.json;
- a whisper.cpp model: one file whose name starts with ggml and ends with .bin (for example ggml-small-q5_1.bin). In the folder window, click that file.

A file with the pt extension (from the openai-whisper program) cannot be used; the app says so.

**Which one to choose:** with an NVIDIA graphics card, or only a processor, use small. With Intel or AMD graphics (most laptops), download cpp-small: it runs on the graphics card. If the graphics card cannot be used (an old driver), it runs on the processor by itself, and the status line says so.

**Note:** If you copy the model folder into the Data folder and then into models, the app finds it by itself and shows it in the model list. On another computer you can also copy this same folder so you do not need to download it again.

### Test on this computer

Because every computer has a different speed, always do this after choosing a model:

1. Click this button:

```
Test on this computer
```

2. The app loads the model into memory and turns a test sentence, spoken with Windows' own English voice, into text. The result shows:

- How often the live text can update (every how many seconds).
- How many seconds the final text of each sentence takes.
- Whether it heard the test sentence correctly or not.
- The overall result: fast, good, slow or very slow for this computer.

3. If the result was slow, choose a smaller model and test again.

4. If you have an NVIDIA graphics card, a box in the Local model card offers one download (about 560 MB, once) that lets the local model use it:

   1. Click **Use the NVIDIA graphics card**.
   2. Wait until the download is done (you can stop it and continue later).
   3. Click **Test on this computer**. The line at the top of the card should say **NVIDIA graphics card**.
   4. To free the space again, click **Remove NVIDIA support**.

   If the graphics card gives an error, choose this option so only the processor is used:

```
Run on: processor only
```

### Choosing what the local model does

After the test, there are three options below the result:

```
Off
```

This means the local model is not used.

```
Live text only
```

**My suggestion.** The temporary live text is built on the computer (fast and free), but the final text of each sentence still comes from Groq (the most accurate).

```
All speech to text
```

All speech-to-text is done on the computer. This is good when your VPN is slow or the Groq quota has run out. If the local model is busy and this option is on, Groq helps:

```
Use Groq as a backup
```

### Setting the live text speed of the local model

In the services section, this row has been added:

```
Local model live text
```

Options:

```
0.5 s
```

```
1 s
```

```
1.5 s
```

```
2 s
```

```
3 s
```

The live text itself does not use tokens, because it is built on the computer. But its live translation does use tokens. How much the translation uses is set with this row:

```
Live translation refresh
```

Choose the number the test suggests. If you choose a lower number and the computer is slow, the app skips the updates it cannot keep up with, so the final text does not have to wait.

### Deleting a model

To free up disk space, choose the model from the list and click this button. Only models inside the models folder can be deleted this way:

```
Delete this model
```

### If the local model does not work

1. If it says the local model engine is not in the app, run the file below again (if services are blocked in your country, turn on your VPN first):

```
build_exe.bat
```

2. If it says there is not enough memory (RAM), choose a smaller model.

3. If none of this fixes it, click the copy button in the log section and send me the text.

---

## During the meeting

1. First connect your headphones, then start the meeting.

2. To start, click this button or press the F9 key:

```
Start
```

3. On the left, the conversation text is written. Below each sentence from the other person, the translation (in your language) appears.

4. On the right, the suggested answer is written in large text. Below it, the meaning of the answer in your language also appears.

5. If a question was asked but no answer came, press the F2 key, or click this button:

```
Answer now
```

6. To get an answer for an older sentence, move the mouse pointer over that sentence and click this button:

```
Answer this
```

7. With the buttons below you can make the answer text smaller or larger:

```
A−
```

```
A+
```

8. At the end, press F9 again. The meeting text is saved automatically.

9. If you later want to continue the same meeting, press these keys together, or click the Continue last button:

```
Shift + F9
```

### Live text

While the other person is still speaking, words that will no longer change are written in bold. The end of the sentence is faded, because it may become more accurate until the sentence is finished. With the local model, the live translation is built only from the bold words. This uses fewer tokens.

### Answer or explanation for a few words

1. Select a few words of a sentence with the mouse (like selecting text in Word).

2. A small bar with two buttons appears above it.

3. For a suggested answer about those words, click this button. The answer appears on the right:

```
Answer this
```

4. To have the meaning of those words explained in your language, click this button. The explanation is written below that sentence:

```
Explain in Persian
```

This is very useful for technical terms or for questions you did not fully understand.

### Correcting a sentence that was heard wrong

1. Move the mouse pointer over that sentence. Next to the answer button, a button with a pencil shape appears. Click it.

2. Correct the text.

3. Press the Enter key. The translation is built again. If that sentence had an answer, its answer is also written again. To cancel, press the Esc key.

Next to the corrected sentence, this word is written:

```
edited
```

### Pause

If something is said in the middle of a meeting that you do not want written or sent, press the F8 key or click this button (at the top of the window):

```
Pause
```

A yellow bar shows that the app is paused. To continue, press F8 again or click this button:

```
Continue
```

### Copy the whole text

To copy the whole conversation text (with translations and answers), click the copy button above the text column. Then you can paste it anywhere.

---

## After the meeting

After you press Stop, the meeting text stays on the screen, and all of these still work:

1. Getting an answer for a sentence, with the button below or with the F2 key:

```
Answer this
```

2. Explanation of selected words in your language.

3. Correcting sentences.

### Meeting summary

1. Click this button (above the text column). You can also do this in the middle of a meeting:

```
Summary
```

2. A window opens and the summary is written in your language, in four parts:

- Summary
- Questions that were asked, and what you answered
- Important points (names, numbers, dates)
- Next steps

3. The summary is also saved at the end of the same meeting file. To copy it, click this button:

```
Copy
```

4. To write the summary again, click this button:

```
Write again
```

For long meetings, the app first takes notes on each part separately and then writes the final summary. If it reaches the Groq free limit, it waits by itself and continues. Its message is shown at the bottom of the summary window.

---

## Converting a recorded file to text and translation

This turns an audio or video file (for example a recording of a meeting or an interview) into text and also writes the translation (in your language) of each sentence.

1. When no meeting is running, click this button (above the text column):

```
Transcribe a file…
```

2. In the window that opens inside the app, go to the file's folder and click the file.

3. A progress bar shows how many minutes of the file have been read. Lines are added one by one, with their translations.

4. To stop, click this button. Everything done up to that moment stays saved:

```
Stop
```

5. The result is saved in the meetings folder. The file name starts with this word:

```
recording_
```

The time next to each line is the time of that sentence in the file (from the start of the file).

**A few notes:**

- These files are read directly:

```
mp3
```

```
wav
```

```
flac
```

```
ogg
```

- For other files (such as m4a or mp4) and for YouTube links, the free program ffmpeg must be installed on the computer. If it is not installed, the app opens a window with these steps.

**Installing ffmpeg (once):**

1. Open the Windows Start menu.
2. Type cmd and press Enter.
3. Paste this line into the black window and press Enter:

```
winget install Gyan.FFmpeg
```

4. If it asks whether you agree, type Y and press Enter.
5. Wait until it says the installation is done.
6. Go back to the app and choose the file or link again. If it still says ffmpeg is missing, close the app and open it again.

Another way: download ffmpeg.exe and put it next to the app file.

To see whether ffmpeg is found:

1. Click Setup.
2. Click the Services tab.
3. Click Check this computer.
4. The ffmpeg line in the report should be green.

- To tell the speakers apart, choose Tell the people apart under Who is speaking before you pick the file. Otherwise all lines are written under the other person's name.
- For a recorded file, suggested answers are not written automatically. But you can get an answer with the answer button or by selecting words.
- The Groq free quota is usually enough for a file of one or two hours. For very long files, the hourly or per-minute quota may run out. In that case the app waits by itself and then continues (this is written at the bottom of the window).
- If you chose the local model for all speech to text, the file is turned into text on the computer itself.

---

## Numbers at the bottom of the window

```
Groq ... ms
```

The connection speed to Groq. Under 300 is excellent. If it is above 800, your VPN is slow; try another server. This number has the biggest effect on the app's speed.

These numbers and the ones below are shown only when no meeting is running (during a meeting, the bottom of the window is kept uncluttered):

```
Delay after speech
```

How many seconds after the end of the sentence these three things appeared:

```
text
```

When the text appeared. Normal: 1 to 2 seconds.

```
translation
```

When the translation appeared, after the text. Normal: less than 1 second.

```
answer
```

When the answer started, after the text. Normal: less than 1.5 seconds.

```
Speech quota
```

The free quota left for this hour. It is enough for a one-hour meeting.

```
This meeting: ... requests · ~... tokens · ... min audio
```

Usage for this meeting: the number of requests, the approximate number of tokens, and how many minutes of audio were sent to be turned into text. Hold the mouse pointer over it to see the usage of each service separately. Tests are not counted. If usage is high, make the preview or live translation interval longer.

---

## Where the meeting texts are

At the bottom right of the window, click this button:

```
Open folder
```

Before the first meeting, this button is named:

```
Saved meetings
```

Meetings are in the Data folder and then the meetings folder, next to the app. Each meeting has a separate file with the date and time. The text is saved continuously during the meeting, so if the app closes in the middle of a meeting, nothing is lost.

---

## Log section (for finding problems)

Everything the app does and every error that happens is written in this section.

1. To open it, click this button at the bottom of the window:

```
Log
```

Or click this button in an error message:

```
Show details in log
```

2. For a full audio check, click this button:

```
Check audio devices
```

The app tries all microphones and speakers one by one. At the end of the report, it writes which one works. If the selected device is broken, it suggests a working device with this mark:

```
>>> This one works. In Setup › Audio choose: ...
```

3. To see only errors, turn on this option:

```
Problems only
```

4. To send me a report, click this button and then paste the text into your message:

```
Copy log
```

To clear the log, click this button. The previous log is kept once, with the name app.log.old:

```
Clear log
```

---

## If something goes wrong

0. **This error for computer audio:**

```
[Errno -9999] Unanticipated host error
```

This means Windows does not allow recording the audio of that device. From this version on, the app tries several other methods by itself. If the error still appears:

1. Stop the meeting.

2. In the log section, click the audio check button.

3. Choose the device the report suggested, in the audio section.

If you have Bluetooth headphones, there are two names for them in the list. Choose the one that has this word:

```
Headphones
```

Not the one that has one of these words:

```
Headset
```

```
Hands-Free
```


1. **The window did not open:** Double-click this file once:

```
run.bat
```

If it still does not open, send me this file from the Data folder next to the app:

```
app.log
```

2. **The bottom of the window says Offline:** Your VPN is off (if you need one to reach these services) or the proxy is not correct. In the connection settings section, click this button so the exact reason is written:

```
Test
```

3. **The microphone bar does not move:** Open these three pages, in order, in Windows settings:

```
Settings
```

```
Privacy & security
```

```
Microphone
```

and turn on this option:

```
Let desktop apps access your microphone
```

4. **The other person's audio bar does not move:** In the audio section, choose the correct device in the box below. If you connected the headphones after starting, stop the meeting once and start it again:

```
Speakers / headphones
```

5. **This message appeared:** You have reached the free per-minute limit. The app waits by itself and continues. Nothing is lost.

```
Free limit reached
```

6. **When closing the window:** The app saves the meeting and closes completely a few seconds later.
