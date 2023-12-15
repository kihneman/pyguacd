from setuptools import setup, find_packages

setup(
    name='pyguacd',
    version='0.9.0',
    description='Keeper Guacamole Server Python SDK',
    long_description='Python SDK for Keeper Guacamole Server',
    author='Keeper Security',
    author_email='ops@keepersecurity.com',
    packages=find_packages(),
    install_requires=[],
    entry_points={
        'console_scripts': [
            'pyguacd=pyguacd.__main__:main'
        ]
    }
)
