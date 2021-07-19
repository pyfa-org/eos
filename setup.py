from setuptools import find_packages, setup

from eos import __version__

try:  # for pip >= 10
    from pip._internal.req import parse_requirements
except ImportError:  # for pip <= 9.0.3
    from pip.req import parse_requirements  # noqa


parsed_reqs = parse_requirements('requirements.txt', session=False)
try:
    install_requires = [str(ir.req) for ir in parsed_reqs]
except:
    install_requires = [str(ir.requirement) for ir in parsed_reqs]


setup(
    name='Eos',
    description='Eos is a fitting engine for EVE Online.',
    version=__version__,
    author='Pyfa Team',
    author_email='',
    url='https://github.com/pyfa-org/eos',
    packages=find_packages(exclude=['tests', 'tests.*']),
    install_requires=install_requires
)
