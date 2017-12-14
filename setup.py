from setuptools import setup, find_packages


with open('README.md', encoding='utf-8') as f:
    long_description = f.read()


def read_requirements(filename):
    def is_pkg(line):
        return line and not line.startswith(('--', 'git', '#'))

    with open(filename, encoding='utf-8') as f:
        return [line for line in f.read().splitlines() if is_pkg(line)]


setup(
    name='Flask Controller Bundle',
    version='0.1.0',
    description='Adds declarative routing and (better) controller classes to Flask',
    long_description=long_description,
    url='https://github.com/briancappello/flask-controller-bundle',
    author='Brian Cappello',
    license='MIT',

    # https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
    packages=find_packages(include=['flask_controller_bundle']),
    install_requires=read_requirements('requirements.txt'),
    include_package_data=True,
    zip_safe=True,
)
