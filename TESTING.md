# What is tested, and how

This file says, part by part, how the program is checked and what cannot be checked without a real Windows computer,
real sound or real services. It is updated with every audit (last: 6.35, six independent reviewers of the whole program — processes, display, flow, features and switches, performance, security/setup — plus two re-reviewers of the fixes; 6.19 and 6.17 before).

Ways of checking:

- **Unit** = automatic tests (`python -m pytest tests`, run on Ubuntu and on Windows for every change, and again in the
  release job).
- **Browser** = the web page is opened in a real browser against the real program with fake services (done before a
  release, not part of CI): live meeting, reading lock, coach line, sizes 820–1920 px, 100 % and 150 % text, dark,
  overlay, video and in-person modes, settings with every part off.
- **Review** = read by independent reviewers who did not write the code.
- **Windows check** = the CI jobs on a real Windows machine: the exe starts and closes, the overlay opens, voice
  learning, keys kept encrypted (DPAPI), a PAC proxy, install / update / uninstall.
- **By hand** = only a person on a real machine can confirm it.

| Part | Unit | Browser | Review | Windows check | Only by hand |
|---|---|---|---|---|---|
| Settings load / save / upgrade | yes | yes | yes | – | old files from very old versions |
| Meeting file, "Continue", export (docx, pdf, srt, txt, json) | yes | yes | yes | – | full disk, antivirus locks, OneDrive |
| Segmenter (cutting speech) | yes | – | yes | – | real voices |
| Translation, answers, coach, review, scores | yes (fake model) | yes | yes | – | quality of real model text |
| Model chain, rate limits, blank replies, previews | yes | – | yes | – | real limits of Groq, OpenAI, Gemini … |
| Speech to text: Groq, OpenAI-compatible | encoder and fallback only | – | yes | – | real services |
| Deepgram live | fake server only | – | yes | – | real account, Farsi, key limits |
| Local Whisper / local AI | – | – | yes | – | real models, GPU / CPU speed |
| Coach (situation, silence, kinds of question, words to say) | yes (fake model) | yes (overlay layout) | yes | – | quality of real coach text, real silence timing |
| Practice interview, job advert, scores | yes | yes | yes (2 rounds) | – | speech reading aloud (voices) |
| Local server, token, host check | yes (real localhost server) | yes | yes | – | – |
| New models list (models.dev, OpenRouter, Hugging Face) | yes (fake lists, odd data, offline) | yes (fake list; Hugging Face reached for real) | yes | – | the real models.dev and OpenRouter lists, buying and adding a real key |
| Readability (sizes, contrast, layout at 1366, 1536@125%, 1920, dark, overlay) | – | yes (screenshots) | yes (3 UX reviewers + re-review) | – | real Segoe UI / Vazirmatn rendering, 150% scaling |
| Web page: transcript, answer panel, settings, tools | – | yes | yes | – | WebView2 differences, fonts |
| Long meetings (thousands of lines) | – | yes (1500 lines) | yes | – | 3-hour real meeting |
| See-through window: open, click-through, alpha, position | logic only | page only | yes | yes | Teams / Zoom / Meet |
| Hidden from screen sharing (6.19: Windows version read with RtlGetVersion; black-box fallback stated in advance; "Test it now" self-test) | yes (the self-test judge with made-up pixels; version detection; action guards) | yes (the setup screen, the three-choice message, the black-box warning) | yes | yes (affinity flag) | real Windows capture with BitBlt / PrintWindow, seeing it from the other side of a call, old Windows (before 2004) |
| Move / resize with mouse and keys | – | – | yes | yes (best effort) | different DPI, several monitors |
| Global keys (Ctrl+Alt …) | – | – | yes | yes (best effort) | keyboard layouts with AltGr |
| Microphone and computer sound (WASAPI) | – | – | yes | – | devices, sleep / wake, Bluetooth |
| Screen reading | logic only | – | yes | – | real screenshots and services |
| Windows shortcut, single instance, paths with Persian letters | – | – | yes | – | Program Files, OneDrive |
| Fast file mode (local model, batched, skips silence) | yes (fake model) | – | yes | – | real faster-whisper batched speed and text on CPU / NVIDIA |
| Speakers in a recording (voice model, grouping) | yes (made-up voice prints, fbank) | – | yes | – | real voices: how well people are told apart |
| whisper.cpp engine (Vulkan) | yes (fake server); real Linux server with the tiny test model, by hand | – | yes | build job | Vulkan on Intel / AMD, speed, the first run of the exe |
| Subtitles (.srt / .vtt) | yes (long lines, long words, escaping, no overlap) | – | yes | – | how they look in a real video player |
| Link to text (yt-dlp) | yes (a page on this computer) | – | yes | – | real YouTube (needs its scripts and quickjs) |
| ffmpeg help (files, links, health check, winget folder) | yes (no ffmpeg on PATH, winget Links folder) | yes (screenshots) | yes | – | a real winget install on Windows |
| UX of the 6.14 screens (file/link window, speakers, ▶, local model, overlay "more") | – | yes (screenshots, play / switch / grouped lines) | yes (3 UX reviewers + re-review of the fixes) | – | WebView2 look, real Intel / AMD driver messages |
| Keep the sound, ▶ on a line | yes (WAV here) | yes (play, switch lines, stop at line end) | yes | – | Opus files (soundfile on Windows), 3-hour meetings |
| Vosk light model (engine via ctypes, zip download, language warning) | yes (download from a local server, unsafe zip paths, which download is used; the real engine with a real English model when given) | yes (real engine + real English model: choose, Test, a real recording) | yes (independent review) | – | the Windows engine (libvosk.dll), downloads from alphacephei.com, Persian and other models, folders with Persian letters |
| NVIDIA support with one button (cuBLAS download, PATH, reload) | yes (fake PyPI: a break in the middle, SHA-256 check, only 2 files kept, remove and remove-at-next-start) | yes (button, progress, stop, continue, remove; fake files) | yes (independent review; CTranslate2 sources read) | – | a real NVIDIA card, the real 560 MB file from pypi.org, real speed |
| 6.19 say mode (F6): my speech in my language → a sentence to say, never a transcript line | yes (language sent, nothing in the transcript, live lines dropped, order of results, a lost piece reports) | yes (whole meeting with a fake Groq: F6, Persian speech, card, overlay) | yes | – | real Persian speech, Deepgram live, the global key Ctrl+Alt+J on Windows |
| 6.19 marks, speaker names, my notes, full notes | yes (files, export, Continue, wrong meeting refused, bad input) | yes (F7, flag, rename, notes saved, notes typed just before Start stay with their meeting) | yes | – | Ctrl+Alt+K on Windows, closing the window while typing |
| 6.19 summary with decisions and action items, Copy as message, glossary from the advert, filler words and pace | yes (prompts, merging, limits, counting "like,") | yes (summary, message text, glossary button) | yes | – | quality of real model text |
| 6.19 meeting reminder (window titles) | yes (titles of Zoom, Teams, Meet, Webex; web pages and chats not counted; once per 10 minutes) | yes (fake window list → message → Start) | yes | – | the real window titles of Zoom, Teams and Meet on Windows |
| Features switches (Setup › Features, presets, hiding, Start needs) | yes (settings, needed services, every action refused when off, lines not translated / answered) | yes (presets, text-only meeting, coach-only panel, narrow window, overlay) | yes (2 reviews) | – | WebView2 look |
| Build (exe), installer and release | – | – | yes | build, start, install / update / uninstall jobs | Windows SmartScreen on a new PC |
| 6.35 reading lock, coach line, room for the answer, end bar, keys list, parts off hidden | – | yes (run_ui9: answer never moves when you speak or a question arrives; Space; sizes; overlay) | yes (re-review with the reviewer's own probes) | – | WebView2 focus after Alt+Tab, real mouse use |
| 6.35 Stop keeps the last sentences, lost speech counted, joins, Continue owner, live retries, live settings changed in a meeting | yes | – | yes (re-review reproduced and re-checked) | – | real Groq limits at the end of a meeting, a real Deepgram outage |

Setup › Services › **Check this computer** tests the Windows parts on the user's own machine and can copy a report.

## Known open points (after 6.35)

Fixed in 6.35 (each checked; tests or browser checks named in the table): the answer being read is never replaced and
never moves; parts that are off take no key, show no settings and send nothing; Stop keeps writing the last sentences;
a recording says when it is incomplete; Continue is always the newest meeting; in-person lines are never joined;
live streams retry for the whole meeting and follow setting changes; a Deepgram 403 from a network block is not taken
for a wrong key; keys from before 6.34 are encrypted at once; uninstall deletes only the Data folder; long meetings
stay quick (one style rule cost 1.3 s per line at 2000 lines).

Still open:

- Three ways to get "what to say" overlap (Answer now F2, Help me say, Ask coach F4): kept as they are; one combined
  "help" may come later.
- A very small answer area at 150 % text (820 × 700) shows only the first line of the answer at once (it scrolls).
- The see-through window has no keys to start, stop or pause the meeting (the main window does it).
- Waiting pieces of one speaker are joined only within 4 seconds: after a long network break the backlog takes more
  requests than before.
- A Windows PAC script that hangs makes the very first request wait up to 3 s.
- Real Windows parts not seen by a person in this audit: focus after Alt+Tab, the global keys on AltGr keyboards,
  a real Deepgram outage, real Groq limits at the end of a meeting.

### From the 6.34 audit (still true)

Fixed in 6.34 (each with a test; the Windows parts with a check on a real Windows machine): speech to text moves on to
the next service after a temporary error; a model that failed is tried again when Setup changes the services; a Windows
PAC proxy is read (Windows check with a real PAC file); Deepgram silence is not sent and failed streams are counted;
"Continue" is at most ~5 s behind; screen reading is never started by the meeting audio; API keys are stored with
DPAPI (Windows check: not in the file, read back after a restart); keys can be Ctrl+Alt+Shift or off for AltGr
keyboards; far lines of long meetings are drawn only when near (browser check, 2000 lines); Teams in a web browser and
the user's own window-title words for the meeting reminder; say mode no longer streams the microphone to Deepgram.

Still open:

- 6.19 say mode: there is no echo check on the say piece; use headphones.
- 6.19 "Test it now" for hiding: the pixel capture half (BitBlt + PrintWindow) is logic-reviewed only; it has not been
  run on a real Windows screen share. The decision logic (judge_hide) is unit-tested. The flag Windows itself reports
  (GetWindowDisplayAffinity) is always the authoritative signal.
- Hiding the mouse cursor from the other side only (while the user still sees it) is not possible on Windows and was
  not added.
- Keys encrypted with DPAPI cannot be read by another Windows user or on another PC (by design): they must be entered
  again there; an older version of the program cannot read them.
- The meeting reminder still reads only window titles (nothing inside the meeting programs).
