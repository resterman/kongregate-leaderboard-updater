import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "Kongregate Leaderboard Updater",
    version = "0.1",
    author = "resterman",
    author_email = "resterman@zoho.com",
    description = ("Updater for the kongregate leaderboard"),
    license = "BSD",
    keywords = "kongregate",
    packages=['updater'],
    long_description=read('README'),
    classifiers=[
        "Development Status :: 0 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
)
