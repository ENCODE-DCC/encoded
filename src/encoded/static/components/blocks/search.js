'use strict';
var React = require('react');
var fetched = require('../fetched');
var collection = require('../collection');
var globals = require('../globals');
var noarg_memoize = require('../../libs/noarg-memoize');
var search = require('../search');

var Listing = search.Listing;
var ResultTable = search.ResultTable;
var Table = collection.Table;


var SearchResultsLayout = React.createClass({
    render: function() {
        var context = this.props.context;
        var results = context['@graph'];
        var columns = context['columns'];
        return (
            <div className="panel">
                <ul className="nav result-table">
                    {results.length ?
                        results.map(function (result) {
                            return Listing({context: result, columns: columns, key: result['@id']});
                        })
                    : null}
                </ul>
            </div>
        );
    }
});


var SearchBlockEdit = module.exports.SearchBlockEdit = React.createClass({
    render: function() {
        var styles = {maxHeight: 300, overflow: 'scroll' };
        return (
            <div className="well" style={styles}>
                <ResultTable {...this.props} context={this.props.data} mode="picker" />)
            </div>
        );
    }
});


var SearchBlock = React.createClass({

    shouldComponentUpdate: function(nextProps) {
        return (nextProps.value != this.props.value);
    },

    render: function() {
        if (this.props.mode === 'edit') {
            var searchBase = this.props.value;
            if (!searchBase) searchBase = '?mode=picker';
            return (
                <fetched.FetchedData>
                    <fetched.Param name="data" url={'/search/' + searchBase} />
                    <SearchBlockEdit searchBase={searchBase} onChange={this.props.onChange} />
                </fetched.FetchedData>
            );
        } else {
            var url = '/search/' + (this.props.value.search || '');
            var Component = this.props.value.display === 'table' ? Table : SearchResultsLayout;
            return (
                <fetched.FetchedData> 
                    <fetched.Param name="context" url={url} />
                    <Component href={url} />
                </fetched.FetchedData>
            );
        }
    }
});


var displayModeSelect = (
    <div><select>
      <option value="search">search results</option>
      <option value="table">table</option>
    </select></div>
);


globals.blocks.register({
    label: 'search block',
    icon: 'icon icon-search',
    schema: noarg_memoize(function() {
        var ReactForms = require('react-forms');
        return ReactForms.schema.Mapping({}, {
            display: ReactForms.schema.Scalar({label: 'Display Layout', input: displayModeSelect, defaultValue: 'search'}),
            search: ReactForms.schema.Scalar({label: 'Search Criteria', input: <SearchBlock mode="edit" />}),
            className: ReactForms.schema.Scalar({label: 'CSS Class'}),
        });
    }),
    view: SearchBlock
}, 'searchblock');
