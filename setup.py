#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages


tests_require = [
]

install_requires = [
    'sentry>=5.4.1',
    'requests>=1.2.0',
]

setup(
    name='sentry-xmpp',
    version='0.1.3',
    author='Viktor Stískala',
    author_email='viktor@stiskala.cz',
    description='A Sentry extension which integrates with XMPP™',
    long_description=__doc__,
    license='BSD',
    packages=find_packages(exclude=['tests']),
    zip_safe=False,
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require={'test': tests_require},
    test_suite='nose.collector',
    entry_points={
        'sentry.plugins': [
            'xmpp = sentry_xmpp.plugin:XMPPSender'
        ],
    },
    include_package_data=True,
    classifiers=[
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'Topic :: Software Development'
    ],
)
