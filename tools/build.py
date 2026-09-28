"""Builds dist/MeetingAssistant.exe with PyInstaller (used by the GitHub release workflow).

build_exe.bat calls this same file on your own computer (and also copies your settings there),
so the PyInstaller options live only here.

    python tools/build.py            (Windows, after: pip install -r requirements.txt pyinstaller)
"""
import importlib.util
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXCLUDE = ["tkinter", "_tkinter", "lib2to3", "pydoc_data", "setuptools", "pip", "distutils", "pkg_resources",
           "sqlite3", "_sqlite3", "curses", "IPython", "matplotlib", "PIL", "scipy", "pandas", "PySide6",
           "shiboken6", "PyQt5", "PyQt6", "numpy.f2py", "numpy.distutils", "av", "onnxruntime", "torch",
           "transformers"]


def main():
    os.chdir(ROOT)
    sep = ";" if os.name == "nt" else ":"
    args = [sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean", "--onefile", "--windowed",
            "--name", "MeetingAssistant", "--icon", "icon.ico",
            "--add-data", f"web{sep}web", "--add-data", f"icon.ico{sep}.",
            "--hidden-import", "socksio", "--collect-submodules", "h2"]
    # the local model engine is optional: included when faster-whisper and ctranslate2 are installed
    if importlib.util.find_spec("faster_whisper") and importlib.util.find_spec("ctranslate2"):
        args += ["--hidden-import", "faster_whisper", "--collect-binaries", "ctranslate2"]
        print("Local model engine: included")
    else:
        print("Local model engine: NOT included (faster-whisper / ctranslate2 not installed)")
    exclude = list(EXCLUDE)
    # the local AI engine (translation and answers on this computer) is optional too
    if importlib.util.find_spec("llama_cpp"):
        args += ["--collect-all", "llama_cpp"]
        exclude = [m for m in exclude if m not in ("sqlite3", "_sqlite3")]      # its cache module needs sqlite3
        print("Local AI engine: included")
    else:
        print("Local AI engine: NOT included (llama-cpp-python not installed)")
    for m in exclude:
        args += ["--exclude-module", m]
    args.append("app.py")
    print(" ".join(args))
    return subprocess.call(args)


if __name__ == "__main__":
    sys.exit(main())
