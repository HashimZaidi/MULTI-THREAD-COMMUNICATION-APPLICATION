from setuptools import setup

with open("requirements.txt", "r") as f:
    required = f.read().splitlines()
    setup(
        name="messaging-app",
        version="0.0.1",
        author="Muhammad Hashim",
        author_email="hashim.muhammad9@gmail.com",
        packages=["app"],
        install_requires=required,
        tests_require=[
            "mock==2.0.0",
        ],
        scripts=["bin/server", "bin/client"],
    )
