from setuptools import setup
import setuptools

import sentify

with open('sentify/requirements.txt') as f:
    required = f.read().splitlines()
with open("README.md", "r") as f:
    long_description = f.read()

version = sentify.__version__
setup(name='sentify',
      version=version,
      description="Converter from urls,pdfs,wikipages to clean text document one sentence per line.",
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='https://github.com/ptarau/sentify.git',
      author='Paul Tarau',
      author_email='ptarau@gmail.com',
      license='MIT',
      packages=setuptools.find_packages(),
      package_data={
          'sentify': [
            '*.txt'
          ]
      },
      include_package_data=True,
      install_requires=required,
      zip_safe=False
      )
