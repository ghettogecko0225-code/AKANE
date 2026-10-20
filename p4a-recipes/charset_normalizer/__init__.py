"""Install charset-normalizer from its pure-Python wheel.

requests depends on charset-normalizer, and charset-normalizer publishes
Android wheels. p4a hands those URLs to the host pip, which refuses to
install a wheel tagged for a platform it does not recognise
("not a supported wheel on this platform"). The pure-Python wheel works
identically on Android, so we install that one instead.
"""
import json
import urllib.request
import zipfile
from os.path import basename, exists, join

from pythonforandroid.logger import info
from pythonforandroid.recipe import Recipe
from pythonforandroid.util import BuildInterruptingException

PYPI_JSON = "https://pypi.org/pypi/{package}/json"


class CharsetNormalizerRecipe(Recipe):
    version = "3.5.2"
    site_packages_name = "charset_normalizer"
    depends = []
    python_depends = []
    call_hostpython_via_targetpython = False

    def _pure_python_wheel(self):
        with urllib.request.urlopen(
            PYPI_JSON.format(package="charset-normalizer"), timeout=60
        ) as response:
            data = json.loads(response.read().decode("utf-8"))
        releases = data["releases"].get(self.version, [])
        for release in releases:
            if release["filename"].endswith("-py3-none-any.whl"):
                return release["filename"], release["url"]
        available = [r["filename"] for r in releases]
        raise BuildInterruptingException(
            f"No pure-Python charset-normalizer wheel found. Available: {available}"
        )

    def build_arch(self, arch):
        install_dir = self.ctx.get_python_install_dir(arch.arch)
        filename, url = self._pure_python_wheel()
        info(f"Installing {filename}")
        wheel_path = join(self.ctx.packages_path, filename)
        if not exists(wheel_path):
            urllib.request.urlretrieve(url, wheel_path)
        info(f"Unpacking {basename(wheel_path)} into site-packages")
        with zipfile.ZipFile(wheel_path) as archive:
            archive.extractall(install_dir)


recipe = CharsetNormalizerRecipe()
