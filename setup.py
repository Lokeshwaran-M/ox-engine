import os
from setuptools import setup, find_packages

setup(
    name='ox-engine',
    version='0.0.1',
    description='prompt data processer engine',
    author='Lokeshwaran M',
    author_email='lokeshwaran.m23072003@gmail.com',
    url="https://github.com/ox-ai/ox-engine.git",
    license="MIT",
    packages=find_packages(),
    package_data={'': ['requirements.txt', 'README.md']},
    install_requires=open('requirements.txt').readlines(),
    keywords='ox-engine ox-ai',
)


