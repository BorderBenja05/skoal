from setuptools import setup, find_packages

setup(
    name='Skoal',
    version='0.421',
    packages=find_packages(),
    scripts=['skoal/main.py'],
    entry_points={
        'console_scripts': [
            'skoal=skoal.main:main',
        ],
    },
    package_data={
        # Include all files inside mypackage/data
        'skoal': ['data/**/*'],
    },
    install_requires=[
        'numpy',
        'scikit-learn',
        'astropy',
        'astropy-healpix',
        'astroplan',
        'scipy',
        'argparse',
        'configparser',
        'requests',
        'ligo-gracedb>=2.10.0',
        'lxml',
        'urllib3>=2.1.0',
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
