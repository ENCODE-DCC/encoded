import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
CHANGES = open(os.path.join(here, 'CHANGES.rst')).read()

requires = [
    'Pillow',
    'PyBrowserID',
    'SQLAlchemy',
    'WSGIProxy2',
    'WebTest',
    'boto',
    'elasticsearch',
    'jsonschema',
    'loremipsum',
    'passlib',
    'pyramid',
    'pyramid_multiauth',
    'pyramid_tm',
    'python-magic',
    'pytz',
    'rdflib',
    'rfc3987',
    'setuptools',
    'simplejson',
    'strict_rfc3339',
    'subprocess_middleware',
    'xlrd',
    'zope.sqlalchemy',
]

tests_require = [
    'behave',
    'behaving',
    'pytest>=2.4.0',
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

        add-date-created = encoded.commands.add_date_created:main
        check-rendering = encoded.commands.check_rendering:main
        deploy = encoded.commands.deploy:main
        dev-servers = encoded.commands.dev_servers:main
        extract_test_data = encoded.commands.extract_test_data:main
        es-index-data = encoded.commands.es_index_data:main
        es-index-listener = encoded.commands.es_index_listener:main
        create-mapping = encoded.commands.create_mapping:main
        generate-ontology = encoded.commands.generate_ontology:main
        import-data = encoded.commands.import_data:main
        migrate-files-aws = encoded.commands.migrate_files_aws:main
        spreadsheet-to-json = encoded.commands.spreadsheet_to_json:main
        update-keys-links = encoded.commands.update_keys_links:main
        upgrade = encoded.commands.upgrade:main



        [paste.app_factory]
        main = encoded:main

        [paste.composite_factory]
        indexer = encoded.commands.es_index_listener:composite
        ''',
)
