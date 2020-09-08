from setuptools import setup

setup(
    name='roboto',
    version='0.1',
    py_modules=['roboto'],
    install_requires=[
        'Click',
    ],
    entry_points='''
        [console_scripts]
        roboto=roboto:cli
    ''',
)