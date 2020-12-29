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
import TooltipImage from '../../libs/ui/tooltip-image';


/** Maximum number of elements in cart that generates warning in download dialog */
const ELEMENT_WARNING_LENGTH_MIN = 500;


/**
 * Displays batch download button for downloading files from experiments in carts. For shared carts
 * or logged-in users.
 */
class CartCbioportalButtonComponent extends React.Component {
    constructor() {
        super();
        this.linkToCBioportal = this.linkToCBioportal.bind(this);
        this.goToLink = this.goToLink.bind(this);
        this.state = {
            //use this for testing/demo then switch to kce patient data
            samples: [
                {id: "AL4602", study: "luad_mskcc_2015"},
                  {id: "AU5884", study: "luad_mskcc_2015"},
                  {id: "H1672", study: "sclc_clcgp"},
                  {id: "H2171", study: "sclc_clcgp"}
              ],
            ids: ""
        }
    }

    linkToCBioportal() {
        this.copyToClipboard();
        this.goToLink();
     }

     copyToClipboard() {
        var ids = this.state.samples.map(sample => sample.study + ":" + sample.id).join("\n");
        var temp = document.getElementById("tempinput");
        var textarea = document.createElement("textarea");
        temp.appendChild(textarea);
        textarea.value = ids;
        textarea.select();
        document.execCommand('copy');
        temp.removeChild(textarea);
     }

     goToLink() {
       var tab = "summary";
       var studies = new Set(this.state.samples.map(sample => sample.study));
       var link = "https://www.cbioportal.org/study/" + tab + "?id=" + [...studies].map(i => i);
       console.log(link);
       window.open(link, '_blank');
     }


    render() {
        const { elements, fileCount, cartInProgress } = this.props;

        return (
            <span>
                <span id="tempinput"></span>
                 <TooltipImage trigger={
                    <button onClick={this.linkToCBioportal}  className="btn btn-info btn-sm no-margin-left" >CBioportal</button>
                } tooltipId="cbioportal-tooltip" css="custom-css-classes">
                    <div>This button opens CBioportal in a new tab<br/>
                    and copies the list of sample ids to your clipboard.<br/>
                    <br/>
                    Then you can paste the list of samples with CTRL+V or &#8984;+V<br/>
                    in Cbioportal by clicking on <b>Custom Selection:</b><br/>
                    <br/>
                    <img width="372px" src='/static/img/cbioportal-custom-selection.png' alt="CBioportal Custom Selection"
                     />



                    </div>
                </TooltipImage>
            </span>
        );
    }
}

CartCbioportalButtonComponent.propTypes = {
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

CartCbioportalButtonComponent.defaultProps = {
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

const CartCbioportalButtonInternal = connect(mapStateToProps, mapDispatchToProps)(CartCbioportalButtonComponent);


/**
 * Wrapper to receive React <App> context and pass them to CartCbioportalButtonInternal as regular
 * props.
 */
const CartCbioportalButton = (props, reactContext) => (
    <CartCbioportalButtonInternal {...props} fetch={reactContext.fetch} />
);

CartCbioportalButton.contextTypes = {
    fetch: PropTypes.func,
};

export default CartCbioportalButton;
