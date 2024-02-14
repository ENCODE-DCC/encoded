/**
 * Renders cart-related controls at the top of search results.
 */
import PropTypes from 'prop-types';
import { CartAddAllSearch } from './add_multiple';
import { isAllowedElementsPossible } from './util';


/**
 * Controls at the top of search result lists. Show the Add All button if the search results could
 * contain experiments.
 */
const CartSearchControls = ({ searchResults }) => {
    if (isAllowedElementsPossible(searchResults.filters)) {
        return (
            <div className="cart__search-controls">
                <CartAddAllSearch searchResults={searchResults} />
            </div>
        );
    }
    return null;
};

CartSearchControls.propTypes = {
    /** Search results object used to render search page */
    searchResults: PropTypes.object.isRequired,
};

export default CartSearchControls;
