'use strict';
var React = require('react');
var moment = require('moment');
var {Panel} = require('../libs/bootstrap/panel');
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
