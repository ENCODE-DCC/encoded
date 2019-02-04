import React from 'react';
import PropTypes from 'prop-types';
import * as globals from './globals';
import { Breadcrumbs } from './navigation';
import { DbxrefList } from './dbxref';
import { RelatedItems } from './item';
import { DisplayAsJson } from './objectutils';
import { ExperimentTable } from './typeutils';


/* eslint-disable react/prefer-stateless-function */
class Target extends React.Component {
    render() {
        let geneIDs = [];
        const context = this.props.context;
        const itemClass = globals.itemClass(context, 'view-detail key-value');
        const source = context.organism ? context.organism.scientific_name : context.investigated_as[0];

        if (context.genes) {
            geneIDs = context.genes.map(gene => `GeneID:${gene.geneid}`);
        }

        // Set up breadcrumbs
        const assayTargets = context.investigated_as.map(assayTarget => `investigated_as=${assayTarget}`);
        const crumbs = [
            { id: 'Targets' },
            { id: context.investigated_as.join(' + '), query: assayTargets.join('&'), tip: context.investigated_as.join(' + ') },
        ];
        if (context.organism) {
            crumbs.push({
                id: <i>{source}</i>,
                query: `organism.scientific_name=${source}`,
                tip: `${context.investigated_as.join(' + ')} and ${source}`,
            });
        }

        const crumbsReleased = (context.status === 'released');

        return (
            <div className={globals.itemClass(context, 'view-item')}>
                <header className="row">
                    <div className="col-sm-12">
                        <Breadcrumbs root="/search/?type=target" crumbs={crumbs} crumbsReleased={crumbsReleased} />
                        <h2>{context.label} (<em>{source}</em>)</h2>
                        <DisplayAsJson />
                    </div>
                </header>

                <div className="panel">
                    <dl className={itemClass}>
                        <div data-test="name">
                            <dt>Target name</dt>
                            <dd>{context.label}</dd>
                        </div>

                        {geneIDs.length > 0 ?
                            <div data-test="gene">
                                <dt>Target gene</dt>
                                <dd>
                                    <DbxrefList context={context} dbxrefs={geneIDs} />
                                </dd>
                            </div>
                        : null}

                        <div data-test="external">
                            <dt>External resources</dt>
                            <dd>
                                {context.dbxref.length ?
                                    <DbxrefList context={context} dbxrefs={context.dbxref} />
                                : <em>None submitted</em> }
                            </dd>
                        </div>
                    </dl>
                </div>

                <RelatedItems
                    title={`Experiments using target ${context.label}`}
                    url={`/search/?type=Experiment&target.uuid=${context.uuid}`}
                    Component={ExperimentTable}
                />
            </div>
        );
    }
}
/* eslint-enable react/prefer-stateless-function */

Target.propTypes = {
    context: PropTypes.object, // Target object to display
};

Target.defaultProps = {
    context: null,
};


globals.contentViews.register(Target, 'Target');
