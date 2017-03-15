import React from 'react';
import moment from 'moment';
import globals from './globals';


// Display a news preview item from a search result @graph object.
const NewsPreviewItem = React.createClass({
    propTypes: {
        item: React.PropTypes.object, // News search result object to display
    },

    render: function () {
        const { item } = this.props;
        return (
            <div key={item['@id']} className="news-listing-item">
                <h3>{item.title}</h3>
                <h4>{moment.utc(item.date_created).format('MMMM D, YYYY')}</h4>
                <div className="news-excerpt">{item.news_excerpt}</div>
                <div className="news-listing-readmore">
                    <a className="btn btn-info btn-sm" href={item['@id']} title={`View news post for ${item.title}`} key={item['@id']}>Read more</a>
                </div>
            </div>
        );
    },
});


// Display a list of news preview items from search results.
const NewsPreviews = React.createClass({
    propTypes: {
        items: React.PropTypes.array, // Items from search result @graph
    },

    render: function () {
        const { items } = this.props;
        if (items && items.length) {
            return (
                <div className="news-listing">
                    {items.map(item => (
                        <NewsPreviewItem item={item} />
                    ))}
                </div>
            );
        }
        return <div className="news-empty">No news available at this time</div>;
    },
});
export default NewsPreviews;


const News = React.createClass({
    propTypes: {
        context: React.PropTypes.object, // Search results
    },

    render: function () {
        const { context } = this.props;
        const items = context['@graph'];
        return (
            <NewsPreviews items={items} />
        );
    },
});

globals.content_views.register(News, 'News');
