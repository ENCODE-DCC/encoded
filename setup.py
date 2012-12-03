from setuptools import setup, find_packages

setup(
    name='encodb',
    version='0.1',
    description='Metadata database for ENCODE',
    long_description=open('README.rst').read() + '\n\n' +
                     open('CHANGES.rst').read(),
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    author='Laurence Rowe',
    author_email='lrowe@stanford.edu',
    url='http://encode-dcc.org',
    license='MIT',
    install_requires=[
        'SQLAlchemy',
        'pyramid',
        'setuptools',
        ],
    extras_require={
        'test': [],
        },
    entry_points='''
        ''',
    )
