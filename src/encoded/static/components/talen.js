'use strict';
var React = require('react');
var globals = require('./globals');
var search = require('./search');
var statuslabel = require('./statuslabel');
var navbar = require('./navbar');

var StatusLabel = statuslabel.StatusLabel;
var Breadcrumbs = navbar.Breadcrumbs;


var Panel = function (props) {
    // XXX not all panels have the same markup
    var context;
    if (props['@id']) {
        context = props;
        props = {context: context, key: context['@id']};
    }
    var PanelView = globals.panel_views.lookup(props.context);
    return <PanelView {...props} />;
};


// Display a stand-alone TALEN page.
var TalenPage = React.createClass({
    render: function() {
        var context = this.props.context;
        var talen = Panel({context: context});
        var itemClass = globals.itemClass(context, 'view-item');

        var crumbs = [
            {id: 'TALENs'},
            {id: context.talen_platform, query: 'talen_platform=' + context.talen_platform, tip: context.talen_platform}
        ];

        return (
            <div className={itemClass}>
                <header className="row">
                    <div className="col-sm-12">
                        <Breadcrumbs root='/search/?type=talen' crumbs={crumbs} />
                        <h2>TALEN summary for {context.name}</h2>
                        <div className="status-line">
                            <div className="characterization-status-labels">
                                <StatusLabel title="Status" status={context.status} />
                            </div>
                        </div>
                    </div>
                </header>
                <div className="panel panel-default">
                    {talen}
                </div>
            </div>
        );
    }
});

globals.content_views.register(TalenPage, 'TALEN');


// Display a TALENs panel. We can have multiple TALENs in one panel
var Talen = React.createClass({
    propTypes: {
        context: React.PropTypes.object.isRequired // TALEN object
    },

    render: function() {
        var context = this.props.context;
        var coordinates = context.target_genomic_coordinates;

        // Collect the TALEN construct documents
        var construct_documents = {};
        context.documents.forEach(function (doc, i) {
            construct_documents[doc['@id']] = Panel({context: doc, key: i + 1});
        });

        return (
            <div className="panel-body">
                <dl className="key-value">
                    <div data-test="name">
                        <dt>Name</dt>
                        <dd>{context.name}</dd>
                    </div>

                    <div data-test="rvd">
                        <dt>RVD sequence</dt>
                        <dd>{context.RVD_sequence}</dd>
                    </div>

                    <div data-test="targetsequence">
                        <dt>Target sequence</dt>
                        <dd>{context.target_sequence}</dd>
                    </div>

                    <div data-test="genomeassembly">
                        <dt>Genome assembly</dt>
                        <dd>{coordinates.assembly}</dd>
                    </div>

                    <div data-test="targetsequence">
                        <dt>Genomic coordinates</dt>
                        <dd>chr{coordinates.chromosome}:{coordinates.start}-{coordinates.end}</dd>
                    </div>

                    <div data-test="platform">
                        <dt>TALEN platform</dt>
                        <dd>{context.talen_platform}</dd>
                    </div>

                    <div data-test="backbone">
                        <dt>Backbone name</dt>
                        <dd>{context.vector_backbone_name}</dd>
                    </div>
                </dl>

                {Object.keys(construct_documents).length ?
                    <div>
                        <h3>Construct documents</h3>
                        <div className="row multi-columns-row">
                            {construct_documents}
                        </div>
                    </div>
                : null}
            </div>
        );
    }
});

globals.panel_views.register(Talen, 'TALEN');


// Search result page output
var Listing = React.createClass({
    mixins: [search.PickerActionsMixin],

    render: function() {
        var result = this.props.context;
        var coordinates = result.target_genomic_coordinates;

        return (
            <li>
                <div className="clearfix">
                    {this.renderActions()}
                    <div className="pull-right search-meta">
                        <p className="type meta-title">TALEN</p>
                        {result.status ? <p className="type meta-status">{' ' + result.status}</p> : ''}
                    </div>
                    <div className="accession">
                        <a href={result['@id']}>{result.name}</a>
                    </div>
                    <div className="data-row">
                        {result.description ? <div>{result.description}</div> : null}
                        <div><strong>Platform: </strong>{result.talen_platform}</div>
                        <div>
                            <strong>Genomic coordinates: </strong>
                            <span>chr{coordinates.chromosome}:{coordinates.start}-{coordinates.end}</span>
                        </div>
                    </div>
                </div>
            </li>
        );
    }
});

globals.listing_views.register(Listing, 'TALEN');
