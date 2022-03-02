import warnings

from setuptools import config, find_packages, setup

try:
    from dunamai import Version
except (ModuleNotFoundError, ImportError):
    raise ModuleNotFoundError('pakcage "dunamai" not found')

try:
    __version__ = Version.from_any_vcs().serialize()
except RuntimeError as error:
    warnings.warn(f'{error.__class__.__name__} - {error}')
    __version__ = '0.0.0'

with open("pyproject.toml", "r") as toml_file:
    requirements = toml.load(toml_file)

setup(
    **requirements['project'],
    version=__version__,
    packages=find_packages(),
    install_requires=list(requirements['dependencies']),
    extras_require=requirements['tool']['poetry']['extras'],
)
