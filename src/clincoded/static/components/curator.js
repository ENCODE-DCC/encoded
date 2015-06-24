'use strict';
var React = require('react');
var _ = require('underscore');
var modal = require('../libs/bootstrap/modal');
var globals = require('./globals');

var Modal = modal.Modal;

// Temporary hard-coded data to display
var pmid_items = require('./testdata').pmid_items;


var CuratorPage = module.exports.CuratorPage = React.createClass({
    render: function() {
        var context = this.props.context;

        var CuratorPageView = globals.curator_page.lookup(context, context.name);
        var content = <CuratorPageView context={this.props.context} />;
        return (
            <div>
                {content}
            </div>
        );
    }
});

globals.content_views.register(CuratorPage, 'curator_page');


// Curator page content
var CuratorCentral = module.exports.CuratorCentral = React.createClass({
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
                                    <div className="pmid-doi-btns">
                                        <a className="btn btn-primary" target="_blank" href={'https://www.ncbi.nlm.nih.gov/pubmed/?term=' + currPmidItem.id}>PubMed</a>
                                        <a className="btn btn-primary" target="_blank" href={'http://dx.doi.org/' + currPmidItem.doi}>doi</a>
                                    </div>
                                    <div className="pmid-overview-abstract">
                                        <h4>Abstract</h4>
                                        <p>{currPmidItem.abstract}</p>
                                    </div>
                                </div>
                            : null}
                        </div>
                        {currPmidItem ?
                            <div className="col-md-3">
                                <nav className="nav-add-evidence">
                                    <h5>Add Evidence for PMID:{currPmidItem.id}</h5>
                                    <ul className="nav nav-pills nav-stacked">
                                        <li><a className="btn btn-primary" href="#"><i className="icon icon-plus-circle"></i> Group Information</a></li>
                                        <li><a className="btn btn-primary" href="#"><i className="icon icon-plus-circle"></i> Family Information</a></li>
                                        <li><a className="btn btn-primary" href="#"><i className="icon icon-plus-circle"></i> Individual Information</a></li>
                                        <li><a className="btn btn-primary" href="#"><i className="icon icon-plus-circle"></i> Functional Information</a></li>
                                        <li><a className="btn btn-primary" href="#">Variant Information</a></li>
                                    </ul>
                                </nav>
                            </div>
                        : null}
                    </div>
                </div>
            </div>
        );
    }
});

globals.curator_page.register(CuratorCentral, 'curator_page', 'curation-central');


// Curation data header for Gene:Disease
var CurationData = React.createClass({
    render: function() {
        return (
            <div className="container curation-data">
                <div className="row equal-height">
                    <GeneCurationData />
                    <DiseaseCurationData />
                </div>
            </div>
        );
    }
});


// Display the gene section of the curation data
var GeneCurationData = React.createClass({
    render: function() {
        return (
            <div className="col-xs-12 col-sm-3 gutter-exc">
                <div className="curation-data-gene">
                    <dl>
                        <dt>Gene A</dt>
                        <dd><a href="#">HGNC:37133</a></dd>
                        <dd>EntrezID: <a href="#">503538</a></dd>
                    </dl>
                </div>
            </div>
        );
    }
});


// Display the disease section of the curation data
var DiseaseCurationData = React.createClass({
    render: function() {
        return (
            <div className="col-xs-12 col-sm-9 gutter-exc">
                <div className="curation-data-disease">
                    <dl>
                        <dt>Disease</dt>
                        <dd>Orphanet ID: <a href="#">166035</a></dd>
                        <dd>OMIM ID: <a href="#">503538</a>, <a href="#">503538</a>, <a href="#">503538</a>, <a href="#">503538</a>, <a href="#">503538</a>, <a href="#">503538</a>, <a href="#">503538</a>, <a href="#">503538</a>, <a href="#">503538</a>, <a href="#">503538</a>, <a href="#">503538</a>, <a href="#">503538</a>, <a href="#">503538</a>, <a href="#">503538</a>, <a href="#">503538</a>, <a href="#">503538</a>, </dd>
                    </dl>
                </div>
            </div>
        );
    }
});


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
                    <Modal title='Modal Title' btnOk='Submit' btnCancel='Cancel'>
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
                    <h4>Text in a modal</h4>
                    <p>Duis mollis, est non commodo luctus, nisi erat porttitor ligula.</p>
                    <h4>Tooltips in a modal</h4>
                </div>
            </div>
        );
    }
});


// Displays the PM item summary, with authors, title, citation, and DOI
var PmidSummary = React.createClass({
    propTypes: {
        pmidItem: React.PropTypes.object
    },

    render: function() {
        var item = this.props.pmidItem;

        return (
            <p>
                {item.authors[0]}
                {item.authors.length > 1 ? <span>, et al </span> : null}
                {item.title + '. '}
                {item.nlm_title + ', '}
                {item.specifier + '. doi: ' + item.doi + '.'}
            </p>
        );
    }
});
