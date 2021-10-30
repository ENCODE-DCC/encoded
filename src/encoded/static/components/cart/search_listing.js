// node_modules
import React from 'react';
import PropTypes from 'prop-types';
import { motion } from 'framer-motion';
import marked from 'marked';
import { sanitize } from 'dompurify';
// libs
import { svgIcon } from '../../libs/svg-icons';
// components
import { auditDecor } from '../audit';
import { PickerActions, resultItemClass } from '../search';
import Status from '../status';


/** Height of collapsed description in pixels */
const DESCRIPTION_COLLAPSED_HEIGHT = 120;


/**
 * Defines the animations for expanding/collapsing a description.
 */
const descriptionVariants = {
    expanded: { height: 'auto' },
    closed: { height: `${DESCRIPTION_COLLAPSED_HEIGHT}px` },
};


/**
 * Display the description of a cart in the cart search results. Include a control to collapse and
 * expand the description when the description has more text than would fit in the allowed vertial
 * space.
 */
const CartDescriptionForSearch = ({ cart, description }) => {
    /** Holds the sanitized cart description after this component mounts */
    const [sanitizedDescription, setSanitizedDescription] = React.useState(null);
    /** True if description expansion button should appear */
    const [isDescriptionOverflowing, setIsDescriptionOverflowing] = React.useState(false);
    /** True if user has expanded the description */
    const [isDescriptionExpanded, setIsDescriptionExpanded] = React.useState(false);
    /** Description element */
    const descriptionRef = React.useRef(null);

    React.useEffect(() => {
        // Must have a DOM to clean the description of any dangerous Javascript within.
        if (description) {
            setSanitizedDescription(marked(sanitize(description)));
        } else {
            setSanitizedDescription(null);
        }
    }, [description]);

    React.useEffect(() => {
        // If the description text overflows the maximum collapsed height, offer a button to expand
        // the description area.
        if (descriptionRef.current && (descriptionRef.current.scrollHeight > DESCRIPTION_COLLAPSED_HEIGHT)) {
            setIsDescriptionOverflowing(true);
        }
    }, [sanitizedDescription, descriptionRef.current]);

    return (
        <>
            <motion.div
                className="cart-description cart-description--search-results"
                id={`description-${cart.uuid}`}
                animate={isDescriptionExpanded || !isDescriptionOverflowing ? 'expanded' : 'closed'}
                variants={descriptionVariants}
                transition={{ type: 'linear', duration: 0.2 }}
            >
                {sanitizedDescription && <div ref={descriptionRef} dangerouslySetInnerHTML={{ __html: sanitizedDescription }} />}
                {isDescriptionOverflowing && !isDescriptionExpanded &&
                    <div className="cart-description__overflow-indicator" />
                }
            </motion.div>
            {isDescriptionOverflowing &&
                <button
                    type="button"
                    className="btn btn-xs cart-description-expander"
                    aria-label={isDescriptionExpanded ? 'Collapse description' : 'Expand description'}
                    aria-controls={`description-${cart.uuid}`}
                    onClick={() => setIsDescriptionExpanded(!isDescriptionExpanded)}
                >
                    {isDescriptionExpanded ? <>Less {svgIcon('chevronUp')}</> : <>More {svgIcon('chevronDown')}</>}
                </button>
            }
        </>
    );
};

CartDescriptionForSearch.propTypes = {
    /** Cart whose entry we display in the search results */
    cart: PropTypes.object.isRequired,
    /** Cart description to display, potentially in Markdown format */
    description: PropTypes.string,
};

CartDescriptionForSearch.defaultProps = {
    description: null,
};


/**
 * Displays search result for cart objects.
 */
const ListingComponent = ({ context: result, auditIndicators, auditDetail }, reactContext) => (
    <div className={resultItemClass(result)}>
        <div className="result-item">
            <div className="result-item__data">
                <a href={result['@id']} className="result-item__link">{result.name}</a>
                <div className="result-item__data-row">
                    {result.submitted_by?.lab && <div><strong>Lab: </strong>{result.submitted_by.lab.title}</div>}
                    <CartDescriptionForSearch cart={result} description={result.description} />
                </div>
            </div>
            <div className="result-item__meta">
                <div className="result-item__meta-title">Cart</div>
                <Status item={result.status} badgeSize="small" css="result-table__status" />
                {auditIndicators(result.audit, result['@id'], { session: reactContext.session, sessionProperties: reactContext.session_properties, search: true })}
            </div>
            <PickerActions context={result} />
        </div>
        {auditDetail(result.audit, result['@id'], { session: reactContext.session, sessionProperties: reactContext.session_properties })}
    </div>
);

ListingComponent.propTypes = {
    /** Search results object */
    context: PropTypes.object.isRequired,
    /** Audit HOC function to show audit details */
    auditDetail: PropTypes.func.isRequired,
    /** Audit HOC function to display audit indicators */
    auditIndicators: PropTypes.func.isRequired,
};

ListingComponent.contextTypes = {
    session: PropTypes.object,
    session_properties: PropTypes.object,
};

const CartSearchListing = auditDecor(ListingComponent);

export default CartSearchListing;
