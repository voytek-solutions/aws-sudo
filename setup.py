from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
if path.exists('README.txt'):
    with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
        long_description = f.read()
else:
    long_description = ""

setup(
    name='aws-sudo',
    version='1.0.2',

    description='sudo but with AWS accounts',
    long_description=long_description,

    url='https://github.com/voytek-solutions/aws-sudo',

    author='Wojtek Oledzki',
    author_email='contact@voytek.solutions',

    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
    ],

    # What does your project relate to?
    keywords=['aws', 'infrastructure', 'ansible', 'terraform', 'packer'],

    packages=find_packages(exclude=['contrib', 'docs', 'tests']),

    install_requires=[
        'boto3<1.4.4', # boto3 >= 1.4.4 requires botocore 1.5
        'botocore==1.4.*',
        'docutils==0.12.*',
        'jmespath==0.9.*',
        'python-dateutil==2.5.*',
        's3transfer==0.1.*',
        'six==1.10.*',
    ],

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={
        'console_scripts': [
            'aws-sudo=aws_sudo:main',
        ],
    },
)
