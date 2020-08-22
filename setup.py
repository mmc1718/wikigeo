import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='wikigeo',
    version='0.0.1',
    description='Getting point of interest data by geographic coordinates from Wikipedia',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    author='Mary McGuire',
    author_email='marymcguire1718@gmail.com',
    install_requires=["requests_html",
    "googletrans", "fuzzywuzzy", "python-Levenshtein-wheels"],
    extras_require={"pytest": "pytest==6.0.1", "tox": "tox==3.19.0"},
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.7",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content :: Wiki"
    ],
    url='https://github.com/mmc1718/wikigeo'
)