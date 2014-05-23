/** @jsx React.DOM */
'use strict';
var React = require('react');
var cx = require('react/lib/cx');
var _ = require('underscore');
var url = require('url');
var globals = require('./globals');
var dataset = require('./dataset');
var fetched = require('./fetched');
var dbxref = require('./dbxref');
var antibody = require('./antibody');

var DbxrefList = dbxref.DbxrefList;
var StatusLabel = antibody.StatusLabel;

var ExperimentTable = dataset.ExperimentTable;
var FetchedItems = fetched.FetchedItems;


var Panel = function (props) {
    // XXX not all panels have the same markup
    var context;
    if (props['@id']) {
        context = props;
        props = {context: context, key: context['@id']};
    }
    return globals.panel_views.lookup(props.context)(props);
};


var Biosample = module.exports.Biosample = React.createClass({
    render: function() {
        var context = this.props.context;
        var itemClass = globals.itemClass(context, 'view-item');
        var aliasList = context.aliases.join(", ");

        // set up construct documents panels
        var constructs = _.sortBy(context.constructs, function(item) {
            return item.uuid;
        });
        var construct_documents = {};
        constructs.forEach(function (construct) {
            construct.documents.forEach(function (doc) {
                construct_documents[doc['@id']] = Panel({context: doc, popoverContent: StdContent});
           }, this);
        }, this);

        // set up RNAi documents panels
        var rnais = _.sortBy(context.rnais, function(item) {
            return item.uuid; //may need to change
        });
        var rnai_documents = {};
        rnais.forEach(function (rnai) {
            rnai.documents.forEach(function (doc) {
                rnai_documents[doc['@id']] = Panel({context: doc, popoverContent: StdContent});
            }, this);
        }, this);

        var protocol_documents = {};
        context.protocol_documents.forEach(function(doc) {
            protocol_documents[doc['@id']] = Panel({context: doc, popoverContent: StdContent});
        }, this);

        var experiments_url = '/search/?type=experiment&replicates.library.biosample.uuid=' + context.uuid;

        return (
            <div className={itemClass}>
                <header className="row">
                    <div className="col-sm-12">
                        <ul className="breadcrumb">
                            <li>Biosamples</li>
                            <li>{context.biosample_type}</li>
                            {context.donor ?
                                <li className="active">{context.donor.organism.name}</li>
                            : null }
                        </ul>
                        <h2>
                            {context.accession}{' / '}<span className="sentence-case">{context.biosample_type}</span>
                        </h2>
                        <div className="characterization-status-labels">
                            <StatusLabel title="Status" status={context.status} />
                        </div>
                    </div>
                </header>
                <div className="panel data-display">
                    <dl className="key-value">
                        <dt>Term name</dt>
                        <dd>{context.biosample_term_name}</dd>

                        <dt>Term ID</dt>
                        <dd>{context.biosample_term_id}</dd>

                        {context.description ? <dt>Description</dt> : null}
                        {context.description ? <dd className="sentence-case">{context.description}</dd> : null}
                        
                        {context.subcellular_fraction_term_name ? <dt>Subcellular fraction</dt> : null}
                        {context.subcellular_fraction_term_name ? <dd>{context.subcellular_fraction_term_name}</dd> : null}

                        <dt>Source</dt>
                        <dd><a href={context.source.url}>{context.source.title}</a></dd>

                        {context.product_id ? <dt>Product ID</dt> : null}
                        {context.product_id ? <dd><maybe_link href={context.url}>{context.product_id}</maybe_link></dd> : null}

                        {context.lot_id ? <dt>Lot ID</dt> : null}
                        {context.lot_id ? <dd>{context.lot_id}</dd> : null}

                        <dt>Project</dt>
                        <dd>{context.award.project}</dd>

                        <dt>Submitted by</dt>
                        <dd>{context.submitted_by.title}</dd>

                        <dt>Lab</dt>
                        <dd>{context.lab.title}</dd>

                        <dt>Grant</dt>
                        <dd>{context.award.name}</dd>

                        {context.aliases.length ? <dt>Aliases</dt> : null}
                        {context.aliases.length ? <dd>{aliasList}</dd>: null}

                        {context.dbxrefs.length ? <dt>External resources</dt> : null}
                        {context.dbxrefs.length ? <dd><DbxrefList values={context.dbxrefs} /></dd> : null}

                        {context.note ? <dt>Note</dt> : null}
                        {context.note ? <dd>{context.note}</dd> : null}
                        
                        {context.date_obtained ? <dt>Date obtained</dt> : null}
						{context.date_obtained ? <dd>{context.date_obtained}</dd> : null}
						
						{context.starting_amount ? <dt>Starting amount</dt> : null}
						{context.starting_amount ? <dd>{context.starting_amount}<span className="unit">{context.starting_amount_units}</span></dd> : null}
                        
                        {context.culture_start_date ? <dt>Culture start date</dt> : null}
						{context.culture_start_date ? <dd>{context.culture_start_date}</dd> : null}
				
						{context.culture_harvest_date ? <dt>Culture harvest date</dt> : null}
						{context.culture_harvest_date ? <dd>{context.culture_harvest_date}</dd> : null}
				
						{context.passage_number ? <dt>Passage number</dt> : null}
						{context.passage_number ? <dd>{context.passage_number}</dd> : null}
                    </dl>

                    {(context.donor) ?
                        <section>
                            <hr />
                            <h4>Donor information</h4>
                            <Panel context={context.donor} biosample={context} />
                        </section>
                    : null}

                     {context.derived_from ?
                        <section>
                            <hr />
                            <h4>Derived from biosample</h4>
                            <a className="non-dl-item" href={context.derived_from['@id']}> {context.derived_from.accession} </a>
                        </section>
                    : null}

                     {context.part_of ?
                        <section>
                            <hr />
                            <h4>Separated from biosample</h4>
                            <a className="non-dl-item" href={context.part_of['@id']}> {context.part_of.accession} </a>
                        </section>
                    : null}

                    {context.pooled_from.length ?
                        <section>
                            <hr />
                            <h4>Pooled from biosamples</h4>
                            <ul className="non-dl-list">
                                {context.pooled_from.map(function (biosample) {
                                    return (
                                        <li key={biosample['@id']}>
                                            <a href={biosample['@id']}>{biosample.accession}</a>
                                        </li>
                                    );
                                })}
                            </ul>

                        </section>
                    : null}

                    {context.treatments.length ?
                        <section>
                            <hr />
                            <h4>Treatment details</h4>
                            {context.treatments.map(Panel)}
                        </section>
                    : null}

                    {context.constructs.length ?
                        <section>
                            <hr />
                            <h4>Construct details</h4>
                            {context.constructs.map(Panel)}
                        </section>
                    : null}

                    {context.rnais.length ?
                        <section>
                            <hr />
                            <h4>RNAi details</h4>
                            {context.rnais.map(Panel)}
                        </section>
                    : null}

                </div>

                {Object.keys(protocol_documents).length ?
                    <div>
                        <h3>Documents</h3>
                        <div className="row multi-columns-row">
                            {protocol_documents}
                        </div>
                    </div>
                : null}

                {context.characterizations.length ?
                    <div>
                        <h3>Characterizations</h3>
                        <div className="row">
                            {context.characterizations.map(Panel)}
                        </div>
                    </div>
                : null}

                {Object.keys(construct_documents).length ?
                    <div>
                        <h3>Construct documents</h3>
                        <div className="row">
                            {construct_documents}
                        </div>
                    </div>
                : null}

                {Object.keys(rnai_documents).length ?
                    <div>
                        <h3>RNAi documents</h3>
                        <div className="row">
                            {rnai_documents}
                        </div>
                    </div>
                : null}

                {this.transferPropsTo(
                    <FetchedItems url={experiments_url} Component={ExperimentsUsingBiosample} />
                )}

            </div>
        );
    }
});

globals.content_views.register(Biosample, 'biosample');


var ExperimentsUsingBiosample = module.exports.ExperimentsUsingBiosample = React.createClass({
    render: function () {
        var context = this.props.context;
        return (
            <div>
                <h3>Experiments using biosample {context.accession}</h3>
                {this.transferPropsTo(
                    <ExperimentTable />
                )}
            </div>
        );
    }
});


var maybe_link = function (props, children) {
    if (props.href == 'N/A') {
        return children;
    } else {
        return (
            <a href={props.href}>{children}</a>
        );
    }
};

var HumanDonor = module.exports.HumanDonor = React.createClass({
    render: function() {
        var context = this.props.context;
        var biosample = this.props.biosample;
        return (
            <dl className="key-value">
                <dt>Accession</dt>
                <dd>{context.accession}</dd>

                {context.aliases.length ? <dt>Aliases</dt> : null}
                {context.aliases.length ? <dd>{context.aliases.join(", ")}</dd> : null}

                {context.organism.name ? <dt>Species</dt> : null}
                {context.organism.name ? <dd className="sentence-case">{context.organism.name}</dd> : null}

                {biosample && biosample.life_stage ? <dt>Life stage</dt> : null}
                {biosample && biosample.life_stage ? <dd className="sentence-case">{biosample.life_stage}</dd> : null}

                {biosample && biosample.age ? <dt>Age</dt> : null}
                {biosample && biosample.age ? <dd>{biosample.age}{' '}{biosample.age_units}</dd> : null}

                {context.sex ? <dt>Sex</dt> : null}
                {context.sex ? <dd className="sentence-case">{context.sex}</dd> : null}

                {biosample && biosample.health_status ? <dt>Health status</dt> : null}
                {biosample && biosample.health_status ? <dd className="sentence-case">{biosample.health_status}</dd> : null}

                {context.ethnicity ? <dt>Ethnicity</dt> : null}
                {context.ethnicity ? <dd>{context.ethnicity}</dd> : null}
            </dl>
        );
    }
});

globals.panel_views.register(HumanDonor, 'human_donor');


var MouseDonor = module.exports.MouseDonor = React.createClass({
    render: function() {
        var context = this.props.context;
        var biosample = this.props.biosample;
        return (
            <dl className="key-value">
                <dt>Accession</dt>
                <dd>{context.accession}</dd>

                {context.aliases.length ? <dt>Aliases</dt> : null}
                {context.aliases.length ? <dd>{context.aliases.join(", ")}</dd> : null}

                {context.organism.name ? <dt>Species</dt> : null}
                {context.organism.name ? <dd className="sentence-case">{context.organism.name}</dd> : null}

                {biosample && biosample.life_stage ? <dt>Life stage</dt> : null}
                {biosample && biosample.life_stage ? <dd className="sentence-case">{biosample.life_stage}</dd> : null}

                {biosample && biosample.age ? <dt>Age</dt> : null}
                {biosample && biosample.age ? <dd>{biosample.age}{' '}{biosample.age_units}</dd> : null}

                <dt>Sex</dt>
                <dd className="sentence-case">{context.sex}</dd>

                {biosample && biosample.health_status ? <dt>Health status</dt> : null}
                {biosample && biosample.health_status ? <dd className="sentence-case">{biosample.health_status}</dd> : null}

                <dt>Strain background</dt>
                <dd>{context.strain_background}</dd>

                {context.strain_name ? <dt>Strain name</dt> : null}
                {context.strain_name ? <dd>{context.strain_name}</dd> : null}
            </dl>
        );
    }
});

globals.panel_views.register(MouseDonor, 'mouse_donor');


var Treatment = module.exports.Treatment = React.createClass({
    render: function() {
        var context = this.props.context;
        var title = '';
        if (context.concentration) {
            title += context.concentration + ' ' + context.concentration_units + ' ';
        }
        title += context.treatment_term_name + ' (' + context.treatment_term_id + ') ';
        if (context.duration) {
            title += 'for ' + context.duration + ' ' + context.duration_units;
        }
        return (
            <dl className="key-value">
                <dt>Treatment</dt>
                <dd>{title}</dd>

                <dt>Type</dt>
                <dd>{context.treatment_type}</dd>

            </dl>
        );
    }
});

globals.panel_views.register(Treatment, 'treatment');


var Construct = module.exports.Construct = React.createClass({
    render: function() {
        var context = this.props.context;
        return (
            <dl className="key-value">
                {context.target ? <dt>Target</dt> : null}
                {context.target ? <dd><a href={context.target['@id']}>{context.target.name}</a></dd> : null}

                {context.vector_backbone_name ? <dt>Vector</dt> : null}
                {context.vector_backbone_name ? <dd>{context.vector_backbone_name}</dd> : null}

                {context.construct_type ? <dt>Construct Type</dt> : null}
                {context.construct_type ? <dd>{context.construct_type}</dd> : null}

                {context.description ?  <dt>Description</dt> : null}
                {context.description ? <dd>{context.description}</dd> : null}

                {context.tags.length ? <dt>Tags</dt> : null}
                {context.tags.length ? <dd>
                    <ul>
                        {context.tags.map(function (tag, index) {
                            return (
                                <li key={index}>
                                    {tag.name} (Location: {tag.location})
                                </li>
                            );
                        })}
                    </ul>
                </dd> : null}


                {context.source.title ? <dt>Source</dt> : null}
                {context.source.title ? <dd>{context.source.title}</dd> : null}

                {context.product_id ? <dt>Product ID</dt> : null}
                {context.product_id ? <dd><maybe_link href={context.url}>{context.product_id}</maybe_link></dd> : null}
            </dl>
        );
    }
});

globals.panel_views.register(Construct, 'construct');


var RNAi = module.exports.RNAi = React.createClass({
    render: function() {
        var context = this.props.context;
        return (
             <dl className="key-value">
                {context.target ? <dt>Target</dt> : null}
                {context.target ? <dd><a href={context.target['@id']}>{context.target.name}</a></dd> : null}
                
                {context.rnai_type ? <dt>RNAi type</dt> : null}
                {context.rnai_type ? <dd>{context.rnai_type}</dd> : null}
                
                {context.source.title ? <dt>Source</dt> : null}
                {context.source.title ? <dd><a href={context.source.url}>{context.source.title}</a></dd> : null}

                {context.product_id ? <dt>Product ID</dt> : null}
                {context.product_id ? <dd><a href={context.url}>{context.product_id}</a></dd> : null}

                {context.rnai_target_sequence ? <dt>Target sequence</dt> : null}
                {context.rnai_target_sequence ? <dd>{context.rnai_target_sequence}</dd> : null}

                {context.vector_backbone_name ? <dt>Vector backbone</dt> : null}
                {context.vector_backbone_name ? <dd>{context.vector_backbone_name}</dd> : null}                
            </dl>
        );
    }
});

globals.panel_views.register(RNAi, 'rnai');


// Popover bubble
var Popover = module.exports.Popover = React.createClass({
    contextTypes: {
        popoverComponent: React.PropTypes.string, // ID of component with visible popup
        onPopoverChange: React.PropTypes.func // Parent function to process popover
    },

    handleClick: function(e) {
        e.preventDefault();
        e.stopPropagation();
    },

    render: function() {
        var popoverContent;
        var context = this.props.context;
        var popoverVisible = this.context.popoverComponent === this.props.popoverComponent;
        if (this.props.popoverContent) {
            popoverContent = this.props.popoverContent({context: context});
        } else {
            popoverContent = StdContent({context: context});
        }
        var popoverClass = cx({
            "key-value-popover": true,
            "active": popoverVisible
        });
        return(
            <dl className={popoverClass} onClick={this.handleClick}>
                {popoverContent}
            </dl>
        );
    }
});


// Component: bar that, when clicked, opens a popover with document data
// Note: uses React context, ≠ props.context
var PopoverTrigger = module.exports.PopoverTrigger = React.createClass({
    contextTypes: {
        popoverComponent: React.PropTypes.string, // ID of component with visible popup
        onPopoverChange: React.PropTypes.func // Parent function to process popover
    },

    // Clicking the Lab bar inverts visible state of the popover
    handleClick: function(e) {
        e.preventDefault();
        e.stopPropagation();

        // Tell parent (App component) about new popover state
        // Pass it this component's React unique node ID
        this.context.onPopoverChange(this._rootNodeID);
    },

    render: function() {
        var context = this.props.context;
        var popoverVisible = this.context.popoverComponent === this._rootNodeID;
        var keyClass = cx({
            "key-value-trigger": true,
            "active": popoverVisible
        });

        return (
            <div className="document-info">
                <dl className={keyClass}>
                    <a href="#" aria-haspopup="true" onClick={this.handleClick}>
                        <dt>Lab</dt>
                        <dd>{context.lab.title}</dd>
                        <i className="trigger-icon icon-info-sign"></i>
                    </a>
                </dl>
                <Popover context={context} popoverContent={this.props.popoverContent} popoverComponent={this._rootNodeID} />
            </div>
        );
    }
});


var StdContent = module.exports.StdContent = React.createClass({
    render: function() {
        var context = this.props.context;
        return(
            <div>
                {context.caption ? <dt>Caption</dt> : null}
                {context.caption ? <dd>{context.caption}</dd> : null}

                <dt>Submitted by</dt>
                <dd>{context.submitted_by.title}</dd>

                <dt>Grant</dt>
                <dd>{context.award.name}</dd>
            </div>
        );
    }
});


// Fixed-position lightbox background and image
var Lightbox = module.exports.Lightbox = React.createClass({
    ignoreClick: function(e) {
        e.preventDefault();
        e.stopPropagation();
    },

    render: function() {
        var lightboxVisible = this.props.lightboxVisible;
        var lightboxClass = cx({
            "lightbox": true,
            "active": lightboxVisible
        });

        return(
            <div className={lightboxClass} onClick={this.props.clearLightbox}>
                <div className="lightbox-img">
                    <img src={this.props.lightboxImg} onClick={this.ignoreClick} />
                    <i className="lightbox-close icon-remove-sign"></i>
                </div>
            </div>
        );
    }
});


var Document = module.exports.Document = React.createClass({
    getInitialState: function() {
        return {lightboxVisible: false};
    },

    // Handle a click on the lightbox trigger (thumbnail)
    lightboxClick: function(attachmentType, e) {
        if(attachmentType === 'image') {
            e.preventDefault();
            e.stopPropagation();
            this.setState({lightboxVisible: true});
        }
    },

    clearLightbox: function() {
        this.setState({lightboxVisible: false});
    },

    // If lightbox visible, ESC key closes it
    handleEscKey: function(e) {
        if(this.state.lightboxVisible && e.keyCode == 27) {
            this.clearLightbox();
        }
    },

    // Register for keyup events for ESC key
    componentDidMount: function() {
        window.addEventListener('keyup', this.handleEscKey);
    },

    // Unregister keyup events when component closes
    componentWillUnmount: function() {
        window.removeEventListener('keyup', this.handleEscKey);
    },

    render: function() {
        var context = this.props.context;
        var attachmentHref, attachmentUri;
        var figure, download, src, alt;
        var imgClass = "characterization-img characterization-file";
        var height = "100";
        var width = "100";
        if (context.attachment) {
            attachmentHref = url.resolve(context['@id'], context.attachment.href);
            var attachmentType = context.attachment.type.split('/', 1)[0];
            if (attachmentType == 'image') {
                var imgClass = 'characterization-img';
                src = attachmentHref;
                height = context.attachment.height;
                width = context.attachment.width;
                alt = "Characterization Image";
                figure = (
                    <a data-bypass="true" href={attachmentHref} onClick={this.lightboxClick.bind(this, attachmentType)}>
                        <img className={imgClass} src={src} height={height} width={width} alt={alt} />
                    </a>
                );
            } else if (context.attachment.type == "application/pdf"){
                figure = (
                    <a data-bypass="true" href={attachmentHref} className="file-pdf text-hide" onClick={this.lightboxClick.bind(this, attachmentType)}>Characterization PDF Icon</a>
                );
            } else {
                figure = (
                    <a data-bypass="true" href={attachmentHref} className="file-generic text-hide" onClick={this.lightboxClick.bind(this, attachmentType)}>Characterization Icon</a>
                );
            }
            var dlFileTitle = "Download file " + context.attachment.download;
            download = (
                <a data-bypass="true" title={dlFileTitle} className="dl-bar" href={attachmentHref} download={context.attachment.download}>
                    {context.attachment.download}
                    <i className="trigger-icon icon-download"></i>
                </a>
            );
        } else {
            figure = (
                <div className="file-missing text-hide">Characterization file broken icon</div>
            );
            download = (
                <em>Document not available</em>
            );
        }

        return (
            <section className="col-xs-12 col-sm-6 col-md-4 col-lg-4">
                <div className="type-document type-popover view-detail panel status-none">
                    <figure>
                        {figure}
                    </figure>
                    <div className="document-intro">
                        <h3 className="sentence-case">{context.document_type}</h3>
                        <p>{context.description}</p>
                    </div>
                    {download}
                    <PopoverTrigger context={context} popoverContent={this.props.popoverContent} />
                    <Lightbox lightboxVisible={this.state.lightboxVisible} lightboxImg={src} clearLightbox={this.clearLightbox} />
                </div>
            </section>
        );
    }
});

globals.panel_views.register(Document, 'document');
globals.panel_views.register(Document, 'biosample_characterization');
