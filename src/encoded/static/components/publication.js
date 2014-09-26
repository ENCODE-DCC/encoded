/** @jsx React.DOM */
'use strict';
var React = require('react');
var globals = require('./globals');
var dbxref = require('./dbxref');
var search = require('./search');

var DbxrefList = dbxref.DbxrefList;
var Dbxref = dbxref.Dbxref;

var Citation = module.exports.Citation = React.createClass({
    render: function() {
        var context = this.props.context;
        return (
            <span>
                {context.journal ? <i>{context.journal}. </i> : ''}{context.date_published ? context.date_published + ';' : ''}{context.volume ? context.volume : ''}{context.issue ? '(' + context.issue + ')' : '' }{context.page ? ':' + context.page + '.' : ''}
            </span>
        );
    }
});


var SupplementaryData = React.createClass({
    render: function() {
        var data = this.props.data;
        return (
            <dl key={data.key}>
                {data.element_type ?
                    <div data-test="elementtype">
                        <dt>Element type</dt>
                        <dd>{data.element_type}</dd>
                    </div>
                : null}

                {data.file_format ?
                    <div data-test="fileformat">
                        <dt>File format</dt>
                        <dd>{data.file_format}</dd>
                    </div>
                : null}

                {data.url ?
                    <div data-test="urls">
                        <dt>URL</dt>
                        <dd><a href={data.url}>{data.url}</a></dd>
                    </div>
                : null}

                {data.method_summary ?
                    <div data-test="methodsummary">
                        <dt>Method summary</dt>
                        <dd>{data.method_summary}</dd>
                    </div>
                : null}
            </dl>
        );
    }
});


var Panel = module.exports.Panel = React.createClass({
    render: function() {
        var context = this.props.context;
        var itemClass = globals.itemClass(context);
        return (
            <div className={itemClass}>
                {context.authors ? <div className="authors">{context.authors}.</div> : null}
                <div className="journal">
                    {this.transferPropsTo(<Citation />)}
                </div>

                {context.abstract || context.data_used || context.references.length ||
                    (context.datasets && context.datasets.length) || (context.supplementary_data && context.supplementary_data.length) ?
                    <div className="view-detail panel">
                        {context.abstract ?
                            <div className="abstract">
                                <h2>Abstract</h2>
                                <p>{context.abstract}</p>
                            </div>
                        : null}

                        <dl className="key-value-left">
                            {context.data_used ?
                                <div data-test="dataused">
                                    <dt>Consortium data referenced in this publication</dt>
                                    <dd>{context.data_used}</dd>
                                </div>
                            : null}

                            {context.references && context.references.length ?
                                <div data-test="references">
                                    <dt>References</dt>
                                    <dd><DbxrefList values={context.references} className="multi-value" /></dd>
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

                            {context.supplementary_data && context.supplementary_data.length ?
                                <div>
                                    <h4>Supplementary data</h4>
                                    {context.supplementary_data.map(function(data) {
                                        return <SupplementaryData data={data} />;
                                    })}
                                </div>
                            : null}
                        </dl>
                    </div>
                : null}
            </div>
        );
    }
});

globals.panel_views.register(Panel, 'publication');


var Listing = React.createClass({
    mixins: [search.PickerActionsMixin],
    render: function() {
        var context = this.props.context;
        var authorList = context.authors ? context.authors.split(', ', 4) : [];
        var authors = authorList.length === 4 ? authorList.splice(0, 3).join(', ') + ', et al' : context.authors;
        return (<li>
                    <div>
                        {this.renderActions()}
                        <div className="pull-right search-meta">
                            <p className="type meta-title">Publication</p>
                            <p className="type meta-status">{' ' + context['status']}</p>
                        </div>
                        <div className="accession"><a href={context['@id']}>{context.title}</a></div>
                    </div>
                    <div className="data-row">
                        {authors ? <p className="list-author">{authors}.</p> : null}
                        <p className="list-citation">{this.transferPropsTo(<Citation />)}</p>
                        {context.references.length ? <div><DbxrefList values={context.references} className="list-reference" /></div> : '' }
                    </div>
            </li>
        );
    }
});
globals.listing_views.register(Listing, 'publication');
