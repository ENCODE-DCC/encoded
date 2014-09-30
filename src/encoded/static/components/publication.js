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
            <div className="publication-subsection" key={this.props.key}>
                {data.element_type ? <span><strong>Available data: </strong>{data.element_type}</span> : null}
                {data.file_format ? <span>{data.element_type ? ' ' : ''}{<span>(<strong>File format: </strong>{data.file_format})</span>}</span> : null}
                {data.url ? <span>{data.element_type || data.file_format ? ': ' : ''}<a href={data.url}>{data.url}</a></span> : null}

                {data.method_summary ?
                    <div><strong>Method summary: </strong>{data.method_summary}</div>
                : null}
            </div>
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
                            <div className="publication-section" data-test="abstract">
                                <h2>Abstract</h2>
                                <p>{context.abstract}</p>
                            </div>
                        : null}

                        {context.supplementary_data && context.supplementary_data.length ?
                            <div className="publication-section" data-test="supplementarydata">
                                <h2>Supplementary data</h2>
                                {context.supplementary_data.map(function(data, i) {
                                    return <SupplementaryData key={i} data={data} />;
                                })}
                            </div>
                        : null}

                        <dl className="key-value-left">
                            {context.data_used ?
                                <div data-test="dataused">
                                    <dt>Consortium data referenced in this publication</dt>
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
