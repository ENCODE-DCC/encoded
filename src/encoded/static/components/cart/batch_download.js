/**
 * Display the batch download modal on the cart page, and with the user confirming the modal,
 * initiate the batch download.
 */
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import QueryString from '../../libs/query_string';
import { BatchDownloadActuator, CartBatchDownloadController, DefaultBatchDownloadContent } from '../batch_download';


/** Maximum number of elements in cart that generates warning in download dialog */
const ELEMENT_WARNING_LENGTH_MIN = 500;


/**
 * Build a QueryString object containing the selections given in the dataset and file facet
 * selections object.
 * @param {object} datasetTerms Selected dataset terms
 * @param {object} fileTerms Selected file terms
 * @param {boolean} visualizable True if only downloading visualizable files
 * @param {array} facetFields Facet field configurations for dataset and file facets
 * @returns {object} QueryString containing dataset and file selections
 */
const buildQueryFromTerms = (datasetTerms, fileTerms, visualizable, facetFields) => {
    const query = new QueryString();

    // Add the selected dataset terms to the query.
    Object.keys(datasetTerms).forEach((term) => {
        if (datasetTerms[term].length > 0) {
            let mappedTerm = term;
            const matchingFacetField = facetFields.find((facetField) => facetField.field === term);
            if (matchingFacetField && matchingFacetField.fieldMapper) {
                // Transform terms to a query for those terms that require that.
                mappedTerm = matchingFacetField.fieldMapper();
            }
            datasetTerms[term].forEach((value) => {
                query.addKeyValue(mappedTerm, value);
            });
        }
    });

    // Add the selected file terms to the query.
    Object.keys(fileTerms).forEach((term) => {
        if (fileTerms[term].length > 0) {
            let mappedTerm = term;
            const matchingFacetField = facetFields.find((facetField) => facetField.field === term);
            if (matchingFacetField && matchingFacetField.fieldMapper) {
                // Transform terms to a query for those terms that require that.
                mappedTerm = matchingFacetField.fieldMapper();
            }
            fileTerms[term].forEach((value) => {
                query.addKeyValue(`files.${mappedTerm}`, value);
            });
        }
    });

    // Add visualizable option.
    if (visualizable) {
        query.addKeyValue('option', 'visualizable');
    }

    return query;
};


/**
 *  Custom batch download actuator that lets us use existing CSS styles on the button.
 */
const CartBatchDownloadButton = ({ title, disabled, onClick }) => (
    <button type="button" className="btn btn-info btn-sm btn-cart-download" disabled={disabled} onClick={onClick}>
        {title}
    </button>
);

CartBatchDownloadButton.propTypes = {
    /** Label for the button */
    title: PropTypes.string.isRequired,
    /** True if button disabled */
    disabled: PropTypes.bool,
    /** Called when the user clicks the button; provided by `BatchDownloadActuator` */
    onClick: PropTypes.func,
};

CartBatchDownloadButton.defaultProps = {
    disabled: false,
    onClick: null, // Actually required; provided by BatchDownloadActuator
};


/**
 * Displays batch download button for downloading files from experiments in carts. For shared carts
 * or logged-in users.
 */
const CartBatchDownloadComponent = (
    {
        cartType,
        selectedFileTerms,
        selectedDatasetTerms,
        facetFields,
        savedCartObj,
        sharedCart,
        cartInProgress,
        visualizable,
    }
) => {
    const selectedDatasetType = selectedDatasetTerms.type && selectedDatasetTerms.type.length === 1
        ? selectedDatasetTerms.type[0]
        : '';
    const disabled = !selectedDatasetType || cartInProgress;
    const actuatorTitle = selectedDatasetType ? 'Download' : 'Select single dataset type to download';

    // Build the cart batch-download controller from the user selections.
    const cart = cartType === 'ACTIVE' ? savedCartObj : sharedCart;
    const selectedAssembly = selectedFileTerms.assembly[0];
    const cartQuery = buildQueryFromTerms(selectedDatasetTerms, selectedFileTerms, visualizable, facetFields);
    const cartController = new CartBatchDownloadController(cart['@id'], selectedDatasetType, selectedAssembly, cartQuery);

    // Display a warning message in the modal if we have more than a threshold number of datasets
    // in the cart.
    const modalContent = (
        <>
            <DefaultBatchDownloadContent />
            {cart.elements.length >= ELEMENT_WARNING_LENGTH_MIN
                ? (
                    <p className="cart__batch-download-warning">
                        The &ldquo;files.txt&rdquo; file can take a very long time to generate
                        with {cart.elements.length} experiments in your cart. Cart operations will be
                        unavailable until this file completes downloading.
                    </p>
                ) : null}
        </>
    );

    return (
        <BatchDownloadActuator
            controller={cartController}
            modalContent={modalContent}
            actuator={
                <CartBatchDownloadButton title={actuatorTitle} disabled={disabled} />
            }
        />
    );
};

CartBatchDownloadComponent.propTypes = {
    /** Type of cart: ACTIVE, OBJECT */
    cartType: PropTypes.string.isRequired,
    /** Selected file facet terms */
    selectedFileTerms: PropTypes.object,
    /** Used facet field definitions */
    facetFields: PropTypes.array.isRequired,
    /** Selected dataset facet terms */
    selectedDatasetTerms: PropTypes.object,
    /** Cart as it exists in the database; use JSON payload method if none */
    savedCartObj: PropTypes.object,
    /** Shared cart object */
    sharedCart: PropTypes.object,
    /** True if cart operation in progress */
    cartInProgress: PropTypes.bool,
    /** True to download only visualizable files */
    visualizable: PropTypes.bool,
};

CartBatchDownloadComponent.defaultProps = {
    selectedFileTerms: null,
    selectedDatasetTerms: null,
    savedCartObj: null,
    sharedCart: null,
    cartInProgress: false,
    visualizable: false,
};

const mapStateToProps = (state, ownProps) => ({
    cartInProgress: state.inProgress,
    elements: ownProps.elements,
    analyses: ownProps.analyses,
    savedCartObj: ownProps.savedCartObj,
    fileCounts: ownProps.fileCounts,
    fetch: ownProps.fetch,
});

const CartBatchDownloadInternal = connect(mapStateToProps)(CartBatchDownloadComponent);


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
