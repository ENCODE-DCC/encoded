import React from 'react';
import PropTypes from 'prop-types';
import * as globals from './globals';


const Collection = (props) => {
    const context = props.context;
    return (
        <div className={globals.itemClass(context, 'view-item')}>
            <header className="row">
                <div className="col-sm-12">
                    <h2>{context.title}</h2>
                </div>
            </header>
            <Panel>
            </Panel>
        </div>
    );
};

Collection.propTypes = {
    context: PropTypes.object.isRequired,
};

globals.contentViews.register(Collection, 'Collection');
