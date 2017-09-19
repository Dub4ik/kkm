# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import re
import os


version = re.search("VERSION.*'(.+)'", open(os.path.join('kkm', '__init__.py')).read()).group(1)
license_data = open('LICENSE', encoding='utf-8').read()
readme_data = open('README.rst', encoding='utf-8').read()

setup(
    name='kkm',
    version=version,
    packages=find_packages(),
    author='Marat Khayrullin, Eugene Kaltashkin',
    author_email='xmm.dev@gmail.com,aborche.aborche@gmail.com',
    description='библиотека для работы с контрольно-кассовыми машинами'
                ' (фискальными регистраторами)',
    license=license_data,
    keywords='фискальный, регистратор, контрольно, кассовая, машина, ккм',
    url='https://github.com/aborche/kkm/',
    long_description=readme_data,
    include_package_data=True,
    install_requires=['pyserial', ],
    scripts=[],
)
