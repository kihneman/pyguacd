from setuptools import setup, find_packages

setup(
    name='guacd',
    version='0.9.0',
    description='Keeper Guacamole Server Python SDK',
    long_description='Python launcher for Keeper Guacamole Server',
    author='Keeper Security',
    author_email='ops@keepersecurity.com',
    packages=find_packages(exclude=['cython']),
    install_requires=[],
    entry_points={
        'console_scripts': [
            'guacd=guacd.daemon:main'
        ]
    }
)
