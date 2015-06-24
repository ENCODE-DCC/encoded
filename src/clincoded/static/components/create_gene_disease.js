'use strict';
var React = require('react');
var globals = require('./globals');
var form = require('../libs/bootstrap/form');

var Input = form.Input;

var hpoValues = [
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
    render: function() {
        return (
            <div className="container">
                <h1>{this.props.context.title}</h1>
                <form className="form-horizontal form-std form-create-gene-disease col-md-8 col-md-offset-2 col-sm-9 col-sm-offset-1">
                    <div className="row">
                        <Input type="text" id="hgnc-gene" label={<LabelHgncGene />} labelClassName="col-sm-4 control-label" wrapperClassName="col-sm-8" groupClassName="form-group" />
                        <Input type="text" id="orphanet-id" label={<LabelOrphanetId />} labelClassName="col-sm-4 control-label" wrapperClassName="col-sm-8" groupClassName="form-group" />
                        <Input type="text" id="omim-id" label={<LabelOmimId />} labelClassName="col-sm-4 control-label" wrapperClassName="col-sm-8" groupClassName="form-group" />
                        <Input type="select" id="hpo" label="Mode of Inheritance" labelClassName="col-sm-4 control-label" wrapperClassName="col-sm-8" groupClassName="form-group" >
                            {hpoValues.map(function(v, i) {
                                return <option key={v.value} value={v.value}>{v.text}</option>;
                            })}
                        </Input>
                        <button className="btn btn-primary pull-right">Submit</button>
                    </div>
                </form>
            </div>
        );
    }
});

globals.curator_page.register(CreateGeneDisease, 'curator_page', 'create-gene-disease');


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
