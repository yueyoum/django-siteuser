from setuptools import setup, find_packages

from siteuser import VERSION

install_requires = [
    'socialoauth',
    'django-celery',
]

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
    install_requires = install_requires,
    include_package_data = True,
    classifiers = [
        'Development Status :: 4 - Beta',
        'Topic :: Internet',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
)
