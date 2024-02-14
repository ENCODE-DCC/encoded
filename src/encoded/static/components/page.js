import PropTypes from 'prop-types';
import dayjs from 'dayjs';
import utc from 'dayjs/plugin/utc';
import { Panel } from '../libs/ui/panel';
import * as globals from './globals';
import Layout from './layout';
import { PickerActions, resultItemClass } from './search';

dayjs.extend(utc);

const Page = (props) => {
    const { context } = props;
    if (context.news) {
        return (
            <Panel addClasses="news-post">
                <div className="news-post-header">
                    <h1>{context.title}</h1>
                    <h2>{dayjs.utc(context.date_created).format('MMMM D, YYYY')} — <NewsShareList post={context} /></h2>
                </div>
                <Layout value={context.layout} />
                <div className="news-keyword-section">
                    <NewsKeywordList post={context} />
                </div>
            </Panel>
        );
    }

    // Non-news page; only layout displayed
    return (
        <div>
            <Layout value={context.layout} />
        </div>
    );
};

Page.propTypes = {
    context: PropTypes.object.isRequired, // Page object being displayed
};

globals.contentViews.register(Page, 'Page');


const Listing = ({ context: result }) => (
    <div className={resultItemClass(result)}>
        <div className="result-item">
            <div className="result-item__data">
                <a href={result['@id']} className="result-item__link">{result.title}</a> <span className="page-listing-date">{dayjs.utc(result.date_created).format('MMMM D, YYYY')}</span>
                <div className="result-item__data-row">
                    {result.news ? result.news_excerpt : null}
                </div>
            </div>
            <PickerActions context={result} />
        </div>
    </div>
);

Listing.propTypes = {
    context: PropTypes.object.isRequired, // Search result object
};

globals.listingViews.register(Listing, 'Page');


// Display a list of keywords for the news article in the `post` prop.
const NewsKeywordList = (props) => {
    const { post } = props;
    if (post.news_keywords && post.news_keywords.length > 0) {
        return (
            <div className="news-keyword-list">
                <p>View news matching these terms, or all recent news</p>
                <a className="btn btn-default btn-sm news-keyword" href="/search/?type=Page&news=true" title="Show all recent news posts">All recent news</a>
                {post.news_keywords.map((keyword) => (
                    <a key={keyword} className="btn btn-default btn-sm news-keyword" href={`/search/?type=Page&news=true&news_keywords=${keyword}`} title={`Show all news posts tagged with ${keyword}`}>{keyword}</a>
                ))}
            </div>
        );
    }
    return null;
};

NewsKeywordList.propTypes = {
    post: PropTypes.object.isRequired, // News post Page object
};


// Display a list of news sharing links/buttons for the news article in the `post` prop.
const NewsShareList = (props, reactContext) => {
    const { post } = props;
    return (
        <div className="news-share-list">
            <a className="share-twitter" href={`http://twitter.com/intent/tweet?url=${reactContext.location_href}&text=${post.title}&via=EncodeDCC`} target="_blank" rel="noopener noreferrer" title="Share this page on Twitter in a new window" aria-label="Share on Twitter">
                <span className="sr-only">Twitter</span>
            </a>
            <a className="share-facebook" href={`https://www.facebook.com/sharer/sharer.php?u=${reactContext.location_href}&t=${post.title}`} target="_blank" rel="noopener noreferrer" title="Share this page on Facebook in a new window" aria-label="Share on Facebook">
                <span className="sr-only">Facebook</span>
            </a>
        </div>
    );
};

NewsShareList.propTypes = {
    post: PropTypes.object.isRequired, // News post Page object
};

NewsShareList.contextTypes = {
    location_href: PropTypes.string,
};


// Write Facebook meta tags to the site header.
export default function newsHead(props, siteUrl) {
    const { context } = props;

    if (context.news) {
        return [
            <meta key="url" property="og:url" content={props.href} />,
            <meta key="type" property="og:type" content="article" />,
            <meta key="title" property="og:title" content={context.title} />,
            <meta key="desc" property="og:description" content={context.news_excerpt} />,
            <meta key="image" property="og:image" content={`${siteUrl}/static/img/encode-logo-small-2x.png`} />,
        ];
    }
    return null;
}
