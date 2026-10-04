# What is tested, and how

This file says, part by part, how the program is checked and what cannot be checked without a real Windows computer,
real sound or real services. It is updated with every audit (last: 6.19, two independent reviewers of the new parts plus a re-review of the fixes; 6.17: seven reviewers).

Ways of checking:

- **Unit** = automatic tests (`python -m pytest tests`, run on Ubuntu and on Windows in the release job).
- **Browser** = the web page is opened in a real browser against the real program with fake services (done by hand
  before a release, not part of CI).
- **Review** = read by independent reviewers who did not write the code.
- **Windows check** = `.github/workflows/windows-check.yml` opens the overlay on a real Windows machine (best effort).
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
| Build (exe) and release | – | – | yes | build job | first run of the exe on a clean PC |

Setup › Services › **Check this computer** tests the Windows parts on the user's own machine and can copy a report.

## Known open points from the last audit (not fixed yet)

- Speech to text does not switch to the next service when the first answers with a temporary error (it retries for up to
  2 minutes, then drops that sentence). Chat does switch.
- A model that returned 404 (wrong address) stays off until the program restarts.
- A Windows proxy set by a PAC file is not read.
- Deepgram: silence is sent (and billed) as zeros; failed streams are not counted in the usage numbers.
- After a crash, up to about 20 seconds of the newest lines may be missing when continuing a meeting.
- Screen reading by itself (off by default) sends the whole screen; a remote voice saying "look at my screen" can
  trigger it. Keep it off unless you want it.
- API keys are stored as plain text in `Data\config.json` (and its backup copy).
- Two overlay hotkeys can collide with other programs on AltGr keyboards; use the buttons then.
- Very long meetings keep every line in the page (no virtual list yet).
- 6.19 meeting reminder: Teams in a web browser and meetings whose window title has no "Meeting" or "Call" are not noticed.
- 6.19 say mode: with a live service (Deepgram) your speech is still sent to it while say mode is on (it is not shown).
- 6.19 say mode: there is no echo check on the say piece; use headphones.
- 6.19 "Test it now" for hiding: the pixel capture half (BitBlt + PrintWindow) is logic-reviewed only; it has not been run on a real Windows screen share. The decision logic (judge_hide) is unit-tested. The flag Windows itself reports (GetWindowDisplayAffinity) is always the authoritative signal.
- Hiding the mouse cursor from the other side only (while the user still sees it) is not possible on Windows and was not added.
