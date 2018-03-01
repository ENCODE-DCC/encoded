import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { addMultipleToCartAndSave } from './actions';
import { encodedURIComponent } from '../globals';
import { requestSearch } from '../objectutils';


class CartAddAllComponent extends React.Component {
    constructor() {
        super();
        this.handleClick = this.handleClick.bind(this);
    }

    handleClick() {
        const searchQuery = `${this.props.searchResults.filters.map(element => (
            `${element.field}=${encodedURIComponent(element.term)}`
        )).join('&')}&limit=all&field=%40id`;
        requestSearch(searchQuery).then((results) => {
            if (Object.keys(results).length > 0 && results['@graph'].length > 0) {
                const itemsForCart = results['@graph'].map(result => result['@id']);
                this.props.addAllResults(itemsForCart);
            }
        });
    }

    render() {
        const { searchResults, inProgress } = this.props;
        return <button disabled={inProgress} className="btn btn-info btn-sm" onClick={this.handleClick}>{`Add ${searchResults.total} items to cart`}</button>;
    }
}

CartAddAllComponent.propTypes = {
    /** Search result object of items to add to cart */
    searchResults: PropTypes.object.isRequired,
    /** True if cart updating operation is in progress */
    inProgress: PropTypes.bool,
    /** Function to call when Add All clicked */
    addAllResults: PropTypes.func.isRequired,
};

CartAddAllComponent.defaultProps = {
    inProgress: false,
};

const mapStateToProps = (state, ownProps) => ({ cart: state.cart, inProgress: state.inProgress, searchResults: ownProps.searchResults });
const mapDispatchToProps = (dispatch, ownProps) => ({
    addAllResults: itemsForCart => dispatch(addMultipleToCartAndSave(itemsForCart, ownProps.sessionProperties.user, ownProps.fetch)),
});

const CartAddAllInternal = connect(mapStateToProps, mapDispatchToProps)(CartAddAllComponent);

const CartAddAll = (props, reactContext) => (
    <CartAddAllInternal searchResults={props.searchResults} sessionProperties={reactContext.session_properties} fetch={reactContext.fetch} />
);

CartAddAll.propTypes = {
    /** Search result object of items to add to cart */
    searchResults: PropTypes.object.isRequired,
};

CartAddAll.contextTypes = {
    session_properties: PropTypes.object,
    fetch: PropTypes.func,
};

export default CartAddAll;
