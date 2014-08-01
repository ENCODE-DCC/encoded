/** @jsx React.DOM */
'use strict';
var React = require('react');
var globals = require('./globals');
var dbxref = require('./dbxref');
var search = require('./search');

var DbxrefList = dbxref.DbxrefList;
var Dbxref = dbxref.Dbxref;

var Citation = React.createClass({
    render: function() {
        var context = this.props.context;
        return (
            <div className="journal">
                <i>{context.journal}</i>. {context.date_published};{context.volume}{context.issue ? '(' + context.issue + ')' : '' }:{context.page}.
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
                <div className="authors">
                    {context.authors}.
                </div>
                {this.transferPropsTo(<Citation />)}

                {context.abstract || context.references.length ?
                    <div className="view-detail panel">
                        {context.abstract ?
                            <div className="abstract">
                                {context.abstract ? <h2>Abstract</h2> : null}
                                {context.abstract ? <p>{context.abstract}</p> : null}
                            </div>
                        : null}
                        {context.references && context.references.length ?
                            <div className="references">
                                {context.references.length ? <span>References: </span> : null}
                                {context.references.length ? <DbxrefList values={context.references} className="multi-value" /> : null}
                            </div>
                        : null}
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
                        <p className="list-citation"><i>{context.journal}</i>. {context.date_published};{context.volume}{context.issue ? '(' + context.issue + ')' : '' }:{context.page}.</p>
                        {context.references.length ? <DbxrefList values={context.references} className="list-reference" /> : '' }
                    </div>
            </li>
        );
    }
});
globals.listing_views.register(Listing, 'publication');
