from distutils.core import setup
from setuptools import find_packages

from siteuser import VERSION


setup(
    name='django-siteuser',
    version = VERSION,
    license = 'BSD',
    description = 'A Django APP for Universal Maintain Accounts',
    long_description = open('README.txt').read(),
    author = 'Wang Chao',
    author_email = 'yueyoum@gmail.com',
    url = 'https://github.com/yueyoum/django-siteuser',
    keywords = 'django, account, login, register, social, avatar',
    packages = find_packages(exclude=('example',)),
    classifiers = [
        'Development Status :: 4 - Beta',
        'Topic :: Internet',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
)

