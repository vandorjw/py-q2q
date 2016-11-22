# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    project_license = f.read()

setup(
    name='q2q',
    version='0.0.1',
    description='Place messages from Postgres Queue on RabbitMQ',
    long_description=readme,
    author='Joost Van Dorp',
    author_email='joostvandorp@gmail.com',
    url='https://github.com/vandorjw/py-q2q',
    license=project_license,
    packages=find_packages(exclude=('tests', 'docs'))
)
