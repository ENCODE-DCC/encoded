"""\
Update files with AWS metadata

"""
import json
import logging
import transaction
from pyramid.paster import get_app
from pyramid.threadlocal import manager
from pyramid.testing import DummyRequest

EPILOG = __doc__

logger = logging.getLogger(__name__)


def run(app, files):
    root = app.root_factory(app)
    collection = root['file']
    dummy_request = DummyRequest(root=root, registry=app.registry, _stats={})
    manager.push({'request': dummy_request, 'registry': app.registry})
    for i, uuid in enumerate(collection):
        item = root.get_by_uuid(uuid)
        dummy_request.context = item
        properties = item.upgrade_properties(finalize=True)
        sheets = None
        value = files.get(str(uuid))
        if value is not None:
            properties['file_size'] = value['file_size']
            sheets = {
                'external': {
                    'service': 's3',
                    'bucket': 'encode-files',
                    'key': value['s3_file_name'],
                },
            }
        item.update(properties, sheets=sheets)
        if (i + 1) % 100 == 0:
            logger.info('Updated %d', i + 1)


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Migrate files to AWS", epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('--app-name', help="Pyramid app name in configfile")
    parser.add_argument('--abort', action='store_true', help="Rollback transaction")
    parser.add_argument('files_processed', type=argparse.FileType('rb'), help="path to json file")
    parser.add_argument('config_uri', help="path to configfile")
    args = parser.parse_args()

    logging.basicConfig()
    app = get_app(args.config_uri, args.app_name)
    # Loading app will have configured from config file. Reconfigure here:
    logging.getLogger('encoded').setLevel(logging.DEBUG)

    files_processed = json.load(args.files_processed)
    good_files = {v['uuid']: v for v in files_processed
        if 'errors' not in v and 'blacklisted' not in v}

    raised = False
    try:
        run(app, good_files)
    except:
        raised = True
        raise
    finally:
        if raised or args.abort:
            transaction.abort()
            logger.info('Rolled back.')
        else:
            transaction.commit()


if __name__ == '__main__':
    main()
