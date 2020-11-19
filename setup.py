import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()
CHANGES = open(os.path.join(here, 'CHANGES.rst')).read()
SNOVAULT_VERSION = "1.0.51"

INSTALL_REQUIRES = [
    "Jinja2==2.10.3",
    "MarkupSafe==1.1.1",
    "PasteDeploy==2.0.1",
    "PyYAML==5.3",
    "SPARQLWrapper==1.8.5",
    "SQLAlchemy==1.3.12",
    "Werkzeug==0.16.0",
    "WSGIProxy2==0.4.6",
    "attrs==19.3.0",
    "aws-sam-translator==1.19.1",
    "aws-xray-sdk==2.4.3",
    "boto3==1.11.9",
    "botocore==1.14.9",
    "certifi==2019.11.28",
    "cffi==1.13.2",
    "cfn-lint==0.26.2",
    "chardet==3.0.4",
    "collective.recipe.cmd==0.11",
    "collective.recipe.modwsgi==2.1",
    "collective.recipe.template==2.1",
    "coverage==5.0.2",
    "cryptography==2.8",
    "ecdsa==0.15",
    "elasticsearch==5.4.0",
    "hupper==1.9.1",
    "idna==2.8",
    "jsonpointer==2.0",
    "jsonschema-serialize-fork @ git+https://github.com/lrowe/jsonschema_serialize_fork.git@2.1.1",  # noqa
    "jsonschema==3.2.0",
    "parse-type==0.5.2",
    "pluggy==0.13.1",
    "psycopg2==2.8.4",
    "pyramid==1.10.4",
    "pyramid-localroles==0.1",
    "pyramid-multiauth==0.9.0",
    "pyramid-tm==2.4",
    "pyramid-translogger==0.1",
    "pyrsistent==0.15.7",
    "python-editor==1.0.4",
    "python-jose==3.1.0",
    "rdflib==4.2.2",
    "rdflib-jsonld==0.4.0",
    "redis==3.5.3",
    "repoze.debug==1.1",
    "responses==0.10.9",
    "rutter==0.2",
    "soupsieve==1.9.5",
    "snovault @ git+https://github.com/ENCODE-DCC/snovault.git@{}".format(SNOVAULT_VERSION),  # noqa
    "splinter==0.13.0",
    "sshpubkeys==3.1.0",
    "strict-rfc3339==0.7",
    "subprocess-middleware @ git+https://github.com/lrowe/subprocess_middleware.git@0.3",  # noqa
    "transaction==3.0.0",
    "translationstring==1.3",
    "venusian==3.0.0",
    "waitress==1.4.2",
    "websocket-client==0.57.0",
    "zc.buildout==2.13.2",
    "zipp==0.6.0",
    "zope.deprecation==4.4.0",
    "zope.interface==4.7.1",
    "zope.sqlalchemy==1.2",
]

EXTRAS_REQUIRE = {
    "tests": [
        "moto==1.3.14",
        "pytest==5.3.2",
        "pytest-bdd==3.2.1",
        "pytest-cov==2.8.1",
        "pytest-exact-fixtures==0.3",
        "pytest-instafail==0.4.1.post0",
        "pytest-mock==2.0.0",
        "pytest-splinter==2.0.1",
        "pytest-timeout==1.3.4",
        "redis-server==5.0.7",
        "WebTest==2.0.33",
    ],
}

EXTRAS_REQUIRE["dev"] = EXTRAS_REQUIRE["tests"]

setup(
    name='encoded',
    version='109.0',
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
    install_requires=INSTALL_REQUIRES,
    extras_require=EXTRAS_REQUIRE,
    entry_points='''
        [console_scripts]
        batchupgrade = snovault.batchupgrade:main
        create-mapping = snovault.elasticsearch.create_mapping:main
        dev-servers = snovault.dev_servers:main
        es-index-listener = snovault.elasticsearch.es_index_listener:main

        add-date-created = encoded.commands.add_date_created:main
        check-rendering = encoded.commands.check_rendering:main
        deploy = encoded.commands.deploy:main
        extract_test_data = encoded.commands.extract_test_data:main
        es-index-data = encoded.commands.es_index_data:main
        generate-ontology = encoded.commands.generate_ontology:main
        import-data = encoded.commands.import_data:main
        jsonld-rdf = encoded.commands.jsonld_rdf:main
        migrate-files-aws = encoded.commands.migrate_files_aws:main
        profile = encoded.commands.profile:main
        spreadsheet-to-json = encoded.commands.spreadsheet_to_json:main
        generate-annotations = encoded.commands.generate_annotations:main
        index-annotations = encoded.commands.index_annotations:main
        migrate-attachments-aws = encoded.commands.migrate_attachments_aws:main
        migrate-dataset-type = encoded.commands.migrate_dataset_type:main
        alembic = encoded.commands.alembic:main

        [paste.app_factory]
        main = encoded:main

        [paste.composite_factory]
        indexer = snovault.elasticsearch.es_index_listener:composite
        visindexer = snovault.elasticsearch.es_index_listener:composite
        regionindexer = snovault.elasticsearch.es_index_listener:composite

        [paste.filter_app_factory]
        memlimit = encoded.memlimit:filter_app
        ''',
)
