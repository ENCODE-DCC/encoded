/** @jsx React.DOM */
'use strict';
var React = require('react');
var _ = require('underscore');
var url = require('url');
var globals = require('./globals');
var dataset = require('./dataset');
var fetched = require('./fetched');
var dbxref = require('./dbxref');
var browserCaps = require('./mixins').browserCaps;

var DbxrefList = dbxref.DbxrefList;

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
                construct_documents[doc['@id']] = Panel({context: doc});
            });
        });

        // set up RNAi documents panels
        var rnais = _.sortBy(context.rnais, function(item) {
            return item.uuid; //may need to change
        });
        var rnai_documents = {};
        rnais.forEach(function (rnai) {
            rnai.documents.forEach(function (doc) {
                rnai_documents[doc['@id']] = Panel({context: doc});
            });
        });

        var experiments_url = '/search/?type=experiment&replicates.library.biosample.uuid=' + context.uuid;

        return (
            <div className={itemClass}>
                <header className="row">
                    <div className="span12">
                        <ul className="breadcrumb">
                            <li>Biosamples <span className="divider">/</span></li>
                            <li>{context.biosample_type}{' '}<span className="divider">/</span></li>{' '}
                            {context.donor ?
                                <li className="active">{context.donor.organism.name}</li>
                            : null }
                        </ul>
                        <h2>{context.accession}{' / '}<span className="sentence-case">{context.biosample_type}</span></h2>
                    </div>
                </header>
                <div className="panel data-display">
                    <dl className="key-value">
                        <dt>Term name</dt>
                        <dd className="sentence-case">{context.biosample_term_name}</dd>

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

                {context.protocol_documents.length ?
                    <div>
                        <h3>Protocol documents</h3>
                        {context.protocol_documents.map(Panel)}
                    </div>
                : null}

                {context.characterizations.length ?
                    <div>
                        <h3>Characterizations</h3>
                        {context.characterizations.map(Panel)}
                    </div>
                : null}

                {Object.keys(construct_documents).length ?
                    <div>
                        <h3>Construct documents</h3>
                        {construct_documents}
                    </div>
                : null}

                {Object.keys(rnai_documents).length ?
                    <div>
                        <h3>RNAi documents</h3>
                        {rnai_documents}
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


var Document = module.exports.Document = React.createClass({

    componentDidMount: function() {
        // If the browser can render SVGs, replace the data-src attribute file extension with '.svg'.
        if (this.refs.fileicon && this.refs.fileicon.props.sourceset) {
            // Only do filename extension replacement if 'fileicon' ref is set
            var node = this.refs.fileicon.getDOMNode();
            var caps = browserCaps();
            var sourceset = this.refs.fileicon.props.sourceset;

            if (sourceset) {
                if (caps.svg && sourceset.svg) {
                    node.src = sourceset.svg;
                } else if (sourceset.png) {
                    node.src = sourceset.png;
                } else if (sourceset.jpg) {
                    node.src = sourceset.jpg;
                } // otherwise, no image to load at all
            }
        } // otherwise, no image to load at all
    },

    render: function() {
        var context = this.props.context;
        var attachmentHref, attachmentUri;
        var figure, download, src, sourceset, alt, ref;
        var imgClass = "characterization-img characterization-file";
        var height = "100";
        var width = "100";
        if (context.attachment) {
            attachmentHref = url.resolve(context['@id'], context.attachment.href);
            if (context.attachment.type.split('/', 1)[0] == 'image') {
                imgClass = 'characterization-img';
                src = attachmentHref;
                sourceset = "";
                height = context.attachment.height;
                width = context.attachment.width;
                alt = "Characterization Image";
                ref = '';
            } else if (context.attachment.type == "application/pdf"){
                src = "";
                sourceset = {png:"/static/img/file-pdf.png",svg:"/static/img/file-pdf.svg"};
                alt = "Characterization PDF Icon";
                ref = "fileicon";
            } else {
                src = "";
                sourceset = {png:"/static/img/file.png",svg:"/static/img/file-pdf.svg"};
                alt = "Characterization Icon";
                ref = "fileicon";
            }
            figure = (
                <a data-bypass="true" href={attachmentHref}>
                    <img className={imgClass} src={src} sourceset={sourceset} ref={ref} height={height} width={width} alt={alt} />
                </a>
            );
            download = (
                <a data-bypass="true" href={attachmentHref} download={context.attachment.download}>
                    {context.attachment.download}
                </a>
            );
        } else {
            src = "";
            sourceset = {png:"/static/img/file-broken.png",svg:"/static/img/file-broken.svg"};
            alt = "Characterization File Broken Icon";
            ref = "fileicon";
            figure = (
                <img className={imgClass} src={src} sourceset={sourceset} ref={ref} height={height} width={width} alt={alt} />
            );
            download = (
                <em>Document not available</em>
            );
        }

        return (
            <section className="type-document view-detail panel status-none">
                <div className="container">
                    <div className="row">
                        <div className="span6">
                            <figure>
                                {figure}
                            </figure>
                        </div>
                        <div className="span5">
                            <h3 className="sentence-case">{context.document_type}</h3>
                            <p>{context.description}</p>
                            <dl className="key-value">
                                {context.caption ? <dt>Caption</dt> : null}
                                {context.caption ? <dd>{context.caption}</dd> : null}

                                <dt>Submitted by</dt>
                                <dd>{context.submitted_by.title}</dd>

                                <dt>Lab</dt>
                                <dd>{context.lab.title}</dd>

                                <dt>Grant</dt>
                                <dd>{context.award.name}</dd>

                                <dt><i className="icon-download-alt"></i> Download</dt>
                                <dd>{download}</dd>
                            </dl>
                        </div>
                    </div>
                </div>
            </section>
        );
    }
});

globals.panel_views.register(Document, 'document');
globals.panel_views.register(Document, 'biosample_characterization');
