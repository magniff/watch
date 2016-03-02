from setuptools import setup


classifiers = [
    (
        'Programming Language :: Python :: %s' % x
    )
    for x in '3.3 3.4 3.5'.split()
]


setup(
    name='watch',
    description='Attribute controlling microframework.',
    version='0.1',
    license='MIT license',
    platforms=['unix', 'linux', 'osx', 'win32'],
    author='magniff',
    classifiers=classifiers,
    packages=['watch'],
)
