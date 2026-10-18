# Security

## What the program keeps

- API keys and settings are stored only on your computer, in `Data/config.json` next to the program
  (or in `%LOCALAPPDATA%\MeetingAssistant` if that folder is read-only).
- The API keys and a proxy password in that file (and its backup) are encrypted by Windows for your Windows user
  (DPAPI). Another Windows user or another PC cannot read them; keys saved by a version before 6.34 are encrypted at
  the first start of 6.35 or later. An earlier single-file copy of the program keeps its own old settings file: delete
  that copy when the new one works.
- The window talks to the program over `127.0.0.1` only, protected by a random key that changes on every start.
- Audio and text are sent only to the services you choose. With the local model, speech never leaves the computer.

## Reporting a problem

Please do **not** open a public issue for a security problem. Use
[GitHub's private vulnerability reporting](../../security/advisories/new) for this repository instead,
and describe how to reproduce it. Never include your API keys in a report or a log you share.
