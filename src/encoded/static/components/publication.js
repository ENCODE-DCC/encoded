/** @jsx React.DOM */
'use strict';
var moment = require('moment');
var React = require('react');
var globals = require('./globals');
var dbxref = require('./dbxref');
var search = require('./search');

var DbxrefList = dbxref.DbxrefList;
var Dbxref = dbxref.Dbxref;

var Citation = React.createClass({
    render: function() {
        var context = this.props.context;
        var date = moment(context.date_published).format('YYYY MMM D');
        return (
            <div className="journal">
                {context.authors} {context.title}. <i>{context.journal}</i>. {date};{context.volume}{context.issue ? '(' + context.issue + ')' : '' }:{context.page}.
            </div>
        );
    }
});



var Panel = React.createClass({
    render: function() {
        var context = this.props.context;
        var itemClass = globals.itemClass(context);
        return (
            <div className={itemClass}>
                <p className="lead">{context.authors}</p>

                <div className="view-detail panel">
                    <div className="row">
                        <div className="col-md-7 abstract">
                            <h2>Abstract</h2>
                            {context.abstract}
                            <div className="references">
                                {context.references.length ? <span>References: </span> : null}
                                {context.references.length ? <DbxrefList values={context.references} className="multi-value" /> : null}
                            </div>
                        </div>

                        <div className="col-md-4 col-md-offset-1 citation">
                            <h3>Citation:</h3>
                            {this.transferPropsTo(<Citation />)}
                        </div>
                    </div>
                </div>
            </div>
        );
    }
});

globals.panel_views.register(Panel, 'publication');


var Listing = React.createClass({
    mixins: [search.PickerActionsMixin],
    render: function() {
        var context = this.props.context;
        var date = moment(context.date_published).format('YYYY MMM D');
        return (<li>
                    <div>
                        {this.renderActions()}
                        <div className="pull-right search-meta">
                            <p className="type meta-title">Publication</p>
                        </div>
                        <div className="accession"><a href={context['@id']}>{context.title}</a></div>
                    </div>
                    <div className="data-row">
                        {context.authors}. {context.title}. <i>{context.journal}</i>. {date}; {context.volume}{context.issue ? '(' + context.issue + ')' : '' }:{context.page}. {context.references.length ? <DbxrefList values={context.references} className="multi-value" /> : '' }
                    </div>
            </li>
        );
    }
});
globals.listing_views.register(Listing, 'publication');
