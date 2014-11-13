/** @jsx React.DOM */
'use strict';
var React = require('react');
var _ = require('underscore');
var d3 = require('d3');
var dagreD3 = require('dagre-d3');
var globals = require('./globals');
var dbxref = require('./dbxref');
var search = require('./search');
var StatusLabel = require('./statuslabel').StatusLabel;
var Citation = require('./publication').Citation;

var _ = require('underscore');

var DbxrefList = dbxref.DbxrefList;

var Panel = function (props) {
    // XXX not all panels have the same markup
    var context;
    if (props['@id']) {
        context = props;
        props = {context: context};
    }
    return globals.panel_views.lookup(props.context)(props);
};



var Pipeline = module.exports.Pipeline = React.createClass({
    render: function() {
        var context = this.props.context;
        var itemClass = globals.itemClass(context, 'view-item');

        var documents = {};
        if (context.documents) {
            context.documents.forEach(function(doc, i) {
                documents[doc['@id']] = Panel({context: doc, key: i + 1});
            });
        }

        return (
            <div className={itemClass}>
                <header className="row">
                    <div className="col-sm-12">
                        <h2>{context.title}</h2>
                        <div className="characterization-status-labels">
                            <StatusLabel title="Status" status={context.status} />
                        </div>
                    </div>
                </header>

                <div className="panel data-display">
                    <dl className="key-value">
                        <div data-test="title">
                            <dt>Title</dt>
                            {context.source_url ?
                                <dd><a href={context.source_url}>{context.title}</a></dd> :
                                <dd>{context.title}</dd>
                            }
                        </div>

                        <div data-test="assay">
                            <dt>Assay</dt>
                            <dd>{context.assay_term_name}</dd>
                        </div>
                    </dl>
                      {context.analysis_steps && context.analysis_steps.length ?
                          <div>
                              <h3>Steps</h3>
                              <div className="panel view-detail" data-test="supplementarydata">
                                  {context.analysis_steps.map(function(props, i) {
                                      return AnalysisStep (props, i) ;
                                  })}
                              </div>
                          </div>
                      : null}
                </div>
                {Object.keys(documents).length ?
                    <div data-test="protocols">
                        <h3>Documents</h3>
                        <div className="row multi-columns-row">
                            {documents}
                        </div>
                    </div>
                : null}
                <Graph />
            </div>

        );
    }
});
globals.content_views.register(Pipeline, 'pipeline');


var d3Chart = {
    // Create the D3 element and insert an SVG element into it
    create: function(el, props, state) {
        var svg = d3.select(el).append('svg')
            .attr('class', 'd3')
            .attr('width', props.width)
            .attr('height', props.height);
        svg.append('g').attr('class', 'd3-points');

        var g = new dagreD3.graphlib.Graph()
            .setGraph({rankdir: "LR"})
            .setDefaultEdgeLabel(function() { return {}; });

        // Here we"re setting nodeclass, which is used by our custom drawNodes function
        // below.
        g.setNode(0,  { label: "TOP",       class: "type-TOP" });
        g.setNode(1,  { label: "S",         class: "type-S" });
        g.setNode(2,  { label: "NP",        class: "type-NP" });
        g.setNode(3,  { label: "DT",        class: "type-DT" });
        g.setNode(4,  { label: "This",      class: "type-TK" });
        g.setNode(5,  { label: "VP",        class: "type-VP" });
        g.setNode(6,  { label: "VBZ",       class: "type-VBZ" });
        g.setNode(7,  { label: "is",        class: "type-TK" });
        g.setNode(8,  { label: "NP",        class: "type-NP" });
        g.setNode(9,  { label: "DT",        class: "type-DT" });
        g.setNode(10, { label: "an",        class: "type-TK" });
        g.setNode(11, { label: "NN",        class: "type-NN" });
        g.setNode(12, { label: "example",   class: "type-TK" });
        g.setNode(13, { label: ".",         class: "type-." });
        g.setNode(14, { label: "sentence",  class: "type-TK" });

        g.nodes().forEach(function(v) {
            var node = g.node(v);
            // Round the corners of the nodes
            node.rx = node.ry = 5;
        });

        // Set up edges, no special attributes.
        g.setEdge(3, 4);
        g.setEdge(2, 3);
        g.setEdge(1, 2);
        g.setEdge(6, 7);
        g.setEdge(5, 6);
        g.setEdge(9, 10);
        g.setEdge(8, 9);
        g.setEdge(11,12);
        g.setEdge(8, 11);
        g.setEdge(5, 8);
        g.setEdge(13,14);
        g.setEdge(1, 13);
        g.setEdge(0, 1);

        // Update the chart
        this.update(el, g);
    },

    update: function(el, g) {
        // Re-compute the scales, and render the data points
        this._drawPoints(el, g);
    },

    destroy: function(el) {
        // Any clean-up would go here
        // in this example there is nothing to do
    },

    _drawPoints: function(el, g) {
        var render = new dagreD3.render();

        // Set up an SVG group so that we can translate the final graph.
        var svg = d3.select("svg");
        var svgGroup = svg.append("g");

        // Run the renderer. This is what draws the final graph.
        render(d3.select("svg g"), g);

        // Center the graph
        var xCenterOffset = (svg.attr("width") - g.graph().width) / 2;
        svgGroup.attr("transform", "translate(" + xCenterOffset + ", 20)");
        svg.attr("height", g.graph().height + 40);
    }
};


var Chart = React.createClass({
    componentDidMount: function() {
        var el = this.getDOMNode();
        d3Chart.create(el, {
            width: '100%',
            height: '300px'
        });
    },

    componentDidUpdate: function() {
        var el = this.getDOMNode();
        d3Chart.update(el);
    },

    componentWillUnmount: function() {
        var el = this.getDOMNode();
        d3Chart.destroy(el);
    },

    render: function() {
        return (
            <div className="Chart"></div>
        );
    }
});


var Graph = React.createClass({
    render: function() {
        return (
            <div className="panel">
                <Chart />
            </div>
        );
    }
});


var AnalysisStep = module.exports.AnalysisStep = function (props) {
    var typesList = props.analysis_step_types.join(", ");

    return (
        <div key={props.key} className="panel-replicate">
            <dl className="panel key-value">
                {props.analysis_step_types.length ?
                    <dl data-test="analysis_step_types">
                        <dt>Category</dt>
                        <dd>{typesList}</dd>
                    </dl>
                : null}
                {props.software_versions.length ?
                	<dl>
                	<dt> Software</dt>
                	<dd>
                	{props.software_versions.map(function(software_version, i) {
                		return ( <span> {
                			i > 0 ? ", ": ""
                		}
                		<a href ={software_version.software['@id']}>{software_version.software.title}</a>
                		</span>)
                	}
                	)}
                	</dd>
                	</dl>
                : null}
            </dl>
        </div>
    );
};



var Listing = React.createClass({
    mixins: [search.PickerActionsMixin],
    render: function() {
        var context = this.props.context;
        var result = this.props.context;
        return (<li>
                    <div>
                        {this.renderActions()}
                        <div className="pull-right search-meta">
                            <p className="type meta-title">Pipeline</p>
                            {context.status ? <p className="type meta-status">{' ' + context.status}</p> : ''}
                        </div>
                        <div className="accession">
                            <a href={result['@id']}>
                            	{result['title']}
                            </a>
                        </div>
                    </div>
            </li>
        );
    }
});
globals.listing_views.register(Listing, 'pipeline');
