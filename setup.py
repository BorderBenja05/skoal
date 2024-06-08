from setuptools import setup, find_packages

setup(
    name='Skoal',
    version='0.403',
    packages=find_packages(),
    scripts=['scripts/skoal.py'],
    entry_points={
        'console_scripts': [
            'skoal=skoal.main:main',
        ],
    },
    install_requires=[
        'numpy>=1.26.4',
        'scikit-learn>=1.4.2',
        'astropy>=6.0.1',
        'astropy-healpix>=1.0.3',
        'astroplan>=0.10',
        'scipy>=1.13.0',
        'argparse',
        'configparser>=7.0.0',
        'requests>=2.31.0',
        'ligo-gracedb>=2.12.0',
        'lxml>=5.2.1',
        'urllib3>=2.2.1',
    ],
    author='Benny Border',
    author_email='borderbenja@gmail.com',
    description='a kilonova followup scheduling package for fermi and lvc notices',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/borderbenja05/skoal',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
