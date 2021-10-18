import BatchDownloadController, { buildDownloadOptionsIndex } from './base';


/**
 * Batch-download controller for downloads for a single dataset. It adds two items to the download
 * options menu, but uses the base options unmodified.
 * @param {object} dataset Contains dataset with files to download
 * @param {object} query QueryString of currently selected file facet terms
 * @param {string} fileQueryKey Query string file parameter prefix; "files" by default
 */
export default class DatasetBatchDownloadController extends BatchDownloadController {
    constructor(dataset, query, fileQueryKey = 'files') {
        super(dataset, query, fileQueryKey);
    }

    /**
     * Initialize the template and index for the custom download options.
     */
    preBuildDownloadOptions(dataset, query, fileQueryKey) {
        this._fileQueryKey = fileQueryKey;
        this._downloadOptionsTemplate = [
            {
                id: 'default-files',
                label: 'Download default files',
                title: 'Default files',
                description: 'Downloads default files within the default analysis along with selected file filters.',
                query: '',
            },
            {
                id: 'default-analysis',
                label: 'Download default analysis files',
                title: 'Default analysis',
                description: 'Downloads files within the default analysis along with selected file filters.',
                query: '',
            },
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
        this._downloadOptionsTemplateIndex = buildDownloadOptionsIndex(this._downloadOptionsTemplate);
    }

    /**
     * Format the default-file download query string.
     */
    formatDefaultFileQuery() {
        const query = this.buildBasicQuery();
        if (this._dataset.default_analysis) {
            query.addKeyValue(`${this._fileQueryKey}.analyses.@id`, this._dataset.default_analysis);
        }
        query.addKeyValue(`${this._fileQueryKey}.preferred_default`, 'true');
        this._defaultFileQueryString = query.format();
    }

    /**
     * Format the default-analysis download query string.
     */
    formatDefaultAnalysisQuery() {
        if (this._dataset.default_analysis) {
            const query = this.buildBasicQuery()
                .addKeyValue(`${this._fileQueryKey}.analyses.@id`, this._dataset.default_analysis);
            this._defaultAnalysisQueryString = query.format();
        } else {
            this._defaultAnalysisQueryString = '';
        }
    }

    /**
     * Format the processed-file download query string.
     */
    formatProcessedQuery() {
        const query = this.buildBasicQuery()
            .addKeyValue(`${this._fileQueryKey}.processed`, 'true');
        this._processedQueryString = query.format();
    }

    /**
     * Build query strings based on the query object, in addition to the base class query strings.
     */
    addQueryStrings() {
        this.formatDefaultFileQuery();
        this.formatDefaultAnalysisQuery();
    }

    buildDownloadOptions() {
        // Build all the query strings based on the dataset.
        this.buildQueryStrings();

        // Add the base download options menu configurations.
        this._downloadOptions = [
            {
                ...this._downloadOptionsTemplate[this._downloadOptionsTemplateIndex['default-files']],
                query: this._defaultFileQueryString,
            },
        ];
        if (this._dataset['@type'][0] !== 'Annotation') {
            if (this._dataset.default_analysis) {
                this._downloadOptions.push(
                    {
                        ...this._downloadOptionsTemplate[this._downloadOptionsTemplateIndex['default-analysis']],
                        query: this._defaultAnalysisQueryString,
                    },
                );
            }
            this._downloadOptions.push(
                {
                    ...this._downloadOptionsTemplate[this._downloadOptionsTemplateIndex['processed-files']],
                    query: this._processedQueryString,
                },
                {
                    ...this._downloadOptionsTemplate[this._downloadOptionsTemplateIndex['raw-files']],
                    query: this._rawQueryString,
                },
            );
        }
        this._downloadOptions.push(
            {
                ...this._downloadOptionsTemplate[this._downloadOptionsTemplateIndex['all-files']],
                query: this._allQueryString,
            },
        );

        // Build the index of all of base and custom download options.
        this._downloadOptionsIndex = buildDownloadOptionsIndex(this._downloadOptions);
    }
}
