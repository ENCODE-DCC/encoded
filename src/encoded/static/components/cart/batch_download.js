/**
 * Display the batch download modal on the cart page, and with the user confirming the modal,
 * initiate the batch download.
 */
import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import _ from 'underscore';
import { encodedURIComponent } from '../globals';
import { BatchDownloadModal } from '../search';
import { cartOperationInProgress } from './actions';


/** Maximum number of elements in cart that generates warning in download dialog */
const ELEMENT_WARNING_LENGTH_MIN = 500;


/**
 * Displays batch download button for downloading files from experiments in carts. For shared carts
 * or logged-in users.
 */
class CartBatchDownloadComponent extends React.Component {
    constructor() {
        super();
        this.batchDownload = this.batchDownload.bind(this);
    }

    /**
     * Called when the user confirms they want to initiate the batch download. For carts, the
     * download uses a POST request with the @id of every experiment in the POST payload. If the
     * user has logged in, we additionally set a "cart" query string parameter with the @id of the
     * user's cart object, which is used in the metadata.tsv line of the resulting files.txt.
     */
    batchDownload() {
        let contentDisposition;
        let cartUuid;
        if (!this.props.cartType === 'OBJECT') {
            cartUuid = this.props.sharedCart.uuid;
        } else {
            cartUuid = this.props.savedCartObj && this.props.savedCartObj.uuid;
        }

        // Form query string from currently selected file formats.
        const fileFormatSelections = _.compact(Object.keys(this.props.selectedTerms).map((field) => {
            let subQueryString = '';
            if (this.props.selectedTerms[field].length > 0) {
                subQueryString = this.props.selectedTerms[field].map(term => `biosamples.${field}=${encodedURIComponent(encodedURIComponent(term))}`).join('&');
            }
            return subQueryString;
        }));

        // Initiate a batch download as a POST, passing it all dataset @ids in the payload.
        this.props.setInProgress(true);
        this.props.fetch(`/batch_download/type=Patient${cartUuid ? `&cart=${cartUuid}` : ''}${fileFormatSelections.length > 0 ? `&${fileFormatSelections.join('&')}` : ''}`, {
            method: 'POST',
            headers: {
                Accept: 'text/plain',
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                elements: this.props.elements,
            }),
        }).then((response) => {
            if (response.ok) {
                contentDisposition = response.headers.get('content-disposition');
                return response.blob();
            }
            throw new Error(response);
        }).then((blob) => {
            this.props.setInProgress(false);

            // Extract filename from batch_download response content disposition tag.
            const matchResults = contentDisposition.match(/biofile="(.*?)"/);
            const filename = matchResults ? matchResults[1] : 'files.txt';

            // Make a temporary link in the DOM with the URL from the response blob and then
            // click the link to automatically download the file. Many references to the technique
            // including https://blog.jayway.com/2017/07/13/open-pdf-downloaded-api-javascript/
            const link = document.createElement('a');
            link.href = window.URL.createObjectURL(blob);
            link.download = filename;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }).catch((err) => {
            this.props.setInProgress(false);
            console.warn('batchDownload error %s:%s', err.name, err.message);
        });
    }

    render() {
        const { elements, fileCount, cartInProgress } = this.props;

        return (
            <BatchDownloadModal
                handleDownloadClick={this.batchDownload}
                title="Download"
                disabled={fileCount === 0 || cartInProgress}
                additionalContent={elements.length >= ELEMENT_WARNING_LENGTH_MIN ?
                    <p className="cart__batch-download-warning">
                        The &ldquo;files.txt&rdquo; file can take a very long time to generate
                        with {elements.length} patients in your cohort. Cohort operations will be
                        unavailable until this file completes downloading.
                    </p>
                : null}
            />
        );
    }
}

CartBatchDownloadComponent.propTypes = {
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

CartBatchDownloadComponent.defaultProps = {
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

const CartBatchDownloadInternal = connect(mapStateToProps, mapDispatchToProps)(CartBatchDownloadComponent);


/**
 * Wrapper to receive React <App> context and pass them to CartBatchDownloadInternal as regular
 * props.
 */
const CartBatchDownload = (props, reactContext) => (
    <CartBatchDownloadInternal {...props} fetch={reactContext.fetch} />
);

CartBatchDownload.contextTypes = {
    fetch: PropTypes.func,
};

export default CartBatchDownload;
