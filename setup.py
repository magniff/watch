import setuptools


with open("README.md") as readme_file:
    long_description = readme_file.read()


classifiers = [
    (
        "Programming Language :: Python :: %s" % x
    )
    for x in "3.1 3.2 3.3 3.4 3.5 3.6 3.7".split()
]


setuptools.setup(
    name="watch",
    description="A stupid monadic fields tracker.",
    long_description=long_description,
    long_description_content_type='text/markdown',
    version="0.2.4",
    license="MIT license",
    platforms=["unix", "linux", "osx", "win32"],
    author="magniff",
    url="https://github.com/magniff/watch",
    classifiers=classifiers,
    packages=[
        "watch",
    ],
    zip_safe=False,
)

