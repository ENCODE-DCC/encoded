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
                    <div className="blog-keyword-section">
                        <BlogKeywordList post={context} />
                    </div>
                    <div className="blog-share-section">
                        <BlogShareList post={context} />
                    </div>
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


var BlogKeywordList = React.createClass({
    propTypes: {
        post: React.PropTypes.object // Blog post Page object
    },

    render: function() {
        var post = this.props.post;
        if (post.blog_keywords && post.blog_keywords.length) {
            return (
                <div className="blog-keyword-list">
                    {post.blog_keywords.map(keyword => <a key={keyword} className="blog-keyword" href={'/search/?type=Page&blog=true&blog_keywords=' + keyword}>{keyword}</a>)}
                </div>
            )
        }
        return null;
    }
});


var BlogShareList = React.createClass({
    propTypes: {
        post: React.PropTypes.object // Blog post Page object
    },

    injectTwitter: function() {
        var js;
        if (!this.initialized) {
            let sharetwitter = this.refs.sharetwitter.getDOMNode();
            this.initialized = true;
            js = document.createElement("script");
            js.id = "share-twitter";
            js.src = "//platform.twitter.com/widgets.js";
            return sharetwitter.parentNode.appendChild(js);
        }
    },

    //componentDidMount: function() { // twitter script from API
    //    if (!this.initialized) {
    //        this.injectTwitter();
    //    }
    //},
//
    //componentDidUpdate: function() { // twitter script from API
    //    if (!this.initialized) {
    //        this.injectTwitter();
    //    }
    //},

    render: function() {
        var post = this.props.post;
        return <a href={'http://twitter.com/intent/tweet?url=http://alistapart.com/blog/post/moving-forward-with-css-shapes&text=' + post.title + '&via=EncodeDCC'}>Tweet</a>;
        //return <a ref="sharetwitter" href="https://twitter.com/share" class="twitter-share-button" data-text={post.title} data-via="EncodeDCC" data-show-count="false" target="_blank">Tweet</a>;
    }
});
