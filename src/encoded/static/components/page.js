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
        if (context.news) {
            return (
                <Panel addClasses="news-post">
                    <div className="news-post-header">
                        <h1>{context.title}</h1>
                        <h2>{moment.utc(context.date_created).format('MMMM D, YYYY')}</h2>
                    </div>
                    <Layout value={context.layout} />
                    <div className="news-keyword-section">
                        <NewsKeywordList post={context} />
                    </div>
                    <div className="news-share-section">
                        <NewsShareList post={context} />
                    </div>
                </Panel>
            )
        }

        // Non-news page; render as title, then content box
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
                        {result.news ? result.news_excerpt : null}
                    </div>
                </div>
            </li>
        );
    }
});

globals.listing_views.register(Listing, 'Page');


var NewsKeywordList = React.createClass({
    propTypes: {
        post: React.PropTypes.object // News post Page object
    },

    render: function() {
        var post = this.props.post;
        if (post.news_keywords && post.news_keywords.length) {
            return (
                <div className="news-keyword-list">
                    {post.news_keywords.map(keyword => <a key={keyword} className="news-keyword" href={'/search/?type=Page&news=true&news_keywords=' + keyword}>{keyword}</a>)}
                </div>
            )
        }
        return null;
    }
});


var NewsShareList = React.createClass({
    propTypes: {
        post: React.PropTypes.object // News post Page object
    },

    contextTypes: {
        location_href: React.PropTypes.string
    },

    render: function() {
        var post = this.props.post;
        return <a href={'http://twitter.com/intent/tweet?url=' + this.context.location_href + '&text=' + post.title + '&via=EncodeDCC'} target="_blank" title="Share this page on twitter in a new window">Tweet</a>;
    }
});
