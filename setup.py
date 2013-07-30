import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
CHANGES = open(os.path.join(here, 'CHANGES.rst')).read()

requires = [
    'Pillow',
    'SQLAlchemy',
    'WebTest',
    'jsonschema',
    'loremipsum',
    'passlib',
    'pyramid',
    'pyramid_multiauth',
    'pyramid_tm',
    'rfc3987',
    'setuptools',
    'strict_rfc3339',
    'xlrd',
    'xlutils',
    'zope.sqlalchemy',
    'PyBrowserID',
    ]

tests_require = [
    'behave',
    'behaving',
    'pytest',
]

setup(
    name='encoded',
    version='0.1',
    description='Metadata database for ENCODE',
    long_description=README + '\n\n' + CHANGES,
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    author='Laurence Rowe',
    author_email='lrowe@stanford.edu',
    url='http://encode-dcc.org',
    license='MIT',
    install_requires=requires,
    tests_require=tests_require,
    extras_require={
        'test': tests_require,
        },
    entry_points='''
        [console_scripts]
        extract_test_data = encoded.commands.extract_test_data:main

        [paste.app_factory]
        main = encoded:main
        ''',
    )
