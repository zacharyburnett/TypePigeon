import warnings

from setuptools import config, find_packages, setup

try:
    from dunamai import Version
except (ModuleNotFoundError, ImportError):
    raise ModuleNotFoundError('pakcage "dunamai" not found')

try:
    version = Version.from_any_vcs().serialize()
except RuntimeError as error:
    warnings.warn(f'{error.__class__.__name__} - {error}')
    version = '0.0.0'

metadata = config.read_configuration('setup.cfg')['metadata']

setup(
    **metadata,
    version=version,
    packages=find_packages(),
    python_requires='>=3.6',
    setup_requires=['dunamai', 'setuptools>=41.2'],
    install_requires=['pyproj', 'python-dateutil', 'shapely'],
    extras_require={
        'testing': ['pytest', 'pytest-cov', 'pytest-xdist', 'wget'],
        'development': ['flake8', 'isort', 'oitnb'],
        'documentation': ['m2r2', 'sphinx', 'sphinx-rtd-theme'],
    },
)
