from setuptools import setup 

setup(
  name='viv',
  version="0.1",
  description="minimal vivado project cli",
  long_description=open("README.md").read(),
  author="Anuraag Warudkar",
  author_email="anuraag.warudkar@gmail.com",
  url="https://github.com/boopdotpng/vivado-cli",
  license="MIT",
  packages=["viv"],
  install_requires=[
    "tomlkit",
  ],
  entry_points={
    'console_scripts': ['viv=viv.cli:cli_main']
  },
  python_requires='>=3.11'
)