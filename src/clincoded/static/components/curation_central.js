'use strict';
var React = require('React');
var _ = require('underscore');
var globals = require('./globals');
var curator = require('./curator');
var modal = require('../libs/bootstrap/modal');
var form = require('../libs/bootstrap/form');

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
        };
    },

    currPmidChange: function(pmid) {
        this.setState({currPmid: pmid, selectionListOpen: false});
    },

    render: function() {
        var currPmidItem;

        if (this.state.currPmid) {
            currPmidItem = _(pmid_items).find(function(item) {
                return item.id === this.state.currPmid;
            }, this);
        }

        return (
            <div>
                <CurationData />
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


var PmidSelectionList = React.createClass({
    propTypes: {
        pmidItems: React.PropTypes.array,
        currPmid: React.PropTypes.number,
        currPmidChange: React.PropTypes.func
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
