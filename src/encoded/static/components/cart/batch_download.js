import React from 'react';


/**
 * Display the batch download modal on the cart page, and with the user confirming the modal,
 * initiate the batch download.
 */
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import QueryString from '../../libs/query_string';
import {
    BatchDownloadActuator,
    CartBatchDownloadController,
    CartStaticBatchDownloadController,
    DefaultBatchDownloadContent,
} from '../batch_download';


/** Maximum number of elements in cart that generates warning in download dialog */
const ELEMENT_WARNING_LENGTH_MIN = 500;


/**
 * Build a QueryString object containing the selections given in the dataset and file facet
 * selections object.
 * @param {object} datasetTerms Selected dataset terms
 * @param {object} fileTerms Selected file terms
 * @param {string} datasetType Dataset type whose files are being downloaded
 * @param {boolean} visualizable True if only downloading visualizable files
 * @param {array} facetFields Facet field configurations for dataset and file facets
 * @returns {object} QueryString containing dataset and file selections
 */
const buildQueryFromTerms = (datasetTerms, fileTerms, datasetType, visualizable, facetFields) => {
    const query = new QueryString();

    // Add the selected dataset terms to the query.
    Object.keys(datasetTerms).forEach((term) => {
        if (datasetTerms[term].length > 0) {
            let mappedTerm = term;
            const matchingFacetField = facetFields.find((facetField) => facetField.field === term);
            if (matchingFacetField && matchingFacetField.fieldMapper) {
                // Transform terms to a query for those terms that require that.
                mappedTerm = matchingFacetField.fieldMapper(datasetType);
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
                mappedTerm = matchingFacetField.fieldMapper(datasetType);
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
        cart,
        selectedFileTerms,
        selectedDatasetTerms,
        selectedDatasetType,
        facetFields,
        cartInProgress,
        visualizable,
        isFileViewOnly,
    }
) => {
    if (cart) {
        const disabled = !selectedDatasetType || cartInProgress || isFileViewOnly;
        let actuatorTitle;
        if (isFileViewOnly) {
            actuatorTitle = 'Turn off file view to download';
        } else {
            actuatorTitle = selectedDatasetType ? 'Download' : 'Select single dataset type to download';
        }

        // Build the cart batch-download controller from the user selections.
        const selectedAssemblies = selectedFileTerms.assembly;
        const cartQuery = buildQueryFromTerms(selectedDatasetTerms, selectedFileTerms, selectedDatasetType, visualizable, facetFields);
        const cartController = new CartBatchDownloadController(cart['@id'], selectedDatasetType, selectedAssemblies, cartQuery);

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
    }
    return null;
};

CartBatchDownloadComponent.propTypes = {
    /** Cart object as it exists in the database */
    cart: PropTypes.object,
    /** Selected file facet terms */
    selectedFileTerms: PropTypes.object,
    /** Currently selected dataset type */
    selectedDatasetType: PropTypes.string.isRequired,
    /** Used facet field definitions */
    facetFields: PropTypes.array.isRequired,
    /** Selected dataset facet terms */
    selectedDatasetTerms: PropTypes.object,
    /** True if cart operation in progress */
    cartInProgress: PropTypes.bool,
    /** True to download only visualizable files */
    visualizable: PropTypes.bool,
    /** True if file view selected */
    isFileViewOnly: PropTypes.bool,
};

CartBatchDownloadComponent.defaultProps = {
    cart: null,
    selectedFileTerms: null,
    selectedDatasetTerms: null,
    cartInProgress: false,
    visualizable: false,
    isFileViewOnly: false,
};

CartBatchDownloadComponent.mapStateToProps = (state, ownProps) => ({
    cart: ownProps.cart,
    cartInProgress: state.inProgress,
    elements: ownProps.elements,
    analyses: ownProps.analyses,
    fileCounts: ownProps.fileCounts,
    fetch: ownProps.fetch,
});

const CartBatchDownloadInternal = connect(CartBatchDownloadComponent.mapStateToProps)(CartBatchDownloadComponent);


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


/**
 * Displays the dropdown that allows the user to select a dataset type to download.
 */
const StaticBatchDownloadDatasetTypeSelector = ({
    datasetTypes,
    selectedDatasetType,
    setSelectedDatasetType,
}, reactContext) => (
    <div className="cart__batch-download-dataset-type-selector">
        <>Select download dataset type</>
        <select value={selectedDatasetType} onChange={(e) => setSelectedDatasetType(e.target.value)}>
            {datasetTypes.map((datasetType) => (
                <option key={datasetType} value={datasetType}>
                    {reactContext.profilesTitles ? reactContext.profilesTitles[datasetType] : datasetType}
                </option>
            ))}
        </select>
    </div>
);

StaticBatchDownloadDatasetTypeSelector.propTypes = {
    /** List of possible dataset types the user can choose from */
    datasetTypes: PropTypes.array.isRequired,
    /** Currently selected dataset type; member of `datasetTypes` */
    selectedDatasetType: PropTypes.string.isRequired,
    /** Called when the user changes the selected dataset type */
    setSelectedDatasetType: PropTypes.func.isRequired,
};

StaticBatchDownloadDatasetTypeSelector.contextTypes = {
    profilesTitles: PropTypes.object,
};


/**
 * Displays batch download button for downloading files from experiments in carts. For shared carts
 * or logged-in users.
 */
const CartStaticBatchDownloadComponent = ({ cart, assembly, datasetTypes, isFileViewActive, cartInProgress }) => {
    /** Selected dataset type from modal dropdown */
    const [selectedDatasetType, setSelectedDatasetType] = React.useState(datasetTypes[0]);

    React.useEffect(() => {
        setSelectedDatasetType(datasetTypes[0]);
    }, [datasetTypes]);

    if (cart && selectedDatasetType) {
        // Build the static cart batch-download controller from the user selections.
        const cartQuery = buildQueryFromTerms({}, {}, selectedDatasetType, false, []);
        const cartController = new CartStaticBatchDownloadController(cart['@id'], selectedDatasetType, assembly, isFileViewActive, cartQuery);

        // Add a dropdown to let the user select a dataset type to download. It also displays a
        // note about carts with file views downloading more than the visible files, and a warning
        // if a large number of elements are in the cart.
        const modalContent = (
            <>
                <DefaultBatchDownloadContent />
                {isFileViewActive &&
                    <p className="cart__batch-download-note">
                        This cart displays files included in its file view which has manually
                        selected files. In addition to these files, other processed files with the
                        <> {assembly}</> assembly will download.
                    </p>
                }
                <StaticBatchDownloadDatasetTypeSelector
                    datasetTypes={datasetTypes}
                    selectedDatasetType={selectedDatasetType}
                    setSelectedDatasetType={setSelectedDatasetType}
                />
                {cart.elements.length >= ELEMENT_WARNING_LENGTH_MIN
                    ? (
                        <p className="cart__batch-download-warning">
                            The &ldquo;files.txt&rdquo; file can take a very long time to generate
                            with {cart.elements.length} experiments in your cart. Cart operations will be
                            unavailable until this file completes downloading.
                        </p>
                    ) : null
                }
            </>
        );

        return (
            <BatchDownloadActuator
                controller={cartController}
                modalContent={modalContent}
                actuator={
                    <CartBatchDownloadButton title="Download" disabled={cartInProgress} />
                }
            />
        );
    }
    return null;
};

CartStaticBatchDownloadComponent.propTypes = {
    /** Cart object as it exists in the database */
    cart: PropTypes.object,
    /** Currently selected assembly */
    assembly: PropTypes.string,
    /** All dataset types from cart elements; don't include series types */
    datasetTypes: PropTypes.arrayOf(PropTypes.string),
    /** True if cart has an active file view */
    isFileViewActive: PropTypes.bool.isRequired,
    /** True if cart operation in progress */
    cartInProgress: PropTypes.bool,
};

CartStaticBatchDownloadComponent.defaultProps = {
    cart: null,
    assembly: '',
    datasetTypes: [],
    cartInProgress: false,
};

CartStaticBatchDownloadComponent.mapStateToProps = (state, ownProps) => ({
    cart: ownProps.cart,
    assembly: ownProps.assembly,
    datasetTypes: ownProps.datasetTypes,
    isFileViewActive: ownProps.isFileViewActive,
    cartInProgress: state.inProgress,
});

const CartStaticBatchDownloadInternal = connect(CartStaticBatchDownloadComponent.mapStateToProps)(CartStaticBatchDownloadComponent);


/**
 * Wrapper to receive React <App> context and pass them to CartStaticBatchDownloadInternal as
 * regular props.
 */
export const CartStaticBatchDownload = (props, reactContext) => (
    <CartStaticBatchDownloadInternal {...props} fetch={reactContext.fetch} />
);

CartStaticBatchDownload.contextTypes = {
    fetch: PropTypes.func,
};
