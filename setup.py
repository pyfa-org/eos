

from pip.req import parse_requirements
from setuptools import setup, find_packages
from eos import __version__


parsed_reqs = parse_requirements('requirements.txt', session=False)
install_requires = [str(ir.req) for ir in parsed_reqs]


setup(
    name='Eos',
    description='Eos is a fitting engine for for EVE Online.',
    version=__version__,
    author='Pyfa Team',
    author_email='',
    url='https://github.com/pyfa-org/eos',
    packages=find_packages(exclude='tests'),
    install_requires=install_requires,
)
