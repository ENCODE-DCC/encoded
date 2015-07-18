'use strict';
var React = require('react');
var url = require('url');
var _ = require('underscore');
var panel = require('../libs/bootstrap/panel');
var form = require('../libs/bootstrap/form');
var globals = require('./globals');
var curator = require('./curator');
var parseAndLogError = require('./mixins').parseAndLogError;
var RestMixin = require('./rest').RestMixin;

var CurationData = curator.CurationData;
var CurationPalette = curator.CurationPalette;
var PmidSummary = curator.PmidSummary;
var PanelGroup = panel.PanelGroup;
var Panel = panel.Panel;
var Form = form.Form;
var FormMixin = form.FormMixin;
var Input = form.Input;
var InputMixin = form.InputMixin;
var PmidDoiButtons = curator.PmidDoiButtons;
var country_codes = globals.country_codes;


var GroupCuration = React.createClass({
    mixins: [FormMixin, RestMixin],

    contextTypes: {
        navigate: React.PropTypes.func
    },

    getInitialState: function() {
        return {
            gdm: {}, // GDM object given in UUID
            annotation: {} // Annotation object given in UUID
        };
    },

    // Retrieve the GDM and annotation objects with the given UUIDs from the DB. If successful, set the component
    // state to the retrieved objects to cause a rerender of the component.
    getGdmAnnotation: function(gdmUuid, annotationUuid) {
        this.getRestDatas([
            '/gdm/' + gdmUuid + '?frame=object',
            '/evidence/' + annotationUuid + '?frame=object'
        ]).then(data => {
            this.setState({gdm: data[0], annotation: data[1]});
        }).catch(parseAndLogError.bind(undefined, 'putRequest'));
    },

    // After the Group Curation page component mounts, grab the annotation UUID from the query
    // string and retrieve the corresponding annotation from the DB, if it exists.
    // Note, we have to do this after the component mounts because AJAX DB queries can't be
    // done from unmounted components.
    componentDidMount: function() {
        // See if there’s a GDM UUID to retrieve
        var annotationUuid, gdmUuid;

        var queryParsed = this.props.href && url.parse(this.props.href, true).query;
        if (queryParsed && Object.keys(queryParsed).length) {
            // Find the first 'gdm' query string item, if any
            var uuidKey = _(Object.keys(queryParsed)).find(function(key) {
                return key === 'evidence';
            });
            if (uuidKey) {
                // Got the GDM key for its UUID from the query string. Now use it to retrieve that GDM
                annotationUuid = queryParsed[uuidKey];
                if (typeof annotationUuid === 'object') {
                    annotationUuid = annotationUuid[0];
                }

            }

            // Find the first 'gdm' query string item, if any
            uuidKey = _(Object.keys(queryParsed)).find(function(key) {
                return key === 'gdm';
            });
            if (uuidKey) {
                // Got the GDM key for its UUID from the query string.
                gdmUuid = queryParsed[uuidKey];
                if (typeof gdmUuid === 'object') {
                    gdmUuid = gdmUuid[0];
                }
            }
        }

        if (annotationUuid && gdmUuid) {
            // Query the DB with this UUID, setting the component state if successful.
            this.getGdmAnnotation(gdmUuid, annotationUuid);
        }
    },

    submitForm: function(e) {
        e.preventDefault(); e.stopPropagation(); // Don't run through HTML submit handler

        // Save all form values from the DOM.
        this.saveAllFormValues();

        // Check if required fields are filled; indicate errors on form if not, then bail
        if (this.validateRequired()) {
            var newGroup = {}; // Holds the new group object;
            var groupDisease;

            // Required fields are filled; check whether field values are allowed
            var orphaMatch = this.getFormValue('orphanetid').match(/^ORPHA([0-9]{1,6})$/i);
            if (!orphaMatch) {
                this.setFormErrors('orphanetid', 'Use Orphanet IDs (e.g. ORPHA15)');
            } else {
                // Verify given Orpha ID exists in DB
                this.getRestData('/diseases/' + orphaMatch[1]).then(disease => {
                    groupDisease = disease;

                    // Make a new method and save it to the DB
                    var newMethod = this.createMethod();

                    // Post the new method to the DB. When the promise returns with the new method
                    // object, pass it to the next promise-processing code.
                    return this.postRestData('/methods/', newMethod).then(data => {
                        return Promise.resolve(data['@graph'][0]);
                    });
                }, e => {
                    // The given orpha ID does *not* exist in the DB
                    this.setFormErrors('orphanetid', 'The given disease not found');
                }).then(newMethod => {
                    // Method successfully created; passed in 'newMethod'. Now make the new group.
                    newGroup.label = this.getFormValue('groupname');
                    newGroup.commonDiagnosis = groupDisease = groupDisease['@id'];
                    newGroup.method = newMethod['@id'];

                    // Post the new group to the DB
                    return this.postRestData('/groups/', newGroup).then(data => {
                        return Promise.resolve(data['@graph'][0]);
                    });
                }).then(newGroup => {
                    // Let's avoid modifying a React state property, so clone it. Add the new group
                    // to the current annotation's 'groups' array.
                    var annotation = _.clone(this.state.annotation);
                    annotation.groups.push(newGroup['@id']);

                    // We'll get 422 (Unprocessible entity) if we PUT any of these fields:
                    delete annotation.uuid;
                    delete annotation['@id'];
                    delete annotation['@type'];

                    // Post the modified annotation to the DB, then go back to Curation Central
                    console.log(annotation);
                    return this.putRestData('/evidence/' + this.state.annotation.uuid, annotation);
                }).then(data => {
                    this.context.navigate('/curation-central/?gdm=' + this.state.gdm.uuid);
                }).catch(function(e) {
                    console.log('ERROR=: %o', e);
                    parseAndLogError.bind(undefined, 'putRequest');
                });
            }
        }
    },

    createMethod: function() {
        var newMethod = {};
        var value;

        // Put together a new 'method' object
        value = this.getFormValue('prevtesting');
        if (value !== 'none') {
            newMethod.previousTesting = value;
        }
        newMethod.previousTestingDescription = this.getFormValue('prevtestingdesc');
        return newMethod;
    },

    render: function() {
        var annotation = this.state.annotation;
        var gdm = this.state.gdm;

        return (
            <div>
                <CurationData />
                <div className="container">
                    <div className="row group-curation-content">
                        <div className="col-sm-9">
                            <Form submitHandler={this.submitForm} formClassName="form-horizontal form-std">
                                <Panel>
                                    {GroupName.call(this)}
                                </Panel>
                                <PanelGroup accordion>
                                    <Panel title="Common diseases &amp; phenotypes" open>
                                        {GroupCommonDiseases.call(this)}
                                    </Panel>
                                </PanelGroup>
                                <PanelGroup accordion>
                                    <Panel title="Methods">
                                        {GroupMethods.call(this)}
                                    </Panel>
                                </PanelGroup>
                                <Input type="submit" inputClassName="btn-primary pull-right" id="submit" />
                            </Form>
                        </div>
                        {annotation && Object.keys(annotation).length ?
                            <div className="col-sm-3">
                                <CurationPalette gdm={gdm} annotation={annotation} />
                            </div>
                        : null}
                    </div>
                </div>
            </div>
        );
    }
});

globals.curator_page.register(GroupCuration, 'curator_page', 'group-curation');


var GroupName = function() {
    return (
        <div className="row">
            <Input type="text" ref="groupname" label="Group name:"
                error={this.getFormError('groupname')} clearError={this.clrFormErrors.bind(null, 'groupname')}
                labelClassName="col-sm-5 control-label" wrapperClassName="col-sm-7" groupClassName="form-group" required />
        </div>
    );
};


var GroupCommonDiseases = function() {
    return (
        <div className="row">
            <Input type="text" ref="orphanetid" label={<LabelOrphanetId />}
                error={this.getFormError('orphanetid')} clearError={this.clrFormErrors.bind(null, 'orphanetid')}
                labelClassName="col-sm-5 control-label" wrapperClassName="col-sm-7" groupClassName="form-group" inputClassName="uppercase-input" required />
            <Input type="text" ref="hpoid" label={<LabelHpoId />}
                labelClassName="col-sm-5 control-label" wrapperClassName="col-sm-7" groupClassName="form-group" inputClassName="uppercase-input" />
            <Input type="textarea" ref="phenoterms" label={<LabelPhenoTerms />} rows="5"
                labelClassName="col-sm-5 control-label" wrapperClassName="col-sm-7" groupClassName="form-group" />
            <p className="col-sm-7 col-sm-offset-5">Enter <em>phenotypes that are NOT present in Group</em> if they are specifically noted in the paper.</p>
            <Input type="text" ref="nothpoid" label={<LabelHpoId not />}
                labelClassName="col-sm-5 control-label" wrapperClassName="col-sm-7" groupClassName="form-group" inputClassName="uppercase-input" />
            <Input type="textarea" ref="phenoterms" label={<LabelPhenoTerms not />} rows="5"
                labelClassName="col-sm-5 control-label" wrapperClassName="col-sm-7" groupClassName="form-group" />
        </div>
    );
};


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


var GroupDemographics = function() {
    return (
        <div className="row">
            <Input type="text" ref="malecount" label="# males:"
                labelClassName="col-sm-5 control-label" wrapperClassName="col-sm-7" groupClassName="form-group" />
            <Input type="text" ref="malecount" label="# females:"
                labelClassName="col-sm-5 control-label" wrapperClassName="col-sm-7" groupClassName="form-group" />
            <Input type="select" ref="country" label="Country of Origin:"
                labelClassName="col-sm-5 control-label" wrapperClassName="col-sm-7" groupClassName="form-group">
                {country_codes.map(function(country_code) {
                    return <option key={country_code.code} value={country_code.code}>{country_code.name}</option>;
                })}
            </Input>
            <Input type="select" ref="ethnicity" label="Ethnicity:"
                labelClassName="col-sm-5 control-label" wrapperClassName="col-sm-7" groupClassName="form-group">
                <option value="hispanic">Hispanic or Latino</option>
                <option value="nonhispanic">Not Hispanic or Latino</option>
            </Input>
            <Input type="select" ref="race" label="Race:"
                labelClassName="col-sm-5 control-label" wrapperClassName="col-sm-7" groupClassName="form-group">
                <option value="nativeamerican">American Indian or Alaska Native</option>
                <option value="asian">Asian</option>
                <option value="black">Black</option>
                <option value="pacificislander">Native Hawaiian or Other Pacific Islander</option>
                <option value="white">White</option>
                <option value="mixed">Mixed</option>
                <option value="unknown">Unknown</option>
            </Input>
            <h4 className="col-sm-7 col-sm-offset-5">Age Range</h4>
            <div className="demographics-age-range">
                <Input type="select" ref="agerangetype" label="Type:"
                    labelClassName="col-sm-5 control-label" wrapperClassName="col-sm-7" groupClassName="form-group">
                    <option value="onset">Onset</option>
                    <option value="report">Report</option>
                    <option value="diagnosis">Diagnosis</option>
                    <option value="death">Death</option>
                </Input>
                <Input type="text-range" labelClassName="col-sm-5 control-label" label="Value:" wrapperClassName="col-sm-7">
                    <Input type="text" ref="agefrom" inputClassName="input-inline" groupClassName="form-group-inline" />
                    <span> to </span>
                    <Input type="text" ref="ageto" inputClassName="input-inline" groupClassName="form-group-inline" />
                </Input>
                <Input type="select" ref="ageunit" label="Unit:"
                    labelClassName="col-sm-5 control-label" wrapperClassName="col-sm-7" groupClassName="form-group">
                    <option value="days">Days</option>
                    <option value="weeks">Weeks</option>
                    <option value="months">Months</option>
                    <option value="years">Years</option>
                </Input>
            </div>
        </div>
    );
};


var GroupProbandInfo = function() {
    return(
        <div className="row">
            <Input type="text" ref="indcount" label="Total number individuals in group:"
                labelClassName="col-sm-6 control-label" wrapperClassName="col-sm-6" groupClassName="form-group" required />
            <Input type="text" ref="indfamilycount" label="# individuals with family information:"
                labelClassName="col-sm-6 control-label" wrapperClassName="col-sm-6" groupClassName="form-group" required />
            <Input type="text" ref="notindfamilycount" label="# individuals WITHOUT family information:"
                labelClassName="col-sm-6 control-label" wrapperClassName="col-sm-6" groupClassName="form-group" required />
            <Input type="text" ref="indvariantgenecount" label="# individuals with variant in gene being curated:"
                labelClassName="col-sm-6 control-label" wrapperClassName="col-sm-6" groupClassName="form-group" required />
            <Input type="text" ref="notindvariantgenecount" label="# individuals without variant in gene being curated:"
                labelClassName="col-sm-6 control-label" wrapperClassName="col-sm-6" groupClassName="form-group" required />
            <Input type="text" ref="indvariantothercount" label="# individuals with variant found in other gene:"
                labelClassName="col-sm-6 control-label" wrapperClassName="col-sm-6" groupClassName="form-group" required />
            <Input type="text" ref="othergenevariants" label="Other genes found to have variants in them:"
                labelClassName="col-sm-6 control-label" wrapperClassName="col-sm-6" groupClassName="form-group" />
        </div>
    );
};


var GroupMethods = function() {
    return (
        <div className="row">
            <Input type="select" ref="prevtesting" label="Previous Testing:" defaultValue="none"
                labelClassName="col-sm-5 control-label" wrapperClassName="col-sm-7" groupClassName="form-group">
                <option value="none" disabled="disabled">Select</option>
                <option disabled="disabled"></option>
                <option value="Yes">Yes</option>
                <option value="No">No</option>
            </Input>
            <Input type="textarea" ref="prevtestingdesc" label="Description of Previous Testing:" rows="5"
                labelClassName="col-sm-5 control-label" wrapperClassName="col-sm-7" groupClassName="form-group" />
            <Input type="select" ref="genomewide" label="Genome-wide Study?:"
                labelClassName="col-sm-5 control-label" wrapperClassName="col-sm-7" groupClassName="form-group">
                <option value="Yes">Yes</option>
                <option value="No">No</option>
            </Input>
            <h4 className="col-sm-7 col-sm-offset-5">Genotyping Method</h4>
            <Input type="select" ref="genotypingmethod1" label="Method 1:"
                labelClassName="col-sm-5 control-label" wrapperClassName="col-sm-7" groupClassName="form-group">
                <option value="yes">Exome sequencing</option>
                <option value="yes">Genotyping</option>
                <option value="yes">HRM</option>
                <option value="yes">PCR</option>
                <option value="yes">Sanger</option>
                <option value="yes">Whole genome shotgun sequencing</option>
            </Input>
            <Input type="select" ref="genotypingmethod2" label="Method 2:"
                labelClassName="col-sm-5 control-label" wrapperClassName="col-sm-7" groupClassName="form-group">
                <option value="yes">Exome sequencing</option>
                <option value="yes">Genotyping</option>
                <option value="yes">HRM</option>
                <option value="yes">PCR</option>
                <option value="yes">Sanger</option>
                <option value="yes">Whole genome shotgun sequencing</option>
            </Input>
            <Input type="select" ref="entiregene" label="Entire gene sequenced?:"
                labelClassName="col-sm-5 control-label" wrapperClassName="col-sm-7" groupClassName="form-group">
                <option value="Yes">Yes</option>
                <option value="No">No</option>
            </Input>
            <Input type="select" ref="copyassessed" label="Copy number assessed?:"
                labelClassName="col-sm-5 control-label" wrapperClassName="col-sm-7" groupClassName="form-group">
                <option value="Yes">Yes</option>
                <option value="No">No</option>
            </Input>
            <Input type="select" ref="mutationsgenotyped" label="Specific Mutations Genotyped?:"
                labelClassName="col-sm-5 control-label" wrapperClassName="col-sm-7" groupClassName="form-group">
                <option value="Yes">Yes</option>
                <option value="No">No</option>
            </Input>
            <Input type="textarea" ref="specificmutation" label="Method by which Specific Mutations Genotyped:" rows="5"
                labelClassName="col-sm-5 control-label" wrapperClassName="col-sm-7" groupClassName="form-group" />
            <Input type="textarea" ref="additionalinfomethod" label="Additional Information about Group Method:" rows="8"
                labelClassName="col-sm-5 control-label" wrapperClassName="col-sm-7" groupClassName="form-group" />
        </div>
    );
};


var GroupAdditional = function() {
    return (
        <div className="row">
            <Input type="textarea" ref="additionalinfogroup" label="Additional Information about Group:" rows="5"
                labelClassName="col-sm-5 control-label" wrapperClassName="col-sm-7" groupClassName="form-group" />
            <Input type="textarea" ref="otherpmids" label="Add any other PMID(s) that have evidence about this same Group:" rows="5"
                labelClassName="col-sm-5 control-label" wrapperClassName="col-sm-7" groupClassName="form-group" />
            <p className="col-sm-7 col-sm-offset-5">Note: Any variants associated with Individuals in the group who will be counted as probands are not captured at the Group level — they need to be captured at the Family level or Individual levels. Submit the Group information and you will be prompted to enter Family or Individual information after that.</p>
        </div>
    );
};
