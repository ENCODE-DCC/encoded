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
var queryKeyValue = globals.queryKeyValue;
var country_codes = globals.country_codes;


var GroupCuration = React.createClass({
    mixins: [FormMixin, RestMixin],

    contextTypes: {
        navigate: React.PropTypes.func
    },

    // Keeps track of values from the query string
    queryValues: {},

    getInitialState: function() {
        return {
            gdm: {}, // GDM object given in UUID
            annotation: {}, // Annotation object given in UUID
            group: {} // If we're editing a group, this gets the fleshed-out group object we're editing
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

    // If a group UUID is given in the query string, load it into the group state variable.
    loadGroup: function(groupUuid) {
        this.getRestData(
            '/group/' + groupUuid
        ).then(group => {
            // Received group data; set the current state with it
            this.setState({group: group});
            return Promise.resolve();
        }).catch(function(e) {
            console.log('GROUP LOAD ERROR=: %o', e);
            parseAndLogError.bind(undefined, 'getRequest');
        });
    },

    // After the Group Curation page component mounts, grab the GDM and annotation UUIDs from the query
    // string and retrieve the corresponding annotation from the DB, if they exist.
    // Note, we have to do this after the component mounts because AJAX DB queries can't be
    // done from unmounted components.
    componentDidMount: function() {
        if (this.queryValues.annotationUuid && this.queryValues.gdmUuid) {
            // Query the DB with this UUID, setting the component state if successful.
            this.getGdmAnnotation(this.queryValues.gdmUuid, this.queryValues.annotationUuid);
        }

        // If a group's UUID was given in the query string, retrieve the group data.
        if (this.queryValues.groupUuid) {
            this.loadGroup(this.queryValues.groupUuid);
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

            // Check that all HPO terms appear valid
            var hpoTerms = this.getFormValue('hpoid');
            if (hpoTerms) {
                var rawHpoids = _.compact(hpoTerms.toUpperCase().split(','));
                var hpoids = _.compact(rawHpoids.map(function(id) { return captureHpoid(id); }));
                if (rawHpoids.length !== hpoids.length) {
                    formError = true;
                    this.setFormErrors('hpoid', 'HPO IDs must be in the form “HP:NNNNNNN,” where N is a digit');
                }
            }

            // Check that all NOT HPO terms appear valid
            hpoTerms = this.getFormValue('nothpoid');
            if (hpoTerms) {
                var rawNotHpoids = _.compact(hpoTerms.toUpperCase().split(','));
                var nothpoids = _.compact(rawNotHpoids.map(function(id) { return captureHpoid(id); }));
                if (rawNotHpoids.length !== nothpoids.length) {
                    formError = true;
                    this.setFormErrors('nothpoid', 'Use HPO IDs, e.g. HP:0000123');
                }
            }

            // Check that all Orphanet IDs have the proper format (will check for existence later)
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
                        if (this.state.group && this.state.group.method && Object.keys(this.state.group.method).length) {
                            // We're editing a group and it had an existing method. Just PUT an update to the method.
                            return this.putRestData('/methods/' + this.state.group.method.uuid, newMethod).then(data => {
                                return Promise.resolve(data['@graph'][0]);
                            });
                        } else {
                            // We're either creating a group, or editing an existing group that didn't have a method
                            // Post the new method to the DB. When the promise returns with the new method
                            // object, pass it to the next promise-processing code.
                            return this.postRestData('/methods/', newMethod).then(data => {
                                return Promise.resolve(data['@graph'][0]);
                            });
                        }
                    } else {
                        // If we're editing a group and it already had a method, then delete the method from the DB.
                        // If we're editing a group and it didn't have a method, do nothing
                        // If we're creating a group, do nothing.
                        // For now, just resolve the promise with no method object. We'll deal with deleting objects
                        // later.
                        return Promise.resolve(null);
                    }
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
                        newGroup.termsInElimination = phenoterms;
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

                    // Either update or create the group object in the DB
                    if (this.state.group && Object.keys(this.state.group).length) {
                        // We're editing a group. PUT the new group object to the DB to update the existing one.
                        return this.putRestData('/groups/' + this.state.group.uuid, newGroup).then(data => {
                            return Promise.resolve(data['@graph'][0]);
                        });
                    } else {
                        // We created a group; post it to the DB
                        return this.postRestData('/groups/', newGroup).then(data => {
                            return Promise.resolve(data['@graph'][0]);
                        });
                    }
                }).then(newGroup => {
                    if (!this.state.group || Object.keys(this.state.group).length === 0) {
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
                    } else {
                        return Promise.resolve(this.state.annotation);
                    }
                }).then(data => {
                    // Navigate back to Curation Central page.
                    // FUTURE: Need to navigate to choices page.
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
        var submitErrClass = 'submit-err pull-right' + (this.anyFormErrors() ? '' : ' hidden');

        // Get the 'evidence', 'gdm', and 'group' UUIDs from the query string and save them locally.
        this.queryValues.annotationUuid = queryKeyValue('evidence', this.props.href);
        this.queryValues.gdmUuid = queryKeyValue('gdm', this.props.href);
        this.queryValues.groupUuid = queryKeyValue('group', this.props.href);

        return (
            <div>
                {(!this.queryValues.groupUuid || Object.keys(this.state.group).length > 0) ?
                    <div>
                        <CurationData />
                        <div className="container">
                            <div className="row group-curation-content">
                                <div className="col-sm-12">
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
                                        <Input type="submit" inputClassName="btn-primary pull-right" id="submit" title="Save" />
                                        <div className={submitErrClass}>Please fix errors on the form and resubmit.</div>
                                    </Form>
                                </div>
                            </div>
                        </div>
                    </div>
                : null}
            </div>
        );
    }
});

globals.curator_page.register(GroupCuration, 'curator_page', 'group-curation');


function captureBase(s, re, uppercase) {
    var match, matchResults = [];

    do {
        match = re.exec(s);
        if (match) {
            matchResults.push(uppercase ? match[1].toUpperCase() : match[1]);
        }
    } while(match);
    return matchResults;
}

// Given a string, find all the comma-separated 'orphaXX' occurrences.
// Return all orpha IDs in an array.
function captureOrphas(s) {
    return captureBase(s, /(?:^|,|\s)orpha(\d+)(?=,|\s|$)/gi, true);
}

// Given a string, find all the comma-separated gene symbol occurrences.
// Return all gene symbols in an array.
function captureGenes(s) {
    return s ? captureBase(s, /(?:^|,|\s*)([a-zA-Z](?:\w)*)(?=,|\s*|$)/gi, true) : null;
}

// Given a string, find all the comma-separated PMID occurrences.
// Return all PMIDs in an array.
function capturePmids(s) {
    return s ? captureBase(s, /(?:^|,|\s*)(\d{1,8})(?=,|\s*|$)/gi) : null;
}

function captureHpoid(s) {
    var match = s.toUpperCase().match(/^ *(HP:\d{7}) *$/i);
    return match ? match[1] : null;
}



// Group Name group curation panel. Call with .call(this) to run in the same context
// as the calling component.
var GroupName = function() {
    return (
        <div className="row">
            <Input type="text" ref="groupname" label="Group name:" value={this.state.group.label}
                error={this.getFormError('groupname')} clearError={this.clrFormErrors.bind(null, 'groupname')}
                labelClassName="col-sm-5 control-label" wrapperClassName="col-sm-7" groupClassName="form-group" required />
        </div>
    );
};


// Common diseases group curation panel. Call with .call(this) to run in the same context
// as the calling component.
var GroupCommonDiseases = function() {
    var group = this.state.group;
    var orphanetidVal, hpoidVal, nothpoidVal;

    if (group) {
        orphanetidVal = group.commonDiagnosis ? group.commonDiagnosis.map(function(disease) { return 'ORPHA' + disease.orphaNumber; }).join() : null;
        hpoidVal = group.hpoIdInDiagnosis ? group.hpoIdInDiagnosis.join() : null;
        nothpoidVal = group.hpoIdInElimination ? group.hpoIdInElimination.join() : null;
    }

    return (
        <div className="row">
            <Input type="text" ref="orphanetid" label={<LabelOrphanetId />} value={orphanetidVal} placeholder="e.g. ORPHA15"
                error={this.getFormError('orphanetid')} clearError={this.clrFormErrors.bind(null, 'orphanetid')}
                labelClassName="col-sm-5 control-label" wrapperClassName="col-sm-7" groupClassName="form-group" inputClassName="uppercase-input" required />
            <Input type="text" ref="hpoid" label={<LabelHpoId />} value={hpoidVal} placeholder="e.g. HP:0010704, HP:0030300"
                error={this.getFormError('hpoid')} clearError={this.clrFormErrors.bind(null, 'hpoid')}
                labelClassName="col-sm-5 control-label" wrapperClassName="col-sm-7" groupClassName="form-group" inputClassName="uppercase-input" />
            <Input type="textarea" ref="phenoterms" label="Shared Phenotype(s) (free text):" rows="5" value={group.termsInDiagnosis}
                labelClassName="col-sm-5 control-label" wrapperClassName="col-sm-7" groupClassName="form-group" />
            <p className="col-sm-7 col-sm-offset-5">Enter <em>phenotypes that are NOT present in Group</em> if they are specifically noted in the paper.</p>
            <Input type="text" ref="nothpoid" label={<LabelNotHpoId />} value={nothpoidVal} placeholder="e.g. HP:0010704, HP:0030300"
                error={this.getFormError('nothpoid')} clearError={this.clrFormErrors.bind(null, 'nothpoid')}
                labelClassName="col-sm-5 control-label" wrapperClassName="col-sm-7" groupClassName="form-group" inputClassName="uppercase-input" />
            <Input type="textarea" ref="notphenoterms" label="Not Phenotype(s) (free text):" rows="5" value={group.termsInElimination}
                labelClassName="col-sm-5 control-label" wrapperClassName="col-sm-7" groupClassName="form-group" />
        </div>
    );
};


// HTML labels for inputs follow.
var LabelOrphanetId = React.createClass({
    render: function() {
        return <span>Disease in Common (<a href="http://www.orpha.net/" target="_blank" title="Orphanet home page in a new tab">Orphanet</a> term):</span>;
    }
});

// HTML labels for inputs follow.
var LabelHpoId = React.createClass({
    render: function() {
        return <span>Shared Phenotypes (HPO ID(s)); <a href="http://compbio.charite.de/phenexplorer/" target="_blank" title="PhenExplorer home page in a new tab">PhenExplorer</a>):</span>;
    }
});

// HTML labels for inputs follow.
var LabelNotHpoId = React.createClass({
    render: function() {
        return <span>NOT Phenotype(s) (HPO ID(s); <a href="http://compbio.charite.de/phenexplorer/" target="_blank" title="PhenExplorer home page in a new tab">PhenExplorer</a>):</span>;
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
    var group = this.state.group;

    return (
        <div className="row">
            <Input type="text" ref="malecount" label="# males:" format="number" value={group.numberOfMale}
                error={this.getFormError('malecount')} clearError={this.clrFormErrors.bind(null, 'malecount')}
                labelClassName="col-sm-5 control-label" wrapperClassName="col-sm-7" groupClassName="form-group" />
            <Input type="text" ref="femalecount" label="# females:" format="number" value={group.numberOfFemale}
                error={this.getFormError('femalecount')} clearError={this.clrFormErrors.bind(null, 'femalecount')}
                labelClassName="col-sm-5 control-label" wrapperClassName="col-sm-7" groupClassName="form-group" />
            <Input type="select" ref="country" label="Country of Origin:" defaultValue="none" value={group.countryOfOrigin}
                labelClassName="col-sm-5 control-label" wrapperClassName="col-sm-7" groupClassName="form-group">
                <option value="none" disabled="disabled">Select</option>
                <option disabled="disabled"></option>
                {country_codes.map(function(country_code) {
                    return <option key={country_code.code}>{country_code.name}</option>;
                })}
            </Input>
            <Input type="select" ref="ethnicity" label="Ethnicity:" defaultValue="none" value={group.ethnicity}
                labelClassName="col-sm-5 control-label" wrapperClassName="col-sm-7" groupClassName="form-group">
                <option value="none" disabled="disabled">Select</option>
                <option disabled="disabled"></option>
                <option>Hispanic or Latino</option>
                <option>Not Hispanic or Latino</option>
            </Input>
            <Input type="select" ref="race" label="Race:" defaultValue="none" value={group.race}
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
                <Input type="select" ref="agerangetype" label="Type:" defaultValue="none" value={group.ageRangeType}
                    labelClassName="col-sm-5 control-label" wrapperClassName="col-sm-7" groupClassName="form-group">
                    <option value="none" disabled="disabled">Select</option>
                    <option disabled="disabled"></option>
                    <option>Onset</option>
                    <option>Report</option>
                    <option>Diagnosis</option>
                    <option>Death</option>
                </Input>
                <Input type="text-range" labelClassName="col-sm-5 control-label" label="Value:" wrapperClassName="col-sm-7 group-age-fromto">
                    <Input type="text" ref="agefrom" inputClassName="input-inline" groupClassName="form-group-inline group-age-input" format="number"
                        error={this.getFormError('agefrom')} clearError={this.clrFormErrors.bind(null, 'agefrom')} value={group.ageRangeFrom} />
                    <span className="group-age-inter">to</span>
                    <Input type="text" ref="ageto" inputClassName="input-inline" groupClassName="form-group-inline group-age-input" format="number"
                        error={this.getFormError('ageto')} clearError={this.clrFormErrors.bind(null, 'ageto')} value={group.ageRangeTo} />
                </Input>
                <Input type="select" ref="ageunit" label="Unit:" defaultValue="none" value={group.ageRangeUnit}
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
    var group = this.state.group;
    var othergenevariantsVal = group && group.otherGenes ? group.otherGenes.map(function(gene) { return gene.symbol; }).join() : null;

    return(
        <div className="row">
            <Input type="text" ref="indcount" label="Total number individuals in group:" format="number" value={group.totalNumberIndividuals}
                error={this.getFormError('indcount')} clearError={this.clrFormErrors.bind(null, 'indcount')}
                labelClassName="col-sm-6 control-label" wrapperClassName="col-sm-6" groupClassName="form-group" required />
            <Input type="text" ref="indfamilycount" label="# individuals with family information:" format="number" value={group.numberOfIndividualsWithFamilyInformation}
                error={this.getFormError('indfamilycount')} clearError={this.clrFormErrors.bind(null, 'indfamilycount')}
                labelClassName="col-sm-6 control-label" wrapperClassName="col-sm-6" groupClassName="form-group" required />
            <Input type="text" ref="notindfamilycount" label="# individuals WITHOUT family information:" format="number" value={group.numberOfIndividualsWithoutFamilyInformation}
                error={this.getFormError('notindfamilycount')} clearError={this.clrFormErrors.bind(null, 'notindfamilycount')}
                labelClassName="col-sm-6 control-label" wrapperClassName="col-sm-6" groupClassName="form-group" required />
            <Input type="text" ref="indvariantgenecount" label="# individuals with variant in gene being curated:" format="number" value={group.numberOfIndividualsWithVariantInCuratedGene}
                error={this.getFormError('indvariantgenecount')} clearError={this.clrFormErrors.bind(null, 'indvariantgenecount')}
                labelClassName="col-sm-6 control-label" wrapperClassName="col-sm-6" groupClassName="form-group" required />
            <Input type="text" ref="notindvariantgenecount" label="# individuals without variant in gene being curated:" format="number" value={group.numberOfIndividualsWithoutVariantInCuratedGene}
                error={this.getFormError('notindvariantgenecount')} clearError={this.clrFormErrors.bind(null, 'notindvariantgenecount')}
                labelClassName="col-sm-6 control-label" wrapperClassName="col-sm-6" groupClassName="form-group" required />
            <Input type="text" ref="indvariantothercount" label="# individuals with variant found in other gene:" format="number" value={group.numberOfIndividualsWithVariantInOtherGene}
                error={this.getFormError('indvariantothercount')} clearError={this.clrFormErrors.bind(null, 'indvariantothercount')}
                labelClassName="col-sm-6 control-label" wrapperClassName="col-sm-6" groupClassName="form-group" required />
            <Input type="text" ref="othergenevariants" label={<LabelOtherGenes />} inputClassName="uppercase-input" value={othergenevariantsVal} placeholder="e.g. DICER1, SMAD3"
                error={this.getFormError('othergenevariants')} clearError={this.clrFormErrors.bind(null, 'othergenevariants')}
                labelClassName="col-sm-6 control-label" wrapperClassName="col-sm-6" groupClassName="form-group" />
        </div>
    );
};

// HTML labels for inputs follow.
var LabelOtherGenes = React.createClass({
    render: function() {
        return <span>Other genes found to have variants in them (<a href="http://www.genenames.org/" title="HGNC home page in a new tab" target="_blank">HGNC</a> symbol):</span>;
    }
});


// Methods group curation panel. Call with .call(this) to run in the same context
// as the calling component.
var GroupMethods = function() {
    var group = this.state.group;
    var method = group && group.method;

    return (
        <div className="row">
            <Input type="select" ref="prevtesting" label="Previous Testing:" defaultValue="none" value={method ? method.previousTesting : null}
                labelClassName="col-sm-5 control-label" wrapperClassName="col-sm-7" groupClassName="form-group">
                <option value="none" disabled="disabled">Select</option>
                <option disabled="disabled"></option>
                <option>Yes</option>
                <option>No</option>
            </Input>
            <Input type="textarea" ref="prevtestingdesc" label="Description of Previous Testing:" rows="5" value={method ? method.previousTestingDescription : null}
                labelClassName="col-sm-5 control-label" wrapperClassName="col-sm-7" groupClassName="form-group" />
            <Input type="select" ref="genomewide" label="Genome-wide Study?:" defaultValue="none" value={method ? method.genomeWideStudy : null}
                labelClassName="col-sm-5 control-label" wrapperClassName="col-sm-7" groupClassName="form-group">
                <option value="none" disabled="disabled">Select</option>
                <option disabled="disabled"></option>
                <option>Yes</option>
                <option>No</option>
            </Input>
            <h4 className="col-sm-7 col-sm-offset-5">Genotyping Method</h4>
            <Input type="select" ref="genotypingmethod1" label="Method 1:" defaultValue="none" value={method && method.genotypingMethods && method.genotypingMethods[0] ? method.genotypingMethods[0] : null}
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
            <Input type="select" ref="genotypingmethod2" label="Method 2:" defaultValue="none" value={method && method.genotypingMethods && method.genotypingMethods[1] ? method.genotypingMethods[1] : null}
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
            <Input type="select" ref="entiregene" label="Entire gene sequenced?:" defaultValue="none" value={method ? method.entireGeneSequenced : null}
                labelClassName="col-sm-5 control-label" wrapperClassName="col-sm-7" groupClassName="form-group">
                <option value="none" disabled="disabled">Select</option>
                <option disabled="disabled"></option>
                <option>Yes</option>
                <option>No</option>
            </Input>
            <Input type="select" ref="copyassessed" label="Copy number assessed?:" defaultValue="none" value={method ? method.copyNumberAssessed : null}
                labelClassName="col-sm-5 control-label" wrapperClassName="col-sm-7" groupClassName="form-group">
                <option value="none" disabled="disabled">Select</option>
                <option disabled="disabled"></option>
                <option>Yes</option>
                <option>No</option>
            </Input>
            <Input type="select" ref="mutationsgenotyped" label="Specific Mutations Genotyped?:" defaultValue="none" value={method ? method.specificMutationsGenotyped : null}
                labelClassName="col-sm-5 control-label" wrapperClassName="col-sm-7" groupClassName="form-group">
                <option value="none" disabled="disabled">Select</option>
                <option disabled="disabled"></option>
                <option>Yes</option>
                <option>No</option>
            </Input>
            <Input type="textarea" ref="specificmutation" label="Method by which Specific Mutations Genotyped:" rows="5" value={method ? method.specificMutationsGenotypedMethod : null}
                labelClassName="col-sm-5 control-label" wrapperClassName="col-sm-7" groupClassName="form-group" />
            <Input type="textarea" ref="additionalinfomethod" label="Additional Information about Group Method:" rows="8" value={method ? method.additionalInformation : null}
                labelClassName="col-sm-5 control-label" wrapperClassName="col-sm-7" groupClassName="form-group" />
        </div>
    );
};


// Additional Information group curation panel. Call with .call(this) to run in the same context
// as the calling component.
var GroupAdditional = function() {
    var otherpmidsVal;
    var group = this.state.group;
    if (group) {
        otherpmidsVal = group.otherPMIDs ? group.otherPMIDs.map(function(article) { return article.pmid; }).join() : null;
    }


    return (
        <div className="row">
            <Input type="textarea" ref="additionalinfogroup" label="Additional Information about Group:" rows="5" value={group.additionalInformation}
                labelClassName="col-sm-5 control-label" wrapperClassName="col-sm-7" groupClassName="form-group" />
            <Input type="textarea" ref="otherpmids" label="Enter PMID(s) that report evidence about this same group:" rows="5" value={otherpmidsVal} placeholder="e.g. 12089445, 21217753"
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
        var method = context.method;

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

                            <div>
                                <dt>HPO IDs</dt>
                                <dd>{context.hpoIdInDiagnosis.join(', ')}</dd>
                            </div>

                            <div>
                                <dt>Phenotype Terms</dt>
                                <dd>{context.termsInDiagnosis}</dd>
                            </div>

                            <div>
                                <dt>NOT HPO IDs</dt>
                                <dd>{context.hpoIdInElimination.join(', ')}</dd>
                            </div>

                            <div>
                                <dt>NOT phenotype terms</dt>
                                <dd>{context.termsInElimination}</dd>
                            </div>
                        </dl>
                    </Panel>

                    <Panel title="Group — Demographics" panelClassName="panel-data">
                        <dl className="dl-horizontal">
                            <div>
                                <dt># Males</dt>
                                <dd>{context.numberOfMale}</dd>
                            </div>

                            <div>
                                <dt># Females</dt>
                                <dd>{context.numberOfFemale}</dd>
                            </div>

                            <div>
                                <dt>Country of Origin</dt>
                                <dd>{context.countryOfOrigin}</dd>
                            </div>

                            <div>
                                <dt>Ethnicity</dt>
                                <dd>{context.ethnicity}</dd>
                            </div>

                            <div>
                                <dt>Race</dt>
                                <dd>{context.race}</dd>
                            </div>

                            <div>
                                <dt>Age Range Type</dt>
                                <dd>{context.ageRangeType}</dd>
                            </div>

                            <div>
                                <dt>Age Range</dt>
                                <dd>{context.ageRangeFrom || context.ageRangeTo ? <span>{context.ageRangeFrom + ' – ' + context.ageRangeTo}</span> : null}</dd>
                            </div>

                            <div>
                                <dt>Age Range Unit</dt>
                                <dd>{context.ageRangeUnit}</dd>
                            </div>
                        </dl>
                    </Panel>

                    <Panel title="Group — Information" panelClassName="panel-data">
                        <dl className="dl-horizontal">
                            <div>
                                <dt>Total number individuals in group</dt>
                                <dd>{context.totalNumberIndividuals}</dd>
                            </div>

                            <div>
                                <dt># individuals with family information</dt>
                                <dd>{context.numberOfIndividualsWithFamilyInformation}</dd>
                            </div>

                            <div>
                                <dt># individuals WITHOUT family information</dt>
                                <dd>{context.numberOfIndividualsWithoutFamilyInformation}</dd>
                            </div>

                            <div>
                                <dt># individuals with variant in gene being curated</dt>
                                <dd>{context.numberOfIndividualsWithVariantInCuratedGene}</dd>
                            </div>

                            <div>
                                <dt># individuals without variant in gene being curated</dt>
                                <dd>{context.numberOfIndividualsWithoutVariantInCuratedGene}</dd>
                            </div>

                            <div>
                                <dt># individuals with variant found in other gene</dt>
                                <dd>{context.numberOfIndividualsWithVariantInOtherGene}</dd>
                            </div>

                            <div>
                                <dt>Other genes found to have variants in them</dt>
                                <dd>{context.otherGenes && context.otherGenes.map(function(gene) { return gene.symbol; }).join(', ')}</dd>
                            </div>
                        </dl>
                    </Panel>

                    <Panel title="Group — Methods" panelClassName="panel-data">
                        <dl className="dl-horizontal">
                            <div>
                                <dt>Previous testing</dt>
                                <dd>{method && method.previousTesting}</dd>
                            </div>

                            <div>
                                <dt>Description of previous testing</dt>
                                <dd>{method && method.previousTestingDescription}</dd>
                            </div>

                            <div>
                                <dt>Genome-wide study</dt>
                                <dd>{method && method.genomeWideStudy}</dd>
                            </div>

                            <div>
                                <dt>Genotyping methods</dt>
                                <dd>{method && method.genotypingMethods.join(', ')}</dd>
                            </div>

                            <div>
                                <dt>Entire gene sequenced</dt>
                                <dd>{method && method.entireGeneSequenced}</dd>
                            </div>

                            <div>
                                <dt>Copy number assessed</dt>
                                <dd>{method && method.copyNumberAssessed}</dd>
                            </div>

                            <div>
                                <dt>Specific Mutations Genotyped</dt>
                                <dd>{method && method.specificMutationsGenotyped}</dd>
                            </div>

                            <div>
                                <dt>Method by which Specific Mutations Genotyped</dt>
                                <dd>{method && method.specificMutationsGenotypedMethod}</dd>
                            </div>

                            <div>
                                <dt>Additional Information about Group Method</dt>
                                <dd>{method && method.additionalInformation}</dd>
                            </div>
                        </dl>
                    </Panel>

                    <Panel title="Group — Additional Information" panelClassName="panel-data">
                        <dl className="dl-horizontal">
                            <div>
                                <dt>Additional Information about Group</dt>
                                <dd>{context.additionalInformation}</dd>
                            </div>

                            <dt>Other PMID(s) that report evidence about this same group</dt>
                            <dd>{context.otherPMIDs && context.otherPMIDs.map(function(article, i) {
                                return (
                                    <span key={i}>
                                        {i > 0 ? ', ' : ''}
                                        {article.pmid}
                                    </span>
                                );
                            })}</dd>
                        </dl>
                    </Panel>
                </div>
            </div>
        );
    }
});

globals.content_views.register(GroupViewer, 'group');
