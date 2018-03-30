import os

from codecs import open
from setuptools import setup, find_packages


ROOT_DIR = os.path.abspath(os.path.dirname(__file__))


with open(os.path.join(ROOT_DIR, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


def read_requirements(filename):
    def is_pkg(line):
        return line and not line.startswith(('--', 'git', '#'))

    with open(os.path.join(ROOT_DIR, filename), encoding='utf-8') as f:
        return [line for line in f.read().splitlines() if is_pkg(line)]


setup(
    name='Flask Controller Bundle',
    version='0.1.0',
    description='Adds class-based views and declarative routing to Flask Unchained',
    long_description=long_description,
    url='https://github.com/briancappello/flask-controller-bundle',
    author='Brian Cappello',
    license='MIT',

    # https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
    packages=find_packages(exclude=['tests']),
    install_requires=read_requirements('requirements.txt'),
    python_requires='>=3.6',
    extras_require={
        'test': ['blinker', 'coverage', 'pytest', 'pytest-flask'],
    },
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'pytest11': [
            'flask_controller_bundle = flask_controller_bundle.pytest',
        ],
    },
)
