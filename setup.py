from setuptools import setup, find_packages
import platform
import os

# Pull version from source without importing
# since we can't import something we haven't built yet :)
exec (open('noorm/version.py').read())

readme = 'README.md'
if os.path.exists('README.rst'):
    readme = 'README.rst'
with open(readme, 'rb') as f:
    long_description = f.read().decode('utf-8')

requires = [
]

test_requires = [
]

setup(name='noorm',
      version=__version__,
      description='Easy pythonic access to SQLite Databases. (Not an ORM)',
      long_description=long_description,
      classifiers=[
          'Development Status :: 4 - Beta',
          'License :: OSI Approved :: Apache Software License',
          'Topic :: Utilities',
          "Programming Language :: Python",
          "Programming Language :: Python :: 2",
          "Programming Language :: Python :: 2.7",
      ],
      keywords='NoORM sqlite3',
      url='http://github.com/phoglx/noorm',
      author='Benjamin Borchert',
      author_email='benjamin.borchert@gmail.com',
      license='Apache',
      packages=find_packages(),
      install_requires=requires,
      tests_require=test_requires,
      include_package_data=True,
      zip_safe=False)
