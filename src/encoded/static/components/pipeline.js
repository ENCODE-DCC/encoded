/** @jsx React.DOM */
'use strict';
var React = require('react');
var _ = require('underscore');
var d3 = require('d3');
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
    create: function(el, props, state) {
        var svg = d3.select(el).append('svg')
            .attr('class', 'd3')
            .attr('width', props.width)
            .attr('height', props.height);

        svg.append('g').attr('class', 'd3-points');

        this.update(el, state);
    },

    update: function(el, state) {
        // Re-compute the scales, and render the data points
        var scales = this._scales(el, state.domain);
        this._drawPoints(el, scales, state.data);
    },

    destroy: function(el) {
        // Any clean-up would go here
        // in this example there is nothing to do
    },

    _scales: function(el, domain) {
        if (!domain) {
            return null;
        }

        var width = el.offsetWidth;
        var height = el.offsetHeight;

        var x = d3.scale.linear()
            .range([0, width])
            .domain(domain.x);

        var y = d3.scale.linear()
            .range([height, 0])
            .domain(domain.y);

        var z = d3.scale.linear()
            .range([5, 20])
            .domain([1, 10]);

        return {x: x, y: y, z: z};
    },

    _drawPoints: function(el, scales, data) {
        var g = d3.select(el).selectAll('.d3-points');

        var point = g.selectAll('.d3-point')
            .data(data, function(d) { return d.id; }).on('mouseenter', function(data, i) {
            console.log('ENTER: %i, %o', i, data);
        }).on('mouseleave', function(data, i) {
            console.log('LEAVE: %i, %o', i, data)
        });

        // ENTER
        point.enter().append('circle')
            .attr('class', 'd3-point');

        // ENTER & UPDATE
        point.attr('cx', function(d) { return scales.x(d.x); })
            .attr('cy', function(d) { return scales.y(d.y); })
            .attr('r', function(d) { return scales.z(d.z); });

        // EXIT
        point.exit().remove();
    }
};


var Chart = React.createClass({
    propTypes: {
        data: React.PropTypes.array,
        domain: React.PropTypes.object
    },

    componentDidMount: function() {
        var el = this.getDOMNode();
        d3Chart.create(el, {
            width: '100%',
            height: '300px'
        }, this.getChartState());
    },

    componentDidUpdate: function() {
        var el = this.getDOMNode();
        d3Chart.update(el, this.getChartState());
    },

    getChartState: function() {
        return {
            data: this.props.data,
            domain: this.props.domain
        };
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


var sampleData = [
    {id: '5fbmzmtc', x: 7, y: 41, z: 6},
    {id: 's4f8phwm', x: 11, y: 45, z: 9},
];


var Graph = React.createClass({
    getInitialState: function() {
        return {
            data: sampleData,
            domain: {x: [0, 30], y: [0, 100]}
        };
    },

    render: function() {
        return (
            <div className="panel">
                <Chart data={this.state.data}
                    domain={this.state.domain} />
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
