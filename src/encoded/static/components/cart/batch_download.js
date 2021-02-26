/**
 * Display the batch download modal on the cart page, and with the user confirming the modal,
 * initiate the batch download.
 */
import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import _ from 'underscore';
import * as encoding from '../../libs/query_encoding';
import * as DropdownButton from '../../libs/ui/button';
import { cartOperationInProgress } from './actions';
import { BatchDownloadModal } from '../view_controls';


/** Maximum number of elements in cart that generates warning in download dialog */
const ELEMENT_WARNING_LENGTH_MIN = 500;


/**
 * Called when the user confirms they want to initiate the batch download. For carts, the
 * download uses a POST request with the @id of every experiment in the POST payload. If the
 * user has logged in, we additionally set a "cart" query string parameter with the @id of the
 * user's cart object, which is used in the metadata.tsv line of the resulting files.txt.
 */
const batchDownload = (
    cartType,
    elements,
    analyses,
    selectedTerms,
    selectedType,
    facetFields,
    savedCartObj,
    sharedCart,
    setInProgress,
    {
        raw = false,
        all = false,
        visualizable = false,
        preferredDefault = false,
    },
    fetch
) => {
    let contentDisposition;
    let cartId;
    if (cartType === 'OBJECT') {
        cartId = sharedCart['@id'];
    } else {
        cartId = savedCartObj && savedCartObj['@id'];
    }

    // Form query string from currently selected file formats.
    const datasetFacets = facetFields.filter((facetField) => facetField.dataset).map((facetField) => facetField.field);
    const fileFormatSelections = (raw || all)
        ? []
        : (
            _.compact(Object.keys(selectedTerms).map((field) => {
                let subQueryString = '';
                let mappedQuery = '';
                if (selectedTerms[field].length > 0) {
                    const matchingFacetField = facetFields.find((facetField) => facetField.field === field);
                    if (matchingFacetField && matchingFacetField.fieldMapper) {
                        mappedQuery = matchingFacetField.fieldMapper(selectedTerms[field], analyses);
                    } else {
                        // Build the query string from `files` properties in the dataset, or from the
                        // dataset properties itself for fields marked in `facets`.
                        subQueryString = selectedTerms[field].map((term) => (
                            `${datasetFacets.includes(field) ? '' : 'files.'}${field}=${encoding.encodedURIComponent(term)}`
                        )).join('&');
                    }
                }
                return `${subQueryString}${mappedQuery ? `&${mappedQuery}` : ''}`;
            }))
        );

    // Initiate a batch download as a POST, passing it all dataset @ids in the payload.
    setInProgress(true);
    const visualizableOption = `${visualizable ? '&option=visualizable' : ''}`;
    const rawOption = `${raw ? '&option=raw' : ''}`;
    const preferredDefaultQuery = preferredDefault ? '&files.preferred_default=true' : '';
    fetch(`/batch_download/?type=${selectedType}${cartId ? `&cart=${encoding.encodedURIComponent(cartId)}` : ''}${fileFormatSelections.length > 0 ? `&${fileFormatSelections.join('&')}` : ''}${visualizableOption}${rawOption}${preferredDefaultQuery}`, {
        method: 'POST',
        headers: {
            Accept: 'text/plain',
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            elements,
        }),
    }).then((response) => {
        if (response.ok) {
            contentDisposition = response.headers.get('content-disposition');
            return response.blob();
        }
        throw new Error(response);
    }).then((blob) => {
        setInProgress(false);

        // Extract filename from batch_download response content disposition tag.
        const matchResults = contentDisposition.match(/filename="(.*?)"/);
        const filename = matchResults ? matchResults[1] : 'files.txt';
        const nav = window.navigator;

        // IE11 workaround (also activates on Edge-Trident but not Edge-Chromium)
        if (nav && nav.msSaveOrOpenBlob) {
            nav.msSaveOrOpenBlob(blob, filename);
        } else {
            // Make a temporary link in the DOM with the URL from the response blob and then
            // click the link to automatically download the file. Many references to the technique
            // including https://blog.jayway.com/2017/07/13/open-pdf-downloaded-api-javascript/
            const link = document.createElement('a');
            link.href = window.URL.createObjectURL(blob);
            link.download = filename;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }
    }).catch((err) => {
        setInProgress(false);
        console.warn('batchDownload error %s:%s', err.name, err.message);
    });
};


/**
 * Converts a download type to human-readable text to be used for relevant messages.
 * @param {string} downloadType Currently selected batch download type.
 *
 * @return {string} Human-readable form of `downloadType`.
 */
const getDownloadTypeText = (downloadType) => {
    if (downloadType === 'processed') {
        return 'processed data files';
    }
    if (downloadType === 'raw') {
        return 'raw data files';
    }
    return 'files';
};


/**
 * Displays batch download button for downloading files from experiments in carts. For shared carts
 * or logged-in users.
 */
const CartBatchDownloadComponent = (
    {
        cartType,
        elements,
        analyses,
        selectedTerms,
        selectedType,
        facetFields,
        savedCartObj,
        sharedCart,
        fileCounts,
        setInProgress,
        cartInProgress,
        visualizable,
        preferredDefault,
        disabledMessage,
        fetch,
    }
) => {
    // Tracks whether the batch-download modal is visible or not.
    const [isModalOpen, setIsModalOpen] = React.useState(false);
    // Keeps track of the currently selected download option.
    const [chosenFileCount, setChosenFileCount] = React.useState(fileCounts.processed);
    // Keeps track of the currently selected download option.
    const [downloadType, setDownloadType] = React.useState('processed');

    const openModal = () => { setIsModalOpen(true); };
    const closeModal = () => { setIsModalOpen(false); };

    // Called when the user clicks the Download button in the batch-download modal.
    const handleDownloadClick = () => {
        const options = {};
        if (downloadType === 'processed') {
            options.visualizable = visualizable;
        } else if (downloadType === 'raw') {
            options.raw = true;
        } else if (downloadType === 'all') {
            options.all = true;
        }
        options.preferredDefault = preferredDefault;
        batchDownload(cartType, elements, analyses, selectedTerms, selectedType, facetFields, savedCartObj, sharedCart, setInProgress, options, fetch);
    };

    // Called when the user clicks the button to make the batch-download modal appear.
    const handleExecute = (selection) => {
        setDownloadType(selection);
        if (selection === 'processed') {
            setChosenFileCount(fileCounts.processed);
        } else if (selection === 'raw') {
            setChosenFileCount(fileCounts.raw);
        } else if (selection === 'all') {
            setChosenFileCount(fileCounts.all);
        }
        openModal();
    };

    return (
        <>
            <DropdownButton.Selected
                labels={{
                    processed: disabledMessage || 'Download processed data files',
                    raw: disabledMessage || 'Download raw data files',
                    all: disabledMessage || 'Download all files',
                }}
                execute={handleExecute}
                id="cart-download"
                triggerVoice="Cart download options"
                css="cart-download"
                disabled={!!disabledMessage}
            >
                <button type="button" id="processed" className="menu-item">
                    <div className="cart-download__option-title">Processed data files</div>
                    <div className="cart-download__option-description">
                        Downloads files using the selected filters.
                    </div>
                </button>
                <button type="button" id="raw" className="menu-item">
                    <div className="cart-download__option-title">Raw data files only</div>
                    <div className="cart-download__option-description">
                        Downloads all files that don&rsquo;t have assemblies and without using any selected filters.
                    </div>
                </button>
                <button type="button" id="all" className="menu-item">
                    <div className="cart-download__option-title">All files</div>
                    <div className="cart-download__option-description">
                        Downloads all files without using any selected filters.
                    </div>
                </button>
            </DropdownButton.Selected>
            {isModalOpen ?
                <BatchDownloadModal
                    disabled={chosenFileCount === 0 || cartInProgress}
                    downloadClickHandler={handleDownloadClick}
                    closeModalHandler={closeModal}
                    additionalContent={
                        <>
                            {elements.length >= ELEMENT_WARNING_LENGTH_MIN ?
                                <p className="cart__batch-download-warning">
                                    The &ldquo;files.txt&rdquo; file can take a very long time to generate
                                    with {elements.length} experiments in your cart. Cart operations will be
                                    unavailable until this file completes downloading.
                                </p>
                            : null}
                            {chosenFileCount === 0 ?
                                <p className="cart__batch-download-warning">
                                    Unable to download as no {getDownloadTypeText(downloadType)} are available.
                                </p>
                            : null}
                        </>
                    }
                />
            : null}
        </>
    );
};

CartBatchDownloadComponent.propTypes = {
    /** Type of cart: ACTIVE, OBJECT */
    cartType: PropTypes.string.isRequired,
    /** Cart elements */
    elements: PropTypes.array,
    /** All compiled analyses in the cart */
    analyses: PropTypes.array.isRequired,
    /** Selected facet terms */
    selectedTerms: PropTypes.object,
    /** Selected object type */
    selectedType: PropTypes.string.isRequired,
    /** Used facet field definitions */
    facetFields: PropTypes.array.isRequired,
    /** Cart as it exists in the database; use JSON payload method if none */
    savedCartObj: PropTypes.object,
    /** Shared cart object */
    sharedCart: PropTypes.object,
    /** Number of files batch download will download for each download type */
    fileCounts: PropTypes.object,
    /** Redux cart action to set the in-progress state of the cart */
    setInProgress: PropTypes.func.isRequired,
    /** True if cart operation in progress */
    cartInProgress: PropTypes.bool,
    /** True to download only visualizable files */
    visualizable: PropTypes.bool,
    /** True to download preferred_default files */
    preferredDefault: PropTypes.bool,
    /** Message to display in browser tooltip when disabled */
    disabledMessage: PropTypes.string,
    /** System fetch function */
    fetch: PropTypes.func.isRequired,
};

CartBatchDownloadComponent.defaultProps = {
    elements: [],
    selectedTerms: null,
    savedCartObj: null,
    sharedCart: null,
    fileCounts: {},
    cartInProgress: false,
    visualizable: false,
    preferredDefault: false,
    disabledMessage: '',
};

const mapStateToProps = (state, ownProps) => ({
    cartInProgress: state.inProgress,
    elements: ownProps.elements,
    analyses: ownProps.analyses,
    selectedTerms: ownProps.selectedTerms,
    savedCartObj: ownProps.savedCartObj,
    fileCounts: ownProps.fileCounts,
    fetch: ownProps.fetch,
});

const mapDispatchToProps = (dispatch) => ({
    setInProgress: (enable) => dispatch(cartOperationInProgress(enable)),
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
