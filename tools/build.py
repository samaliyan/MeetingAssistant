"""Builds dist/MeetingAssistant.exe with PyInstaller (used by the GitHub release workflow).

build_exe.bat calls this same file on your own computer (and also copies your settings there),
so the PyInstaller options live only here.

    python tools/build.py            (Windows, after: pip install -r requirements.txt pyinstaller)
"""
import importlib.util
import os
import types
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXCLUDE = ["tkinter", "_tkinter", "lib2to3", "pydoc_data", "setuptools", "pip", "pkg_resources",
           "sqlite3", "_sqlite3", "curses", "IPython", "matplotlib", "PIL", "scipy", "pandas", "PySide6",
           "shiboken6", "PyQt5", "PyQt6", "numpy.f2py", "numpy.distutils", "av", "torch", "transformers"]


def imports(name):
    """True when the package really imports (installed but broken = left out, never packed broken)."""
    if importlib.util.find_spec(name) is None:
        return False
    sys.modules.setdefault("av", types.ModuleType("av"))      # faster-whisper imports it; the program never uses it
    try:
        __import__(name)
        return True
    except Exception as e:
        print(f"{name} is installed but does not import ({e}) - left out")
        return False


def main():
    os.chdir(ROOT)
    sep = ";" if os.name == "nt" else ":"
    args = [sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean", "--onefile", "--windowed",
            "--name", "MeetingAssistant", "--icon", "icon.ico",
            "--add-data", f"web{sep}web", "--add-data", f"icon.ico{sep}.",
            "--hidden-import", "socksio", "--collect-submodules", "h2"]
    # the local model engine is optional: included when faster-whisper and ctranslate2 are installed
    if imports("faster_whisper") and imports("ctranslate2"):
        # --collect-data: the voice-activity model (silero, .onnx) that the fast file mode uses
        args += ["--hidden-import", "faster_whisper", "--collect-data", "faster_whisper", "--collect-binaries", "ctranslate2"]
        print("Local model engine: included")
    else:
        print("Local model engine: NOT included (faster-whisper / ctranslate2 not installed)")
    exclude = list(EXCLUDE)
    # onnxruntime: finds the speech in a recording (fast file mode) and tells speakers apart
    if imports("onnxruntime"):
        args += ["--collect-binaries", "onnxruntime", "--hidden-import", "onnxruntime"]
        print("onnxruntime (voice activity, speakers): included")
    else:
        exclude.append("onnxruntime")
        print("onnxruntime: NOT included (fast file mode and speaker separation are off)")
    # whisper.cpp (built with Vulkan by the workflow): local speech to text on ANY graphics card
    srv = os.path.join("whisper_cpp", "whisper-server.exe" if os.name == "nt" else "whisper-server")
    if os.path.isfile(srv):
        args += ["--add-binary", f"{srv}{sep}whisper_cpp"]
        vk = os.path.join("whisper_cpp", "vulkan-1.dll")
        if os.path.isfile(vk):
            args += ["--add-binary", f"{vk}{sep}whisper_cpp"]      # starts even where no Vulkan driver is installed
        print("whisper.cpp engine: included")
    else:
        print("whisper.cpp engine: NOT included (whisper_cpp/whisper-server.exe not built)")
    # yt-dlp: a YouTube (or other) link to text
    if imports("yt_dlp"):
        args += ["--collect-submodules", "yt_dlp", "--collect-data", "yt_dlp"]
        print("Links (yt-dlp): included")
        # YouTube needs the yt-dlp-ejs scripts and a JavaScript program to run them (quickjs, put in jsrt/ by the workflow)
        if imports("yt_dlp_ejs"):
            args += ["--collect-all", "yt_dlp_ejs"]
            print("YouTube scripts (yt-dlp-ejs): included")
        else:
            print("YouTube scripts (yt-dlp-ejs): NOT included (YouTube links may fail)")
        qjs = os.path.join("jsrt", "qjs.exe")
        if os.path.isfile(qjs):
            args += ["--add-binary", f"{qjs}{sep}jsrt"]
            print("JavaScript runtime (quickjs): included")
        else:
            print("JavaScript runtime (quickjs): NOT included (YouTube works only if deno or node is installed)")
    else:
        print("Links (yt-dlp): NOT included")
    # the local AI engine (translation and answers on this computer) is optional too
    if imports("llama_cpp"):
        args += ["--collect-all", "llama_cpp"]
        exclude = [m for m in exclude if m not in ("sqlite3", "_sqlite3")]      # its cache module needs sqlite3
        print("Local AI engine: included")
    else:
        print("Local AI engine: NOT included (llama-cpp-python not installed)")
    # a window that screen sharing cannot see (optional): a helper window made with pywebview / WebView2
    if sys.platform == "win32" and imports("webview"):
        args += ["--collect-all", "webview", "--hidden-import", "clr"]
        for extra in ("pythonnet", "clr_loader"):
            if importlib.util.find_spec(extra) is not None:
                args += ["--collect-all", extra]
        print("Hidden window (screen sharing): included")
    else:
        print("Hidden window (screen sharing): NOT included (pywebview not installed)")
    for m in exclude:
        args += ["--exclude-module", m]
    args.append("app.py")
    print(" ".join(args))
    return subprocess.call(args)


if __name__ == "__main__":
    sys.exit(main())
