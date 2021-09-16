#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['Click>=7.0', 'cloudsigma>=1.0', 'PyYAML>=5.4.1' ]

test_requirements = ['pytest>=3', ]

setup(
    author="Matt Krueger",
    author_email='mkrueger@rstms.net',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="CloudSigma administration CLI",
    entry_points={
        'console_scripts': [
            'cscli=cscli.cli:cli',
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='cscli',
    name='cscli',
    packages=find_packages(include=['cscli', 'cscli.*']),
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/rstms/cscli',
    version='0.3.3',
    zip_safe=False,
)
