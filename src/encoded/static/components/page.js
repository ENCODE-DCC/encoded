'use strict';
var React = require('react');
var moment = require('moment');
var {Panel} = require('../libs/bootstrap/panel');
var { PickerActions } = require('./search');
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
                        <h2>{moment.utc(context.date_created).format('MMMM D, YYYY')} — <NewsShareList post={context} /></h2>
                    </div>
                    <Layout value={context.layout} />
                    <div className="news-keyword-section">
                        <NewsKeywordList post={context} />
                    </div>
                </Panel>
            );
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
    render: function() {
        var result = this.props.context;
        return (
            <li>
                <div className="clearfix">
                    <PickerActions {...this.props} />
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


// Display a list of keywords for the news article in the `post` prop.
var NewsKeywordList = React.createClass({
    propTypes: {
        post: React.PropTypes.object // News post Page object
    },

    render: function() {
        var post = this.props.post;
        if (post.news_keywords && post.news_keywords.length) {
            return (
                <div className="news-keyword-list">
                    <p>View news matching these terms, or all recent news</p>
                    <a className="news-keyword" href={'/news/'} title="Show all recent news posts">All recent news</a>
                    {post.news_keywords.map(keyword => {
                        return <a key={keyword} className="news-keyword" href={'/news/?news_keywords=' + keyword} title={'Show all news posts tagged with ' + keyword}>{keyword}</a>;
                    })}
                </div>
            );
        }
        return null;
    }
});


// Display a list of news sharing links/buttons for the news article in the `post` prop.
var NewsShareList = React.createClass({
    propTypes: {
        post: React.PropTypes.object // News post Page object
    },

    contextTypes: {
        location_href: React.PropTypes.string
    },

    render: function() {
        var post = this.props.post;
        return (
            <div className="news-share-list">
                <a className="share-twitter" href={'http://twitter.com/intent/tweet?url=' + this.context.location_href + '&text=' + post.title + '&via=EncodeDCC'} target="_blank" title="Share this page on Twitter in a new window" aria-label="Share on Twitter">
                    <span className="sr-only">Twitter</span>
                </a>
                <a className="share-facebook" href={'https://www.facebook.com/sharer/sharer.php?u=' + this.context.location_href + '&t=' + post.title} target="_blank" title="Share this page on Facebook in a new window" aria-label="Share on Facebook">
                    <span className="sr-only">Facebook</span>
                </a>
                <a className="share-googleplus" href={'https://plus.google.com/share?url=' + this.context.location_href} target="_blank" title="Share this page on Google Plus in a new window" aria-label="Share on Google+">
                    <span className="sr-only">Google+</span>
                </a>
            </div>
        );
    }
});


// Write Facebook meta tags to the site header.
var newsHead = module.exports.newsHead = function(props, siteUrl) {
    var context = props.context;

    if (context.news) {
        return [
            <meta property="og:url" content={props.href} />,
            <meta property="og:type" content="article" />,
            <meta property="og:title" content={context.title} />,
            <meta property="og:description" content={context.news_excerpt} />,
            <meta property="og:image" content={siteUrl + '/static/img/encode-logo-small-2x.png'} />
        ];
    }
    return null;
};
