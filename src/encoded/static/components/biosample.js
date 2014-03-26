/** @jsx React.DOM */
'use strict';
var React = require('react/addons');
var _ = require('underscore');
var url = require('url');
var globals = require('./globals');
var dataset = require('./dataset');
var fetched = require('./fetched');
var dbxref = require('./dbxref');

var DbxrefList = dbxref.DbxrefList;

var ExperimentTable = dataset.ExperimentTable;
var FetchedItems = fetched.FetchedItems;


var Panel = function (props) {
    // XXX not all panels have the same markup
    console.dir(props);
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

                        <dt hidden={!context.description}>Description</dt>
                        <dd hidden={!context.description} className="sentence-case">{context.description}</dd>
                        
                        <dt hidden={!context.subcellular_fraction_term_name}>Subcellular fraction</dt>
                        <dd hidden={!context.subcellular_fraction_term_name}>{context.subcellular_fraction_term_name}</dd>

                        <dt>Source</dt>
                        <dd><a href={context.source.url}>{context.source.title}</a></dd>

                        <dt hidden={!context.product_id}>Product ID</dt>
                        <dd hidden={!context.product_id}><maybe_link href={context.url}>{context.product_id}</maybe_link></dd>

                        <dt hidden={!context.lot_id}>Lot ID</dt>
                        <dd hidden={!context.lot_id}>{context.lot_id}</dd>

                        <dt>Project</dt>
                        <dd>{context.award.project}</dd>

                        <dt>Submitted by</dt>
                        <dd>{context.submitted_by.title}</dd>

                        <dt>Lab</dt>
                        <dd>{context.lab.title}</dd>

                        <dt>Grant</dt>
                        <dd>{context.award.name}</dd>

                        <dt hidden={!context.aliases.length}>Aliases</dt>
                        <dd hidden={!context.aliases.length}>{aliasList}</dd>

                        <dt hidden={!context.dbxrefs.length}>External resources</dt>
                        <dd hidden={!context.dbxrefs.length}>
                            <DbxrefList values={context.dbxrefs} />
                        </dd>

                        <dt hidden={!context.note}>Note</dt>
                        <dd hidden={!context.note}>{context.note}</dd>
                        
                        <dt hidden={!context.date_obtained}>Date obtained</dt>
						<dd hidden={!context.date_obtained}>{context.date_obtained}</dd>
						
						<dt hidden={!context.starting_amount}>Starting amount</dt>
						<dd hidden={!context.starting_amount}>{context.starting_amount}<span className="unit">{context.starting_amount_units}</span></dd>
                        
                        <dt hidden={!context.culture_start_date}>Culture start date</dt>
						<dd hidden={!context.culture_start_date}>{context.culture_start_date}</dd>
				
						<dt hidden={!context.culture_harvest_date}>Culture harvest date</dt>
						<dd hidden={!context.culture_harvest_date}>{context.culture_harvest_date}</dd>
				
						<dt hidden={!context.passage_number}>Passage number</dt>
						<dd hidden={!context.passage_number}>{context.passage_number}</dd>
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
                        <div className="row">
                            {context.protocol_documents.map(Panel)}
                        </div>
                    </div>
                : null}

                {context.characterizations.length ?
                    <div>
                        <h3>Characterizations</h3>
                        {context.characterizations.map(Panel)}
                    </div>
                : null}

                <div hidden={!Object.keys(construct_documents).length}>
                    <h3>Construct documents</h3>
                    {construct_documents}
                </div>

                <div hidden={!Object.keys(rnai_documents).length}>
                    <h3>RNAi documents</h3>
                    {rnai_documents}
                </div>

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

                <dt hidden={!context.aliases.length}>Aliases</dt>
                <dd hidden={!context.aliases.length}>{context.aliases.join(", ")}</dd>

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

                <dt hidden={!context.aliases.length}>Aliases</dt>
                <dd hidden={!context.aliases.length}>{context.aliases.join(", ")}</dd>

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

                <dt hidden={!context.tags.length}>Tags</dt>
                <dd hidden={!context.tags.length}>
                    <ul>
                        {context.tags.map(function (tag, index) {
                            return (
                                <li key={index}>
                                    {tag.name} (Location: {tag.location})
                                </li>
                            );
                        })}
                    </ul>
                </dd>


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


var PopoverTrigger = module.exports.PopoverTrigger = React.createClass({
    getInitialState: function() {
        return {
            popoverVisible: false
        };
    },

    // Clicking the Lab bar inverts visible state of the popover
    handleClick: function(e) {
        e.preventDefault();
        e.stopPropagation();
        this.setState({
            popoverVisible: !this.state.popoverVisible
        });

        // Tell parent (Document) about new popover state
        this.props.onPopoverClick({popoverVisible: !this.state.popoverVisible});
    },

    render: function() {
        var context = this.props.context;
        var cx = React.addons.classSet;
        var popoverClass = cx({
            "key-value-popover": true,
            "active": this.state.popoverVisible
        });
        var keyClass = cx({
            "key-value-trigger": true,
            "active": this.state.popoverVisible
        });

        return (
            <div className="document-info">
                <dl className={keyClass}>
                    <a href="#" onClick={this.handleClick}>
                        <dt>Lab</dt>
                        <dd>{context.lab.title}</dd>
                        <i className="icon icon-chevron-up"></i>
                    </a>
                </dl>
                <dl className={popoverClass}>
                    <dt>Caption</dt>
                    {context.caption ? <dd>{context.caption}</dd> : <dd><em>No caption</em></dd>}

                    <dt>Submitted by</dt>
                    <dd>{context.submitted_by.title}</dd>

                    <dt>Grant</dt>
                    <dd>{context.award.name}</dd>
                </dl>
            </div>
        );
    }
});


var Document = module.exports.Document = React.createClass({
    handlePopoverClick: function(popoverVisible) {
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
            if (context.attachment.type.split('/', 1)[0] == 'image') {
                imgClass = 'characterization-img';
                src = attachmentHref;
                height = context.attachment.height;
                width = context.attachment.width;
                alt = "Characterization Image";
            } else if (context.attachment.type == "application/pdf"){
                src = "/static/img/file-pdf.png";
                alt = "Characterization PDF Icon";
            } else {
                src = "/static/img/file.png";
                alt = "Characterization Icon";
            }
            figure = (
                <a data-bypass="true" href={attachmentHref}>
                    <img className={imgClass} src={src} height={height} width={width} alt={alt} />
                </a>
            );
            download = (
                <a data-bypass="true" className="dl-bar" href={attachmentHref} download={context.attachment.download}>
                    {context.attachment.download}
                    <i className="icon icon-download"></i>
                </a>
            );
        } else {
            src = "/static/img/file-broken.png";
            alt = "Characterization File Broken Icon";
            figure = (
                <img className={imgClass} src={src} height={height} width={width} alt={alt} />
            );
            download = (
                <em>Document not available</em>
            );
        }

        return (
            <section className="span4 type-document view-detail panel status-none">
                <figure>
                    {figure}
                </figure>
                <div className="document-intro">
                    <h3 className="sentence-case">{context.document_type}</h3>
                    <p>{context.description}</p>
                </div>
                {download}
                <PopoverTrigger context={context} onPopoverClick={this.handlePopoverClick} />
            </section>
        );
    }
});

globals.panel_views.register(Document, 'document');
globals.panel_views.register(Document, 'biosample_characterization');
