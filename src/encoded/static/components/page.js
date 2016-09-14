'use strict';
var React = require('react');
var moment = require('moment');
var {Panel} = require('../libs/bootstrap/panel');
var {PickerActionsMixin} = require('./search');
var Layout = require('./layout').Layout;
var globals = require('./globals');
var _ = require('underscore');


var Page = module.exports.Page = React.createClass({
    render: function() {
        var context = this.props.context;
        if (context.blog) {
            return (
                <Panel addClasses="blog-post">
                    <div className="blog-post-header">
                        <h1>{context.title}</h1>
                        <h2>{moment.utc(context.date_created).format('MMMM D, YYYY')}</h2>
                    </div>
                    <Layout value={context.layout} />
                </Panel>
            )
        }

        // Non-blog page; render as title, then content box
        return (
            <div>
                <header className="row">
                    <div className="col-sm-12">
                        <h1 className="page-title">{context.title}</h1>
                    </div>
                </header>
                <Layout value={context.layout} />
            </div>
        );
    }
});

globals.content_views.register(Page, 'Page');


var Listing = React.createClass({
    mixins: [PickerActionsMixin],
    render: function() {
        var result = this.props.context;
        return (
            <li>
                <div className="clearfix">
                    {this.renderActions()}
                    <div className="accession">
                        <a href={result['@id']}>{result.title}</a> <span className="page-listing-date">{moment.utc(result.date_created).format('MMMM D, YYYY')}</span>
                    </div>
                    <div className="data-row">
                        {result.blog ? result.blog_excerpt : null}
                    </div>
                </div>
            </li>
        );
    }
});

globals.listing_views.register(Listing, 'Page');
