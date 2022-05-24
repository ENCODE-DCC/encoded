import PropTypes from 'prop-types';

/**
 * Default number of results when no "limit=x" specified in the query string. Determined by our
 * back-end search code.
 */
const DEFAULT_PAGE_LIMIT = 25;

/**
 * Displays a control allowing the user to select the maximum number of items to display on one page.
 */
const LimitSelector = ({ pageLimit, query, pageLimitOptions, displayText, ariaLabel }) => (
    <div className="page-limit-selector">
        {displayText ?
            <div className="page-limit-selector__label">{displayText}:</div>
        : null}
        <div className="page-limit-selector__options">
            {pageLimitOptions.map((limit) => {
                // When changing the number of items per page, also go back to the first page by
                // removing the "from=x" query-string parameter.
                const limitQuery = query.clone();
                limitQuery.deleteKeyValue('from');
                if (limit === DEFAULT_PAGE_LIMIT) {
                    limitQuery.deleteKeyValue('limit');
                } else {
                    limitQuery.replaceKeyValue('limit', limit);
                }

                return (
                    <a
                        key={limit}
                        href={`?${limitQuery.format()}`}
                        className={`page-limit-selector__option${limit === pageLimit ? ' page-limit-selector__option--selected' : ''}`}
                        aria-label={`Show ${limit} ${ariaLabel}`}
                    >
                        {limit}
                    </a>
                );
            })}
        </div>
    </div>
);

LimitSelector.defaultProps = {
    /** Page limit options */
    pageLimitOptions: [25, 50, 100, 200],
    /** Display text */
    displayText: 'Items per page',
    /** Aria-label text */
    ariaLabel: 'items per page',
};

LimitSelector.propTypes = {
    /** New page limit to display */
    pageLimit: PropTypes.number.isRequired,
    /** Current page's QueryString query */
    query: PropTypes.object.isRequired,
    /** Page limit options */
    pageLimitOptions: PropTypes.array,
    /** Display text */
    displayText: PropTypes.string,
    /** Aria-label text */
    ariaLabel: PropTypes.string,
};

export default LimitSelector;
