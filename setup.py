import pathlib
from setuptools import setup

HERE = pathlib.Path(__file__).parent

README = (HERE / 'README.md').read_text()

setup(
    name='suite8080',
    version='0.1.1',
    description='Suite of Intel 8080 Assembly tools',
    long_description=README,
    long_description_content_type='text/markdown',
    url='https://github.com/pamoroso/suite8080',
    author='Paolo Amoroso',
    author_email='info@paoloamoroso.com',
    license='MIT',
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
    ],
    packages=['suite8080'],
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'asm80=suite8080.asm80:main',
            'dis80=suite8080.dis80:main'
        ]
    }
)