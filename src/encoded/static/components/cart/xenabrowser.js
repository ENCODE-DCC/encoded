/**
 * Display the batch download modal on the cart page, and with the user confirming the modal,
 * initiate the batch download.
 */
import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import _ from 'underscore';
import { cartOperationInProgress } from './actions';
import { documentViews } from '../globals';
import Tooltip from '../../libs/ui/tooltip';


/** Maximum number of elements in cart that generates warning in download dialog */
const ELEMENT_WARNING_LENGTH_MIN = 500;


/**
 * Displays batch download button for downloading files from experiments in carts. For shared carts
 * or logged-in users.
 */
class CartXenaBrowserButtonComponent extends React.Component {
    constructor() {
        super();
        this.goToLink = this.goToLink.bind(this);
        this.state = {
        }
    }

     goToLink() {
       var hub = "localhost:7223"; //need the real hub once installed on biohpc
       var link = "https://xenabrowser.net/datapages/?host=" + encodeURI(hub);
       console.log(link);
       window.open(link, '_blank');
     }


    render() {
        const { elements, fileCount, cartInProgress } = this.props;

        return (
            <span>
                <span id="tempinput"></span>
                 <Tooltip trigger={
                    <button onClick={this.goToLink}  className="btn btn-info btn-sm no-margin-left" >Xena Browser</button>
                } tooltipId="xena-tooltip" css="custom-css-classes">
                    <div>Open Xena Browser in a new tab</div>
                </Tooltip>
            </span>
        );
    }
}

CartXenaBrowserButtonComponent.propTypes = {
    /** Type of cart, ACTIVE, OBJECT, MEMORY */
    cartType: PropTypes.string.isRequired,
    /** Cart elements */
    elements: PropTypes.array,
    /** Selected facet terms */
    selectedTerms: PropTypes.object,
    /** Cart as it exists in the database; use JSON payload method if none */
    savedCartObj: PropTypes.object,
    /** Shared cart object */
    sharedCart: PropTypes.object,
    /** Number of files batch download will cause to be downloaded */
    fileCount: PropTypes.number,
    /** Redux cart action to set the in-progress state of the cart */
    setInProgress: PropTypes.func.isRequired,
    /** True if cart operation in progress */
    cartInProgress: PropTypes.bool,
    /** System fetch function */
    fetch: PropTypes.func.isRequired,
};

CartXenaBrowserButtonComponent.defaultProps = {
    elements: [],
    selectedTerms: null,
    savedCartObj: null,
    sharedCart: null,
    fileCount: 0,
    cartInProgress: false,
};

const mapStateToProps = (state, ownProps) => ({
    cartInProgress: state.inProgress,
    elements: ownProps.elements,
    selectedTerms: ownProps.selectedTerms,
    savedCartObj: ownProps.savedCartObj,
    fileCount: ownProps.fileCount,
    fetch: ownProps.fetch,
});

const mapDispatchToProps = dispatch => ({
    setInProgress: enable => dispatch(cartOperationInProgress(enable)),
});

const CartXenaBrowserButtonInternal = connect(mapStateToProps, mapDispatchToProps)(CartXenaBrowserButtonComponent);


/**
 * Wrapper to receive React <App> context and pass them to CartXenaBrowserButtonInternal as regular
 * props.
 */
const CartXenaBrowserButton = (props, reactContext) => (
    <CartXenaBrowserButtonInternal {...props} fetch={reactContext.fetch} />
);

CartXenaBrowserButton.contextTypes = {
    fetch: PropTypes.func,
};

export default CartXenaBrowserButton;
