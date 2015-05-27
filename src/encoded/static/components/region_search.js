'use strict';
var React = require('react');
var globals = require('./globals');

var RegionSearch = module.exports.RegionSearch = React.createClass({
    render: function() {
        var context = this.props.context;
        return (
          <div className="panel data-display main-panel">
              Nikhil R Podduturi
          </div>
        );
    }
});

globals.content_views.register(RegionSearch, 'region-search');
