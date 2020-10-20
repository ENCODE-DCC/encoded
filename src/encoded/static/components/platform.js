import React from 'react';
import PropTypes from 'prop-types';
import * as globals from './globals';
import { DbxrefList } from './dbxref';
import { PanelBody } from '../libs/ui/panel';

const Platform = (props) => {
    const context = props.context;
    const itemClass = globals.itemClass(context, 'key-value');
    return (
        <PanelBody>
            <dl className={itemClass}>
                <div data-test="name">
                    <dt>Platform name</dt>
                    <dd><a href={context.url}>{context.title}</a></dd>
                </div>

                <div data-test="obiid">
                    <dt>OBI ID</dt>
                    <dd>{context.term_id}</dd>
                </div>

                <div data-test="externalresources">
                    <dt>External resources</dt>
                    <dd>
                        {context.dbxrefs.length > 0 ?
                            <DbxrefList context={context} dbxrefs={context.dbxrefs} />
                        : <em>None submitted</em> }
                    </dd>
                </div>
            </dl>
        </PanelBody>
    );
};

Platform.propTypes = {
    context: PropTypes.object.isRequired,
};

globals.panelViews.register(Platform, 'Platform');

// Need to export this for Jest tests.
export default Platform;
