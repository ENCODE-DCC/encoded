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
    propTypes: {
        gdm: React.PropTypes.object // GDM data to display
    },

    render: function() {
        var gdm = this.props.gdm;

        if (gdm && Object.keys(gdm).length > 0 && gdm['@type'][0] === 'gdm') {
            var gene = this.props.gdm.gene;
            var disease = this.props.gdm.disease;
            var mode = this.props.gdm.modeInheritance.match(/^(.*?)(?: \(HP:[0-9]*?\)){0,1}$/)[1];

            return (
                <div>
                    <div className="curation-data-title">
                        <div className="container">
                            <h1>{gene.symbol} – {disease.term}</h1>
                            <h2>{mode}</h2>
                        </div>
                    </div>
                    <div className="container curation-data">
                        <div className="row equal-height">
                            <GeneCurationData gene={gene} />
                            <DiseaseCurationData disease={disease} />
                        </div>
                    </div>
                </div>
            );
        } else {
            return null;
        }
    }
});


// Displays the PM item summary, with authors, title, citation
var PmidSummary = module.exports.PmidSummary = React.createClass({
    propTypes: {
        article: React.PropTypes.object
    },

    render: function() {
        var article = this.props.article;

        return (
            <p>
                {article.firstAuthor + '. '}
                {article.title + '. '}
                {article.date}
            </p>
        );
    }
});


var CurationPalette = module.exports.CurationPalette = React.createClass({
    propTypes: {
        article: React.PropTypes.object
    },

    render: function() {
        return (
            <Panel panelClassName="panel-evidence-group" title={'Evidence for PMID:' + this.props.article.pmid}>
                <Panel title={<CurationPaletteTitles title="Group" />} panelClassName="panel-evidence">Stuff</Panel>
                <Panel title={<CurationPaletteTitles title="Family" />} panelClassName="panel-evidence">Stuff</Panel>
                <Panel title={<CurationPaletteTitles title="Individual" />} panelClassName="panel-evidence">Stuff</Panel>
                <Panel title={<CurationPaletteTitles title="Functional" />} panelClassName="panel-evidence">Stuff</Panel>
            </Panel>
        );
    }
});


// Title for each section of the curation palette. Contains the title and an Add button.
var CurationPaletteTitles = React.createClass({
    propTypes: {
        title: React.PropTypes.string // Title to display
    },

    render: function() {
        return (
            <a href="#" className="clearfix">
                <h4 className="pull-left">{this.props.title}</h4>
                <i className="icon icon-plus-circle pull-right"></i>
            </a>
        );
    }
});


// Display the gene section of the curation data
var GeneCurationData = React.createClass({
    propTypes: {
        gene: React.PropTypes.object // Object to display
    },

    render: function() {
        var gene = this.props.gene;

        return (
            <div className="col-xs-12 col-sm-3 gutter-exc">
                <div className="curation-data-gene">
                    {gene ?
                        <dl>
                            <dt>{gene.symbol}</dt>
                            <dd><a href={gene.hgncurl} target="_blank">{gene.hgncId}</a></dd>
                            <dd>EntrezID:<a href={gene.entrezurl} target="_blank">{gene.entrezId}</a></dd>
                        </dl>
                    : null}
                </div>
            </div>
        );
    }
});


// Display the disease section of the curation data
var DiseaseCurationData = React.createClass({
    propTypes: {
        disease: React.PropTypes.object // Object to display
    },

    render: function() {
        var disease = this.props.disease;

        return (
            <div className="col-xs-12 col-sm-9 gutter-exc">
                <div className="curation-data-disease">
                    {disease ?
                        <dl>
                            <dt>{disease.term}</dt>
                            <dd>Orphanet ID: <a href={disease.url} target="_blank">{disease.orphaNumber}</a></dd>
                        </dl>
                    : null}
                </div>
            </div>
        );
    }
});


// Display buttons to bring up the PubMed and doi-specified web pages.
// For now, no doi is available
var PmidDoiButtons = module.exports.PmidDoiButtons = React.createClass({
    propTypes: {
        pmid: React.PropTypes.string // Numeric string PMID for PubMed page
    },

    render: function() {
        var pmid = this.props.pmid;

        return (
            <div className="pmid-doi-btns">
                {pmid ? <a className="btn btn-primary" target="_blank" href={'https://www.ncbi.nlm.nih.gov/pubmed/?term=' + pmid}>PubMed</a> : null}
            </div>
        );
    }
});
