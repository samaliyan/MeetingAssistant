# What is tested, and how

This file says, part by part, how the program is checked and what cannot be checked without a real Windows computer,
real sound or real services. It is updated with every audit.

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
| Hidden from screen sharing | – | – | yes | yes (affinity flag) | seeing it from the other side of a call |
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
| Keep the sound, ▶ on a line | yes (WAV here) | yes (play, switch lines, stop at line end) | yes | – | Opus files (soundfile on Windows), 3-hour meetings |
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
