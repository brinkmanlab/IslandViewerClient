from distutils.core import setup

from setuptools import find_packages

classifiers = """
Development Status :: 4 - Beta
Environment :: Console
License :: OSI Approved :: MIT License
Intended Audience :: Science/Research
Topic :: Scientific/Engineering
Topic :: Scientific/Engineering :: Bio-Informatics
Programming Language :: Python :: 2.7
Programming Language :: Python :: 3.6
Operating System :: POSIX :: Linux
""".strip().split('\n')

setup(name='IslandViewerClient',
      version='0.0.0',
      description='',
      author='Geoff Winsor',
      author_email='',
      url='https://github.com/glwinsor/IslandViewerClient',
      license='MIT',
      classifiers=classifiers,
      install_requires=[
          'requests',
          'requests-toolbelt'
      ],
      test_suite='nose.collector',
      tests_require=['nose'],
      packages=find_packages(),
      include_package_data=True,
      scripts=['ivclient.py']
)
