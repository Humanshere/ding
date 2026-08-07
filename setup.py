from setuptools import setup

setup(
    name="ding",
    version="1.0",
    py_modules=["ding", "data"],
    entry_points={
        "console_scripts": [
            "ding=ding:main",
        ],
    },
)