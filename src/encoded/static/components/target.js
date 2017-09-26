import React from 'react';
import PropTypes from 'prop-types';
import _ from 'underscore';
import * as globals from './globals';
import { Breadcrumbs } from './navigation';
import { ExperimentTable } from './dataset';
import { DbxrefList } from './dbxref';
import { RelatedItems } from './item';


class Target extends React.Component {
    render() {
        const context = this.props.context;
        const itemClass = globals.itemClass(context, 'view-detail key-value');
        let geneLink;
        let geneRef;
        let baseName;
        let sep;
        let base;

        if (context.organism.name === 'human') {
            geneLink = globals.dbxrefPrefixMap.HGNC + context.gene_name;
        } else if (context.organism.name === 'mouse') {
            const mgiRef = _(context.dbxref).find(ref => ref.substr(0, 4) === 'MGI:');
            if (mgiRef) {
                base = globals.dbxrefPrefixMap.MGI;
                geneLink = base + mgiRef;
            }
        } else if (context.organism.name === 'dmelanogaster' || context.organism.name === 'celegans') {
            const organismPrefix = context.organism.name === 'dmelanogaster' ? 'FBgn' : 'WBGene';
            const baseUrl = context.organism.name === 'dmelanogaster' ? globals.dbxrefPrefixMap.FlyBase : globals.dbxrefPrefixMap.WormBase;
            geneRef = _.find(context.dbxref, ref => ref.indexOf(organismPrefix) !== -1);
            if (geneRef) {
                sep = geneRef.indexOf(':') + 1;
                baseName = geneRef.substring(sep, geneRef.length);
                geneLink = baseUrl + baseName;
            }
        }

        // Set up breadcrumbs
        const assayTargets = context.investigated_as.map(assayTarget => `investigated_as=${assayTarget}`);
        const crumbs = [
            { id: 'Targets' },
            { id: context.investigated_as.join(' + '), query: assayTargets.join('&'), tip: context.investigated_as.join(' + ') },
            {
                id: <i>{context.organism.scientific_name}</i>,
                query: `organism.scientific_name=${context.organism.scientific_name}`,
                tip: `${context.investigated_as.join(' + ')} and ${context.organism.scientific_name}`,
            },
        ];

        return (
            <div className={globals.itemClass(context, 'view-item')}>
                <header className="row">
                    <div className="col-sm-12">
                        <Breadcrumbs root="/search/?type=target" crumbs={crumbs} />
                        <h2>{context.label} (<em>{context.organism.scientific_name}</em>)</h2>
                    </div>
                </header>

                <div className="panel">
                    <dl className={itemClass}>
                        <div data-test="name">
                            <dt>Target name</dt>
                            <dd>{context.label}</dd>
                        </div>

                        {context.gene_name && geneLink ?
                            <div data-test="gene">
                                <dt>Target gene</dt>
                                <dd><a href={geneLink}>{context.gene_name}</a></dd>
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

Target.propTypes = {
    context: PropTypes.object, // Target object to display
};

Target.defaultProps = {
    context: null,
};


globals.contentViews.register(Target, 'Target');
