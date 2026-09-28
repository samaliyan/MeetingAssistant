# Contributing

Thanks for helping! Bug reports, translations of the guide and pull requests are welcome.

## Set up

```bat
install.bat
run.bat
```

The program runs on Windows (it records the computer's sound with WASAPI loopback). The tests do not need
Windows or an audio device:

```
python -m pip install -r requirements-test.txt
python -m pytest tests
```

## Pull requests

1. Keep changes focused; describe what you changed and how you tested it.
2. Add or update a test in `tests/` when you change logic that does not need audio.
3. User-facing changes go into `CHANGELOG.md`.
4. Never commit the `Data` folder, API keys, meeting files or logs (`.gitignore` already excludes them).

## Releases (maintainer)

1. Raise `VERSION` in `app.py` and add its section to `CHANGELOG.md`.
2. Commit to `main` with `[release]` in the commit message.
3. GitHub Actions runs the tests, builds `MeetingAssistant.exe` and publishes the release `vX.Y`.
