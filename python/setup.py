# ! important
# see https://stackoverflow.com/a/27868004/1497139
from setuptools import setup

# read the contents of your README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, '../README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='vertx-eventbus-python',
    version='3.8.5a5',

    packages=['Vertx',],
    author='Jayamine Alupotha',
    maintainer='Wolfgang Fahl',
    url='https://github.com/rc-dukes/vertx-eventbus-python',
    license='MIT License',
    description='vert.x tcp eventbus client for python',
    long_description=long_description,
    long_description_content_type='text/markdown'
)
