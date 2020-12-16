import React from 'react';
import PropTypes from 'prop-types';
import pluralize from 'pluralize';
import url from 'url';
import { svgIcon } from '../libs/svg-icons';
import { TextFilter } from './search';


/**
 * Maximum number of selected items that can be visualized.
 * @constant
 */
export const MATRIX_VISUALIZE_LIMIT = 500;


/**
 * Render the expander button for a row category, and react to clicks by calling the parent to
 * render the expansion change.
 */
export class RowCategoryExpander extends React.Component {
    constructor() {
        super();
        this.handleClick = this.handleClick.bind(this);
    }

    /**
     * Called when the user clicks the expander button to expand or collapse the section.
     */
    handleClick() {
        this.props.expanderClickHandler(this.props.categoryName);
    }

    render() {
        const { categoryId, expanderColor, expanderBgColor, expanded } = this.props;
        return (
            <button
                className="matrix__category-expander"
                aria-expanded={expanded}
                aria-controls={categoryId}
                onClick={this.handleClick}
                style={{ backgroundColor: expanderBgColor }}
            >
                {svgIcon(expanded ? 'chevronUp' : 'chevronDown', { fill: expanderColor })}
            </button>
        );
    }
}

RowCategoryExpander.propTypes = {
    /** Unique ID; should match id of expanded element */
    categoryId: PropTypes.string.isRequired,
    /** Category name; gets passed to click handler */
    categoryName: PropTypes.string.isRequired,
    /** Color to draw the icon or text of the expander button */
    expanderColor: PropTypes.string,
    /** Color to draw the background of the expander button */
    expanderBgColor: PropTypes.string,
    /** True if category is currently expanded */
    expanded: PropTypes.bool,
    /** Function to call to handle clicks in the expander button */
    expanderClickHandler: PropTypes.func.isRequired,
};

RowCategoryExpander.defaultProps = {
    expanderColor: '#000',
    expanderBgColor: 'transparent',
    expanded: false,
};


/**
 * Render and handle the free-text search box. After the user presses the return key, this
 * navigates to the current URL plus the given search term.
 */
export class SearchFilter extends React.Component {
    constructor() {
        super();
        this.onChange = this.onChange.bind(this);
    }

    onChange(href) {
        this.context.navigate(href);
    }

    render() {
        const { context } = this.props;
        const parsedUrl = url.parse(this.context.location_href);
        const matrixBase = parsedUrl.search || '';
        const matrixSearch = matrixBase + (matrixBase ? '&' : '?');
        const parsed = url.parse(matrixBase, true);
        const queryStringType = parsed.query.type || '';
        const type = pluralize(queryStringType.toLocaleLowerCase());
        return (
            <div className="matrix-general-search">
                <div className="general-search-entry">
                    <p>
                        <i className="icon icon-search" />
                        Filter the {type} included in the matrix:
                    </p>
                </div>
                <div className="searchform">
                    <TextFilter filters={context.filters} searchBase={matrixSearch} onChange={this.onChange} />
                </div>
            </div>
        );
    }
}

SearchFilter.propTypes = {
    /** Matrix search results object */
    context: PropTypes.object.isRequired,
};

SearchFilter.contextTypes = {
    navigate: PropTypes.func,
    location_href: PropTypes.string,
};
