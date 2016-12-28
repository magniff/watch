import setuptools


classifiers = [
    (
        'Programming Language :: Python :: %s' % x
    )
    for x in '3.1 3.2 3.3 3.4 3.5'.split()
]


setuptools.setup(
    name='watch',
    description='Attribute controlling microframework.',
    version='0.1.13',
    license='MIT license',
    platforms=['unix', 'linux', 'osx', 'win32'],
    author='magniff',
    url='https://github.com/magniff/watch',
    classifiers=classifiers,
    packages=['watch'],
    zip_safe=False,
)
