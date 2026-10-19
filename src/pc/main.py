import sys
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
from pc.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Japanese Sensei AI")
    app.setApplicationVersion("0.1.0")
    window = MainWindow(ROOT)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
