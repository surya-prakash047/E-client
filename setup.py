from setuptools import setup, find_packages

setup(
    name='eclient',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'google-auth-oauthlib',
        'google-auth-httplib2',
        'google-api-python-client',
        'beautifulsoup4',
        'sqlalchemy'
    ],
    entry_points={
        'console_scripts': [
            'eclient=main:main',
        ],
    },
)