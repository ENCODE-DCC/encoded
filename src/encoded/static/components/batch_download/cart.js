import QueryString from '../../libs/query_string';
import BatchDownloadController, { buildDownloadOptionsIndex } from './base';


/**
 * Controller to handle batch downloads on the cart-view page.
 * @param {string} cartPath @id of the cart with the dataset files to download
 * @param {string} datasetType @type of dataset to select
 * @param {string} assembly Currently selected assembly
 * @param {object} query QueryString object with facet selections
 */
export default class CartBatchDownloadController extends BatchDownloadController {
    constructor(cartPath, datasetType, assembly, query) {
        // Just need to reorder the parameters so `preBuildDownloadOptions` can access the
        // parameters beyond `dataset` and `query`.
        super(null, query, cartPath, datasetType, assembly);
    }

    preBuildDownloadOptions(dataset, query, cartPath, datasetType, assembly) {
        this._cartPath = cartPath;
        this._datasetType = datasetType;
        this._assembly = assembly;
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
                description: 'Downloads all files that don\u2019t have assemblies and without using any selected filters.',
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
     * Utility method to add the 'type=' and 'cart' queries to the object's _query and return the
     * result.
     * @returns {object} QueryString modified with the "type" and "cart" query-string parameters.
     */
    buildBasicQuery() {
        const query = this._query.clone();
        query
            .deleteKeyValue('type')
            .deleteKeyValue('files.assembly')
            .addKeyValue('type', this._datasetType)
            .addKeyValue('cart', this._cartPath);
        return query;
    }

    /**
     * Format the default-file download query string.
     */
    formatDefaultFileQuery() {
        const query = this.buildBasicQuery();
        if (this._assembly) {
            // In rare cases, no selected files include an assembly.
            query.addKeyValue('files.assembly', this._assembly);
        }
        query
            .addKeyValue('files.analyses.status', 'released')
            .addKeyValue('files.preferred_default', 'true');
        this._defaultFileQueryString = query.format();
    }

    /**
     * Format the default-analysis download query string.
     */
    formatDefaultAnalysisQuery() {
        const query = this.buildBasicQuery();
        if (this._assembly) {
            // In rare cases, no selected files include an assembly.
            query.addKeyValue('files.assembly', this._assembly);
        }
        query.addKeyValue('files.analyses.status', 'released');
        this._defaultAnalysisQueryString = query.format();
    }

    /**
     * Format the processed-file download query string, overriding the base class's version.
     */
    formatProcessedQuery() {
        const query = this.buildBasicQuery();
        query.addKeyValue('files.assembly', this._assembly || '*');
        this._processedQueryString = query.format();
    }

    /**
     * Format the raw-file download query string, overriding the base class's version.
     */
    formatRawQuery() {
        const query = new QueryString();
        query
            .addKeyValue('type', this._datasetType)
            .addKeyValue('cart', this._cartPath)
            .addKeyValue('option', 'raw');
        this._rawQueryString = query.format();
    }

    /**
     * Format the all-file download query string.
     */
    formatAllQuery() {
        const query = new QueryString();
        query
            .addKeyValue('type', this._datasetType)
            .addKeyValue('cart', this._cartPath);
        this._allQueryString = query.format();
    }

    /**
     * Build all the query strings based on the cart and query object, overriding the base class's
     * version.
     */
    buildQueryStrings() {
        this.formatDefaultFileQuery();
        this.formatAllQuery();
        if (this._datasetType !== 'Annotation') {
            this.formatDefaultAnalysisQuery();
            this.formatProcessedQuery();
            this.formatRawQuery();
        }
    }

    /**
     * Overrides the base class's method to build the download options.
     */
    buildDownloadOptions() {
        // Build all the query strings based on the dataset.
        this.buildQueryStrings();

        // Add the entire options menu. Annotations only have two items, while experiments and FCCs
        // have the whole set.
        this._downloadOptions = [
            {
                ...this._downloadOptionsTemplate[this._downloadOptionsTemplateIndex['default-files']],
                query: this._defaultFileQueryString,
            },
        ];
        if (this._datasetType !== 'Annotation') {
            this._downloadOptions.push(
                {
                    ...this._downloadOptionsTemplate[this._downloadOptionsTemplateIndex['default-analysis']],
                    query: this._defaultAnalysisQueryString,
                },
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

        // Build the index of all of all the download options.
        this._downloadOptionsIndex = buildDownloadOptionsIndex(this._downloadOptions);
    }
}
