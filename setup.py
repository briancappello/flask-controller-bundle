import os

from codecs import open
from setuptools import setup, find_packages


ROOT_DIR = os.path.abspath(os.path.dirname(__file__))


with open(os.path.join(ROOT_DIR, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='Flask Controller Bundle',
    version='0.2.1',
    description='Adds class-based views and declarative routing to Flask Unchained',
    long_description=long_description,
    url='https://github.com/briancappello/flask-controller-bundle',
    author='Brian Cappello',
    license='MIT',

    # https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Flask',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
    packages=find_packages(exclude=['docs', 'tests']),
    include_package_data=True,
    zip_safe=False,
    python_requires='>=3.6',
    install_requires=[
        'flask-unchained>=0.2.0',
    ],
    extras_require={
        'dev': [
            'blinker',
            'coverage',
            'pytest',
            'pytest-flask',
            'tox',
        ],
    },
    entry_points={
        'pytest11': [
            'flask_controller_bundle = flask_controller_bundle.pytest',
        ],
    },
)
