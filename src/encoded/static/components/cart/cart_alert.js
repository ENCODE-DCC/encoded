import PropTypes from 'prop-types';
import { connect } from 'react-redux';


/**
 * Display an alert relevant to the cart, or hide an already-visible one. The alert React component
 * gets set in the cart Redux store `alert` property.
 */
const CartAlertComponent = ({ alert }) => (
    <>{alert ? <>{alert}</> : null}</>
);

CartAlertComponent.propTypes = {
    /** React component for alert */
    alert: PropTypes.object,
};

CartAlertComponent.defaultProps = {
    alert: null,
};

CartAlertComponent.mapStateToProps = (state) => ({
    alert: state.alert,
});

const CartAlert = connect(CartAlertComponent.mapStateToProps)(CartAlertComponent);

export default CartAlert;
