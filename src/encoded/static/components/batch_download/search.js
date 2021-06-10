import BatchDownloadController, { buildDownloadOptionsIndex } from './base';


/**
 * Batch-download controller for downloads on search-result pages.
 * @param {string} datasetType @type of dataset currently selected in search results
 * @param {string} query QueryString object with facet selections
 */
export default class SearchBatchDownloadController extends BatchDownloadController {
    constructor(datasetType, query) {
        // Just need to reorder the parameters so `preBuildDownloadOptions` can access the
        // parameters beyond `dataset` and `query`.
        super(null, query, datasetType);
    }

    preBuildDownloadOptions(dataset, query, datasetType) {
        this._datasetType = datasetType;
        this._downloadOptionsTemplate = [
            {
                id: 'default-files',
                label: 'Download default files',
                title: 'Default files',
                description: 'Downloads default files within the default analysis along with selected filters.',
                query: '',
            },
            {
                id: 'default-analysis',
                label: 'Download default analysis files',
                title: 'Default analysis',
                description: 'Downloads files within the default analysis along with selected filters.',
                query: '',
            },
            {
                id: 'processed-files',
                label: 'Download processed files',
                title: 'Processed files',
                description: 'Downloads processed files matching the selected filters.',
                query: '',
            },
        ];
        this._downloadOptionsTemplateIndex = buildDownloadOptionsIndex(this._downloadOptionsTemplate);
    }

    /**
     * Utility method to add the 'type=' query to the object's _query and return the result.
     * @returns {object} QueryString modified with basic query parameters
     */
    buildBasicQuery() {
        const query = this._query.clone();
        query
            .deleteKeyValue('type')
            .addKeyValue('type', this._datasetType);
        return query;
    }

    /**
     * Format the default-file download query string.
     */
    formatDefaultFileQuery() {
        const query = this.buildBasicQuery();
        query.addKeyValue('files.analyses.status', 'released');
        query.addKeyValue('files.preferred_default', 'true');
        this._defaultFileQueryString = query.format();
    }

    /**
     * Format the default-analysis download query string.
     */
    formatDefaultAnalysisQuery() {
        const query = this.buildBasicQuery();
        query.addKeyValue('files.analyses.status', 'released');
        this._defaultAnalysisQueryString = query.format();
    }

    /**
     * Format the processed-file download query string, overriding the base class's version.
     */
    formatProcessedQuery() {
        const query = this.buildBasicQuery()
            .addKeyValue('files.assembly', '*');
        this._processedQueryString = query.format();
    }

    /**
     * Build all the query strings based on the query object, overriding the base class's version
     * of this method.
     */
    buildQueryStrings() {
        this.formatDefaultFileQuery();
        this.formatDefaultAnalysisQuery();
        this.formatProcessedQuery();
    }

    /**
     * Overrides the base class's method to build the download options.
     */
    buildDownloadOptions() {
        // Build all the query strings based on the dataset.
        this.buildQueryStrings();

        // Add the base download options menu configurations.
        this._downloadOptions = [
            {
                ...this._downloadOptionsTemplate[this._downloadOptionsTemplateIndex['default-files']],
                query: this._defaultFileQueryString,
            },
            {
                ...this._downloadOptionsTemplate[this._downloadOptionsTemplateIndex['default-analysis']],
                query: this._defaultAnalysisQueryString,
            },
            {
                ...this._downloadOptionsTemplate[this._downloadOptionsTemplateIndex['processed-files']],
                query: this._processedQueryString,
            },
        ];

        // Build the index of all of base and custom download options.
        this._downloadOptionsIndex = buildDownloadOptionsIndex(this._downloadOptions);
    }
}
