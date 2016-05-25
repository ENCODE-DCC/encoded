"""\
Move attachment blobs to S3.
This is provided as an example upgrade script, it was used by the ENCODE project to migrate
attachment BLOBs from postgres to s3
"""
import copy
import logging
import transaction
from hashlib import md5
from pyramid.paster import get_app
from pyramid.threadlocal import manager
from pyramid.testing import DummyRequest
from snovault.interfaces import (
    BLOBS,
    DBSESSION
)
from snovault.storage import (
    PropertySheet,
    RDBBlobStorage,
)

EPILOG = __doc__

logger = logging.getLogger(__name__)


def run(app):
    root = app.root_factory(app)
    dummy_request = DummyRequest(root=root, registry=app.registry, _stats={})
    manager.push({'request': dummy_request, 'registry': app.registry})
    session = app.registry[DBSESSION]()
    blob_storage = app.registry[BLOBS]
    rdb_blobs = RDBBlobStorage(app.registry[DBSESSION])

    for sheet in session.query(PropertySheet).filter(PropertySheet.name == 'downloads'):
        # Copy the properties so sqlalchemy realizes it changed after it's mutated
        properties = copy.deepcopy(sheet.properties)
        download_meta = properties['attachment']
        if 'bucket' not in download_meta:
            # Re-writing the blob while the S3BlobStorage is in use
            # will move it to S3.
            data = rdb_blobs.get_blob(download_meta)
            blob_id = download_meta.pop('blob_id')
            download_meta['md5sum'] = md5(data).hexdigest()
            blob_storage.store_blob(data, download_meta, blob_id=blob_id)
            sheet.properties = properties
            logger.info('Updated %s' % sheet.sid)


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Move attachment blobs to S3", epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('--app-name', help="Pyramid app name in configfile")
    parser.add_argument('--abort', action='store_true', help="Rollback transaction")
    parser.add_argument('config_uri', help="path to configfile")
    args = parser.parse_args()

    logging.basicConfig()
    app = get_app(args.config_uri, args.app_name)
    # Loading app will have configured from config file. Reconfigure here:
    logging.getLogger('snovault').setLevel(logging.DEBUG)

    raised = False
    try:
        run(app)
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
