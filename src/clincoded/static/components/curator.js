'use strict';
var React = require('react');
var panel = require('../libs/bootstrap/panel');
var globals = require('./globals');

var Panel = panel.Panel;


var CuratorPage = module.exports.CuratorPage = React.createClass({
    render: function() {
        var context = this.props.context;

        var CuratorPageView = globals.curator_page.lookup(context, context.name);
        var content = <CuratorPageView {...this.props} />;
        return (
            <div>{content}</div>
        );
    }
});

globals.content_views.register(CuratorPage, 'curator_page');


// Curation data header for Gene:Disease
var CurationData = module.exports.CurationData = React.createClass({
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


// Displays the PM item summary, with authors, title, citation, and DOI
var PmidSummary = module.exports.PmidSummary = React.createClass({
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


var CurationNav = module.exports.CurationNav = React.createClass({
    render: function() {
        return (
            <Panel panelClassName="panel-evidence-group" title={'Evidence for PMID:' + this.props.currPmidItem.id}>
                <Panel title="Group">Stuff</Panel>
                <Panel title="Family">Stuff</Panel>
                <Panel title="Individual">Stuff</Panel>
                <Panel title="Functional">Stuff</Panel>
            </Panel>
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
                    </dl>
                </div>
            </div>
        );
    }
});


var PmidDoiButtons = module.exports.PmidDoiButtons = React.createClass({
    propTypes: {
        pmidId: React.PropTypes.string, // Numeric string PMID
        doiId: React.PropTypes.string // DOI ID
    },

    render: function() {
        var pmidId = this.props.pmidId;
        var doiId = this.props.doiId;

        return (
            <div className="pmid-doi-btns">
                {pmidId ? <a className="btn btn-primary" target="_blank" href={'https://www.ncbi.nlm.nih.gov/pubmed/?term=' + pmidId}>PubMed</a> : null}
                {doiId ? <a className="btn btn-primary" target="_blank" href={'http://dx.doi.org/' + doiId}>doi</a> : null}
            </div>
        );
    }
});
