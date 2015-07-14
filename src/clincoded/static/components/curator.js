'use strict';
var React = require('react');
var _ = require('underscore');
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
        var article = this.props.article;
        var date = (/^([\d]{4})(.*?)$/).exec(article.date);

        return (
            <p>
                {article.firstAuthor + '. '}
                {article.title + ' '}
                {this.props.displayJournal ? <i>{article.journal + '. '}</i> : null}
                <strong>{date[1]}</strong>{date[2]}
            </p>
        );
    }
});


var CurationPalette = module.exports.CurationPalette = React.createClass({
    propTypes: {
        article: React.PropTypes.object
    },

    render: function() {
        return (
            <Panel panelClassName="panel-evidence-group" title={'Evidence for PMID:' + this.props.article.pmid}>
                <Panel title={<CurationPaletteTitles title="Group" />} panelClassName="panel-evidence">Stuff</Panel>
                <Panel title={<CurationPaletteTitles title="Family" />} panelClassName="panel-evidence">Stuff</Panel>
                <Panel title={<CurationPaletteTitles title="Individual" />} panelClassName="panel-evidence">Stuff</Panel>
                <Panel title={<CurationPaletteTitles title="Functional" />} panelClassName="panel-evidence">Stuff</Panel>
            </Panel>
        );
    }
});


// Title for each section of the curation palette. Contains the title and an Add button.
var CurationPaletteTitles = React.createClass({
    propTypes: {
        title: React.PropTypes.string // Title to display
    },

    render: function() {
        return (
            <a href="#" className="clearfix">
                <h4 className="pull-left">{this.props.title}</h4>
                <i className="icon icon-plus-circle pull-right"></i>
            </a>
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
                            <dd><a href={external_url_map['HGNC'] + gene.hgncId} target="_blank" title={'HGNC page for ' + gene.hgncId + ' in a new window'}>{gene.hgncId}</a></dd>
                            <dd>EntrezID:<a href={external_url_map['Entrez'] + gene.entrezId} target="_blank" title={'NCBI page for gene ' + gene.entrezId + ' in a new window'}>{gene.entrezId}</a></dd>
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

        return (
            <div className="col-xs-12 col-sm-3 gutter-exc">
                <div className="curation-data-disease">
                    {disease ?
                        <dl>
                            <dt>{disease.term}</dt>
                            <dd><a href="http://www.orpha.net/" target="_blank" title="Orphanet home page in a new window">Orphanet</a> ID: <a href={external_url_map['OrphaNet'] + disease.orphaNumber} target="_blank" title={'Orphanet page for ORPHA' + disease.orphaNumber + ' in a new window'}>{disease.orphaNumber}</a></dd>
                            <dd>
                                <a href="http://omim.org/" target="_blank" title="Online Mendelian Inheritance in Man home page in a new window">OMIM</a> ID: {this.props.omimId ?
                                    <a href={external_url_map['OMIM'] + this.props.omimId} title={'Open Online Mendelian Inheritance in Man page for OMIM ID ' + this.props.omimId + ' in a new window'} target="_blank">
                                        {this.props.omimId}
                                    </a>
                                : 'not set'}&nbsp;
                                <Modal title="Add/Change OMIM ID">
                                    <a modal={<AddOmimIdModal closeModal={this.closeModal} updateOmimId={this.props.updateOmimId} />} href="#">Edit OMIM phenotype ID</a>
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
        // Check if required fields have values
        var valid = this.validateRequired();

        // Valid if the field has only 10 or fewer digits 
        if (valid) {
            valid = this.getFormValue('omimid').match(/^[0-9]{1,10}$/i);
            if (!valid) {
                this.setFormErrors('omimid', 'Only numbers allowed');
            }
        }
        return valid;
    },

    // Called when the modal form’s submit button is clicked. Handles validation and triggering
    // the process to add an article.
    submitForm: function(e) {
        e.preventDefault(); e.stopPropagation(); // Don't run through HTML submit handler
        this.setFormValue('omimid', this.refs.omimid.getValue());
        if (this.validateForm()) {
            // Form is valid -- we have a good PMID. Fetch the article with that PMID
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

    render: function() {
        var gdm = this.props.gdm;
        var annotationOwners = _.uniq(gdm.annotations.map(function(annotation) {
            return annotation.owner;
        })).sort();

        return (
            <div className="col-xs-12 col-sm-6 gutter-exc">
                <div className="curation-data-curator">
                    {gdm ?
                        <dl>
                            <dt>{gdm.status} – {gdm.owner} – {gdm.dateTime}</dt>
                            <dd>
                                {annotationOwners.map(function(owner, i) {
                                    return (
                                        <span key={i}>
                                            {i > 0 ? ', ' : ''}
                                            {owner}
                                        </span>
                                    );
                                })}
                            </dd>
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
