"""\
Migrate dataset type

"""
import logging
import transaction
from pyramid.paster import get_app
from snowfort.interfaces import (
    STORAGE,
)

EPILOG = __doc__

logger = logging.getLogger(__name__)


TYPE_MAP = {
    'project': 'project',
    'composite': 'ucsc_browser_composite',
    'publication': 'publication_data',
    'reference': 'reference',
    'paired set': 'matched_set',
    'annotation': 'annotation',
}


def run(app):
    storage = app.registry[STORAGE].write

    for rid in storage.__iter__('dataset'):
        model = storage.get_by_uuid(str(rid))
        dataset_type = model.properties['dataset_type']
        new_type = TYPE_MAP[dataset_type]
        model.item_type = new_type
        logger.info('Updated %s, %r -> %s', model.rid, dataset_type, new_type)


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Migrate dataset type", epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('--app-name', help="Pyramid app name in configfile")
    parser.add_argument('--abort', action='store_true', help="Rollback transaction")
    parser.add_argument('config_uri', help="path to configfile")
    args = parser.parse_args()

    logging.basicConfig()
    app = get_app(args.config_uri, args.app_name)
    # Loading app will have configured from config file. Reconfigure here:
    logging.getLogger('encoded').setLevel(logging.DEBUG)

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
