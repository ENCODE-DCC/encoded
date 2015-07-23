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

        // Start with default validation; indicate errors on form if not, then bail
        if (this.validateDefault()) {
            var newGroup = {}; // Holds the new group object;
            var groupDiseases, groupGenes, groupArticles;
            var formError = false;

            // Parse the comma-separated list of Orphanet IDs
            var orphaIds = captureOrphas(this.getFormValue('orphanetid'));
            var geneSymbols = captureGenes(this.getFormValue('othergenevariants'));
            var pmids = capturePmids(this.getFormValue('otherpmids'));

            if (!orphaIds || !orphaIds.length) {
                // No 'orphaXX' found 
                formError = true;
                this.setFormErrors('orphanetid', 'Use Orphanet IDs (e.g. ORPHA15) separated by commas');
            }
            if (!formError) {
                // Build search string from given ORPHA IDs
                var searchStr = '/search/?type=orphaPhenotype&' + orphaIds.map(function(id) { return 'orphaNumber=' + id; }).join('&');

                // Verify given Orpha ID exists in DB
                this.getRestData(searchStr).then(diseases => {
                    if (diseases['@graph'].length === orphaIds.length) {
                        // Successfully retrieved all diseases
                        groupDiseases = diseases;
                        return Promise.resolve(diseases);
                    } else {
                        // Get array of missing Orphanet IDs
                        var missingOrphas = _.difference(orphaIds, diseases['@graph'].map(function(disease) { return disease.orphaNumber; }));
                        this.setFormErrors('orphanetid', missingOrphas.map(function(id) { return 'ORPHA' + id; }).join(', ') + ' not found');
                        throw diseases;
                    }
                }, e => {
                    // The given orpha IDs couldn't be retrieved for some reason.
                    this.setFormErrors('orphanetid', 'The given diseases not found');
                    throw e;
                }).then(diseases => {
                    if (geneSymbols) {
                        // At least one gene symbol entered; search the DB for them.
                        searchStr = '/search/?type=gene&' + geneSymbols.map(function(symbol) { return 'symbol=' + symbol; }).join('&');
                        return this.getRestData(searchStr).then(genes => {
                            if (genes['@graph'].length === geneSymbols.length) {
                                // Successfully retrieved all genes
                                groupGenes = genes;
                                return Promise.resolve(genes);
                            } else {
                                var missingGenes = _.difference(geneSymbols, genes['@graph'].map(function(gene) { return gene.symbol; }));
                                this.setFormErrors('othergenevariants', missingGenes.join(', ') + ' not found');
                                throw genes;
                            }
                        });
                    } else {
                        // No genes entered; just pass null to the next then
                        return Promise.resolve(null);
                    }
                }).then(data => {
                    // Handle 'Add any other PMID(s) that have evidence about this same Group' list of PMIDs
                    if (pmids) {
                        // User entered at least one PMID
                        searchStr = '/search/?type=article&' + pmids.map(function(pmid) { return 'pmid=' + pmid; }).join('&');
                        return this.getRestData(searchStr).then(articles => {
                            if (articles['@graph'].length === pmids.length) {
                                // Successfully retrieved all genes
                                groupArticles = articles;
                                return Promise.resolve(articles);
                            } else {
                                var missingPmids = _.difference(pmids, articles['@graph'].map(function(article) { return article.pmid; }));
                                this.setFormErrors('otherpmids', missingPmids.join(', ') + ' not found');
                                throw articles;
                            }
                        });
                    } else {
                        // No PMIDs entered; just pass null to the next then
                        return Promise.resolve(null);
                    }
                }).then(data => {
                    // Make a new method and save it to the DB
                    var newMethod = this.createMethod();
                    if (newMethod) {
                        // Post the new method to the DB. When the promise returns with the new method
                        // object, pass it to the next promise-processing code.
                        return this.postRestData('/methods/', newMethod).then(data => {
                            return Promise.resolve(data['@graph'][0]);
                        });
                    }

                    // No method fields were set; just resolve the promise with no method object
                    return Promise.resolve(null);
                }).then(newMethod => {
                    // Method successfully created if needed (null if not); passed in 'newMethod'. Now make the new group.
                    newGroup.label = this.getFormValue('groupname');

                    // Get an array of all given disease IDs
                    newGroup.commonDiagnosis = groupDiseases['@graph'].map(function(disease) { return disease['@id']; });

                    // If a method object was created (at least one method field set), get its new object's 
                    if (newMethod) {
                        newGroup.method = newMethod['@id'];
                    }

                    // Fill in the group fields from the Common Diseases & Phenotypes panel
                    var hpoTerms = this.getFormValue('hpoid');
                    if (hpoTerms) {
                        newGroup.hpoIdInDiagnosis = _.compact(hpoTerms.toUpperCase().split(','));
                    }
                    var phenoterms = this.getFormValue('phenoterms');
                    if (phenoterms) {
                        newGroup.termsInDiagnosis = phenoterms;
                    }
                    hpoTerms = this.getFormValue('nothpoid');
                    if (hpoTerms) {
                        newGroup.hpoIdInElimination = _.compact(hpoTerms.toUpperCase().split(','));
                    }
                    phenoterms = this.getFormValue('notphenoterms');
                    if (phenoterms) {
                        // Assign to group once new group schema merged in.
                    }

                    // Fill in the group fields from the Group Demographics panel
                    var value = this.getFormValue('malecount');
                    if (value) {
                        newGroup.numberOfMale = value + '';
                    }
                    value = this.getFormValue('femalecount');
                    if (value) {
                        newGroup.numberOfFemale = value + '';
                    }
                    value = this.getFormValue('country');
                    if (value !== 'none') {
                        newGroup.countryOfOrigin = value;
                    }
                    value = this.getFormValue('ethnicity');
                    if (value !== 'none') {
                        newGroup.ethnicity = value;
                    }
                    value = this.getFormValue('race');
                    if (value !== 'none') {
                        newGroup.race = value;
                    }
                    value = this.getFormValue('agerangetype');
                    if (value !== 'none') {
                        newGroup.ageRangeType = value + '';
                    }
                    value = this.getFormValue('agefrom');
                    if (value) {
                        newGroup.ageRangeFrom = value + '';
                    }
                    value = this.getFormValue('ageto');
                    if (value) {
                        newGroup.ageRangeTo = value + '';
                    }
                    value = this.getFormValue('ageunit');
                    if (value !== 'none') {
                        newGroup.ageRangeUnit = value + '';
                    }

                    // Fill in the group fields from Group Information panel
                    newGroup.totalNumberIndividuals = this.getFormValue('indcount');
                    newGroup.numberOfIndividualsWithFamilyInformation = this.getFormValue('indfamilycount');
                    newGroup.numberOfIndividualsWithoutFamilyInformation = this.getFormValue('notindfamilycount');
                    newGroup.numberOfIndividualsWithVariantInCuratedGene = this.getFormValue('indvariantgenecount');
                    newGroup.numberOfIndividualsWithoutVariantInCuratedGene = this.getFormValue('notindvariantgenecount');
                    newGroup.numberOfIndividualsWithVariantInOtherGene = this.getFormValue('indvariantothercount');

                    // Add array of 'Other genes found to have variants in them'
                    if (groupGenes) {
                        newGroup.otherGenes = groupGenes['@graph'].map(function(article) { return article['@id']; });
                    }

                    // Add array of other PMIDs
                    if (groupArticles) {
                        newGroup.otherPMIDs = groupArticles['@graph'].map(function(article) { return article['@id']; });
                    }

                    value = this.getFormValue('additionalinfogroup');
                    if (value) {
                        newGroup.additionalInformation = value;
                    }

                    // Post the new group to the DB
                    console.log('GROUP: %o', newGroup);
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
                    return this.putRestData('/evidence/' + this.state.annotation.uuid, annotation);
                }).then(data => {
                    this.context.navigate('/curation-central/?gdm=' + this.state.gdm.uuid);
                }).catch(function(e) {
                    console.log('GROUP CREATION ERROR=: %o', e);
                    parseAndLogError.bind(undefined, 'putRequest');
                });
            }
        }
    },

    // Create method object based on the form values
    createMethod: function() {
        var newMethod = {};
        var value1, value2;

        // Put together a new 'method' object
        value1 = this.getFormValue('prevtesting');
        if (value1 !== 'none') {
            newMethod.previousTesting = value1;
        }
        value1 = this.getFormValue('prevtestingdesc');
        if (value1) {
            newMethod.previousTestingDescription = value1;
        }
        value1 = this.getFormValue('genomewide');
        if (value1 !== 'none') {
            newMethod.genomeWideStudy = value1;
        }
        value1 = this.getFormValue('genotypingmethod1');
        value2 = this.getFormValue('genotypingmethod2');
        if (value1 !== 'none' || value2 !== 'none') {
            newMethod.genotypingMethods = [];
            newMethod.genotypingMethods[0] = value1 !== 'none' ? value1 : '';
            newMethod.genotypingMethods[1] = value2 !== 'none' ? value2 : '';
        }
        value1 = this.getFormValue('entiregene');
        if (value1 !== 'none') {
            newMethod.entireGeneSequenced = value1;
        }
        value1 = this.getFormValue('copyassessed');
        if (value1 !== 'none') {
            newMethod.copyNumberAssessed = value1;
        }
        value1 = this.getFormValue('mutationsgenotyped');
        if (value1 !== 'none') {
            newMethod.specificMutationsGenotyped = value1;
        }
        value1 = this.getFormValue('specificmutation');
        if (value1) {
            newMethod.specificMutationsGenotypedMethod = value1;
        }
        value1 = this.getFormValue('additionalinfomethod');
        if (value1) {
            newMethod.additionalInformation = value1;
        }

        return Object.keys(newMethod).length ? newMethod : null;
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
                                    <Panel title="Group Demographics" open>
                                        {GroupDemographics.call(this)}
                                    </Panel>
                                </PanelGroup>
                                <PanelGroup accordion>
                                    <Panel title="Group Information" open>
                                        {GroupProbandInfo.call(this)}
                                    </Panel>
                                </PanelGroup>
                                <PanelGroup accordion>
                                    <Panel title="Group Methods" open>
                                        {GroupMethods.call(this)}
                                    </Panel>
                                </PanelGroup>
                                <PanelGroup accordion>
                                    <Panel title="Group Additional Information" open>
                                        {GroupAdditional.call(this)}
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


function captureBase(s, re) {
    var match, matchResults = [];

    do {
        match = re.exec(s);
        if (match) {
            matchResults.push(match[1]);
        }
    } while(match);
    return matchResults;
}

// Given a string, find all the comma-separated 'orphaXX' occurrences.
// Return all orpha IDs in an array.
function captureOrphas(s) {
    return captureBase(s, /(?:^|,|\s)orpha(\d+)(?=,|\s|$)/gi);
}

// Given a string, find all the comma-separated gene symbol occurrences.
// Return all gene symbols in an array.
function captureGenes(s) {
    return s ? captureBase(s, /(?:^|,|\s*)([a-zA-Z](?:\w)*)(?=,|\s*|$)/gi) : null;
}

// Given a string, find all the comma-separated PMID occurrences.
// Return all PMIDs in an array.
function capturePmids(s) {
    return s ? captureBase(s, /(?:^|,|\s*)(\d{1,8})(?=,|\s*|$)/gi) : null;
}



// Group Name group curation panel. Call with .call(this) to run in the same context
// as the calling component.
var GroupName = function() {
    return (
        <div className="row">
            <Input type="text" ref="groupname" label="Group name:"
                error={this.getFormError('groupname')} clearError={this.clrFormErrors.bind(null, 'groupname')}
                labelClassName="col-sm-5 control-label" wrapperClassName="col-sm-7" groupClassName="form-group" required />
        </div>
    );
};


// Common diseases group curation panel. Call with .call(this) to run in the same context
// as the calling component.
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
            <Input type="textarea" ref="notphenoterms" label={<LabelPhenoTerms not />} rows="5"
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


// Demographics group curation panel. Call with .call(this) to run in the same context
// as the calling component.
var GroupDemographics = function() {
    return (
        <div className="row">
            <Input type="text" ref="malecount" label="# males:" format="number"
                error={this.getFormError('malecount')} clearError={this.clrFormErrors.bind(null, 'malecount')}
                labelClassName="col-sm-5 control-label" wrapperClassName="col-sm-7" groupClassName="form-group" />
            <Input type="text" ref="femalecount" label="# females:" format="number"
                error={this.getFormError('femalecount')} clearError={this.clrFormErrors.bind(null, 'femalecount')}
                labelClassName="col-sm-5 control-label" wrapperClassName="col-sm-7" groupClassName="form-group" />
            <Input type="select" ref="country" label="Country of Origin:" defaultValue="none"
                labelClassName="col-sm-5 control-label" wrapperClassName="col-sm-7" groupClassName="form-group">
                <option value="none" disabled="disabled">Select</option>
                <option disabled="disabled"></option>
                {country_codes.map(function(country_code) {
                    return <option key={country_code.code} value={country_code.code}>{country_code.name}</option>;
                })}
            </Input>
            <Input type="select" ref="ethnicity" label="Ethnicity:" defaultValue="none"
                labelClassName="col-sm-5 control-label" wrapperClassName="col-sm-7" groupClassName="form-group">
                <option value="none" disabled="disabled">Select</option>
                <option disabled="disabled"></option>
                <option>Hispanic or Latino</option>
                <option>Not Hispanic or Latino</option>
            </Input>
            <Input type="select" ref="race" label="Race:" defaultValue="none"
                labelClassName="col-sm-5 control-label" wrapperClassName="col-sm-7" groupClassName="form-group">
                <option value="none" disabled="disabled">Select</option>
                <option disabled="disabled"></option>
                <option>American Indian or Alaska Native</option>
                <option>Asian</option>
                <option>Black</option>
                <option>Native Hawaiian or Other Pacific Islander</option>
                <option>White</option>
                <option>Mixed</option>
                <option>Unknown</option>
            </Input>
            <h4 className="col-sm-7 col-sm-offset-5">Age Range</h4>
            <div className="demographics-age-range">
                <Input type="select" ref="agerangetype" label="Type:" defaultValue="none"
                    labelClassName="col-sm-5 control-label" wrapperClassName="col-sm-7" groupClassName="form-group">
                    <option value="none" disabled="disabled">Select</option>
                    <option disabled="disabled"></option>
                    <option>Onset</option>
                    <option>Report</option>
                    <option>Diagnosis</option>
                    <option>Death</option>
                </Input>
                <Input type="text-range" labelClassName="col-sm-5 control-label" label="Value:" wrapperClassName="col-sm-7">
                    <Input type="text" ref="agefrom" inputClassName="input-inline" groupClassName="form-group-inline" format="number"
                        error={this.getFormError('agefrom')} clearError={this.clrFormErrors.bind(null, 'agefrom')} />
                    <span> to </span>
                    <Input type="text" ref="ageto" inputClassName="input-inline" groupClassName="form-group-inline" format="number"
                        error={this.getFormError('ageto')} clearError={this.clrFormErrors.bind(null, 'ageto')} />
                </Input>
                <Input type="select" ref="ageunit" label="Unit:" defaultValue="none"
                    labelClassName="col-sm-5 control-label" wrapperClassName="col-sm-7" groupClassName="form-group">
                    <option value="none" disabled="disabled">Select</option>
                    <option disabled="disabled"></option>
                    <option>Days</option>
                    <option>Weeks</option>
                    <option>Months</option>
                    <option>Years</option>
                </Input>
            </div>
        </div>
    );
};


// Group information group curation panel. Call with .call(this) to run in the same context
// as the calling component.
var GroupProbandInfo = function() {
    return(
        <div className="row">
            <Input type="text" ref="indcount" label="Total number individuals in group:" format="number"
                error={this.getFormError('indcount')} clearError={this.clrFormErrors.bind(null, 'indcount')}
                labelClassName="col-sm-6 control-label" wrapperClassName="col-sm-6" groupClassName="form-group" required />
            <Input type="text" ref="indfamilycount" label="# individuals with family information:" format="number"
                error={this.getFormError('indfamilycount')} clearError={this.clrFormErrors.bind(null, 'indfamilycount')}
                labelClassName="col-sm-6 control-label" wrapperClassName="col-sm-6" groupClassName="form-group" required />
            <Input type="text" ref="notindfamilycount" label="# individuals WITHOUT family information:" format="number"
                error={this.getFormError('notindfamilycount')} clearError={this.clrFormErrors.bind(null, 'notindfamilycount')}
                labelClassName="col-sm-6 control-label" wrapperClassName="col-sm-6" groupClassName="form-group" required />
            <Input type="text" ref="indvariantgenecount" label="# individuals with variant in gene being curated:" format="number"
                error={this.getFormError('indvariantgenecount')} clearError={this.clrFormErrors.bind(null, 'indvariantgenecount')}
                labelClassName="col-sm-6 control-label" wrapperClassName="col-sm-6" groupClassName="form-group" required />
            <Input type="text" ref="notindvariantgenecount" label="# individuals without variant in gene being curated:" format="number"
                error={this.getFormError('notindvariantgenecount')} clearError={this.clrFormErrors.bind(null, 'notindvariantgenecount')}
                labelClassName="col-sm-6 control-label" wrapperClassName="col-sm-6" groupClassName="form-group" required />
            <Input type="text" ref="indvariantothercount" label="# individuals with variant found in other gene:" format="number"
                error={this.getFormError('indvariantothercount')} clearError={this.clrFormErrors.bind(null, 'indvariantothercount')}
                labelClassName="col-sm-6 control-label" wrapperClassName="col-sm-6" groupClassName="form-group" required />
            <Input type="text" ref="othergenevariants" label="Other genes found to have variants in them:"
                error={this.getFormError('othergenevariants')} clearError={this.clrFormErrors.bind(null, 'othergenevariants')}
                labelClassName="col-sm-6 control-label" wrapperClassName="col-sm-6" groupClassName="form-group" />
        </div>
    );
};


// Methods group curation panel. Call with .call(this) to run in the same context
// as the calling component.
var GroupMethods = function() {
    return (
        <div className="row">
            <Input type="select" ref="prevtesting" label="Previous Testing:" defaultValue="none"
                labelClassName="col-sm-5 control-label" wrapperClassName="col-sm-7" groupClassName="form-group">
                <option value="none" disabled="disabled">Select</option>
                <option disabled="disabled"></option>
                <option>Yes</option>
                <option>No</option>
            </Input>
            <Input type="textarea" ref="prevtestingdesc" label="Description of Previous Testing:" rows="5"
                labelClassName="col-sm-5 control-label" wrapperClassName="col-sm-7" groupClassName="form-group" />
            <Input type="select" ref="genomewide" label="Genome-wide Study?:" defaultValue="none"
                labelClassName="col-sm-5 control-label" wrapperClassName="col-sm-7" groupClassName="form-group">
                <option value="none" disabled="disabled">Select</option>
                <option disabled="disabled"></option>
                <option>Yes</option>
                <option>No</option>
            </Input>
            <h4 className="col-sm-7 col-sm-offset-5">Genotyping Method</h4>
            <Input type="select" ref="genotypingmethod1" label="Method 1:" defaultValue="none"
                labelClassName="col-sm-5 control-label" wrapperClassName="col-sm-7" groupClassName="form-group">
                <option value="none" disabled="disabled">Select</option>
                <option disabled="disabled"></option>
                <option>Exome sequencing</option>
                <option>Genotyping</option>
                <option>HRM</option>
                <option>PCR</option>
                <option>Sanger</option>
                <option>Whole genome shotgun sequencing</option>
            </Input>
            <Input type="select" ref="genotypingmethod2" label="Method 2:" defaultValue="none"
                labelClassName="col-sm-5 control-label" wrapperClassName="col-sm-7" groupClassName="form-group">
                <option value="none" disabled="disabled">Select</option>
                <option disabled="disabled"></option>
                <option>Exome sequencing</option>
                <option>Genotyping</option>
                <option>HRM</option>
                <option>PCR</option>
                <option>Sanger</option>
                <option>Whole genome shotgun sequencing</option>
            </Input>
            <Input type="select" ref="entiregene" label="Entire gene sequenced?:" defaultValue="none"
                labelClassName="col-sm-5 control-label" wrapperClassName="col-sm-7" groupClassName="form-group">
                <option value="none" disabled="disabled">Select</option>
                <option disabled="disabled"></option>
                <option>Yes</option>
                <option>No</option>
            </Input>
            <Input type="select" ref="copyassessed" label="Copy number assessed?:" defaultValue="none"
                labelClassName="col-sm-5 control-label" wrapperClassName="col-sm-7" groupClassName="form-group">
                <option value="none" disabled="disabled">Select</option>
                <option disabled="disabled"></option>
                <option>Yes</option>
                <option>No</option>
            </Input>
            <Input type="select" ref="mutationsgenotyped" label="Specific Mutations Genotyped?:" defaultValue="none"
                labelClassName="col-sm-5 control-label" wrapperClassName="col-sm-7" groupClassName="form-group">
                <option value="none" disabled="disabled">Select</option>
                <option disabled="disabled"></option>
                <option>Yes</option>
                <option>No</option>
            </Input>
            <Input type="textarea" ref="specificmutation" label="Method by which Specific Mutations Genotyped:" rows="5"
                labelClassName="col-sm-5 control-label" wrapperClassName="col-sm-7" groupClassName="form-group" />
            <Input type="textarea" ref="additionalinfomethod" label="Additional Information about Group Method:" rows="8"
                labelClassName="col-sm-5 control-label" wrapperClassName="col-sm-7" groupClassName="form-group" />
        </div>
    );
};


// Additional Information group curation panel. Call with .call(this) to run in the same context
// as the calling component.
var GroupAdditional = function() {
    return (
        <div className="row">
            <Input type="textarea" ref="additionalinfogroup" label="Additional Information about Group:" rows="5"
                labelClassName="col-sm-5 control-label" wrapperClassName="col-sm-7" groupClassName="form-group" />
            <Input type="textarea" ref="otherpmids" label="Enter PMID(s) that report evidence about this same group:" rows="5"
                error={this.getFormError('otherpmids')} clearError={this.clrFormErrors.bind(null, 'otherpmids')}
                labelClassName="col-sm-5 control-label" wrapperClassName="col-sm-7" groupClassName="form-group" />
            <p className="col-sm-7 col-sm-offset-5">
                Note: Any variants associated with probands that will be counted towards the Classification are not
                captured at the Group level - variants and their association with probands are required to be captured
                at the Family or Individual level. Once you submit the Group information, you will be prompted to enter
                Family/Individual information.
            </p>
        </div>
    );
};


var GroupViewer = React.createClass({
    render: function() {
        var context = this.props.context;
        var demographicOutput = groupDemographicsViewer(context);

        return (
            <div className="container">
                <div className="row group-curation-content">
                    <h1>{context.label}</h1>
                    <Panel title="Common diseases &amp; phenotypes" panelClassName="panel-data">
                        <dl className="dl-horizontal">
                            <div>
                                <dt>Orphanet Common Diagnosis</dt>
                                <dd>
                                    {context.commonDiagnosis.map(function(disease, i) {
                                        return (
                                            <span key={disease.orphaNumber}>
                                                {i > 0 ? ', ' : ''}
                                                {'ORPHA' + disease.orphaNumber}
                                            </span>
                                        );
                                    })}
                                </dd>
                            </div>

                            {context.hpoIdInDiagnosis && context.hpoIdInDiagnosis.length ?
                                <div>
                                    <dt>HPO IDs</dt>
                                    <dd>{context.hpoIdInDiagnosis.join(', ')}</dd>
                                </div>
                            : null}

                            {context.termsInDiagnosis ?
                                <div>
                                    <dt>Phenotype Terms</dt>
                                    <dd>{context.termsInDiagnosis}</dd>
                                </div>
                            : null}

                            {context.hpoIdInElimination && context.hpoIdInElimination.length ?
                                <div>
                                    <dt>Not HPO IDs</dt>
                                    <dd>{context.hpoIdInElimination.join(', ')}</dd>
                                </div>
                            : null}
                        </dl>
                    </Panel>

                    {demographicOutput ?
                        <Panel title="Group — Demographics" panelClassName="panel-data">
                            <dl className="dl-horizontal">
                                {demographicOutput.map(function(view) { return view; })}
                            </dl>
                        </Panel>
                    : null}

                    <Panel title="Group — Information" panelClassName="panel-data">
                        <dl className="dl-horizontal">
                            {context.totalNumberIndividuals ?
                                <div>
                                    <dt>Total number individuals in group</dt>
                                    <dd>{context.totalNumberIndividuals}</dd>
                                </div>
                            : null}

                            {context.numberOfIndividualsWithFamilyInformation ?
                                <div>
                                    <dt># individuals with family information</dt>
                                    <dd>{context.numberOfIndividualsWithFamilyInformation}</dd>
                                </div>
                            : null}

                            {context.numberOfIndividualsWithoutFamilyInformation ?
                                <div>
                                    <dt># individuals WITHOUT family information</dt>
                                    <dd>{context.numberOfIndividualsWithoutFamilyInformation}</dd>
                                </div>
                            : null}

                            {context.numberOfIndividualsWithVariantInCuratedGene ?
                                <div>
                                    <dt># individuals with variant in gene being curated</dt>
                                    <dd>{context.numberOfIndividualsWithVariantInCuratedGene}</dd>
                                </div>
                            : null}

                            {context.numberOfIndividualsWithoutVariantInCuratedGene ?
                                <div>
                                    <dt># individuals without variant in gene being curated</dt>
                                    <dd>{context.numberOfIndividualsWithoutVariantInCuratedGene}</dd>
                                </div>
                            : null}

                            {context.numberOfIndividualsWithVariantInOtherGene ?
                                <div>
                                    <dt># individuals with variant found in other gene</dt>
                                    <dd>{context.numberOfIndividualsWithVariantInOtherGene}</dd>
                                </div>
                            : null}

                            {context.otherGenes && context.otherGenes.length ?
                                <div>
                                    <dt>Other genes found to have variants in them</dt>
                                    <dd>{context.otherGenes.map(function(gene) { return gene.symbol; }).join(', ')}</dd>
                                </div>
                            : null}
                        </dl>
                    </Panel>

                    {context.method && Object.keys(context.method).length ?
                        <Panel title="Group — Methods" panelClassName="panel-data">
                            <dl className="dl-horizontal">
                                {context.method.previousTesting ?
                                    <div>
                                        <dt>Previous testing</dt>
                                        <dd>{context.method.previousTesting}</dd>
                                    </div>
                                : null}

                                {context.method.previousTestingDescription ?
                                    <div>
                                        <dt>Description of previous testing</dt>
                                        <dd>{context.method.previousTestingDescription}</dd>
                                    </div>
                                : null}

                                {context.method.genomeWideStudy ?
                                    <div>
                                        <dt>Genome-wide study</dt>
                                        <dd>{context.method.genomeWideStudy}</dd>
                                    </div>
                                : null}

                                {context.method.genotypingMethods && context.method.genotypingMethods.length ?
                                    <div>
                                        <dt>Genotyping methods</dt>
                                        <dd>{context.method.genotypingMethods.join(', ')}</dd>
                                    </div>
                                : null}

                                {context.method.entireGeneSequenced ?
                                    <div>
                                        <dt>Entire gene sequenced</dt>
                                        <dd>{context.method.entireGeneSequenced}</dd>
                                    </div>
                                : null}

                                {context.method.copyNumberAssessed ?
                                    <div>
                                        <dt>Copy number assessed</dt>
                                        <dd>{context.method.copyNumberAssessed}</dd>
                                    </div>
                                : null}

                                {context.method.specificMutationsGenotyped ?
                                    <div>
                                        <dt>Specific Mutations Genotyped</dt>
                                        <dd>{context.method.specificMutationsGenotyped}</dd>
                                    </div>
                                : null}

                                {context.method.specificMutationsGenotypedMethod ?
                                    <div>
                                        <dt>Method by which Specific Mutations Genotyped</dt>
                                        <dd>{context.method.specificMutationsGenotypedMethod}</dd>
                                    </div>
                                : null}

                                {context.method.specificMutationsGenotypedMethod ?
                                    <div>
                                        <dt>Additional Information about Group Method</dt>
                                        <dd>{context.method.additionalInformation}</dd>
                                    </div>
                                : null}
                            </dl>
                        </Panel>
                    : null}

                    {context.additionalInformation || (context.otherPMIDs && context.otherPMIDs.length) ?
                        <Panel title="Group — Additional Information" panelClassName="panel-data">
                            <dl className="dl-horizontal">
                                {context.additionalInformation ?
                                    <div>
                                        <dt>Additional Information about Group</dt>
                                        <dd>{context.additionalInformation}</dd>
                                    </div>
                                : null}

                                {context.otherPMIDs && context.otherPMIDs.length ?
                                    <div>
                                        <dt>Additional Information about Group</dt>
                                        <dd>{context.otherPMIDs.map(function(article, i) {
                                            return (
                                                <span key={i}>
                                                    {i > 0 ? ', ' : ''}
                                                    {article.pmid}
                                                </span>
                                            );
                                        })}</dd>
                                    </div>
                                : null}
                            </dl>
                        </Panel>
                    : null}
                </div>
            </div>
        );
    }
});

globals.content_views.register(GroupViewer, 'group');


// Generate a rendering of the Group Demographics panel contents.
// If no property of the demographics section of the group has
// any information, this returns null. It otherwise returns an
// array of React components that can be rendered from a .map loop.
function groupDemographicsViewer(context) {
    var i = 0;
    var output = [];

    output[i++] = (context.numberOfMale ?
        <div>
            <dt># Males</dt>
            <dd>{context.numberOfMale}</dd>
        </div>
    : null);

    output[i++] = (context.numberOfFemale ?
        <div>
            <dt># Females</dt>
            <dd>{context.numberOfFemale}</dd>
        </div>
    : null);

    output[i++] = (context.countryOfOrigin ?
        <div>
            <dt>Country of Origin</dt>
            <dd>{context.countryOfOrigin}</dd>
        </div>
    : null);

    output[i++] = (context.ethnicity ?
        <div>
            <dt>Ethnicity</dt>
            <dd>{context.ethnicity}</dd>
        </div>
    : null);

    output[i++] = (context.race ?
        <div>
            <dt>Race</dt>
            <dd>{context.race}</dd>
        </div>
    : null);

    output[i++] = (context.ageRangeType ?
        <div>
            <dt>Age Range Type</dt>
            <dd>{context.ageRangeType}</dd>
        </div>
    : null);

    output[i++] = (context.ageRangeFrom || context.ageRangeTo ?
        <div>
            <dt>Age Range</dt>
            <dd>{context.ageRangeFrom + ' – ' + context.ageRangeTo}</dd>
        </div>
    : null);

    output[i++] = (context.ageRangeUnit ?
        <div>
            <dt>Age Range Unit</dt>
            <dd>{context.ageRangeUnit}</dd>
        </div>
    : null);

    if (_.some(output)) {
        return output;
    }
    return null;
}

// Generate a rendering of the Group Information panel contents.
// If no property of the demographics section of the group has
// any information, this returns null. It otherwise returns an
// array of React components that can be rendered from a .map loop.
function groupInformationViewer(context) {
    var i = 0;
    var output = [];

    output[i++] = (context.numberOfMale ?
        <div>
            <dt># Males</dt>
            <dd>{context.numberOfMale}</dd>
        </div>
    : null);

    output[i++] = (context.numberOfFemale ?
        <div>
            <dt># Females</dt>
            <dd>{context.numberOfFemale}</dd>
        </div>
    : null);

    output[i++] = (context.countryOfOrigin ?
        <div>
            <dt>Country of Origin</dt>
            <dd>{context.countryOfOrigin}</dd>
        </div>
    : null);

    output[i++] = (context.ethnicity ?
        <div>
            <dt>Ethnicity</dt>
            <dd>{context.ethnicity}</dd>
        </div>
    : null);

    output[i++] = (context.race ?
        <div>
            <dt>Race</dt>
            <dd>{context.race}</dd>
        </div>
    : null);

    output[i++] = (context.race ?
        <div>
            <dt>Race</dt>
            <dd>{context.race}</dd>
        </div>
    : null);

    output[i++] = (context.ageRangeType ?
        <div>
            <dt>Age Range Type</dt>
            <dd>{context.ageRangeType}</dd>
        </div>
    : null);

    output[i++] = (context.ageRangeFrom || context.ageRangeTo ?
        <div>
            <dt>Age Range</dt>
            <dd>{context.ageRangeFrom + ' – ' + context.ageRangeTo}</dd>
        </div>
    : null);

    output[i++] = (context.ageRangeFrom || context.ageRangeTo ?
        <div>
            <dt>Age Range</dt>
            <dd>{context.ageRangeFrom + ' – ' + context.ageRangeTo}</dd>
        </div>
    : null);

    if (_.some(output)) {
        return output;
    }
    return null;
}
