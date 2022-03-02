import subprocess
import sys

from setuptools import setup

try:
    import gartersnake
except (ImportError, ModuleNotFoundError):
    subprocess.run(f'{sys.executable} -m pip install gartersnake')
    import gartersnake

if 'toml' not in gartersnake.installed_packages():
    subprocess.run(f'{sys.executable} -m pip install toml')
import toml

with open("pyproject.toml", "r") as toml_file:
    requirements = toml.load(toml_file)

for package in requirements['build-system']['requires']:
    if package not in gartersnake.installed_packages():
        subprocess.run(f'{sys.executable} -m pip install {package}')

__version__ = gartersnake.vcs_version()

setup(
    **requirements['project'],
    version=__version__,
    install_requires=list(requirements['dependencies']),
    extras_require=requirements['tool']['poetry']['extras'],
)
