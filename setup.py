from setuptools import setup, find_packages

setup(
    name="docker-manager",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "PyQt5",
        "docker",
    ],
    entry_points={
        'console_scripts': [
            'docker-manager=main:main',
        ],
    },
)
