'use strict';
var React = require('react');
var url = require('url');
var _ = require('underscore');
var panel = require('../libs/bootstrap/panel');
var form = require('../libs/bootstrap/form');
var globals = require('./globals');
var curator = require('./curator');

var CurationData = curator.CurationData;
var CurationNav = curator.CurationNav;
var PmidSummary = curator.PmidSummary;
var PanelGroup = panel.PanelGroup;
var Panel = panel.Panel;
var Input = form.Input;
var InputMixin = form.InputMixin;


// Temporary hard-coded data to display
var pmid_items = require('./testdata').pmid_items;
var country_codes = require('./testdata').country_codes;


var GroupCuration = React.createClass({
    render: function() {
        var currPmidItem;

        var queryParsed = this.props.href && url.parse(this.props.href, true).query;
        if (queryParsed && Object.keys(queryParsed).length) {
            // Find the first 'pmid' query string item, if any
            var pmidKey = _(Object.keys(queryParsed)).find(function(key) {
                return key === 'pmid';
            });
            var pmid = parseInt(queryParsed[pmidKey], 10);
            currPmidItem = _(pmid_items).find(function(item) {
                return item.id === pmid;
            });
        }

        return (
            <div>
                <CurationData />
                <div className="container">
                    {currPmidItem ?
                        <div className="panel-curator">
                            <PmidSummary pmidItem={currPmidItem} />
                        </div>
                    : null}
                    <div className="row group-curation-content">
                        <div className="col-sm-8">
                            <form className="form-horizontal">
                                <Panel>
                                    <GroupName />
                                </Panel>
                                <PanelGroup accordion>
                                    <Panel title="Common diseases &amp; phenotypes" open>
                                        <GroupCommonDiseases />
                                    </Panel>
                                </PanelGroup>
                                <PanelGroup accordion>
                                    <Panel title="Demographics">
                                        <GroupDemographics />
                                    </Panel>
                                </PanelGroup>
                            </form>
                        </div>
                        {currPmidItem ?
                            <div className="col-sm-4">
                                <CurationNav currPmidItem={currPmidItem} />
                            </div>
                        : null}
                    </div>
                </div>
            </div>
        );
    }
});

globals.curator_page.register(GroupCuration, 'curator_page', 'group-curation');


var GroupName = React.createClass({
    render: function() {
        return (
            <div className="row">
                <Input type="text" id="groupname" ref="groupname" label="Group name (optional):"
                    labelClassName="col-sm-5 control-label" wrapperClassName="col-sm-7" groupClassName="form-group" />
            </div>
        );
    }
});


var GroupCommonDiseases = React.createClass({
    render: function() {
        return (
            <div className="row">
                <Input type="text" id="orphanetid" ref="orphanetid" label={<LabelOrphanetId />}
                    labelClassName="col-sm-5 control-label" wrapperClassName="col-sm-7" groupClassName="form-group" required />
                <Input type="text" id="hpoid" ref="hpoid" label={<LabelHpoId />}
                    labelClassName="col-sm-5 control-label" wrapperClassName="col-sm-7" groupClassName="form-group" inputClassName="uppercase-input" />
                <Input type="textarea" id="phenoterms" ref="phenoterms" label={<LabelPhenoTerms />} rows="5"
                    labelClassName="col-sm-5 control-label" wrapperClassName="col-sm-7" groupClassName="form-group" />
                <h4>Enter <em>phenotypes that are NOT present in Group</em> if they are specifically noted in the paper</h4>
                <Input type="text" id="nothpoid" ref="nothpoid" label={<LabelHpoId not />}
                    labelClassName="col-sm-5 control-label" wrapperClassName="col-sm-7" groupClassName="form-group" inputClassName="uppercase-input" />
                <Input type="textarea" id="phenoterms" ref="phenoterms" label={<LabelPhenoTerms not />} rows="5"
                    labelClassName="col-sm-5 control-label" wrapperClassName="col-sm-7" groupClassName="form-group" />
            </div>
        );
    }
});


// HTML labels for inputs follow.
var LabelOrphanetId = React.createClass({
    render: function() {
        return <span><a href="http://www.orpha.net/" target="_blank" title="Orphanet home page in a new tab">Orphanet</a> common diagnosis:</span>;
    }
});


// HTML labels for inputs follow.
var LabelHpoId = React.createClass({
    propTypes: {
        not: React.PropTypes.bool
    },

    render: function() {
        return <span>{this.props.not ? <span span style={{color: 'red'}}>NOT</span> : null} <a href="http://compbio.charite.de/phenexplorer/" target="_blank" title="PhenExplorer home page in a new tab">HPO</a> ID(s):</span>;
    }
});

// HTML labels for inputs follow.
var LabelPhenoTerms = React.createClass({
    propTypes: {
        not: React.PropTypes.bool
    },

    render: function() {
        return <span>Free text{this.props.not ? <span style={{color: 'red'}}> NOT</span> : null} phenotype terms:</span>;
    }
});


var GroupDemographics = React.createClass({
    render: function() {
        return (
            <div className="row">
                <Input type="text" id="malecount" ref="malecount" label="# males:"
                    labelClassName="col-sm-5 control-label" wrapperClassName="col-sm-7" groupClassName="form-group" />
                <Input type="text" id="femalecount" ref="malecount" label="# females:"
                    labelClassName="col-sm-5 control-label" wrapperClassName="col-sm-7" groupClassName="form-group" />
                <Input type="select" id="country" ref="country" label="Country of Origin:"
                    labelClassName="col-sm-5 control-label" wrapperClassName="col-sm-7" groupClassName="form-group">
                    {country_codes.map(function(country_code) {
                        return <option key={country_code.code} value={country_code.code}>{country_code.name}</option>;
                    })}
                </Input>
                <Input type="select" id="ethnicity" ref="ethnicity" label="Ethnicity:"
                    labelClassName="col-sm-5 control-label" wrapperClassName="col-sm-7" groupClassName="form-group">
                    <option value="hispanic">Hispanic or Latino</option>
                    <option value="nonhispanic">Not Hispanic or Latino</option>
                </Input>
                <Input type="select" id="race" ref="race" label="Race:"
                    labelClassName="col-sm-5 control-label" wrapperClassName="col-sm-7" groupClassName="form-group">
                    <option value="nativeamerican">American Indian or Alaska Native</option>
                    <option value="asian">Asian</option>
                    <option value="black">Black</option>
                    <option value="pacificislander">Native Hawaiian or Other Pacific Islander</option>
                    <option value="white">White</option>
                    <option value="mixed">Mixed</option>
                    <option value="unknown">Unknown</option>
                </Input>
                <h4>Age Range</h4>
                <div className="demographics-age-range">
                    <Input type="select" id="agerangetype" ref="agerangetype" label="Type:"
                        labelClassName="col-sm-5 control-label" wrapperClassName="col-sm-7" groupClassName="form-group">
                        <option value="onset">Onset</option>
                        <option value="report">Report</option>
                        <option value="diagnosis">Diagnosis</option>
                        <option value="death">Death</option>
                    </Input>
                    <div className="form-inline">
                    </div>
                </div>
            </div>
        );
    }
});
