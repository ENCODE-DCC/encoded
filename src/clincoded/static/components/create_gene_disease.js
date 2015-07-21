'use strict';
var React = require('react');
var _ = require('underscore');
var moment = require('moment');
var globals = require('./globals');
var fetched = require('./fetched');
var form = require('../libs/bootstrap/form');
var panel = require('../libs/bootstrap/panel');
var parseAndLogError = require('./mixins').parseAndLogError;
var RestMixin = require('./rest').RestMixin;

var Form = form.Form;
var FormMixin = form.FormMixin;
var Input = form.Input;
var Panel = panel.Panel;


var hpoValues = [
    {value: '', text: 'Select', disabled: true},
    {value: '', text: '', disabled: true},
    {value: 'hp-0000006', text: 'Autosomal dominant inheritance (HP:0000006)'},
    {value: 'hp-0012275', text: 'Autosomal dominant inheritance with maternal imprinting (HP:0012275)'},
    {value: 'hp-0012274', text: 'Autosomal dominant inheritance with paternal imprinting (HP:0012274)'},
    {value: 'hp-0000007', text: 'Autosomal recessive inheritance (HP:0000007)'},
    {value: 'autosomal-unknown', text: 'Autosomal unknown'},
    {value: 'codominant', text: 'Codominant'},
    {value: 'hp-0003743', text: 'Genetic anticipation (HP:0003743)'},
    {value: 'hp-0001427', text: 'Mitochondrial inheritance (HP:0001427)'},
    {value: 'hp-0001470', text: 'Sex-limited autosomal dominant (HP:0001470)'},
    {value: 'hp-0001428', text: 'Somatic mutation (HP:0001428)'},
    {value: 'hp-0003745', text: 'Sporadic (HP:0003745)'},
    {value: 'hp-0001423', text: 'X-linked dominant inheritance (HP:0001423)'},
    {value: 'hp-0001417', text: 'X-linked inheritance (HP:0001417)'},
    {value: 'hp-0001419', text: 'X-linked recessive inheritance (HP:0001419)'},
    {value: 'hp-0001450', text: 'Y-linked inheritance (HP:0001450)'},
    {value: 'other', text: 'Other'}
];


var CreateGeneDisease = React.createClass({
    mixins: [FormMixin, RestMixin],

    contextTypes: {
        fetch: React.PropTypes.func,
        navigate: React.PropTypes.func
    },

    // Form content validation
    validateForm: function() {
        // Start with default validation
        var valid = this.validateDefault();

        // Check if orphanetid 
        if (valid) {
            valid = this.getFormValue('orphanetid').match(/^ORPHA[0-9]{1,6}$/i);
            if (!valid) {
                this.setFormErrors('orphanetid', 'Use Orphanet IDs (e.g. ORPHA15)');
            }
        }
        return valid;
    },

    // When the form is submitted...
    submitForm: function(e) {
        e.preventDefault(); e.stopPropagation(); // Don't run through HTML submit handler

        // Get values from form and validate them
        this.saveFormValue('hgncgene', this.refs.hgncgene.getValue().toUpperCase());
        this.saveFormValue('orphanetid', this.refs.orphanetid.getValue());
        var hpoDOMNode = this.refs.hpo.refs.input.getDOMNode();
        this.saveFormValue('hpo', hpoDOMNode[hpoDOMNode.selectedIndex].text);
        if (this.validateForm()) {
            // Get the free-text values for the Orphanet ID and the Gene ID to check against the DB
            var orphaId = this.getFormValue('orphanetid').match(/^ORPHA([0-9]{1,6})$/i)[1];
            var geneId = this.getFormValue('hgncgene');
            var mode = this.getFormValue('hpo');

            // Get the disease and gene objects corresponding to the given Orphanet and Gene IDs in parallel.
            // If either error out, set the form error fields
            this.getRestDatas([
                '/diseases/' + orphaId,
                '/genes/' + geneId
            ], [
                function() { this.setFormErrors('orphanetid', 'Orphanet ID not found'); }.bind(this),
                function() { this.setFormErrors('hgncgene', 'HGNC gene symbol not found'); }.bind(this)
            ]).then(data => {
                // Load GDM if one with matching gene/disease/mode already exists
                return this.getRestData(
                    '/search/?type=gdm&disease.orphaNumber=' + orphaId + '&gene.symbol=' + geneId + '&modeInheritance=' + mode
                ).then(gdmSearch => {
                    // Found matching GDM. Get its UUID and pass it to curation central page
                    if (gdmSearch.total === 0) {
                        throw gdmSearch;
                    } else {
                        var uuid = gdmSearch['@graph'][0].uuid;
                        this.context.navigate('/curation-central/?gdm=' + uuid);
                    }
                });
            }).catch(e => {
                if (e && e.total === 0) {
                    // No matching GDM found; make a new GDM
                    this.createGdm();
                } else {
                    // Some unexpected error happened
                    parseAndLogError.bind(undefined, 'fetchedRequest');
                }
            });
        }
    },

    // Create the GDM once its disease and gene data have been verified to exist.
    createGdm: function() {
        // Put together the new GDM object with form data and other info
        var newGdm = {
            gene: this.getFormValue('hgncgene'),
            disease: this.getFormValue('orphanetid').match(/^ORPHA([0-9]{1,6})$/i)[1],
            modeInheritance: this.getFormValue('hpo'),
            owner: this.props.session['auth.userid'],
            status: 'Creation',
            dateTime: moment().format()
        };

        // Post the new GDM to the DB. Once promise returns, go to /curation-central page with the UUID
        // of the new GDM in the query string.
        this.postRestData('/gdm/', newGdm).then(data => {
            var uuid = data['@graph'][0].uuid;
            this.context.navigate('/curation-central/?gdm=' + uuid);
        }).catch(parseAndLogError.bind(undefined, 'putRequest'));
    },

    render: function() {
        return (
            <div className="container">
                <h1>{this.props.context.title}</h1>
                <div className="col-md-8 col-md-offset-2 col-sm-9 col-sm-offset-1 form-create-gene-disease">
                    <Panel panelClassName="panel-create-gene-disease">
                        <Form submitHandler={this.submitForm} formClassName="form-horizontal form-std">
                            <div className="row">
                                <Input type="text" ref="hgncgene" label={<LabelHgncGene />} placeholder="e.g. DICER1"
                                    error={this.getFormError('hgncgene')} clearError={this.clrFormErrors.bind(null, 'hgncgene')}
                                    labelClassName="col-sm-5 control-label" wrapperClassName="col-sm-7" groupClassName="form-group" inputClassName="uppercase-input" required />
                                <Input type="text" ref="orphanetid" label={<LabelOrphanetId />} placeholder="e.g. ORPHA15"
                                    error={this.getFormError('orphanetid')} clearError={this.clrFormErrors.bind(null, 'orphanetid')}
                                    labelClassName="col-sm-5 control-label" wrapperClassName="col-sm-7" groupClassName="form-group" inputClassName="uppercase-input" required />
                                <Input type="select" ref="hpo" label="Mode of Inheritance" defaultValue={hpoValues[0].value}
                                    error={this.getFormError('hpo')} clearError={this.clrFormErrors.bind(null, 'hpo')}
                                    labelClassName="col-sm-5 control-label" wrapperClassName="col-sm-7" groupClassName="form-group" required>
                                    {hpoValues.map(function(v, i) {
                                        return <option key={i} value={v.value} disabled={v.disabled ? 'disabled' : ''}>{v.text}</option>;
                                    })}
                                </Input>
                                <Input type="submit" inputClassName="btn-primary pull-right" id="submit" />
                            </div>
                        </Form>
                    </Panel>
                </div>
            </div>
        );
    }
});

globals.curator_page.register(CreateGeneDisease, 'curator_page', 'create-gene-disease');


// HTML labels for inputs follow.
var LabelHgncGene = React.createClass({
    render: function() {
        return <span>Enter <a href="http://www.genenames.org" target="_blank" title="HGNC home page in a new tab">HGNC</a> gene symbol</span>;
    }
});

var LabelOrphanetId = React.createClass({
    render: function() {
        return <span>Enter <a href="http://www.orpha.net/" target="_blank" title="Orphanet home page in a new tab">Orphanet</a> ID</span>;
    }
});
