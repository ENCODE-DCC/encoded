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


var graphData = {
   nodes:[
      {
         "x":444,
         "y":275
      },
      {
         "x":378,
         "y":324
      },
      {
         "x":478,
         "y":278
      },
      {
         "x":471,
         "y":256
      },
      {
         "x":382,
         "y":269
      },
      {
         "x":371,
         "y":247
      },
      {
         "x":359,
         "y":276
      },
      {
         "x":364,
         "y":302
      },
      {
         "x":400,
         "y":330
      },
      {
         "x":388,
         "y":298
      },
      {
         "x":524,
         "y":296
      },
      {
         "x":570,
         "y":243
      },
      {
         "x":552,
         "y":159
      },
      {
         "x":502,
         "y":287
      },
      {
         "x":511,
         "y":313
      },
      {
         "x":513,
         "y":265
      },
      {
         "x":602,
         "y":132
      },
      {
         "x":610,
         "y":90
      },
      {
         "x":592,
         "y":91
      },
      {
         "x":575,
         "y":89
      },
      {
         "x":607,
         "y":73
      },
      {
         "x":591,
         "y":68
      },
      {
         "x":574,
         "y":73
      },
      {
         "x":589,
         "y":149
      },
      {
         "x":620,
         "y":205
      },
      {
         "x":621,
         "y":230
      },
      {
         "x":589,
         "y":234
      },
      {
         "x":602,
         "y":223
      },
      {
         "x":548,
         "y":188
      },
      {
         "x":532,
         "y":196
      },
      {
         "x":548,
         "y":114
      },
      {
         "x":575,
         "y":174
      },
      {
         "x":497,
         "y":250
      },
      {
         "x":576,
         "y":196
      },
      {
         "x":504,
         "y":201
      },
      {
         "x":494,
         "y":186
      },
      {
         "x":482,
         "y":199
      },
      {
         "x":505,
         "y":219
      },
      {
         "x":486,
         "y":216
      },
      {
         "x":590,
         "y":306
      },
      {
         "x":677,
         "y":169
      },
      {
         "x":657,
         "y":258
      },
      {
         "x":667,
         "y":205
      },
      {
         "x":552,
         "y":227
      },
      {
         "x":518,
         "y":173
      },
      {
         "x":473,
         "y":125
      },
      {
         "x":796,
         "y":260
      },
      {
         "x":731,
         "y":272
      },
      {
         "x":642,
         "y":288
      },
      {
         "x":576,
         "y":269
      },
      {
         "x":605,
         "y":187
      },
      {
         "x":559,
         "y":289
      },
      {
         "x":544,
         "y":356
      },
      {
         "x":505,
         "y":365
      },
      {
         "x":579,
         "y":289
      },
      {
         "x":619,
         "y":282
      },
      {
         "x":574,
         "y":329
      },
      {
         "x":664,
         "y":306
      },
      {
         "x":627,
         "y":304
      },
      {
         "x":643,
         "y":327
      },
      {
         "x":664,
         "y":348
      },
      {
         "x":665,
         "y":327
      },
      {
         "x":653,
         "y":317
      },
      {
         "x":650,
         "y":338
      },
      {
         "x":622,
         "y":321
      },
      {
         "x":633,
         "y":338
      },
      {
         "x":647,
         "y":357
      },
      {
         "x":718,
         "y":362
      },
      {
         "x":636,
         "y":240
      },
      {
         "x":640,
         "y":227
      },
      {
         "x":617,
         "y":249
      },
      {
         "x":631,
         "y":254
      },
      {
         "x":566,
         "y":213
      },
      {
         "x":713,
         "y":322
      },
      {
         "x":716,
         "y":298
      },
      {
         "x":666,
         "y":241
      },
      {
         "x":627,
         "y":355
      }
   ],
   links:[
      {
         "source":1,
         "target":0
      },
      {
         "source":2,
         "target":0
      },
      {
         "source":3,
         "target":0
      },
      {
         "source":3,
         "target":2
      },
      {
         "source":4,
         "target":0
      },
      {
         "source":5,
         "target":0
      },
      {
         "source":6,
         "target":0
      },
      {
         "source":7,
         "target":0
      },
      {
         "source":8,
         "target":0
      },
      {
         "source":9,
         "target":0
      },
      {
         "source":11,
         "target":10
      },
      {
         "source":11,
         "target":3
      },
      {
         "source":11,
         "target":2
      },
      {
         "source":11,
         "target":0
      },
      {
         "source":12,
         "target":11
      },
      {
         "source":13,
         "target":11
      },
      {
         "source":14,
         "target":11
      },
      {
         "source":15,
         "target":11
      },
      {
         "source":17,
         "target":16
      },
      {
         "source":18,
         "target":16
      },
      {
         "source":18,
         "target":17
      },
      {
         "source":19,
         "target":16
      },
      {
         "source":19,
         "target":17
      },
      {
         "source":19,
         "target":18
      },
      {
         "source":20,
         "target":16
      },
      {
         "source":20,
         "target":17
      },
      {
         "source":20,
         "target":18
      },
      {
         "source":20,
         "target":19
      },
      {
         "source":21,
         "target":16
      },
      {
         "source":21,
         "target":17
      },
      {
         "source":21,
         "target":18
      },
      {
         "source":21,
         "target":19
      },
      {
         "source":21,
         "target":20
      },
      {
         "source":22,
         "target":16
      },
      {
         "source":22,
         "target":17
      },
      {
         "source":22,
         "target":18
      },
      {
         "source":22,
         "target":19
      },
      {
         "source":22,
         "target":20
      },
      {
         "source":22,
         "target":21
      },
      {
         "source":23,
         "target":16
      },
      {
         "source":23,
         "target":17
      },
      {
         "source":23,
         "target":18
      },
      {
         "source":23,
         "target":19
      },
      {
         "source":23,
         "target":20
      },
      {
         "source":23,
         "target":21
      },
      {
         "source":23,
         "target":22
      },
      {
         "source":23,
         "target":12
      },
      {
         "source":23,
         "target":11
      },
      {
         "source":24,
         "target":23
      },
      {
         "source":24,
         "target":11
      },
      {
         "source":25,
         "target":24
      },
      {
         "source":25,
         "target":23
      },
      {
         "source":25,
         "target":11
      },
      {
         "source":26,
         "target":24
      },
      {
         "source":26,
         "target":11
      },
      {
         "source":26,
         "target":16
      },
      {
         "source":26,
         "target":25
      },
      {
         "source":27,
         "target":11
      },
      {
         "source":27,
         "target":23
      },
      {
         "source":27,
         "target":25
      },
      {
         "source":27,
         "target":24
      },
      {
         "source":27,
         "target":26
      },
      {
         "source":28,
         "target":11
      },
      {
         "source":28,
         "target":27
      },
      {
         "source":29,
         "target":23
      },
      {
         "source":29,
         "target":27
      },
      {
         "source":29,
         "target":11
      },
      {
         "source":30,
         "target":23
      },
      {
         "source":31,
         "target":30
      },
      {
         "source":31,
         "target":11
      },
      {
         "source":31,
         "target":23
      },
      {
         "source":31,
         "target":27
      },
      {
         "source":32,
         "target":11
      },
      {
         "source":33,
         "target":11
      },
      {
         "source":33,
         "target":27
      },
      {
         "source":34,
         "target":11
      },
      {
         "source":34,
         "target":29
      },
      {
         "source":35,
         "target":11
      },
      {
         "source":35,
         "target":34
      },
      {
         "source":35,
         "target":29
      },
      {
         "source":36,
         "target":34
      },
      {
         "source":36,
         "target":35
      },
      {
         "source":36,
         "target":11
      },
      {
         "source":36,
         "target":29
      },
      {
         "source":37,
         "target":34
      },
      {
         "source":37,
         "target":35
      },
      {
         "source":37,
         "target":36
      },
      {
         "source":37,
         "target":11
      },
      {
         "source":37,
         "target":29
      },
      {
         "source":38,
         "target":34
      },
      {
         "source":38,
         "target":35
      },
      {
         "source":38,
         "target":36
      },
      {
         "source":38,
         "target":37
      },
      {
         "source":38,
         "target":11
      },
      {
         "source":38,
         "target":29
      },
      {
         "source":39,
         "target":25
      },
      {
         "source":40,
         "target":25
      },
      {
         "source":41,
         "target":24
      },
      {
         "source":41,
         "target":25
      },
      {
         "source":42,
         "target":41
      },
      {
         "source":42,
         "target":25
      },
      {
         "source":42,
         "target":24
      },
      {
         "source":43,
         "target":11
      },
      {
         "source":43,
         "target":26
      },
      {
         "source":43,
         "target":27
      },
      {
         "source":44,
         "target":28
      },
      {
         "source":44,
         "target":11
      },
      {
         "source":45,
         "target":28
      },
      {
         "source":47,
         "target":46
      },
      {
         "source":48,
         "target":47
      },
      {
         "source":48,
         "target":25
      },
      {
         "source":48,
         "target":27
      },
      {
         "source":48,
         "target":11
      },
      {
         "source":49,
         "target":26
      },
      {
         "source":49,
         "target":11
      },
      {
         "source":50,
         "target":49
      },
      {
         "source":50,
         "target":24
      },
      {
         "source":51,
         "target":49
      },
      {
         "source":51,
         "target":26
      },
      {
         "source":51,
         "target":11
      },
      {
         "source":52,
         "target":51
      },
      {
         "source":52,
         "target":39
      },
      {
         "source":53,
         "target":51
      },
      {
         "source":54,
         "target":51
      },
      {
         "source":54,
         "target":49
      },
      {
         "source":54,
         "target":26
      },
      {
         "source":55,
         "target":51
      },
      {
         "source":55,
         "target":49
      },
      {
         "source":55,
         "target":39
      },
      {
         "source":55,
         "target":54
      },
      {
         "source":55,
         "target":26
      },
      {
         "source":55,
         "target":11
      },
      {
         "source":55,
         "target":16
      },
      {
         "source":55,
         "target":25
      },
      {
         "source":55,
         "target":41
      },
      {
         "source":55,
         "target":48
      },
      {
         "source":56,
         "target":49
      },
      {
         "source":56,
         "target":55
      },
      {
         "source":57,
         "target":55
      },
      {
         "source":57,
         "target":41
      },
      {
         "source":57,
         "target":48
      },
      {
         "source":58,
         "target":55
      },
      {
         "source":58,
         "target":48
      },
      {
         "source":58,
         "target":27
      },
      {
         "source":58,
         "target":57
      },
      {
         "source":58,
         "target":11
      },
      {
         "source":59,
         "target":58
      },
      {
         "source":59,
         "target":55
      },
      {
         "source":59,
         "target":48
      },
      {
         "source":59,
         "target":57
      },
      {
         "source":60,
         "target":48
      },
      {
         "source":60,
         "target":58
      },
      {
         "source":60,
         "target":59
      },
      {
         "source":61,
         "target":48
      },
      {
         "source":61,
         "target":58
      },
      {
         "source":61,
         "target":60
      },
      {
         "source":61,
         "target":59
      },
      {
         "source":61,
         "target":57
      },
      {
         "source":61,
         "target":55
      },
      {
         "source":62,
         "target":55
      },
      {
         "source":62,
         "target":58
      },
      {
         "source":62,
         "target":59
      },
      {
         "source":62,
         "target":48
      },
      {
         "source":62,
         "target":57
      },
      {
         "source":62,
         "target":41
      },
      {
         "source":62,
         "target":61
      },
      {
         "source":62,
         "target":60
      },
      {
         "source":63,
         "target":59
      },
      {
         "source":63,
         "target":48
      },
      {
         "source":63,
         "target":62
      },
      {
         "source":63,
         "target":57
      },
      {
         "source":63,
         "target":58
      },
      {
         "source":63,
         "target":61
      },
      {
         "source":63,
         "target":60
      },
      {
         "source":63,
         "target":55
      },
      {
         "source":64,
         "target":55
      },
      {
         "source":64,
         "target":62
      },
      {
         "source":64,
         "target":48
      },
      {
         "source":64,
         "target":63
      },
      {
         "source":64,
         "target":58
      },
      {
         "source":64,
         "target":61
      },
      {
         "source":64,
         "target":60
      },
      {
         "source":64,
         "target":59
      },
      {
         "source":64,
         "target":57
      },
      {
         "source":64,
         "target":11
      },
      {
         "source":65,
         "target":63
      },
      {
         "source":65,
         "target":64
      },
      {
         "source":65,
         "target":48
      },
      {
         "source":65,
         "target":62
      },
      {
         "source":65,
         "target":58
      },
      {
         "source":65,
         "target":61
      },
      {
         "source":65,
         "target":60
      },
      {
         "source":65,
         "target":59
      },
      {
         "source":65,
         "target":57
      },
      {
         "source":65,
         "target":55
      },
      {
         "source":66,
         "target":64
      },
      {
         "source":66,
         "target":58
      },
      {
         "source":66,
         "target":59
      },
      {
         "source":66,
         "target":62
      },
      {
         "source":66,
         "target":65
      },
      {
         "source":66,
         "target":48
      },
      {
         "source":66,
         "target":63
      },
      {
         "source":66,
         "target":61
      },
      {
         "source":66,
         "target":60
      },
      {
         "source":67,
         "target":57
      },
      {
         "source":68,
         "target":25
      },
      {
         "source":68,
         "target":11
      },
      {
         "source":68,
         "target":24
      },
      {
         "source":68,
         "target":27
      },
      {
         "source":68,
         "target":48
      },
      {
         "source":68,
         "target":41
      },
      {
         "source":69,
         "target":25
      },
      {
         "source":69,
         "target":68
      },
      {
         "source":69,
         "target":11
      },
      {
         "source":69,
         "target":24
      },
      {
         "source":69,
         "target":27
      },
      {
         "source":69,
         "target":48
      },
      {
         "source":69,
         "target":41
      },
      {
         "source":70,
         "target":25
      },
      {
         "source":70,
         "target":69
      },
      {
         "source":70,
         "target":68
      },
      {
         "source":70,
         "target":11
      },
      {
         "source":70,
         "target":24
      },
      {
         "source":70,
         "target":27
      },
      {
         "source":70,
         "target":41
      },
      {
         "source":70,
         "target":58
      },
      {
         "source":71,
         "target":27
      },
      {
         "source":71,
         "target":69
      },
      {
         "source":71,
         "target":68
      },
      {
         "source":71,
         "target":70
      },
      {
         "source":71,
         "target":11
      },
      {
         "source":71,
         "target":48
      },
      {
         "source":71,
         "target":41
      },
      {
         "source":71,
         "target":25
      },
      {
         "source":72,
         "target":26
      },
      {
         "source":72,
         "target":27
      },
      {
         "source":72,
         "target":11
      },
      {
         "source":73,
         "target":48
      },
      {
         "source":74,
         "target":48
      },
      {
         "source":74,
         "target":73
      },
      {
         "source":75,
         "target":69
      },
      {
         "source":75,
         "target":68
      },
      {
         "source":75,
         "target":25
      },
      {
         "source":75,
         "target":48
      },
      {
         "source":75,
         "target":41
      },
      {
         "source":75,
         "target":70
      },
      {
         "source":75,
         "target":71
      },
      {
         "source":76,
         "target":64
      },
      {
         "source":76,
         "target":65
      },
      {
         "source":76,
         "target":66
      },
      {
         "source":76,
         "target":63
      },
      {
         "source":76,
         "target":62
      },
      {
         "source":76,
         "target":48
      },
      {
         "source":76,
         "target":58
      }
   ]
};

var d3Chart = {
    // Create the D3 element and insert an SVG element into it
    create: function(el, props, state) {
        var svg = d3.select(el).append('svg')
            .attr('class', 'd3')
            .attr('width', props.width)
            .attr('height', props.height);
        svg.append('g').attr('class', 'd3-points');

        // Replace link indices with refs to node objects
        graphData.links.forEach(function(d) {
            d.source = graphData.nodes[d.source];
            d.target = graphData.nodes[d.target];
        });

        // Update the chart
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

        var link = g.attr("class", "link")
            .selectAll("line")
            .data(graphData.links)
            .enter().append("line")
            .attr("x1", function(d) { return d.source.x; })
            .attr("y1", function(d) { return d.source.y; })
            .attr("x2", function(d) { return d.target.x; })
            .attr("y2", function(d) { return d.target.y; });

        var node = g.attr("class", "node")
            .selectAll("circle")
            .data(graphData.nodes)
            .enter().append("circle")
            .attr("r", 4)
            .attr("cx", function(d) { return d.x; })
            .attr("cy", function(d) { return d.y; });
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
