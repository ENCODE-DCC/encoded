'use strict';
var React = require('react');
var globals = require('./globals');
var fetched = require('./fetched');
var form = require('../libs/bootstrap/form');
var parseAndLogError = require('./mixins').parseAndLogError;

var Input = form.Input;
var InputMixin = form.InputMixin;


var hpoValues = [
    {value: 'hp-0000006', text: 'Autosomal dominant inheritance'},
    {value: 'hp-0012275', text: 'Autosomal dominant inheritance with maternal imprinting'},
    {value: 'hp-0012274', text: 'Autosomal dominant inheritance with paternal imprinting'},
    {value: 'hp-0000007', text: 'Autosomal recessive inheritance'},
    {value: 'autosomal-unknown', text: 'Autosomal unknown'},
    {value: 'codominant', text: 'Codominant'},
    {value: 'hp-0003743', text: 'Genetic anticipation'},
    {value: 'hp-0001427', text: 'Mitochondrial inheritance'},
    {value: 'hp-0001470', text: 'Sex-limited autosomal dominant'},
    {value: 'hp-0001428', text: 'Somatic mutation'},
    {value: 'hp-0003745', text: 'Sporadic'},
    {value: 'hp-0001423', text: 'X-linked dominant inheritance'},
    {value: 'hp-0001417', text: 'X-linked inheritance'},
    {value: 'hp-0001419', text: 'X-linked recessive inheritance'},
    {value: 'hp-0001450', text: 'Y-linked inheritance'},
    {value: 'other', text: 'Other'}
];


var CreateGeneDisease = React.createClass({
    mixins: [InputMixin],

    contextTypes: {
        fetch: React.PropTypes.func,
        navigate: React.PropTypes.func
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
        this.setFormValue('hgncgene', this.refs.hgncgene.getValue());
        this.setFormValue('orphanetid', this.refs.orphanetid.getValue());
        this.setFormValue('omimid', this.refs.omimid.getValue());
        this.setFormValue('hpo', this.refs.hpo.getValue());
        if (this.validateForm()) {
            var orphaId = this.getFormValue('orphanetid').match(/^ORPHA([0-9]{1,6})$/i)[1];

            // Verify orphanet ID exists in DB
            var url = '/diseases/' + orphaId;
            var request = this.context.fetch(url, {
                headers: {'Accept': 'application/json'}
            });
            request.then(function(response) {
                if (!response.ok) { 
                    throw response;
                }
                return response.json();
            })
            .catch(function() {
                parseAndLogError.bind(undefined, 'fetchedRequest');
                this.setFormErrors('orphanetid', 'Orphanet ID not found');
            }.bind(this))
            .then(this.receive);
        }
    },

    // Receive data from JSON request.
    receive: function(data) {
        console.log('data: %o', data);
        if (data) {
            this.context.navigate('/curation-central');
        }
    },

    render: function() {
        return (
            <div className="container">
                <h1>{this.props.context.title}</h1>
                <form onSubmit={this.submitForm} className="form-horizontal form-std form-create-gene-disease col-md-8 col-md-offset-2 col-sm-9 col-sm-offset-1">
                    <div className="row">
                        <Input type="text" id="hgncgene" ref="hgncgene" label={<LabelHgncGene />}
                            error={this.getFormError('hgncgene')} clearError={this.clrFormErrors.bind(null, 'hgncgene')}
                            labelClassName="col-sm-5 control-label" wrapperClassName="col-sm-7" groupClassName="form-group" required />
                        <Input type="text" id="orphanetid" ref="orphanetid" label={<LabelOrphanetId />}
                            error={this.getFormError('orphanetid')} clearError={this.clrFormErrors.bind(null, 'orphanetid')}
                            labelClassName="col-sm-5 control-label" wrapperClassName="col-sm-7" groupClassName="form-group" inputClassName="uppercase-input" required />
                        <Input type="select" id="hpo" ref="hpo" label="Mode of Inheritance"
                            labelClassName="col-sm-5 control-label" wrapperClassName="col-sm-7" groupClassName="form-group" required>
                            {hpoValues.map(function(v, i) {
                                return <option key={v.value} value={v.value}>{v.text}</option>;
                            })}
                        </Input>
                        <Input type="text" id="omimid" ref="omimid" label={<LabelOmimId />}
                            error={this.getFormError('omimid')} clearError={this.clrFormErrors.bind(null, 'omim-id')}
                            labelClassName="col-sm-5 control-label" wrapperClassName="col-sm-7" groupClassName="form-group" />
                        <Input type="submit" wrapperClassName="pull-right" id="submit" />
                    </div>
                </form>
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

var LabelOmimId = React.createClass({
    render: function() {
        return <span>Enter <a href="http://www.omim.org/" target="_blank" title="Online Mendelian Inheritance in Man home page in a new tab">OMIM</a> phenotype ID</span>;
    }
});
