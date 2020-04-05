import React from 'react';
import PropTypes from 'prop-types';
import { Panel, PanelBody } from '../libs/ui/panel';
import * as globals from './globals';
import { Breadcrumbs } from './navigation';
import { DbxrefList } from './dbxref';
import { RelatedItems } from './item';
import { ItemAccessories } from './objectutils';
import { ExperimentTable } from './typeutils';


const Target = ({ context }) => {
    let geneIDs = [];
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
            <header>
                <Breadcrumbs root="/search/?type=Target" crumbs={crumbs} crumbsReleased={crumbsReleased} />
                <h2>{context.label} (<em>{source}</em>)</h2>
                <ItemAccessories item={context} />
            </header>

            <Panel>
                <PanelBody>
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
                                {context.dbxref.length > 0 ?
                                    <DbxrefList context={context} dbxrefs={context.dbxref} />
                                : <em>None submitted</em> }
                            </dd>
                        </div>
                    </dl>
                </PanelBody>
            </Panel>

            <RelatedItems
                title={`Experiments using target ${context.label}`}
                url={`/search/?type=Experiment&target.uuid=${context.uuid}`}
                Component={ExperimentTable}
            />
        </div>
    );
};

Target.propTypes = {
    context: PropTypes.object, // Target object to display
};

Target.defaultProps = {
    context: null,
};


globals.contentViews.register(Target, 'Target');
