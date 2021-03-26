/**
 * Displays a button to remove a specific set of datasets from the cart.
 */
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { removeMultipleFromCartAndSave } from './actions';


/**
 * Renders a button to remove all the given datasets from the current cart.
 */
const CartRemoveElementsComponent = ({
    savedCartObj,
    elements,
    inProgress,
    removeMultipleItems,
    loggedIn,
}) => {
    const handleClick = () => {
        if (loggedIn && elements.length > 0) {
            removeMultipleItems(elements);
        }
    };

    const cartName = savedCartObj && Object.keys(savedCartObj).length > 0 ? savedCartObj.name : '';
    return (
        <button
            type="button"
            disabled={inProgress || (savedCartObj && savedCartObj.locked)}
            className="btn btn-info btn-sm"
            onClick={handleClick}
            title={`Add all related experiments to cart${cartName ? `: ${cartName}` : ''}`}
        >
            Remove displayed items from cart
        </button>
    );
};

CartRemoveElementsComponent.propTypes = {
    /** Current cart saved object */
    savedCartObj: PropTypes.object,
    /** New elements to add to cart as array of @ids */
    elements: PropTypes.array.isRequired,
    /** True if cart updating operation is in progress */
    inProgress: PropTypes.bool.isRequired,
    /** Function to call when Add All clicked */
    removeMultipleItems: PropTypes.func.isRequired,
    /** True if user has logged in */
    loggedIn: PropTypes.bool.isRequired,
};

CartRemoveElementsComponent.defaultProps = {
    savedCartObj: null,
};

CartRemoveElementsComponent.mapStateToProps = (state, ownProps) => ({
    savedCartObj: state.savedCartObj,
    elements: ownProps.elements,
    inProgress: state.inProgress,
    loggedIn: ownProps.loggedIn,
});

CartRemoveElementsComponent.mapDispatchToProps = (dispatch, ownProps) => ({
    removeMultipleItems: (elements) => dispatch(removeMultipleFromCartAndSave(elements, ownProps.fetch)),
});

const CartRemoveElementsInternal = connect(CartRemoveElementsComponent.mapStateToProps, CartRemoveElementsComponent.mapDispatchToProps)(CartRemoveElementsComponent);


// Public component used to bind to context properties.
const CartRemoveElements = ({ elements }, reactContext) => (
    <CartRemoveElementsInternal elements={elements} fetch={reactContext.fetch} loggedIn={!!(reactContext.session && reactContext.session['auth.userid'])} />
);

CartRemoveElements.propTypes = {
    /** New elements to add to cart as array of @ids */
    elements: PropTypes.array,
};

CartRemoveElements.defaultProps = {
    elements: [],
};

CartRemoveElements.contextTypes = {
    session: PropTypes.object,
    fetch: PropTypes.func,
};

export default CartRemoveElements;
