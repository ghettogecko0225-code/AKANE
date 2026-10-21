import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

# Native stacks must load before PyQt6 (DLL clash)
try:
    import onnxruntime  # noqa
except Exception:
    pass
try:
    import faster_whisper  # noqa
except Exception:
    pass

from PyQt6.QtWidgets import QApplication
from core.brand import APP_NAME
from core.paths import resource_root, data_root
from pc.main_window import MainWindow


def _crash_log(exc_type, exc, tb):
    try:
        from core.paths import data_root
        log = data_root() / "crash_log.txt"
        with open(log, "a", encoding="utf-8") as f:
            f.write("\n=== crash ===\n")
            f.write("".join(traceback.format_exception(exc_type, exc, tb)))
    except Exception:
        pass


def main():
    sys.excepthook = _crash_log
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion("1.0.0")
    window = MainWindow(resource_root(), data_root())
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
