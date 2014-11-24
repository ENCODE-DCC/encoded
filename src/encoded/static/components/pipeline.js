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
    getInitialState: function() {
        return {
            infoNode: '' // ID of node whose info panel is open
        };
    },

    // Draw the graph on initial draw as well as on state changes
    drawGraph: function(el) {
        var svg = d3.select(el).select('svg');

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

            // Render each node. Set node ID to analysis step object ID so we can find it later
            g.setNode(step['@id'], {label: stepTypesList.join(', '), rx: 4, ry: 4, class: 'analysis-step' + (this.state.infoNode === step['@id'] ? ' active' : '')});

            // If the node has parents, render the edges to those parents
            if (step.parents && step.parents.length) {
                step.parents.forEach(function(parent) {
                    g.setEdge(parent, step['@id']);
                });
            }
        }, this);

        // Run the renderer. This is what draws the final graph.
        var render = new dagreD3.render();
        render(svg, g);

        // Dagre-D3 has a width and height for the graph.
        // Set the viewbox's and viewport's width and height to that plus a little extra
        var width = g.graph().width;
        var height = g.graph().height;
        svg.attr("width", width + 20);
        svg.attr("height", height + 20);
        svg.attr("viewBox", "-10 -10 " + (width + 20) + " " + (height + 20));
    },

    // After the graph panel is mounted in the DOM, use D3/Dagre/Dagre-D3 to draw into it
    componentDidMount: function() {
        var el = this.getDOMNode();

        // Add SVG element to the graph component, and assign it classes, sizes, and a group
        var svg = d3.select(el).insert('svg', '.graph-node-info')
            .attr('class', 'd3')
            .attr('width', '960px') // Just choose an initial viewport size; we'll resize it later
            .attr('height', '300px')
            .attr('viewBox', '0 0 960 300') // Choose an inital viewbox size; we'll resize it later
            .attr('preserveAspectRatio', 'xMidYMid');
        svg.append('g').attr('class', 'd3-points');

        // Draw the graph into the panel
        this.drawGraph(el);

        // Add hover event listeners to each node rendering. Node's ID is its ENCODE object ID
        var handleMouseEnter = this.handleMouseEnter;
        var reactThis = this;
        svg.selectAll("g.node").each(function(nodeId) {
            this.addEventListener('click', function(e) {
                reactThis.handleMouseClick(e, nodeId);
            });
        });
    },

    // State change; redraw the graph
    componentDidUpdate: function() {
        var el = this.getDOMNode();
        this.drawGraph(el);
    },

    // Handle mouse clicks in any of the nodes
    handleMouseClick: function(e, nodeId) {
        this.setState({infoNode: this.state.infoNode !== nodeId ? nodeId : ''});
    },

    render: function() {
        // Find analysis step matching selected node, if any
        var displayStep;
        if (this.state.infoNode) {
            this.props.analysis_steps.some(function(step) {
                if (step['@id'] === this.state.infoNode) {
                    displayStep = step;
                    return true; // Found it; save the matching analysis step and exit loop
                } else {
                    return false; // Keep searching...
                }
            }, this);
        }

        return (
            <div className="panel graph-display">
                <div className="graph-node-info">
                    <hr />
                    <dl className="key-value">
                        <div>
                            <dt>Categories</dt>
                            <dd>
                                {displayStep ?
                                    <span>
                                        {displayStep.analysis_step_types ?
                                            <span>
                                                {displayStep.analysis_step_types.map(function(type) {
                                                    return type;
                                                }).join(', ')}
                                            </span>
                                        :
                                            <span className="select-note">Unspecified</span>
                                        }
                                    </span>
                                :
                                    <span className="select-note">Select a node above</span>
                                }
                            </dd>
                        </div>

                        <div>
                            <dt>Software</dt>
                            <dd>
                                {displayStep ?
                                    <span>
                                        {displayStep.software_versions ?
                                            <span>
                                                {displayStep.software_versions.map(function(sw, i) {
                                                    return (
                                                        <span>
                                                            {i > 0 ? ', ' : null}
                                                            <a href={sw.software['@id']}>{sw.software.title}</a>
                                                        </span>
                                                    );
                                                })}
                                            </span>
                                        :
                                            <span className="select-note">Unspecified</span>
                                        }
                                    </span>
                                :
                                    <span className="select-note">Select a node above</span>
                                }
                            </dd>
                        </div>

                        <div>
                            <dt>Input file types</dt>
                            <dd>
                                {displayStep ?
                                    <span>
                                        {displayStep.input_file_types ?
                                            <span>
                                                {displayStep.input_file_types.map(function(type) {
                                                    return type;
                                                }).join(', ')}
                                            </span>
                                        :
                                            <span className="select-note">Unspecified</span>
                                        }
                                    </span>
                                :
                                    <span className="select-note">Select a node above</span>
                                }
                            </dd>
                        </div>

                        <div>
                            <dt>Output file types</dt>
                            <dd>
                                {displayStep ?
                                    <span>
                                        {displayStep.output_file_types ?
                                            <span>
                                                {displayStep.output_file_types.map(function(type) {
                                                    return type;
                                                }).join(', ')}
                                            </span>
                                        :
                                            <span className="select-note">Unspecified</span>
                                        }
                                    </span>
                                :
                                    <span className="select-note">Select a node above</span>
                                }
                            </dd>
                        </div>
                    </dl>
                </div>
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
