import React from 'react';
import moment from 'moment';
import globals from './globals';


const News = React.createClass({
    propTypes: {
        context: React.PropTypes.object, // Search results
    },

    render: function () {
        const { context } = this.props;
        const items = context['@graph'];
        if (items && items.length) {
            return (
                <div className="news-listing">
                    {items.map(item => (
                        <div key={item['@id']} className="news-listing-item">
                            <h3>{item.title}</h3>
                            <h4>{moment.utc(item.date_created).format('MMMM D, YYYY')}</h4>
                            <div className="news-excerpt">{item.news_excerpt}</div>
                            <div className="news-listing-readmore">
                                <a className="btn btn-info btn-sm" href={item['@id']} title={`View news post for ${item.title}`} key={item['@id']}>Read more</a>
                            </div>
                        </div>
                    ))}
                </div>
            );
        }
        return <div className="news-empty">No news available at this time</div>;
    },
});

globals.content_views.register(News, 'News');
