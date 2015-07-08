'use strict';
var React = require('react');
var _ = require('underscore');
var globals = require('./globals');
var fetched = require('./fetched');
var form = require('../libs/bootstrap/form');
var panel = require('../libs/bootstrap/panel');
var parseAndLogError = require('./mixins').parseAndLogError;

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
    mixins: [FormMixin],

    contextTypes: {
        fetch: React.PropTypes.func,
        navigate: React.PropTypes.func
    },

    getHpoText: function(value) {
        var matchingValue = _(hpoValues).find(function(hpoValue) {
            return hpoValue.value === value;
        });
        return matchingValue ? matchingValue.text : '';
    },

    // Form content validation
    validateForm: function() {
        // Check if required fields have values
        var valid = this.validateRequired();

        // Check if orphanetid 
        if (valid) {
            valid = this.getFormValue('orphanetid').match(/^ORPHA[0-9]{1,6}$/i);
            if (!valid) {
                this.setFormErrors('orphanetid', 'Use the form ORPHAxxxx');
            }
        }
        return valid;
    },

    // When the form is submitted...
    submitForm: function(e) {
        e.preventDefault(); // Don't run through HTML submit handler

        // Get values from form and validate them
        this.setFormValue('hgncgene', this.refs.hgncgene.getValue().toUpperCase());
        this.setFormValue('orphanetid', this.refs.orphanetid.getValue());
        this.setFormValue('hpo', this.refs.hpo.getValue());
        if (this.validateForm()) {
            var orphaId = this.getFormValue('orphanetid').match(/^ORPHA([0-9]{1,6})$/i)[1];
            var geneId = this.getFormValue('hgncgene');

            // Verify user-entered orphanet ID and HGNC gene exist in DB. Start by doing JSON
            // requests for both and getting back their promises.
            var orphaRequest = this.context.fetch('/diseases/' + orphaId, {
                headers: {'Accept': 'application/json'}
            });
            var geneRequest = this.context.fetch('/genes/' + geneId, {
                headers: {'Accept': 'application/json'}
            });

            // Handle server responses for orphanet ID and HGNC gene ID through their promises.
            var orphaJson = orphaRequest.then(response => {
                // Received Orphanet ID response or error. If the response is fine, request
                // the JSON in a promise.
                if (!response.ok) { 
                    this.setFormErrors('orphanetid', 'Orphanet ID not found');
                    throw response;
                }
                return response.json();
            });
            var geneJson = geneRequest.then(response => {
                // Received HGNC gene response or error. If the response is fine, request
                // the JSON in a promise.
                if (!response.ok) { 
                    this.setFormErrors('hgncgene', 'HGNC gene symbol not found');
                    throw response;
                }
                return response.json();
            });

            // Once both json() promises return, handle their data. If either errors, use the catch case.
            Promise.all([orphaJson, geneJson])
            .then(this.createGdm)
            .catch(function(e) {
                parseAndLogError.bind(undefined, 'fetchedRequest');
            });
        }
    },

    // Receive data from JSON request.
    createGdm: function(data) {
        // Put together the new GDM object with form data and other info
        var value = {
            gdmId: (Math.floor(Math.random() * (9999 - 1000 + 1)) + 1000) + '',
            gene: this.getFormValue('hgncgene'),
            disease: this.getFormValue('orphanetid').match(/^ORPHA([0-9]{1,6})$/i)[1],
            modeInheritance: this.getHpoText(this.getFormValue('hpo')),
            owner: this.props.session['auth.userid'],
            status: 'Creation',
            dateTime: new Date().toISOString()
        };

        // Post the new data to the DB. fetch returns a JS promise.
        var request = this.context.fetch('/gdm/', {
            method: 'POST',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(value)
        });
        request.then(response => {
            // GDM DB object creation done. Throw error or get JSON from response
            if (!response.ok) { throw response; }
            return response.json();
        })
        .catch(parseAndLogError.bind(undefined, 'putRequest'))
        .then(data => {
            var uuid = data['@graph'][0].uuid;
            this.context.navigate('/curation-central/' + '?gdm=' + uuid);
        });
    },

    render: function() {
        return (
            <div className="container">
                <h1>{this.props.context.title}</h1>
                <div className="col-md-8 col-md-offset-2 col-sm-9 col-sm-offset-1 form-create-gene-disease">
                    <Panel>
                        <Form submitHandler={this.submitForm} formClassName="form-horizontal form-std">
                            <div className="row">
                                <Input type="text" ref="hgncgene" label={<LabelHgncGene />}
                                    error={this.getFormError('hgncgene')} clearError={this.clrFormErrors.bind(null, 'hgncgene')}
                                    labelClassName="col-sm-5 control-label" wrapperClassName="col-sm-7" groupClassName="form-group" inputClassName="uppercase-input" required />
                                <Input type="text" ref="orphanetid" label={<LabelOrphanetId />}
                                    error={this.getFormError('orphanetid')} clearError={this.clrFormErrors.bind(null, 'orphanetid')}
                                    labelClassName="col-sm-5 control-label" wrapperClassName="col-sm-7" groupClassName="form-group" inputClassName="uppercase-input" required />
                                <Input type="select" ref="hpo" label="Mode of Inheritance" defaultValue={hpoValues[0].value}
                                    error={this.getFormError('hpo')} clearError={this.clrFormErrors.bind(null, 'hpo')}
                                    labelClassName="col-sm-5 control-label" wrapperClassName="col-sm-7" groupClassName="form-group" required>
                                    {hpoValues.map(function(v, i) {
                                        return <option key={i} value={v.value} disabled={v.disabled ? 'disabled' : ''}>{v.text}</option>;
                                    })}
                                </Input>
                                <Input type="submit" wrapperClassName="pull-right" id="submit" />
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
        return <span>Enter <a href="http://www.orpha.net/" target="_blank" title="Orphanet home page in a new tab">Orphanet ID</a></span>;
    }
});
