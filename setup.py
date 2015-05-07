import os
import sys
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
CHANGES = open(os.path.join(here, 'CHANGES.rst')).read()

requires = [
    'Pillow',
    'PyBrowserID',
    'SQLAlchemy>=1.0.0b1',
    'WSGIProxy2',
    'WebTest',
    'boto',
    'elasticsearch',
    'future',
    'humanfriendly',
    'jsonschema',
    'loremipsum',
    'passlib',
    'psutil',
    'pyramid',
    'pyramid_localroles',
    'pyramid_multiauth',
    'pyramid_tm',
    'python-magic',
    'pytz',
    'rdflib',
    'rdflib-jsonld',
    'rfc3987',
    'setuptools',
    'simplejson',
    'strict_rfc3339',
    'subprocess_middleware',
    'xlrd',
    'zope.sqlalchemy',
]

if sys.version_info.major == 2:
    requires.extend([
        'subprocess32',
    ])

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
        check-files = encoded.commands.check_files:main
        check-rendering = encoded.commands.check_rendering:main
        create-mapping = encoded.commands.create_mapping:main
        deploy = encoded.commands.deploy:main
        dev-servers = encoded.commands.dev_servers:main
        extract_test_data = encoded.commands.extract_test_data:main
        es-index-data = encoded.commands.es_index_data:main
        es-index-listener = encoded.commands.es_index_listener:main
        generate-ontology = encoded.commands.generate_ontology:main
        import-data = encoded.commands.import_data:main
        jsonld-rdf = encoded.commands.jsonld_rdf:main
        migrate-files-aws = encoded.commands.migrate_files_aws:main
        profile = encoded.commands.profile:main
        spreadsheet-to-json = encoded.commands.spreadsheet_to_json:main
        update-file-status = encoded.commands.update_file_status:main
        update-keys-links = encoded.commands.update_keys_links:main
        upgrade = encoded.commands.upgrade:main

        [paste.app_factory]
        main = encoded:main

        [paste.composite_factory]
        indexer = encoded.commands.es_index_listener:composite

        [paste.filter_app_factory]
        memlimit = encoded.memlimit:filter_app
        ''',
)
