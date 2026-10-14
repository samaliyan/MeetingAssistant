"""Real Windows check of the installer (run by .github/workflows/ci.yml, not by pytest).

    python tests/win_install_check.py MeetingAssistant-Setup.exe

Like a user who had the earlier single-file copy on the computer (with a desktop shortcut, settings, a meeting and a
model), it installs the program silently, starts it, updates it while it runs, and uninstalls it. Checks:
  - the program, its Start menu and desktop shortcuts and its uninstall entry are there;
  - the first start brings the settings and the meeting of the earlier copy along (and moves its model);
  - an update installs over the running program and keeps the settings;
  - uninstalling removes the program but keeps the settings (the default answer), and its Start menu entry.
Prints one line per check (also as GitHub annotations); exit 1 when one fails."""
import json
import os
import shutil
import subprocess
import sys
import time

SETUP = os.path.abspath(sys.argv[1])
LOCAL = os.environ["LOCALAPPDATA"]
APP = os.path.join(LOCAL, "Programs", "Meeting Assistant")
EXE = os.path.join(APP, "MeetingAssistant.exe")
DATA = os.path.join(APP, "Data")
HOME = os.path.expanduser("~")
DESKTOP = subprocess.run(["powershell", "-NoProfile", "-Command", "[Environment]::GetFolderPath('Desktop')"],
                         capture_output=True, text=True).stdout.strip() or os.path.join(HOME, "Desktop")
PROGRAMS = os.path.join(os.environ["APPDATA"], "Microsoft", "Windows", "Start Menu", "Programs")
OLD = os.path.join(HOME, "Downloads", "MA old copy")
results = []


def check(name, ok, detail=""):
    results.append(bool(ok))
    line = f"[{'OK' if ok else 'FAIL'}] {name}" + (f": {detail}" if detail else "")
    print(line, flush=True)
    if os.environ.get("GITHUB_ACTIONS"):
        print(("::notice" if ok else "::error") + " title=Install::" + line.replace("%", "%25").replace("\n", "%0A"), flush=True)


def ps(cmd):
    return subprocess.run(["powershell", "-NoProfile", "-Command", cmd], capture_output=True, text=True, timeout=120).stdout.strip()


def shortcut_target(lnk):
    return ps(f"(New-Object -ComObject WScript.Shell).CreateShortcut('{lnk}').TargetPath") if os.path.isfile(lnk) else ""


def run_setup(*extra):
    t = time.time()
    r = subprocess.run([SETUP, "/VERYSILENT", "/SUPPRESSMSGBOXES", "/NORESTART", "/TASKS=desktopicon", *extra], timeout=600)
    return r.returncode, time.time() - t


def start_program():
    for p in (os.path.join(DATA, ".port"),):
        if os.path.exists(p):
            os.remove(p)
    env = dict(os.environ, MA_NO_BROWSER="1")
    t = time.time()
    proc = subprocess.Popen([EXE], cwd=APP, env=env)
    while time.time() - t < 120 and not os.path.exists(os.path.join(DATA, ".port")):
        if proc.poll() is not None:
            break
        time.sleep(0.1)
    return proc, (time.time() - t) if os.path.exists(os.path.join(DATA, ".port")) else None


# ---- the earlier single-file copy, as people had it ----
shutil.rmtree(OLD, ignore_errors=True)
os.makedirs(os.path.join(OLD, "Data", "meetings"))
os.makedirs(os.path.join(OLD, "Data", "models", "speech"))
with open(os.path.join(OLD, "MeetingAssistant.exe"), "wb") as f:
    f.write(b"MZ (stand-in for the old exe)")
with open(os.path.join(OLD, "Data", "config.json"), "w", encoding="utf-8") as f:
    json.dump({"context": "Interview at the old company", "hide_from_share": False}, f)
with open(os.path.join(OLD, "Data", "meetings", "2026-10-01 interview.md"), "w", encoding="utf-8") as f:
    f.write("# An old meeting\n")
with open(os.path.join(OLD, "Data", "models", "speech", "model.bin"), "wb") as f:
    f.write(b"\0" * 1024)
ps("$s=(New-Object -ComObject WScript.Shell).CreateShortcut([Environment]::GetFolderPath('Desktop')+'\\Meeting Assistant.lnk');"
   f"$s.TargetPath='{os.path.join(OLD, 'MeetingAssistant.exe')}';$s.Save()")
check("the earlier copy's desktop shortcut is there", shortcut_target(os.path.join(DESKTOP, "Meeting Assistant.lnk")).endswith("MeetingAssistant.exe"))

# ---- install ----
code, took = run_setup()
check("the installer finishes", code == 0, f"code {code}, {took:.0f} s")
check("the program is installed for this user", os.path.isfile(EXE) and os.path.isdir(os.path.join(APP, "_internal")), APP)
check("Start menu shortcut", shortcut_target(os.path.join(PROGRAMS, "Meeting Assistant.lnk")).lower() == EXE.lower())
check("desktop shortcut now starts the installed program", shortcut_target(os.path.join(DESKTOP, "Meeting Assistant.lnk")).lower() == EXE.lower())
check("it is listed in Settings > Apps (uninstall entry)", "Meeting Assistant" in ps(
    "Get-ChildItem HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall | ForEach-Object { (Get-ItemProperty $_.PSPath).DisplayName }"))
hint = os.path.join(DATA, ".old_portable")
check("the installer left the earlier copy's folder for the program", os.path.isfile(hint) and
      open(hint, encoding="utf-8-sig").read().strip().lower() == OLD.lower())

# ---- first start ----
proc, took = start_program()
check("the installed program starts", took is not None, f"running after {took:.1f} s" if took else "no .port")
cfg = {}
try:
    with open(os.path.join(DATA, "config.json"), encoding="utf-8") as f:
        cfg = json.load(f)
except (OSError, ValueError):
    pass
check("first start: the settings of the earlier copy came along", cfg.get("context") == "Interview at the old company", str(cfg.get("context")))
check("first start: its meeting came along", os.path.isfile(os.path.join(DATA, "meetings", "2026-10-01 interview.md")))
check("first start: its model was moved (not copied twice)", os.path.isfile(os.path.join(DATA, "models", "speech", "model.bin"))
      and not os.path.exists(os.path.join(OLD, "Data", "models")))
check("the earlier copy keeps its own settings", os.path.isfile(os.path.join(OLD, "Data", "config.json")))
check("the note is used once", not os.path.exists(hint))

# ---- update while it runs ----
code, took = run_setup()
time.sleep(2)
check("an update installs over the running program", code == 0 and os.path.isfile(EXE), f"code {code}, {took:.0f} s")
check("…the program was closed for it", proc.poll() is not None)
if proc.poll() is None:
    proc.kill()
check("…and the settings stay", os.path.isfile(os.path.join(DATA, "config.json")))
proc, took = start_program()
check("the updated program starts", took is not None, f"running after {took:.1f} s" if took else "no .port")
subprocess.run(["taskkill", "/F", "/T", "/IM", "MeetingAssistant.exe"], capture_output=True)
time.sleep(2)

# ---- uninstall ----
unins = os.path.join(APP, "unins000.exe")
r = subprocess.run([unins, "/VERYSILENT", "/SUPPRESSMSGBOXES", "/NORESTART"], timeout=300) if os.path.isfile(unins) else None
time.sleep(3)
check("uninstall finishes", r is not None and r.returncode == 0, "unins000.exe missing" if r is None else f"code {r.returncode}")
check("uninstall removes the program", not os.path.exists(EXE) and not os.path.exists(os.path.join(APP, "_internal")))
check("uninstall keeps the settings and meetings (the default answer)", os.path.isfile(os.path.join(DATA, "config.json"))
      and os.path.isfile(os.path.join(DATA, "meetings", "2026-10-01 interview.md")))
check("uninstall removes the Start menu shortcut", not os.path.exists(os.path.join(PROGRAMS, "Meeting Assistant.lnk")))

shutil.rmtree(APP, ignore_errors=True)
shutil.rmtree(OLD, ignore_errors=True)
ok = all(results)
print("RESULT:", "OK" if ok else "FAILED", flush=True)
sys.exit(0 if ok else 1)
