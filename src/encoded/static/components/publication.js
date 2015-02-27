'use strict';
var React = require('react');
var globals = require('./globals');
var dbxref = require('./dbxref');
var search = require('./search');

var DbxrefList = dbxref.DbxrefList;
var Dbxref = dbxref.Dbxref;


var Publication = module.exports.Panel = React.createClass({
    render: function() {
        var context = this.props.context;
        var itemClass = globals.itemClass(context, 'view-item');
        return (
            <div className={itemClass}>
                <h2>{context.title}</h2>
                {context.authors ? <div className="authors">{context.authors}.</div> : null}
                <div className="journal">
                    {this.transferPropsTo(<Citation />)}
                </div>

                {context.abstract || context.data_used || (context.datasets && context.datasets.length) || (context.references && context.references.length) ?
                    <div className="view-detail panel">
                        {this.transferPropsTo(<Abstract />)}
                    </div>
                : null}

                {context.supplementary_data && context.supplementary_data.length ?
                    <div>
                        <h3>Related data</h3>
                        <div className="panel view-detail" data-test="supplementarydata">
                            {context.supplementary_data.map(function(data, i) {
                                return <SupplementaryData data={data} key={i} />;
                            })}
                        </div>
                    </div>
                : null}
            </div>
        );
    }
});

globals.content_views.register(Publication, 'publication');


var Citation = module.exports.Citation = React.createClass({
    render: function() {
        var context = this.props.context;
        return (
            <span>
                {context.journal ? <i>{context.journal}. </i> : ''}{context.date_published ? context.date_published + ';' : ''}
                {context.volume ? context.volume : ''}{context.issue ? '(' + context.issue + ')' : '' }{context.page ? ':' + context.page + '.' : ''}
            </span>
        );
    }
});


var Abstract = React.createClass({
    render: function() {
        var context = this.props.context;
        return (
            <dl className="key-value">
                {context.abstract ?
                    <div data-test="abstract">
                        <dt>Abstract</dt>
                        <dd>{context.abstract}</dd>
                    </div>
                : null}

                {context.data_used ?
                    <div data-test="dataused">
                        <dt>Consortium data used in this publication</dt>
                        <dd>{context.data_used}</dd>
                    </div>
                : null}

                {context.datasets && context.datasets.length ?
                    <div data-test="datasets">
                        <dt>Datasets</dt>
                        <dd>
                            {context.datasets.map(function(dataset, i) {
                                return (
                                    <span key={i}>
                                        {i > 0 ? ', ' : ''}
                                        <a href={dataset['@id']}>{dataset.accession}</a>
                                    </span>
                                );
                            })}
                        </dd>
                    </div>
                : null}

                {context.references && context.references.length ?
                    <div data-test="references">
                        <dt>References</dt>
                        <dd><DbxrefList values={context.references} className="multi-value" /></dd>
                    </div>
                : null}
           </dl>
        );
    }
});


var SupplementaryData = React.createClass({
    render: function() {
        var data = this.props.data;
        return (
            <section>
                {this.props.key > 0 ? <hr /> : null}
                <dl className="key-value" key={this.props.key}>
                    {data.supplementary_data_type ?
                        <div data-test="availabledata">
                            <dt>Available data</dt>
                            <dd>{data.supplementary_data_type}</dd>
                        </div>
                    : null}

                    {data.file_format ?
                        <div data-test="fileformat">
                            <dt>File format</dt>
                            <dd>{data.file_format}</dd>
                        </div>
                    : null}

                    {data.url ?
                        <div data-test="url">
                            <dt>URL</dt>
                            <dd><a href={data.url}>{data.url}</a></dd>
                        </div>
                    : null}

                    {data.data_summary ?
                        <div data-test="datasummary">
                            <dt>Data summary</dt>
                            <dd>{data.data_summary}</dd>
                        </div>
                    : null}
                </dl>
            </section>
        );
    }
});


var SupplementaryDataListing = React.createClass({
    getInitialState: function() {
        return {excerptExpanded: false};
    },

    handleClick: function() {
        this.setState({excerptExpanded: !this.state.excerptExpanded});
    },

    render: function() {
        var data = this.props.data;
        var columns = this.props.columns;

        var summary = data.data_summary;
        var excerpt = (summary && (summary.length > 100) ? globals.truncateString(summary, 100) : undefined);

        // Make unique ID for ARIA identification
        var nodeId = this.props.id.replace(/\//g, '') + this.props.key;

        return (
            <div className="list-supplementary" key={this.props.key}>
                {data.supplementary_data_type ?
                    <span><strong>{columns['supplementary_data.supplementary_data_type']['title']}</strong>: {data.supplementary_data_type}<br /></span>
                : null}

                {data.file_format ?
                    <span><strong>{columns['supplementary_data.file_format']['title']}</strong>: {data.file_format}<br /></span>
                : null}

                {data.url ?
                    <span><strong>{columns['supplementary_data.url']['title']}</strong>: <a href={data.url}>{data.url}</a><br /></span>
                : null}

                {summary ?
                    <span id={nodeId} aria-expanded={excerpt ? this.state.excerptExpanded : true}>
                        <strong>{columns['supplementary_data.data_summary']['title']}</strong>: {excerpt ?
                            <span>
                                {this.state.excerptExpanded ? summary : excerpt}
                                <button className="btn btn-link" aria-controls={nodeId} onClick={this.handleClick}>
                                    {this.state.excerptExpanded ? <span>See less</span> : <span>See more</span>}
                                </button>
                            </span>
                        : summary}
                    </span>
                : null}
            </div>
        );
    }
});


var Listing = React.createClass({
    mixins: [search.PickerActionsMixin],
    render: function() {
        var result = this.props.context;
        var columns = this.props.columns;
        var authorList = result.authors && result.authors.length ? result.authors.split(', ', 4) : [];
        var authors = authorList.length === 4 ? authorList.splice(0, 3).join(', ') + ', et al' : result.authors;

        return (
            <li>
                {this.renderActions()}
                <div className="pull-right search-meta">
                    <p className="type meta-title">Publication</p>
                    <p className="type meta-status">{' ' + result.status}</p>
                </div>
                <div className="accession"><a href={result['@id']}>{result.title}</a></div>
                <div className="data-row">
                    {authors ? <p className="list-author">{authors}.</p> : null}
                    <p className="list-citation">{this.transferPropsTo(<Citation />)}</p>
                    {result.references && result.references.length ? <DbxrefList values={result.references} className="list-reference" /> : '' }
                    {result.supplementary_data && result.supplementary_data.length ?
                        <div>
                            {result.supplementary_data.map(function(data, i) {
                                return <SupplementaryDataListing data={data} columns={columns} id={result['@id']} key={i} />;
                            })}
                        </div>
                    : null}
                </div>
            </li>
        );
    }
});

globals.listing_views.register(Listing, 'publication');
