'use strict';
var React = require('react');
var _ = require('underscore');
var moment = require('moment');
var modal = require('../libs/bootstrap/modal');
var panel = require('../libs/bootstrap/panel');
var form = require('../libs/bootstrap/form');
var globals = require('./globals');

var Panel = panel.Panel;
var Modal = modal.Modal;
var ModalMixin = modal.ModalMixin;
var Form = form.Form;
var FormMixin = form.FormMixin;
var Input = form.Input;
var external_url_map = globals.external_url_map;


var CuratorPage = module.exports.CuratorPage = React.createClass({
    render: function() {
        var context = this.props.context;

        var CuratorPageView = globals.curator_page.lookup(context, context.name);
        var content = <CuratorPageView {...this.props} />;
        return (
            <div>{content}</div>
        );
    }
});

globals.content_views.register(CuratorPage, 'curator_page');


// Curation data header for Gene:Disease
var CurationData = module.exports.CurationData = React.createClass({
    propTypes: {
        gdm: React.PropTypes.object, // GDM data to display
        omimId: React.PropTypes.string, // OMIM ID to display
        updateOmimId: React.PropTypes.func // Function to call when OMIM ID changes
    },

    render: function() {
        var gdm = this.props.gdm;

        if (gdm && Object.keys(gdm).length > 0 && gdm['@type'][0] === 'gdm') {
            var gene = this.props.gdm.gene;
            var disease = this.props.gdm.disease;
            var mode = this.props.gdm.modeInheritance.match(/^(.*?)(?: \(HP:[0-9]*?\)){0,1}$/)[1];

            return (
                <div>
                    <div className="curation-data-title">
                        <div className="container">
                            <h1>{gene.symbol} – {disease.term}</h1>
                            <h2>{mode}</h2>
                        </div>
                    </div>
                    <div className="container curation-data">
                        <div className="row equal-height">
                            <GeneCurationData gene={gene} />
                            <DiseaseCurationData gdm={this.props.gdm} omimId={this.props.omimId} updateOmimId={this.props.updateOmimId} />
                            <CuratorCurationData gdm={this.props.gdm} />
                        </div>
                    </div>
                </div>
            );
        } else {
            return null;
        }
    }
});


// Displays the PM item summary, with authors, title, citation
var PmidSummary = module.exports.PmidSummary = React.createClass({
    propTypes: {
        article: React.PropTypes.object, // Article object to display
        displayJournal: React.PropTypes.bool // T to display article journal
    },

    render: function() {
        var authors;
        var article = this.props.article;
        var date = (/^([\d]{4})(.*?)$/).exec(article.date);

        if (article.authors && article.authors.length) {
            authors = article.authors[0] + (article.authors.length > 1 ? ' et al. ' : '. ');
        }

        return (
            <p>
                {authors}
                {article.title + ' '}
                {this.props.displayJournal ? <i>{article.journal + '. '}</i> : null}
                <strong>{date[1]}</strong>{date[2]}
            </p>
        );
    }
});


var CurationPalette = module.exports.CurationPalette = React.createClass({
    propTypes: {
        annotation: React.PropTypes.object.isRequired, // Current annotation that owns the article
        gdm: React.PropTypes.object.isRequired, // Current GDM that owns the given annotation
        session: React.PropTypes.object // Session object
    },

    render: function() {
        var annotation = this.props.annotation;
        var session = this.props.session;
        var curatorMatch = annotation.owner === (session && session.user_properties && session.user_properties.email);
        var url = curatorMatch ? ('/group-curation/?gdm=' + this.props.gdm.uuid + '&evidence=' + this.props.annotation.uuid) : null;

        return (
            <Panel panelClassName="panel-evidence-groups" title={'Evidence for PMID:' + this.props.annotation.article.pmid}>
                <Panel title={<CurationPaletteTitles title="Group" url={url} />} panelClassName="panel-evidence">
                    {annotation.groups && annotation.groups.map(function(group) {
                        return (
                            <div className="panel-evidence-group" key={group.uuid}>
                                <h5>{group.label}</h5>
                                <div className="evidence-curation-info">
                                    <p className="evidence-curation-info">{annotation.owner}</p>
                                    <p>{moment(annotation.dateTime).format('YYYY MMM DD, h:mm a')}</p>
                                </div>
                                <a href={'/group/' + group.uuid} target="_blank">View</a>{curatorMatch ? <span> | <a href={'/group-curation/?gdm=' + this.props.gdm.uuid + '&evidence=' + annotation.uuid + '&group=' + group.uuid}>Edit</a></span> : null}
                            </div>
                        );
                    }.bind(this))}
                </Panel>
            </Panel>
        );
    }
});


// Title for each section of the curation palette. Contains the title and an Add button.
var CurationPaletteTitles = React.createClass({
    propTypes: {
        title: React.PropTypes.string, // Title to display
        url: React.PropTypes.string // URL for panel title click to go to.
    },

    render: function() {
        return (
            <div>
                {this.props.url ?
                    <a href={this.props.url} className="curation-palette-title clearfix">
                        <h4 className="pull-left">{this.props.title}</h4>
                        <i className="icon icon-plus-circle pull-right"></i>
                    </a>
                :
                    <span className="curation-palette-title clearfix">
                        <h4 className="pull-left">{this.props.title}</h4>
                    </span>
                }
            </div>
        );
    }
});


// Display the gene section of the curation data
var GeneCurationData = React.createClass({
    propTypes: {
        gene: React.PropTypes.object // Object to display
    },

    render: function() {
        var gene = this.props.gene;

        return (
            <div className="col-xs-12 col-sm-3 gutter-exc">
                <div className="curation-data-gene">
                    {gene ?
                        <dl>
                            <dt>{gene.symbol}</dt>
                            <dd>HGNC Symbol: <a href={external_url_map['HGNC'] + gene.hgncId} target="_blank" title={'HGNC page for ' + gene.symbol + ' in a new window'}>{gene.symbol}</a></dd>
                            <dd>NCBI Gene ID: <a href={external_url_map['Entrez'] + gene.entrezId} target="_blank" title={'NCBI page for gene ' + gene.entrezId + ' in a new window'}>{gene.entrezId}</a></dd>
                        </dl>
                    : null}
                </div>
            </div>
        );
    }
});


// Display the disease section of the curation data
var DiseaseCurationData = React.createClass({
    mixins: [ModalMixin],

    propTypes: {
        gdm: React.PropTypes.object, // Object to display
        omimId: React.PropTypes.string, // OMIM ID to display
        updateOmimId: React.PropTypes.func // Function to call when OMIM ID changes
    },

    render: function() {
        var gdm = this.props.gdm;
        var disease = gdm.disease;
        var addEdit = this.props.omimId ? 'Edit' : 'Add';

        return (
            <div className="col-xs-12 col-sm-3 gutter-exc">
                <div className="curation-data-disease">
                    {disease ?
                        <dl>
                            <dt>{disease.term}</dt>
                            <dd>Orphanet ID: <a href={external_url_map['OrphaNet'] + disease.orphaNumber} target="_blank" title={'Orphanet page for ORPHA' + disease.orphaNumber + ' in a new window'}>{'ORPHA' + disease.orphaNumber}</a></dd>
                            <dd>
                                <a href="http://omim.org/" target="_blank" title="Online Mendelian Inheritance in Man home page in a new window">OMIM</a> ID: {this.props.omimId ?
                                    <a href={external_url_map['OMIM'] + this.props.omimId} title={'Open Online Mendelian Inheritance in Man page for OMIM ID ' + this.props.omimId + ' in a new window'} target="_blank">
                                        {this.props.omimId}
                                    </a>
                                : null}&nbsp;
                                <Modal title="Add/Change OMIM ID" wrapperClassName="edit-omim-modal">
                                    <span>[</span><a modal={<AddOmimIdModal closeModal={this.closeModal} updateOmimId={this.props.updateOmimId} />} href="#">{addEdit}</a><span>]</span>
                                </Modal>
                            </dd>
                        </dl>
                    : null}
                </div>
            </div>
        );
    }
});


// The content of the Add PMID(s) modal dialog box
var AddOmimIdModal = React.createClass({
    mixins: [FormMixin],

    propTypes: {
        closeModal: React.PropTypes.func, // Function to call to close the modal
        updateOmimId: React.PropTypes.func // Function to call when we have a new OMIM ID
    },

    // Form content validation
    validateForm: function() {
        // Start with default validation
        var valid = this.validateDefault();

        // Valid if the field has only 10 or fewer digits 
        if (valid) {
            valid = this.getFormValue('omimid').match(/^[0-9]{1,10}$/i);
            if (!valid) {
                this.setFormErrors('omimid', 'Only numbers allowed');
            }
        }
        return valid;
    },

    // Called when the modal form’s submit button is clicked. Handles validation and updating the OMIM in the GDM.
    submitForm: function(e) {
        e.preventDefault(); e.stopPropagation(); // Don't run through HTML submit handler
        this.saveFormValue('omimid', this.refs.omimid.getValue());
        if (this.validateForm()) {
            // Form is valid -- we have a good OMIM ID. Close the modal and update the current GDM's OMIM ID
            this.props.closeModal();
            var enteredOmimId = this.getFormValue('omimid');
                this.props.updateOmimId(enteredOmimId);
        }
    },

    // Called when the modal form's cancel button is clicked. Just closes the modal like
    // nothing happened.
    cancelForm: function(e) {
        e.preventDefault(); e.stopPropagation(); // Don't run through HTML submit handler
        this.props.closeModal();
    },

    render: function() {
        return (
            <Form submitHandler={this.submitForm} formClassName="form-std">
                <div className="modal-body">
                    <Input type="text" ref="omimid" label="Enter an OMIM ID"
                        error={this.getFormError('omimid')} clearError={this.clrFormErrors.bind(null, 'omim')}
                        labelClassName="control-label" groupClassName="form-group" required />
                </div>
                <div className='modal-footer'>
                    <Input type="cancel" inputClassName="btn-default btn-inline-spacer" cancelHandler={this.cancelForm} />
                    <Input type="submit" inputClassName="btn-primary btn-inline-spacer" title="Add/Change OMIM ID" />
                </div>
            </Form>
        );
    }
});


// Display the curator data of the curation data
var CuratorCurationData = React.createClass({
    propTypes: {
        gdm: React.PropTypes.object // GDM with curator data to display
    },

    // Return the latest annotation in the given GDM
    findLatestAnnotation: function() {
        var annotations = this.props.gdm.annotations;
        var latestAnnotation = {};
        var latestTime = 0;
        if (annotations && annotations.length) {
            annotations.forEach(function(annotation) {
                // Get Unix timestamp version of annotation's time and compare against the saved version.
                var time = moment(annotation.dateTime).format('x');
                if (latestTime < time) {
                    latestAnnotation = annotation;
                    latestTime = time;
                }
            });
        }
        return latestAnnotation;
    },

    render: function() {
        var gdm = this.props.gdm;
        var annotationOwners = _.uniq(gdm.annotations.map(function(annotation) {
            return annotation.owner;
        })).sort();
        var latestAnnotation = this.findLatestAnnotation();

        return (
            <div className="col-xs-12 col-sm-6 gutter-exc">
                <div className="curation-data-curator">
                    {gdm ?
                        <dl className="inline-dl clearfix">
                            <dt>Status: </dt><dd>{gdm.status}</dd>
                            <dt>Creator: </dt><dd><a href={'mailto:' + gdm.owner}>{gdm.owner}</a> – {moment(gdm.dateTime).format('YYYY MMM DD, h:mm a')}</dd>
                            {annotationOwners && annotationOwners.length ?
                                <div>
                                    <dt>Participants: </dt>
                                    <dd>
                                        {annotationOwners.map(function(owner, i) {
                                            return (
                                                <span key={i}>
                                                    {i > 0 ? ', ' : ''}
                                                    <a href={'mailto:' + owner}>{owner}</a>
                                                </span>
                                            );
                                        })}
                                    </dd>
                                    <dt>Last edited: </dt>
                                    <dd><a href={'mailto:' + latestAnnotation.owner}>{latestAnnotation.owner}</a> — {moment(latestAnnotation.dateTime).format('YYYY MMM DD, h:mm a')}</dd>
                                </div>
                            : null}
                        </dl>
                    : null}
                </div>
            </div>
        );
    }
});


// Display buttons to bring up the PubMed and doi-specified web pages.
// For now, no doi is available
var PmidDoiButtons = module.exports.PmidDoiButtons = React.createClass({
    propTypes: {
        pmid: React.PropTypes.string // Numeric string PMID for PubMed page
    },

    render: function() {
        var pmid = this.props.pmid;

        return (
            <div className="pmid-doi-btns">
                {pmid ? <a className="btn btn-primary" target="_blank" href={external_url_map['PubMed'] + pmid}>PubMed</a> : null}
            </div>
        );
    }
});
