"""
diffy
=====

:copyright: (c) 2018 by Netflix, see AUTHORS for more
:license: Apache, see LICENSE for more details.
"""
import pip

import io
from distutils.core import setup

from setuptools import find_packages

if tuple(map(int, pip.__version__.split('.'))) >= (10, 0, 0):
    from pip._internal.download import PipSession
    from pip._internal.req import parse_requirements
else:
    from pip.download import PipSession
    from pip.req import parse_requirements


with io.open('README.rst', encoding='utf-8') as readme:
    long_description = readme.read()


def load_requirements(filename):
    with io.open(filename, encoding='utf-8') as reqfile:
        return [line.split()[0] for line in reqfile if not line.startswith(('#', '-'))]


def moto_broken():
    """Until https://github.com/spulec/moto/pull/1589 is resolved.

    Then we will no longer need to fork moto, roll our own release, and rely either on
    this hack, or the dependency_links declaration.
    """
    reqts = load_requirements('dev-requirements.txt')
    return reqts.append('moto==1.3.5')


# Populates __version__ without importing the package
__version__ = None
with io.open('diffy/_version.py', encoding='utf-8') as ver_file:
    exec(ver_file.read())  # nosec: config file safe
if not __version__:
    print('Could not find __version__ from diffy/_version.py')
    exit(1)


setup(
    name='diffy',
    version=__version__,
    author='Netflix',
    author_email='security@netflix.com',
    url='https://github.com/Netflix-Skunkworks/diffy',
    description='Forensic differentiator',
    long_description=long_description,
    packages=find_packages(exclude=['diffy.tests']),
    include_package_data=True,
    dependency_links=['git+https://github.com/forestmonster/moto.git@master#egg=moto-1.3.5'],
    install_requires=load_requirements('requirements.txt'),
    tests_require=['pytest'],
    extras_require={
        'dev': load_requirements('dev-requirements.txt'),
        'web': load_requirements('web-requirements.txt'),
    },
    entry_points={
      'console_scripts': [
          'diffy = diffy_cli.core:entry_point'
      ],
      'diffy.plugins': [
          'aws_persistence_s3 = diffy.plugins.diffy_aws.plugin:S3PersistencePlugin',
          'aws_collection_ssm = diffy.plugins.diffy_aws.plugin:SSMCollectionPlugin',
          'aws_target_auto_scaling_group = diffy.plugins.diffy_aws.plugin:AutoScalingTargetPlugin',
          'local_analysis_simple = diffy.plugins.diffy_local.plugin:SimpleAnalysisPlugin',
          'local_analysis_cluster = diffy.plugins.diffy_local.plugin:ClusterAnalysisPlugin',
          'local_persistence_file = diffy.plugins.diffy_local.plugin:FilePersistencePlugin',
          'local_payload_command = diffy.plugins.diffy_local.plugin:CommandPayloadPlugin',
          'local_shell_collection = diffy.plugins.diffy_local.plugin:LocalShellCollectionPlugin',
          'local_target = diffy.plugins.diffy_local.plugin:LocalTargetPlugin',
          'osquery_payload = diffy.plugins.diffy_osquery.plugin:OSQueryPayloadPlugin'
      ]
    },
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'Topic :: Software Development',
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Natural Language :: English",
        "License :: OSI Approved :: Apache Software License"
    ],
    python_requires='>=3.6'
)
