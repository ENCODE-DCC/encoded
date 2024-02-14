import React from 'react';
import PropTypes from 'prop-types';
import QueryString from '../../libs/query_string';
import * as DropdownButton from '../../libs/ui/button';
import { Modal, ModalHeader, ModalBody, ModalFooter } from '../../libs/ui/modal';


/**
 * Displays default contents of the batch download modal. You can import this into your own
 * component if you want to add content above or below the default contents. If you need to insert
 * items into the middle, copy the contents of this component and modify as you need to.
 */
export const DefaultBatchDownloadContent = () => (
    <div className="batch-download-content">
        <p>
            Click the &ldquo;Download&rdquo; button below to download a &ldquo;files.txt&rdquo;
            file that contains a list of URLs to a file containing all the experimental metadata
            and links to download the file. The first line of the file has the URL or command line
            to download the metadata file.
        </p>
        <p>
            Further description of the contents of the metadata file are described in the <a href="/help/batch-download/">Batch Download help doc</a>.
        </p>
        <p>
            The &ldquo;files.txt&rdquo; file can be copied to any server.<br />
            The following command using cURL can be used to download all the files in the list:
        </p>
        <code>xargs -L 1 curl -O -J -L &lt; files.txt</code><br />
    </div>
);


/**
 * Manages the batch download modal. It always renders the modal unconditionally, so
 * `BatchDownloadActuator` controls its visibility.
 */
const BatchDownloadModal = ({ controller, modalContent, downloadRequestHandler, closeModalHandler, disabled }) => {
    /** True to disable the download button in the modal; automatic after user clicks button */
    const [isDownloadButtonDisabled, setIsDownloadButtonDisabled] = React.useState(disabled);
    /** Ref for the dropdown button so we can give it keyboard focus when the modal appears */
    const executeRef = React.useRef(null);

    /**
     * Called when the user clicks the download button.
     * @param {string} selectedOption Current user-selected download option id
     */
    const handleExecute = (selectedOption) => {
        // Disable the Download button immediately after click to prevent a double click.
        setIsDownloadButtonDisabled(true);
        downloadRequestHandler(selectedOption);
    };

    React.useEffect(() => {
        // Focus on the modal's execute (Download) button at mount.
        executeRef.current.focus();
    }, []);

    return (
        <Modal focusId="batch-download-submit" closeModal={closeModalHandler}>
            <ModalHeader title="Using batch download" closeModal={closeModalHandler} />
            <ModalBody>
                {modalContent}
            </ModalBody>
            <ModalFooter addCss="batch-download-modal-footer">
                {isDownloadButtonDisabled ?
                    <div className="batch-download-modal-footer__note">
                        Allow time for files.txt to download. You can close this dialog at any time.
                    </div>
                : null}
                <button type="button" className="btn btn-info btn-sm batch-download-modal-footer__close" onClick={closeModalHandler}>Close</button>
                <DropdownButton.Selected
                    labels={controller.downloadOptionLabels}
                    execute={handleExecute}
                    executeRef={executeRef}
                    id="batch-download"
                    css="batch-download-submit"
                    triggerVoice="Download options"
                    disabled={isDownloadButtonDisabled}
                >
                    {controller.downloadOptions.map((downloadOption) => (
                        <button key={downloadOption.id} type="button" id={downloadOption.id} className="batch-download-option">
                            <div className="batch-download-option__title">
                                {downloadOption.title}
                            </div>
                            <div className="batch-download-option__description">
                                {downloadOption.description}
                            </div>
                        </button>
                    ))}
                </DropdownButton.Selected>
            </ModalFooter>
        </Modal>
    );
};

BatchDownloadModal.propTypes = {
    /** Batch download controller object */
    controller: PropTypes.object.isRequired,
    /** Content to replace default batch download modal content */
    modalContent: PropTypes.node.isRequired,
    /** Called when the user requests the download */
    downloadRequestHandler: PropTypes.func.isRequired,
    /** Called when user closes the modal without requesting downloading */
    closeModalHandler: PropTypes.func.isRequired,
    /** True to show the download button in the modal footer disabled */
    disabled: PropTypes.bool,
};

BatchDownloadModal.defaultProps = {
    disabled: false,
};


/**
 * Renders a Download button that controls the visibility of the batch download modal.
 */
export const BatchDownloadActuator = ({ controller, actuator, modalContent, containerCss, disabled }, { navigate }) => {
    /** True if the batch download modal is visible */
    const [isModalVisible, setIsModalVisible] = React.useState(false);

    /**
     * Called when the user clicks the batch download actuator to bring up the modal.
     */
    const handleActuatorClick = () => {
        setIsModalVisible(true);
    };

    /**
     * Called when the user closes the batch download modal.
     */
    const handleClose = () => {
        setIsModalVisible(false);
    };

    /**
     * Called when the user clicks the download button in the batch download modal. It calls the
     * controller's method for initiating the download.
     * @param {string} selectedOption ID of the currently selected download option
     */
    const handleDownload = (selectedOption) => {
        controller.initiateDownload(selectedOption, navigate);
    };

    // Attach a click handler to the optional actuator.
    const actuatorWithClickHandler = actuator ? React.cloneElement(actuator, { onClick: handleActuatorClick }) : null;

    return (
        <div className={`batch-download-actuator${containerCss ? ` ${containerCss}` : ''}`}>
            {actuatorWithClickHandler || (
                <button
                    type="button"
                    className="btn btn-info btn-sm"
                    onClick={handleActuatorClick}
                    disabled={disabled}
                    data-test="batch-download"
                >
                    Download
                </button>
            )}
            {isModalVisible
                ? (
                    <BatchDownloadModal
                        controller={controller}
                        modalContent={modalContent || <DefaultBatchDownloadContent />}
                        downloadRequestHandler={handleDownload}
                        closeModalHandler={handleClose}
                    />
                )
                : null
            }
        </div>
    );
};

BatchDownloadActuator.propTypes = {
    /** Batch download controller object */
    controller: PropTypes.object.isRequired,
    /** Actuator for batch download modal to override default button; no onClick needed */
    actuator: PropTypes.element,
    /** Descriptive content of batch download modal to replace default */
    modalContent: PropTypes.node,
    /** CSS classes to add to the actuator container div */
    containerCss: PropTypes.string,
    /** True if button should appear disabled */
    disabled: PropTypes.bool,
};

BatchDownloadActuator.defaultProps = {
    actuator: null,
    /** null instead of default component to avoid https://github.com/facebook/react/issues/2166 */
    modalContent: null,
    containerCss: '',
    disabled: false,
};

BatchDownloadActuator.contextTypes = {
    navigate: PropTypes.func,
};


/**
 * Build an index into the given download options array so that you can map a download options ID
 * to the corresponding entry in the download options array.
 * @param {array} options Download options to index
 * @returns {object} Maps download option id to corresponding index in option array
 */
export const buildDownloadOptionsIndex = (options) => (
    options.reduce((indices, option, index) => {
        indices[option.id] = index;
        return indices;
    }, {})
);


/**
 * Default download options. Derived batch-download classes can insert items before or after these,
 * or overwrite these completely.
 */
const downloadOptionsTemplate = [
    {
        id: 'processed-files',
        label: 'Download processed files',
        title: 'Processed files',
        description: 'Downloads processed files matching the selected file filters.',
        query: '',
    },
    {
        id: 'raw-files',
        label: 'Download raw files',
        title: 'Raw files',
        description: 'Downloads all raw data files without using any selected filters.',
        query: '',
    },
    {
        id: 'all-files',
        label: 'Download all files',
        title: 'All files',
        description: 'Downloads all files without using any selected filters.',
        query: '',
    },
];


/**
 * Indices into `downloadOptions` array keyed by id, e.g.:
 * downloadOptions[downloadOptionsIndices['processed-files']]
 * => Index into `downloadOptions` of entry with id "processed-files"
 */
const downloadOptionsTemplateIndex = buildDownloadOptionsIndex(downloadOptionsTemplate);


/**
 * Base class for the batch-download controller. Extend from this class to implement specific
 * scenarios of batch downloads.
 */
export default class BatchDownloadController {
    constructor(dataset, query, ...extraArgs) {
        this._dataset = dataset;
        this._query = query.clone();

        // If derived classes need to perform any operations before building the download options,
        // they should implement the `preBuildDownloadOption` method.
        if (this.preBuildDownloadOptions) {
            this.preBuildDownloadOptions(dataset, query, ...extraArgs);
        }

        // Build download query strings and use them to put together the download options menu.
        this.buildDownloadOptions();
    }

    /**
     * Utility method to add the 'type=' and '@id=' queries to the object's _query, based on the
     * given dataset, and return the result. This assumes the incoming query doesn't include "type"
     * and "@id" query-string parameters.
     * @returns {object} QueryString modified with basic query parameters
     */
    buildBasicQuery() {
        const query = this._query.clone();
        query
            .addKeyValue('type', this._dataset['@type'][0])
            .addKeyValue('@id', this._dataset['@id']);
        return query;
    }

    /**
     * Format the processed-file download query string.
     */
    formatProcessedQuery() {
        const query = this.buildBasicQuery()
            .addKeyValue('files.processed', 'true');
        this._processedQueryString = query.format();
    }

    /**
     * Format the raw-file download query string.
     */
    formatRawQuery() {
        const query = new QueryString();
        query
            .addKeyValue('type', this._dataset['@type'][0])
            .addKeyValue('@id', this._dataset['@id'])
            .addKeyValue('files.output_category', 'raw data');
        this._rawQueryString = query.format();
    }

    /**
     * Format the all-file download query string.
     */
    formatAllQuery() {
        const query = new QueryString();
        query
            .addKeyValue('type', this._dataset['@type'][0])
            .addKeyValue('@id', this._dataset['@id']);
        this._allQueryString = query.format();
    }

    /**
     * Build all the query strings based on the query object. Derived classes can add to these
     * query strings by implementing the `addQueryString` method.
     */
    buildQueryStrings() {
        this.formatProcessedQuery();
        this.formatRawQuery();
        this.formatAllQuery();

        // Add other query strings in derived classes.
        if (this.addQueryStrings) {
            this.addQueryStrings();
        }
    }

    /**
     * Build the download options menu configuration using `downloadOptionsTemplate` as a source.
     * For subclasses, build any download options to insert before and after the base ones by
     * implementing `buildPreDownloadOptions` and/or `buildPostDownloadOptions` methods that return
     * arrays of custom download options to insert before or after the base options. If you need to
     * delete any of the base entries, override `buildDownloadOptions` instead and build them from
     * scratch.
     */
    buildDownloadOptions() {
        // Build all the query strings based on the dataset.
        this.buildQueryStrings();

        // If subclasses need to insert their own options at the beginning or ends of the base
        // options, build them here.
        const preDownloadOptions = this.buildPreDownloadOptions ? this.buildPreDownloadOptions() : [];
        const postDownloadOptions = this.buildPostDownloadOptions ? this.buildPostDownloadOptions() : [];

        // Add the base download options menu configurations.
        this._downloadOptions = preDownloadOptions.concat([
            {
                ...downloadOptionsTemplate[downloadOptionsTemplateIndex['processed-files']],
                query: this._processedQueryString,
            },
            {
                ...downloadOptionsTemplate[downloadOptionsTemplateIndex['raw-files']],
                query: this._rawQueryString,
            },
            {
                ...downloadOptionsTemplate[downloadOptionsTemplateIndex['all-files']],
                query: this._allQueryString,
            },
        ], postDownloadOptions);

        // Build the index of all of base and custom download options.
        this._downloadOptionsIndex = buildDownloadOptionsIndex(this._downloadOptions);
    }

    /**
     * Used to retrieve the single download options object with an id matching the given one.
     * @param {string} id of desired download option
     * @returns {object} Single download option object matching `id`, or undefined if no match.
     */
    getDownloadOption(id) {
        return this._downloadOptions[this._downloadOptionsIndex[id]];
    }

    /**
     * Return all the download options in an array.
     * @returns {array} All this class's download option objects.
     */
    get downloadOptions() {
        return this._downloadOptions;
    }

    /**
     * Get an object keyed by download option id and with the corresponding download option labels
     * as the values. This is useful for passing to the `labels` property of
     * <DropdownButton.selected>.
     * @returns {object} Download options in form suitable for dropdown button
     */
    get downloadOptionLabels() {
        return this._downloadOptions.reduce((coalescedLabels, option) => (
            { ...coalescedLabels, [option.id]: option.label }
        ), {});
    }

    /**
     * Initiate the batch download using the query string for the specified download option ID.
     * @param {string} id Specifies which download option's query string to use
     * @param {function} navigate System navigation function from `contextTypes`
     */
    initiateDownload(id, navigate) {
        const downloadOption = this.getDownloadOption(id);
        navigate(`/batch_download/?${downloadOption.query}`);
    }
}
