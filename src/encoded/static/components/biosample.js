import React from 'react';
import PropTypes from 'prop-types';
import { Panel, PanelBody } from '../libs/ui/panel';
import { auditDecor } from './audit';
import { DbxrefList } from './dbxref';
import { Document, DocumentsPanel, DocumentPreview, DocumentFile } from './doc';
import * as globals from './globals';
import { Breadcrumbs } from './navigation';
import { singleTreatment, treatmentDisplay, PanelLookup, AlternateAccession, ItemAccessories } from './objectutils';
import pubReferenceList from './reference';
import Status from './status';
import { CollectBiosampleDocs, BiosampleTable } from './typeutils';
import formatMeasurement from './../libs/formatMeasurement';


/* eslint-disable react/prefer-stateless-function */
class BiosampleComponent extends React.Component {
    render() {
        const context = this.props.context;
        const itemClass = globals.itemClass(context, 'view-item');
        const aliasList = context.aliases.join(', ');

        // Set up the breadcrumbs.
        const crumbs = [
            { id: 'Biosamples' },
            { id: context.biosample_ontology.term_name, query: `biosample_ontology.term_name=${context.biosample_ontology.term_name}`, tip: context.biosample_ontology.term_name },
        ];

        const crumbsReleased = (context.status === 'released');

        // Collect all documents in this biosample
        let combinedDocs = CollectBiosampleDocs(context);

        // If this biosample is part of another, collect those documents too, then remove
        // any duplicate documents in the combinedDocs array.
        if (context.part_of) {
            const parentCombinedDocs = CollectBiosampleDocs(context.part_of);
            combinedDocs = combinedDocs.concat(parentCombinedDocs);
        }
        combinedDocs = globals.uniqueObjectsArray(combinedDocs);

        // Get a list of reference links, if any
        const references = pubReferenceList(context.references);

        // Collect dbxrefs from biosample.dbxrefs and biosample.biosample_ontology.dbxrefs.
        const dbxrefs = (context.dbxrefs || []).concat(context.biosample_ontology.dbxrefs || []);

        return (
            <div className={itemClass}>
                <header>
                    <Breadcrumbs root="/search/?type=Biosample" crumbs={crumbs} crumbsReleased={crumbsReleased} />
                    <h1>{context.accession}</h1>
                    <div className="replacement-accessions">
                        <AlternateAccession altAcc={context.alternate_accessions} />
                    </div>
                    <ItemAccessories item={context} audit={{ auditIndicators: this.props.auditIndicators, auditId: 'biosample-audit' }} />
                </header>
                {this.props.auditDetail(context.audit, 'biosample-audit', { session: this.context.session, sessionProperties: this.context.session_properties, except: context['@id'] })}
                <Panel>
                    <PanelBody addClasses="panel__split">
                        <div className="panel__split-element">
                            <div className="panel__split-heading panel__split-heading--biosample">
                                <h4>Summary</h4>
                            </div>
                            <dl className="key-value">
                                <div data-test="status">
                                    <dt>Status</dt>
                                    <dd><Status item={context} inline /></dd>
                                </div>

                                <div data-test="term-name">
                                    <dt>Term name</dt>
                                    <dd>{context.biosample_ontology.term_name}</dd>
                                </div>

                                <div data-test="term-id">
                                    <dt>Term ID</dt>
                                    <dd><BiosampleTermId termId={context.biosample_ontology.term_id} /></dd>
                                </div>

                                {context.description ?
                                    <div data-test="description">
                                        <dt>Description</dt>
                                        <dd className="sentence-case">{context.description}</dd>
                                    </div>
                                : null}

                                {context.product_id ?
                                    <div data-test="productid">
                                        <dt>Product ID</dt>
                                        <dd><MaybeLink href={context.url}>{context.product_id}</MaybeLink></dd>
                                    </div>
                                : null}

                                {context.lot_id ?
                                    <div data-test="lotid">
                                        <dt>Lot ID</dt>
                                        <dd>{context.lot_id}</dd>
                                    </div>
                                : null}

                                {context.notes ?
                                    <div data-test="notes">
                                        <dt>Notes</dt>
                                        <dd>{context.notes}</dd>
                                    </div>
                                : null}

                                {context.starting_quantity ?
                                    <div data-test="startingquantity">
                                        <dt>Starting quantity</dt>
                                        <dd>{context.starting_quantity}<span className="unit">{context.starting_quantity_units}</span></dd>
                                    </div>
                                : null}

                                {context.derivation_process ?
                                    <div data-test="derivation_process">
                                        <dt>Derivation process</dt>
                                        <dd>{context.derivation_process}</dd>
                                    </div>
                                : null}

                                {context.fixed ?
                                    <div data-test="fixed">
                                        <dt>Fixed</dt>
                                        <dd>{context.fixed}</dd>
                                    </div>
                                : null}

                                {context.donors ?
                                    <div data-test="donors">
                                        <dt>Donors</dt>
                                        <dd>{context.donors}</dd>
                                    </div>
                                : null}
                            </dl>
                        </div>

                        <div className="panel__split-element">
                            <div className="panel__split-heading panel__split-heading--biosample">
                                <h4>Attribution</h4>
                            </div>
                            <dl className="key-value">
                                {context.source ?
                                    <div data-test="source">
                                        <dt>Source</dt>
                                        <dd>
                                            {context.source.url ?
                                                <a href={context.source.url}>{context.source}</a>
                                            :
                                                <span>{context.source}</span>
                                            }
                                        </dd>
                                    </div>
                                : null}


                                {dbxrefs.length > 0 ?
                                    <div data-test="externalresources">
                                        <dt>External resources</dt>
                                        <dd><DbxrefList context={context} dbxrefs={dbxrefs} /></dd>
                                    </div>
                                : null}

                                {references ?
                                    <div data-test="references">
                                        <dt>References</dt>
                                        <dd>{references}</dd>
                                    </div>
                                : null}

                                {context.aliases.length > 0 ?
                                    <div data-test="aliases">
                                        <dt>Aliases</dt>
                                        <dd>{aliasList}</dd>
                                    </div>
                                : null}

                            </dl>
                        </div>
                    </PanelBody>

                    {context.treatments.length > 0 ?
                        <PanelBody addClasses="panel__below-split">
                            <h4>Treatment details</h4>
                            {context.treatments.map(treatment => treatmentDisplay(treatment))}
                        </PanelBody>
                    : null}
                </Panel>
                {context.derived_from && context.derived_from.length > 0 ?
                    <BiosampleTable
                        title="Derived from"
                        items={context.derived_from}
                        total={context.derived_from.length}
                    />
                : null}

                {context.donor ?
                    <div>
                        {PanelLookup({ context: context.donor, biosample: context })}
                    </div>
                : null}

                {combinedDocs.length > 0 ?
                    <DocumentsPanel documentSpecs={[{ documents: combinedDocs }]} />
                : null}
            </div>
        );
    }
}
/* eslint-enable react/prefer-stateless-function */

BiosampleComponent.propTypes = {
    context: PropTypes.object.isRequired, // ENCODE biosample object to be rendered
    auditIndicators: PropTypes.func.isRequired, // Audit decorator function
    auditDetail: PropTypes.func.isRequired, // Audit decorator function
};

BiosampleComponent.contextTypes = {
    session: PropTypes.object, // Login information
    session_properties: PropTypes.object,
};

const Biosample = auditDecor(BiosampleComponent);

globals.contentViews.register(Biosample, 'Biosample');


// Certain hrefs in a biosample context object could be empty, or have the value 'N/A'. This
// component renders the child components of this one (likely just a string) as just an unadorned
// component. But if href has any value besides this, the child component is rendered as a link
// with this href.

const MaybeLink = (props) => {
    const { href, children } = props;

    if (!href || href === 'N/A') {
        return <span>{children}</span>;
    }
    return <a {...props}>{children}</a>;
};

MaybeLink.propTypes = {
    href: PropTypes.string, // String
    children: PropTypes.node.isRequired, // React child components to this one
};

MaybeLink.defaultProps = {
    href: '',
};


// Map from prefixes to corresponding URL bases. Not all term ID prefixes covered here. Specific
// term IDs are appended to these after converting ':' to '_'.
const urlMap = {
    EFO: 'http://www.ebi.ac.uk/efo/',
    UBERON: 'http://www.ontobee.org/ontology/UBERON?iri=http://purl.obolibrary.org/obo/',
    CL: 'http://www.ontobee.org/ontology/CL?iri=http://purl.obolibrary.org/obo/',
    CLO: 'http://www.ontobee.org/ontology/CLO?iri=http://purl.obolibrary.org/obo/',
};

// Display the biosample term ID given in `termId`, and link to a corresponding site if the prefix
// of the term ID needs it. Any term IDs with prefixes not maching any in the `urlMap` property
// simply display without a link.
const BiosampleTermId = (props) => {
    const termId = props.termId;

    if (termId) {
        // All are of the form XXX:nnnnnnn...
        const idPieces = termId.split(':');
        if (idPieces.length === 2) {
            const urlBase = urlMap[idPieces[0]];
            if (urlBase) {
                return <a href={urlBase + termId.replace(':', '_')}>{termId}</a>;
            }
        }

        // Either term ID not in specified form (schema should disallow) or not one of the ones
        // we link to. Just display the term ID without linking out.
        return <span>{termId}</span>;
    }

    // biosample_ontology is a required property, but just in case...
    return null;
};

BiosampleTermId.propTypes = {
    termId: PropTypes.string, // Biosample whose term is being displayed.
};

BiosampleTermId.defaultProps = {
    termId: '',
};

export default BiosampleTermId;


const Treatment = (props) => {
    const context = props.context;

    const treatmentText = singleTreatment(context);
    return (
        <dl className="key-value">
            <div data-test="treatment">
                <dt>Treatment</dt>
                <dd>{treatmentText}</dd>
            </div>

            <div data-test="type">
                <dt>Type</dt>
                <dd>{context.treatment_type}</dd>
            </div>
        </dl>
    );
};

Treatment.propTypes = {
    context: PropTypes.object.isRequired, // Treatment context object
};

globals.panelViews.register(Treatment, 'Treatment');


const TreatmentContent = ({ context }) => {
    const itemClass = globals.itemClass(context, 'view-item');
    return (
        <div className={itemClass}>
            <header>
                <h1>{context.treatment_term_name}</h1>
                <ItemAccessories item={context} />
            </header>
            <Panel>
                <PanelBody>
                    <Treatment context={context} />
                </PanelBody>
            </Panel>
        </div>
    );
};

TreatmentContent.propTypes = {
    /** Treatment object to display on its own page */
    context: PropTypes.object.isRequired,
};

globals.contentViews.register(TreatmentContent, 'Treatment');
