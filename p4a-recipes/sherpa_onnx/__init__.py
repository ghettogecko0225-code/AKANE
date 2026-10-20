"""Install sherpa-onnx from its prebuilt Android wheels.

p4a's generic "install with pip" path cannot install wheels that are
tagged for Android (pip on the build host does not recognise the
android_* platform tag), so we fetch the matching wheels ourselves and
unpack them straight into the target's site-packages.

Wheels used:
  sherpa_onnx-1.13.8-cp314-cp314-android_24_arm64_v8a.whl
  sherpa_onnx_core-1.13.8-py3-none-android_24_arm64_v8a.whl
"""
import json
import urllib.request
import zipfile
from os.path import basename, exists, join

from pythonforandroid.logger import info
from pythonforandroid.recipe import Recipe
from pythonforandroid.util import BuildInterruptingException, ensure_dir

PYPI_JSON = "https://pypi.org/pypi/{package}/json"

ARCH_TAGS = {
    "arm64-v8a": "arm64_v8a",
    "armeabi-v7a": "armeabi_v7a",
    "x86_64": "x86_64",
    "x86": "x86",
}


class SherpaOnnxRecipe(Recipe):
    version = "1.13.8"
    site_packages_name = "sherpa_onnx"
    depends = []
    python_depends = []
    call_hostpython_via_targetpython = False

    def _wheel_name(self, package, arch, python_tag, abi_tag):
        tag = ARCH_TAGS.get(arch.arch)
        if tag is None:
            supported = ", ".join(sorted(ARCH_TAGS))
            raise BuildInterruptingException(
                f"sherpa-onnx has no Android wheel for {arch.arch}. "
                f"Supported ABIs: {supported}"
            )
        with urllib.request.urlopen(
            PYPI_JSON.format(package=package), timeout=60
        ) as response:
            data = json.loads(response.read().decode("utf-8"))
        releases = data["releases"].get(self.version, [])
        wanted = (
            f"{package}-{self.version}-{python_tag}-{abi_tag}"
            f"-android_24_{tag}.whl"
        )
        for release in releases:
            if release["filename"] == wanted:
                return release["filename"], release["url"]
        available = [r["filename"] for r in releases if "android_24" in r["filename"]]
        raise BuildInterruptingException(
            f"No matching {package} wheel for {arch.arch}. Available: {available}"
        )

    def build_arch(self, arch):
        install_dir = self.ctx.get_python_install_dir(arch.arch)
        ensure_dir(install_dir)
        for package, python_tag, abi_tag in (
            ("sherpa_onnx", "cp314", "cp314"),
            ("sherpa_onnx_core", "py3", "none"),
        ):
            filename, url = self._wheel_name(package, arch, python_tag, abi_tag)
            info(f"Installing {filename}")
            wheel_path = join(self.ctx.packages_path, filename)
            if not exists(wheel_path):
                urllib.request.urlretrieve(url, wheel_path)
            info(f"Unpacking {basename(wheel_path)} into site-packages")
            with zipfile.ZipFile(wheel_path) as archive:
                archive.extractall(install_dir)


recipe = SherpaOnnxRecipe()
