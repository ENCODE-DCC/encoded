#!/bin/bash

if [ "$ENCD_REMOTE_INDEXING" == 'true' ]; then
    if [ "$ENCD_INDEX_PRIMARY" == 'true' ]; then
        a2ensite 111-indexer-primary.conf
    fi
    if [ "$ENCD_INDEX_VIS" == 'true' ]; then
        a2ensite 222-indexer-vis.conf
    fi
    if [ "$ENCD_INDEX_REGION" == 'true' ]; then
        a2ensite 333-indexer-region.conf
    fi
fi

systemctl reload apache2
