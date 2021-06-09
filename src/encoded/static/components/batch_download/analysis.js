import BatchDownloadController, { buildDownloadOptionsIndex } from './base';


/**
 * Batch-download controller for downloads in individual sections within a file table of the file
 * gallery. It only offers two download options.
 */
export default class AnalysisBatchDownloadController extends BatchDownloadController {
    constructor(dataset, analysisPath, query, fileQueryKey = 'files') {
        // Just need to reorder the parameters so `preBuildDownloadOptions` can access the
        // parameters beyond `dataset` and `query`.
        super(dataset, query, analysisPath, fileQueryKey);
    }

    preBuildDownloadOptions(dataset, query, analysisPath, fileQueryKey) {
        this._analysisPath = analysisPath;
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
                id: 'processed-files',
                label: 'Download processed files',
                title: 'Processed files',
                description: 'Downloads processed files matching the selected file filters.',
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
        query.addKeyValue(`${this._fileQueryKey}.analyses.@id`, this._analysisPath);
        query.addKeyValue(`${this._fileQueryKey}.preferred_default`, 'true');
        this._defaultFileQueryString = query.format();
    }

    /**
     * Format the processed-file download query string, overriding the base class's version.
     */
    formatProcessedQuery() {
        const query = this.buildBasicQuery()
            .addKeyValue(`${this._fileQueryKey}.analyses.@id`, this._analysisPath);
        this._processedQueryString = query.format();
    }

    /**
     * Overrides the base class's method to build all applicable query strings.
     */
    buildQueryStrings() {
        this.formatDefaultFileQuery();
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
                ...this._downloadOptionsTemplate[this._downloadOptionsTemplateIndex['processed-files']],
                query: this._processedQueryString,
            },
        ];

        // Build the index of this class's custom download options.
        this._downloadOptionsIndex = buildDownloadOptionsIndex(this._downloadOptions);
    }
}

