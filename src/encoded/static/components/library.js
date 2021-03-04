import React from 'react';
import PropTypes from 'prop-types';
import { Panel, PanelBody } from '../libs/ui/panel';
import { auditDecor } from './audit';
import { DbxrefList } from './dbxref';
import * as globals from './globals';
import { Breadcrumbs } from './navigation';
import { PanelLookup, AlternateAccession, ItemAccessories } from './objectutils';
import Status from './status';
import { CollectBiosampleDocs, BiosampleTable, DonorTable } from './typeutils';


/* eslint-disable react/prefer-stateless-function */
class LibraryComponent extends React.Component {
    render() {
        const context = this.props.context;
        const itemClass = globals.itemClass(context, 'view-item');
        const aliasList = context.aliases.join(', ');

        function libraryList(values, field) {
            if (values && values.length > 0) {
                return Array.from(new Set(values.map(function(value) { return value[field] }))).join(", ");
            }
            return null;
        }

        const bio_onts  = libraryList(context.biosample_ontologies, 'term_name');

        // Set up the breadcrumbs.
        const crumbs = [
            { id: 'Libraries' },
            { id: context.protocol.title, query: `protocol.title=${context.protocol.title}`, tip: context.protocol.title },
        ];

        const crumbsReleased = (context.status === 'released');

        // Collect all documents in this biosample
        let combinedDocs = CollectBiosampleDocs(context);

        // Collect dbxrefs from biosample.dbxrefs and biosample.biosample_ontology.dbxrefs.
        const dbxrefs = (context.dbxrefs || []);

        return (
            <div className={itemClass}>
                <header>
                    <Breadcrumbs root="/search/?type=Library" crumbs={crumbs} crumbsReleased={crumbsReleased} />
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

                                <div data-test="protocol-title">
                                    <dt>Protocol</dt>
                                    <dd>{context.protocol.title}</dd>
                                </div>

                                <div data-test="assay">
                                    <dt>Assay</dt>
                                    <dd>{context.assay}</dd>
                                </div>

                                {bio_onts ?
                                    <div data-test="bio_onts">
                                        <dt>Biosamples</dt>
                                        <dd>{bio_onts}</dd>
                                    </div>
                                : null}

                                {context.starting_quantity ?
                                    <div data-test="startingquantity">
                                        <dt>Starting quantity</dt>
                                        <dd>{context.starting_quantity}<span className="unit">{context.starting_quantity_units}</span></dd>
                                    </div>
                                : null}
                            </dl>
                        </div>

                        <div className="panel__split-element">
                            <div className="panel__split-heading panel__split-heading--biosample">
                                <h4>Attribution</h4>
                            </div>
                            <dl className="key-value">
                                <div data-test="dataset">
                                    <dt>Dataset</dt>
                                    <dd>{context.dataset}</dd>
                                </div>

                                {context.lab ?
                                    <div data-test="lab">
                                        <dt>Lab</dt>
                                        <dd>{context.lab.title}</dd>
                                    </div>
                                : null}

                                <div data-test="award-name">
                                    <dt>Award name</dt>
                                    <dd>{context.award.name}</dd>
                                </div>

                                {context.dbxrefs ?
                                    <div data-test="externalresources">
                                        <dt>External resources</dt>
                                        <dd><DbxrefList context={context} dbxrefs={dbxrefs} /></dd>
                                    </div>
                                : null}

                                {context.aliases ?
                                    <div data-test="aliases">
                                        <dt>Aliases</dt>
                                        <dd>{aliasList}</dd>
                                    </div>
                                : null}

                            </dl>
                        </div>
                    </PanelBody>
                </Panel>

                {context.donors && context.donors.length > 0 ?
                    <DonorTable
                        title="Donors"
                        items={context.donors}
                        total={context.donors.length}
                    />
                : null}

                {context.donor ?
                    <div>
                        {PanelLookup({ context: context.donor, biosample: context })}
                    </div>
                : null}
            </div>
        );
    }
}
/* eslint-enable react/prefer-stateless-function */

LibraryComponent.propTypes = {
    context: PropTypes.object.isRequired, // ENCODE biosample object to be rendered
    auditIndicators: PropTypes.func.isRequired, // Audit decorator function
    auditDetail: PropTypes.func.isRequired, // Audit decorator function
};

LibraryComponent.contextTypes = {
    session: PropTypes.object, // Login information
    session_properties: PropTypes.object,
};

const Library = auditDecor(LibraryComponent);

globals.contentViews.register(Library, 'Library');


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
