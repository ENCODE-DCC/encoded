/** @jsx React.DOM */
'use strict';
var React = require('react');
var FetchedData = require('../fetched').FetchedData;
var collection = require('../collection');
var globals = require('../globals');
var search = require('../search');

var Listing = search.Listing;
var ResultTable = search.ResultTable;
var Table = collection.Table;

var ReactForms = require('react-forms');
var Schema = ReactForms.schema.Schema;
var Property = ReactForms.schema.Property;


var SearchResultsLayout = React.createClass({
    render: function() {
        var context = this.props.data;
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


var TableLayout = React.createClass({
    render: function() {
        return (
            <Table context={this.props.data} href={this.props.href} />
        );
    }
});


var SearchBlockEdit = module.exports.SearchBlockEdit = React.createClass({
    render: function() {
        var styles = {maxHeight: 300, overflow: 'scroll' };
        return (
            <div className="well" style={styles}>
                {this.transferPropsTo(<ResultTable context={this.props.data} mode="picker" />)}
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
            var url = '/search' + this.props.value;
            return <FetchedData url={url} Component={SearchBlockEdit} loadingComplete={true}
                                searchBase={this.props.value} onChange={this.props.onChange} />;
        } else {
            var url = '/search' + this.props.value.search;
            if (this.props.value.display === 'table') {
                return <FetchedData url={url} Component={TableLayout} loadingComplete={true} href={url} />;
            } else {
                return <FetchedData url={url} Component={SearchResultsLayout} loadingComplete={true} />;
            }
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
    icon: 'icon-search',
    schema: (
        <Schema>
          <Property name="display" label="Display Layout" input={displayModeSelect} defaultValue="search" />
          <Property name="search" label="Search Criteria" input={<SearchBlock mode="edit" />} />
        </Schema>
    ),
    view: SearchBlock
}, 'searchblock');
