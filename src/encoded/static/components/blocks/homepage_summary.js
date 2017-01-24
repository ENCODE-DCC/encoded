'use strict';
var React = require('react');
var fetched = require('../fetched');
var globals = require('../globals');
var search = require('../search');
var url = require('url');
var svgIcon = require('../../libs/svg-icons').svgIcon;

var Facet = search.Facet;


var HomepageSummary = React.createClass({
    render: function() {
        var {data, searchBase, onFilter} = this.props;

        var facetMap = {};
        if (data.facets !== undefined) {
            data.facets.forEach((facet) => {
                facetMap[facet.field] = facet;
            });
        }

        var facetProps = {
            filters: data.filters,
            searchBase: searchBase,
            onFilter: onFilter,
            width: null,
            hideZeros: false
        };

        return (
            <div className="homepage-facets">
                <h3>Search by...</h3>
                <div className="homepage-summary-row">
                    <Facet facet={facetMap['replicates.library.biosample.donor.organism.scientific_name']} {...facetProps} />
                    <Facet facet={facetMap['award.project']} {...facetProps} />
                </div>
                <div className="homepage-summary-count">
                    <h2>{data.total} experiment{data.total === 1 ? '' : 's'} found.</h2>
                    <div>
                        <a className="btn btn-info" href={'/search/' + searchBase}>{svgIcon('search')} List</a>
                        {' '}<a className="btn btn-info" href={'/report/' + searchBase}>{svgIcon('table')} Table</a>
                        {' '}<a className="btn btn-info" href={'/matrix/' + searchBase}>{svgIcon('matrix')} Matrix</a>
                    </div>
                </div>
                <div className="homepage-summary-row">
                    <Facet facet={facetMap['organ_slims']} {...facetProps} />
                    <Facet facet={facetMap['assay_slims']} {...facetProps} />
                </div>
            </div>
        );
    },

});


var HomepageSummaryLoader = React.createClass({

    getDefaultProps: function () {
        return {searchBase: '?type=Experiment'};
    },

    getInitialState: function() {
        return {search: this.props.searchBase};
    },

    render: function() {
        return (
            <fetched.FetchedData>
                <fetched.Param name="data" url={'/search/' + this.state.search} />
                <HomepageSummary searchBase={this.state.search + '&'} onFilter={this.onFilter} />
            </fetched.FetchedData>
        );
    },

    onFilter: function(e) {
        e.stopPropagation();
        e.preventDefault();
        var search = url.parse(e.currentTarget.getAttribute('href')).search;
        this.setState({search: search});
    }

});


globals.blocks.register({
    label: 'homepage summary',
    icon: 'icon icon-house',
    view: HomepageSummaryLoader,
    edit: null
}, 'homepage-summary-block');
