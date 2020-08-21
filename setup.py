from setuptools import setup

setup(
    name='wikigeo',
    version='0.0.1',
    description='Supplementing geographic data with point of interests from wikipedia',
    package_dir={'': 'wikigeo'},
    author='Mary McGuire',
    author_email='marymcguire1718@gmail.com',
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Operating System :: OS Independent"
    ],
    url='https://github.com/mmc1718/wikigeo'
)