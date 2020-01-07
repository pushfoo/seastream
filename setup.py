from setuptools import setup
from setuptools import find_packages

with open("README.md", "r") as f:
    readme = f.read()

setup(
    name='seastream',
    version='0.0.1',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    license='BSD 2-Clause',
    author="pushfoo",
    url="https://github.com/pushfoo/seastream",
    description='Smoother reading and writing of types with binary streams',
    long_description=readme,
    content_type="text/markdown",
    tests_require=["pytest"],
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'License :: OSI Approved',
    ],
    keywords='binary struct stream read write'
)
