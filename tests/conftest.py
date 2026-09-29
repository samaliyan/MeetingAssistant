"""The program keeps its data next to app.py, so the tests import a copy from a temporary folder.

Run from the project folder:
    python -m pip install -r requirements-test.txt
    python -m pytest tests
"""
import importlib.util
import os
import shutil
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture(scope="session")
def app(tmp_path_factory):
    d = tmp_path_factory.mktemp("ma")
    shutil.copy(os.path.join(ROOT, "app.py"), d / "app.py")
    shutil.copytree(os.path.join(ROOT, "web"), d / "web")
    old_env = os.environ.get("MA_NO_BROWSER")
    os.environ["MA_NO_BROWSER"] = "1"
    spec = importlib.util.spec_from_file_location("ma_app", d / "app.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["ma_app"] = mod
    spec.loader.exec_module(mod)
    yield mod
    sys.modules.pop("ma_app", None)
    if old_env is None:
        os.environ.pop("MA_NO_BROWSER", None)
    else:
        os.environ["MA_NO_BROWSER"] = old_env


@pytest.fixture(autouse=True)
def clean_data(request):
    """Every test starts without settings, meetings or a remembered last meeting."""
    if "app" not in request.fixturenames:
        yield
        return
    mod = request.getfixturevalue("app")

    def wipe():
        for p in (mod.CONFIG_PATH, mod.CONFIG_PATH + ".bak", mod.LAST_MEETING):
            if os.path.exists(p):
                os.remove(p)
        shutil.rmtree(mod.MEETINGS_DIR, ignore_errors=True)
    wipe()
    yield
    wipe()
