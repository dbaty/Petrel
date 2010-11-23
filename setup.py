import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'pyramid',
    'repoze.catalog',
    'repoze.folder',
    'repoze.tm',
    'repoze.zodbconn',
    'wtforms',
    'ZODB3',
    ]

test_requires = requires + [
    'nose',
    'coverage',
    ]

setup(name='Petrel',
      version='0.0',
      description='Petrel',
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
        ## FIXME
        "Programming Language :: Python",
        "Framework :: BFG",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='',
      author_email='',
      url='',
      keywords='web wsgi lightweight cms',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      tests_require=requires,
      test_suite="petrel.tests",
      entry_points="""\
      [paste.app_factory]
      app = petrel.run:app
      [paste.filter_app_factory]
      authoringmode = petrel.authoringmode:make_middleware
      """
      )

