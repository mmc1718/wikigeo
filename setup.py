import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='wikigeo',
    version='0.0.1',
    description='Supplementing geographic data with data on points of interest from wikipedia',
    long_description=long_description,
    packages=setuptools.find_packages(),
    author='Mary McGuire',
    author_email='marymcguire1718@gmail.com',
    install_requires=["requests_html",
    "googletrans", "fuzzywuzzy", "python-Levenshtein-wheels"],
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Operating System :: OS Independent"
    ],
    url='https://github.com/mmc1718/wikigeo'
)