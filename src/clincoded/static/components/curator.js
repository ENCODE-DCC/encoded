'use strict';
var React = require('react');
var _ = require('underscore');
var globals = require('./globals');

// Temporary hard-coded data to display
var pmid_items = require('./testdata').pmid_items;


// Curator page content
var Curator = module.exports.Curator = React.createClass({
    getInitialState: function() {
        return {
            currPmid: '',
            selectionListOpen: false
        };
    },

    selectionListOpenChange: function() {
        this.setState({selectionListOpen: !this.state.selectionListOpen});
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
                        <div className="col-sm-8">
                            <PmidSelectionTrigger pmidItems={pmid_items} selectionListOpenChange={this.selectionListOpenChange} currPmid={this.state.currPmid} />
                            {this.state.selectionListOpen ? <PmidSelectionList pmidItems={pmid_items} currPmidChange={this.currPmidChange} /> : null}
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
                            <div className="col-sm-4">
                                <nav className="nav-add-evidence">
                                    <h5>Add Evidence for PMID:{currPmidItem.id}</h5>
                                    <ul className="nav nav-pills nav-stacked">
                                        <li><a className="btn btn-primary" href="#">Add New Group Information</a></li>
                                        <li><a className="btn btn-primary" href="#">Add New Family Information</a></li>
                                        <li><a className="btn btn-primary" href="#">Add New Individual Information</a></li>
                                        <li><a className="btn btn-primary" href="#">Add New Functional Information</a></li>
                                        <li><a className="btn btn-primary" href="#">View Variant Information</a></li>
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

globals.cg_template.register(Curator, 'curator');


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


// Controls the display of the Pmid selection area; this is the trigger part
var PmidSelectionTrigger = React.createClass({
    propTypes: {
        selectionListOpenChange: React.PropTypes.func,
        currPmid: React.PropTypes.string
    },

    render: function() {
        return (
            <div className="pmid-selection-trigger clearfix">
                <div className="pmid-selection-selected">
                    <button className="btn btn-primary" onClick={this.props.selectionListOpenChange}>Select</button>
                    <span className="pmid-selection-curr-id">{'PMID: ' + this.props.currPmid}</span>
                </div>
                <button className="btn btn-primary btn-add-new-pmid">Add New PMID</button>
            </div>
        );
    }
});


var PmidSelectionList = React.createClass({
    propTypes: {
        pmidItems: React.PropTypes.object,
        currPmidChange: React.PropTypes.func
    },

    render: function() {
        var items = this.props.pmidItems;

        return (
            <div className="pmid-selection-list">
                {items.map(function(item) {
                    return (
                        <div key={item.id} className="pmid-selection-list-item" onClick={this.props.currPmidChange.bind(this, item.id)}>
                            <div className="pmid-selection-list-pmid"><a href={'https://www.ncbi.nlm.nih.gov/pubmed/?term=' + item.id}>PMID: {item.id}</a></div>
                            <div className="pmid-selection-list-specs">
                                <PmidSummary pmidItem={item} />
                            </div>
                        </div>
                    );
                }, this)}
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
