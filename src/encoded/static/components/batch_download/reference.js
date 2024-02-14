import BatchDownloadController, { buildDownloadOptionsIndex } from './base';


/**
 * Batch-download controller for downloads in individual sections within a file table of the file
 * gallery. It only offers two download options.
 * @param {object} dataset Contains dataset with files to download
 * @param {object} query QueryString of currently selected file facet terms
 * @param {string} outputType output_type value for filtering downloaded files
 * @param {string} outputCategory output_category value for filtering downloaded files
 * @param {string} fileQueryKey Query string file parameter prefix; "files" by default
 */
export default class ReferenceBatchDownloadController extends BatchDownloadController {
    constructor(dataset, query, outputType, outputCategory, fileQueryKey = 'files') {
        // Just need to reorder the parameters so `preBuildDownloadOptions` can access the
        // parameters beyond `dataset` and `query`.
        super(dataset, query, outputType, outputCategory, fileQueryKey);
    }

    preBuildDownloadOptions(dataset, query, outputType, outputCategory, fileQueryKey) {
        this._outputType = outputType;
        this._outputCategory = outputCategory;
        this._fileQueryKey = fileQueryKey;
        this._downloadOptionsTemplate = [
            {
                id: 'reference-files',
                label: 'Download reference files',
                title: 'Reference files',
                description: 'Downloads reference files with the selected output types.',
                query: '',
            },
        ];
        this._downloadOptionsTemplateIndex = buildDownloadOptionsIndex(this._downloadOptionsTemplate);
    }

    /**
     * Format the reference-file download query string.
     */
    formatReferenceFileQuery() {
        const query = this.buildBasicQuery();
        query.addKeyValue(`${this._fileQueryKey}.output_category`, this._outputCategory);
        if (this.outputType) {
            query.addKeyValue(`${this._fileQueryKey}.output_type`, this._outputType);
        }
        this._referenceFileQueryString = query.format();
    }

    /**
     * Overrides the base class's method to build all applicable query strings.
     */
    buildQueryStrings() {
        this.formatReferenceFileQuery();
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
                ...this._downloadOptionsTemplate[this._downloadOptionsTemplateIndex['reference-files']],
                query: this._referenceFileQueryString,
            },
        ];

        // Build the index of this class's custom download options.
        this._downloadOptionsIndex = buildDownloadOptionsIndex(this._downloadOptions);
    }
}
