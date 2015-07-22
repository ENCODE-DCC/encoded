'use strict';
var React = require('react');
var _ = require('underscore');
var url = require('url');
var globals = require('./globals');
var curator = require('./curator');
var modal = require('../libs/bootstrap/modal');
var form = require('../libs/bootstrap/form');
var parseAndLogError = require('./mixins').parseAndLogError;
var RestMixin = require('./rest').RestMixin;
var parsePubmed = require('../libs/parse-pubmed').parsePubmed;

var Modal = modal.Modal;
var ModalMixin = modal.ModalMixin;
var Form = form.Form;
var FormMixin = form.FormMixin;
var Input = form.Input;
var PmidDoiButtons = curator.PmidDoiButtons;
var CurationData = curator.CurationData;
var CurationPalette = curator.CurationPalette;
var PmidSummary = curator.PmidSummary;
var external_url_map = globals.external_url_map;

// Curator page content
var CurationCentral = React.createClass({
    mixins: [RestMixin],

    getInitialState: function() {
        return {
            tempPmid: '',
            currPmid: '',
            currOmimId: '',
            currGdm: {}
        };
    },

    // Called when currently selected PMID changes
    currPmidChange: function(pmid) {
        this.setState({currPmid: pmid, selectionListOpen: false});
    },

    // Retrieve the GDM object from the DB with the given uuid
    getGdm: function(uuid) {
        this.getRestData('/gdm/' + uuid).then(gdm => {
            // The GDM object successfully retrieved; set the Curator Central component
            this.setState({currGdm: gdm, currOmimId: gdm.omimId});
        }).catch(parseAndLogError.bind(undefined, 'putRequest'));
    },

    // After the Curator Central page component mounts, grab the uuid from the query string and
    // retrieve the corresponding GDM from the DB.
    componentDidMount: function() {
        // See if there’s a GDM UUID to retrieve
        var gdmUuid, pmid;
        var queryParsed = this.props.href && url.parse(this.props.href, true).query;
        if (queryParsed && Object.keys(queryParsed).length) {
            // Find the first 'gdm' query string item, if any
            var uuidKey = _(Object.keys(queryParsed)).find(function(key) {
                return key === 'gdm';
            });
            var pmidKey = _(Object.keys(queryParsed)).find(function(key) {
                return key === 'pmid';
            });
            if (uuidKey) {
                // Got the GDM key for its UUID from the query string. Now use it to retrieve that GDM
                gdmUuid = queryParsed[uuidKey];
                if (typeof gdmUuid === 'object') {
                    gdmUuid = gdmUuid[0];
                }
                this.getGdm(gdmUuid);

                pmid = queryParsed[pmidKey];
                if (typeof pmid === 'object') {
                    pmid = pmid[0];
                }
                this.setState({tempPmid: pmid});
            }
        }
    },

    componentWillReceiveProps: function(nextProps) {
        if (nextProps.loadingComplete === true && this.state.tempPmid !== '') {
            this.currPmidChange(this.state.tempPmid);
        }
    },

    // Add an article whose object is given to the current GDM
    updateGdmArticles: function(article) {
        var newAnnotation;
        var currGdm = this.state.currGdm;

        // Put together a new annotation object with the article reference
        var newAnnotationObj = {
            owner: this.props.session['auth.userid'],
            article: article.pmid,
            dateTime: new Date().toISOString(),
            active: true
        };

        // Post new annotation to the DB. fetch returns a JS promise.
        this.postRestData('/evidence/', newAnnotationObj).then(data => {
            // Save the new annotation; fetch the currently displayed GDM as an object without its embedded
            // objects; basically the object as it exists in the DB. We'll update that and write it back to the DB.
            newAnnotation = data['@graph'][0];
            return this.getRestData('/gdm/' + this.state.currGdm.uuid + '/?frame=object');
        }).then(gdmObj => {
            // We'll get 422 (Unprocessible entity) if we PUT any of these fields:
            delete gdmObj.uuid;
            delete gdmObj['@id'];
            delete gdmObj['@type'];

            // Add our new annotation reference to the array of annotations in the GDM.
            gdmObj.annotations.push('/evidence/' + newAnnotation.uuid + '/');
            return this.putRestData('/gdm/' + this.state.currGdm.uuid, gdmObj);
        }).then(data => {
            // Retrieve the updated GDM and set it as the new state GDM to force a rerendering.
            this.getGdm(data['@graph'][0].uuid);
        }).catch(parseAndLogError.bind(undefined, 'putRequest'));
    },

    updateOmimId: function(omimId) {
        this.getRestData(
            '/gdm/' + this.state.currGdm.uuid + '/?frame=object'
        ).then(gdmObj => {
            // We'll get 422 (Unprocessible entity) if we PUT any of these fields:
            delete gdmObj.uuid;
            delete gdmObj['@id'];
            delete gdmObj['@type'];

            gdmObj.omimId = omimId;
            return this.putRestData('/gdm/' + this.state.currGdm.uuid, gdmObj);
        }).then(data => {
            this.setState({currOmimId: omimId});
        }).catch(parseAndLogError.bind(undefined, 'putRequest'));
    },

    render: function() {
        var currArticle;
        var gdm = this.state.currGdm;

        // Get the PM item for the currently selected PMID
        if (this.state.currPmid) {
            var currAnnotation = _(gdm.annotations).find(annotation => {
                return annotation.article.pmid === this.state.currPmid;
            });
            currArticle = currAnnotation ? currAnnotation.article : null;
        }

        return (
            <div>
                <CurationData gdm={gdm} omimId={this.state.currOmimId} updateOmimId={this.updateOmimId} />
                <div className="container">
                    <div className="row curation-content">
                        <div className="col-md-3">
                            <PmidSelectionList annotations={gdm.annotations} currPmid={this.state.currPmid} currPmidChange={this.currPmidChange}
                                    updateGdmArticles={this.updateGdmArticles} />
                        </div>
                        <div className="col-md-6">
                            {currArticle ?
                                <div className="curr-pmid-overview">
                                    <PmidSummary article={currArticle} displayJournal />
                                    <PmidDoiButtons pmid={currArticle.pmid} />
                                    <div className="pmid-overview-abstract">
                                        <h4>Abstract</h4>
                                        <p>{currArticle.abstract}</p>
                                    </div>
                                </div>
                            : null}
                        </div>
                        {currArticle ?
                            <div className="col-md-3">
                                <CurationPalette article={currArticle} />
                            </div>
                        : null}
                    </div>
                </div>
            </div>
        );
    }
});

globals.curator_page.register(CurationCentral, 'curator_page', 'curation-central');


// Display the list of PubMed articles passed in pmidItems.
var PmidSelectionList = React.createClass({
    mixins: [ModalMixin],

    propTypes: {
        annotations: React.PropTypes.array, // List of PubMed items
        currPmid: React.PropTypes.string, // PMID of currently selected article
        currPmidChange: React.PropTypes.func, // Function to call when currently selected article changes
        updateGdmArticles: React.PropTypes.func // Function to call when we have an article to add to the GDM
    },

    render: function() {
        var annotations = _(this.props.annotations).sortBy(function(annotation) {
            // Sort list of articles by author
            return annotation.article.firstAuthor;
        });

        return (
            <div>
                <div className="pmid-selection-add">
                    <Modal title='Add new PubMed Article'>
                        <button className="btn btn-primary pmid-selection-add-btn" modal={<AddPmidModal closeModal={this.closeModal} updateGdmArticles={this.props.updateGdmArticles} />}>
                            Add New PMID(s)
                        </button>
                    </Modal>
                </div>
                {annotations ?
                    <div className="pmid-selection-list">
                        {annotations.map(annotation => {
                            var classList = 'pmid-selection-list-item' + (annotation.article.pmid === this.props.currPmid ? ' curr-pmid' : '');

                            return (
                                <div key={annotation.article.pmid} className={classList} onClick={this.props.currPmidChange.bind(null, annotation.article.pmid)}>
                                    <div className="pmid-selection-list-specs">
                                        <PmidSummary article={annotation.article} />
                                    </div>
                                    <div className="pmid-selection-list-pmid"><a href={external_url_map['PubMed'] + annotation.article.pmid} target="_blank">PMID: {annotation.article.pmid}</a></div>
                                </div>
                            );
                        })}
                    </div>
                : null}
            </div>
        );
    }
});


// The content of the Add PMID(s) modal dialog box
var AddPmidModal = React.createClass({
    mixins: [FormMixin, RestMixin],

    propTypes: {
        closeModal: React.PropTypes.func, // Function to call to close the modal
        updateGdmArticles: React.PropTypes.func // Function to call when we have an article to add to the GDM
    },

    contextTypes: {
        fetch: React.PropTypes.func // Function to perform a search
    },

    // Form content validation
    validateForm: function() {
        // Check if required fields have values
        var valid = this.validateRequired();

        // Valid if the field has only 10 or fewer digits
        if (valid) {
            valid = this.getFormValue('pmid').match(/^[0-9]{1,10}$/i);
            if (!valid) {
                this.setFormErrors('pmid', 'Only numbers allowed');
            }
        }
        return valid;
    },

    // Called when the modal form’s submit button is clicked. Handles validation and triggering
    // the process to add an article.
    submitForm: function(e) {
        e.preventDefault(); e.stopPropagation(); // Don't run through HTML submit handler
        this.setFormValue('pmid', this.refs.pmid.getValue());
        if (this.validateForm()) {
            // Form is valid -- we have a good PMID. Fetch the article with that PMID
            var enteredPmid = this.getFormValue('pmid');
            this.getRestData('/articles/' + enteredPmid).then(article => {
                // Close the modal; update the GDM with this article.
                return Promise.resolve(article);
            }, e => {
                // PubMed article not in our DB; go out to PubMed itself to retrieve it as XML
                return this.getRestDataXml(external_url_map['PubMedSearch'] + enteredPmid).then(xml => {
                    var newArticle = parsePubmed(xml, enteredPmid);
                    return this.postRestData('/articles/', newArticle).then(data => {
                        return Promise.resolve(data['@graph'][0]);
                    });
                });
            }).then(article => {
                this.props.closeModal();
                this.props.updateGdmArticles(article);
            }).catch(function(e) {
                console.log('ERROR %o', e);
            });
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
                    <Input type="text" ref="pmid" label="Enter a PubMed ID"
                        error={this.getFormError('pmid')} clearError={this.clrFormErrors.bind(null, 'pmid')}
                        labelClassName="control-label" groupClassName="form-group" required />
                </div>
                <div className='modal-footer'>
                    <Input type="cancel" inputClassName="btn-default btn-inline-spacer" cancelHandler={this.cancelForm} />
                    <Input type="submit" inputClassName="btn-primary btn-inline-spacer" title="Add Article" />
                </div>
            </Form>
        );
    }
});
