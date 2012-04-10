import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
CHANGES = open(os.path.join(here, 'CHANGES.rst')).read()

requires = [
    'pyramid',
    'pyramid_beaker',
    'repoze.catalog',
    'repoze.folder',
    'repoze.tm',
    'repoze.who',
    'repoze.whoplugins.zodb',
    'repoze.zodbconn',
    'wtforms',
    'ZODB3',
    ]

test_requires = requires + [
    'nose',
    'coverage',
    ]

# FIXME
setup(name='Petrel',
      version='0.1',
      description='Petrel',
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: BFG",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='',
      author_email='',
      url='https://github.com/dbaty/Petrel',
      keywords='web wsgi lightweight cms',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      tests_require=requires,
      test_suite="petrel.tests",
      )

