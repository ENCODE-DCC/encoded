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
                {context.analysis_steps && context.analysis_steps.length ?
                    <Graph analysis_steps={context.analysis_steps} />                                      
                : null}
            </div>

        );
    }
});
globals.content_views.register(Pipeline, 'pipeline');


var Graph = React.createClass({
    componentDidMount: function() {
        var el = this.getDOMNode();

        // Add SVG element to this component, and assign it classes, sizes, and a group
        var svg = d3.select(el).append('svg')
            .attr('class', 'd3')
            .attr('width', '100%')
            .attr('height', '300px');
        svg.append('g').attr('class', 'd3-points');

        // Define a linear gradient, called #step-gradient
        svg.append('linearGradient')
            .attr('id', 'step-gradient')
            .attr('x1', 0).attr('x2', 0).attr('y1', 0).attr('y2', 1)
            .selectAll('stop')
            .data([
                {offset: '0%', color: '#FEFCEA'},
                {offset: '100%', color: '#FFF5BA'}
            ])
        .enter().append("stop")
            .attr('offset', function(d) { return d.offset; })
            .attr('stop-color', function(d) { return d.color; });

        // Create a new empty graph
        var g = new dagreD3.graphlib.Graph()
            .setGraph({rankdir: "LR"})
            .setDefaultEdgeLabel(function() { return {}; });

        // Loop over each analysis step to insert it into the graph
        this.props.analysis_steps.forEach(function(step) {
            // Make an array of step types
            var stepTypesList = step.analysis_step_types.map(function(type) {
                return type;
            });

            // Render each node
            g.setNode(step['@id'], {label: stepTypesList.join(', '), rx: 4, ry: 4, class: 'analysis-step', style: 'fill: url(#step-gradient)'});
            if (step.parents && step.parents.length) {
                step.parents.forEach(function(parent) {
                    g.setEdge(step['@id'], parent);
                });
            }
        });

        // Run the renderer. This is what draws the final graph.
        var render = new dagreD3.render();
        render(d3.select("svg g"), g);

        // Center the graph
        var svgGroup = svg.append("g");
        var xCenterOffset = (svg.attr("width") - g.graph().width) / 2;
        svgGroup.attr("transform", "translate(" + xCenterOffset + ", 20)");
        svg.attr("height", g.graph().height + 40);
    },

    render: function() {
        return (
            <div className="panel">
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
