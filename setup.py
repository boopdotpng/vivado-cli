from setuptools import setup 

setup(
  name='viv',
  version="0.1",
  packages=["viv"],
  entry_points={
    'console_scripts': ['viv=viv.cli:cli_main']
  }
)