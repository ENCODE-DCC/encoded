'use strict';
var React = require('react');
var _ = require('underscore');
var url = require('url');
var globals = require('./globals');
var curator = require('./curator');
var modal = require('../libs/bootstrap/modal');
var form = require('../libs/bootstrap/form');
var parseAndLogError = require('./mixins').parseAndLogError;

var Modal = modal.Modal;
var Input = form.Input;
var PmidDoiButtons = curator.PmidDoiButtons;
var CurationData = curator.CurationData;
var CurationNav = curator.CurationNav;
var PmidSummary = curator.PmidSummary;

// Temporary hard-coded data to display
var pmid_items = require('./testdata').pmid_items;


// Curator page content
var CuratorCentral = React.createClass({
    getInitialState: function() {
        return {
            currPmid: -1,
            currGdm: {}
        };
    },

    contextTypes: {
        fetch: React.PropTypes.func
    },

    currPmidChange: function(pmid) {
        this.setState({currPmid: pmid, selectionListOpen: false});
    },

    getGdm: function(uuid) {
        // Retrieve the GDM with the UUID from the query string
        var gdmRequest = this.context.fetch('/gdm/' + uuid, {
            headers: {'Accept': 'application/json'}
        }).then(response => {
            // Received Orphanet ID response or error. If the response is fine, request
            // the JSON in a promise.
            if (!response.ok) { 
                throw response;
            }
            return response.json();
        }).catch(parseAndLogError.bind(undefined, 'putRequest'))
        .then(data => {
            this.setState({currGdm: data});
        });
    },

    componentWillMount: function() {
        // See if there’s a GDM UUID to retrieve
        var gdmUuid;
        var queryParsed = this.props.href && url.parse(this.props.href, true).query;
        if (queryParsed && Object.keys(queryParsed).length) {
            // Find the first 'version' query string item, if any
            var uuidKey = _(Object.keys(queryParsed)).find(function(key) {
                return key === 'gdm';
            });
            if (uuidKey) {
                gdmUuid = queryParsed[uuidKey];
                if (typeof gdmUuid === 'object') {
                    gdmUuid = gdmUuid[0];
                }
                this.getGdm(gdmUuid);
            }
        }
    },

    render: function() {
        var currPmidItem;

        // Get the PM item for the currently selected PMID
        if (this.state.currPmid) {
            currPmidItem = _(pmid_items).find(function(item) {
                return item.id === this.state.currPmid;
            }, this);
        }

        return (
            <div>
                <CurationData gdm={this.state.currGdm} />
                <div className="container">
                    <div className="row curation-content">
                        <div className="col-md-3">
                            <PmidSelectionList pmidItems={pmid_items} currPmid={this.state.currPmid} currPmidChange={this.currPmidChange} /> 
                        </div>
                        <div className="col-md-6">
                            {currPmidItem ?
                                <div className="curr-pmid-overview">
                                    <PmidSummary pmidItem={currPmidItem} />
                                    <PmidDoiButtons pmidId={currPmidItem.id} doiId={currPmidItem.doi} />
                                    <div className="pmid-overview-abstract">
                                        <h4>Abstract</h4>
                                        <p>{currPmidItem.abstract}</p>
                                    </div>
                                </div>
                            : null}
                        </div>
                        {currPmidItem ?
                            <div className="col-md-3">
                                <CurationNav currPmidItem={currPmidItem} />
                            </div>
                        : null}
                    </div>
                </div>
            </div>
        );
    }
});

globals.curator_page.register(CuratorCentral, 'curator_page', 'curation-central');


// Display the list of PubMed articles passed in pmidItems.
var PmidSelectionList = React.createClass({
    propTypes: {
        pmidItems: React.PropTypes.array, // List of PubMed items
        currPmid: React.PropTypes.number, // PMID of currently selected article
        currPmidChange: React.PropTypes.func // Function to call when currently selected article changes
    },

    render: function() {
        var items = this.props.pmidItems;

        return (
            <div>
                <div className="pmid-selection-add">
                    <Modal title='Add New PMID(s)' btnOk='Submit' btnCancel='Cancel'>
                        <button className="btn btn-primary pmid-selection-add-btn" modal={<AddPmidModal />}>Add New PMID(s)</button>
                    </Modal>
                </div>
                <div className="pmid-selection-list">
                    {items.map(function(item) {
                        var classList = 'pmid-selection-list-item' + (item.id === this.props.currPmid ? ' curr-pmid' : '');

                        return (
                            <div key={item.id} className={classList} onClick={this.props.currPmidChange.bind(null, item.id)}>
                                <div className="pmid-selection-list-specs">
                                    <PmidSummary pmidItem={item} />
                                </div>
                                <div className="pmid-selection-list-pmid"><a href={'https://www.ncbi.nlm.nih.gov/pubmed/?term=' + item.id} target="_blank">PMID: {item.id}</a></div>
                            </div>
                        );
                    }, this)}
                </div>
            </div>
        );
    }
});


// The content of the Add PMID(s) modal dialog box
var AddPmidModal = React.createClass({
    render: function() {
        return (
            <div>
                <div className="modal-body">
                    <p>Enter a PMID ID</p>
                    <Input type="text" id="pmid-input" ref="pmid-input" label="PMID to search" />
                </div>
            </div>
        );
    }
});
