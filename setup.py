from setuptools import setup, find_packages

setup(
    name='flemopt',
    version='0.1',
    packages=find_packages(),
    scripts=['scripts/flemopt.py'],
    entry_points={
        'console_scripts': [
            'flemopt=flemopt.main:main',
        ],
    },
    install_requires=[
        # Add any dependencies your package needs here
    ],
    author='Benny Border',
    author_email='borderbenja@gmail.com',
    description='A brief description of your package',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/borderbenja05/flemopt',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
