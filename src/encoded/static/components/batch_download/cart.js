import QueryString from '../../libs/query_string';
import BatchDownloadController, { buildDownloadOptionsIndex } from './base';


/**
 * Download-menu template when the user has selected an assembly.
 */
const selectedAssemblyTemplate = [
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
        description: 'Download processed files associated with an assembly that match the selected file filters.',
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
 * Download-menu template when the user has not selected an assembly.
 */
const noSelectedAssemblyTemplate = [
    {
        id: 'processed-files',
        label: 'Download processed files',
        title: 'Processed files',
        description: 'Download processed files that match the selected file filters',
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
 * Controller to handle batch downloads on the cart-view page.
 * @param {string} cartPath @id of the cart with the dataset files to download
 * @param {string} datasetType @type of dataset to select
 * @param {string} assemblies Currently selected assemblies
 * @param {object} query QueryString object with facet selections
 */
export default class CartBatchDownloadController extends BatchDownloadController {
    constructor(cartPath, datasetType, assemblies, query) {
        // Just need to reorder the parameters so `preBuildDownloadOptions` can access the
        // parameters beyond `dataset` and `query`.
        super(null, query, cartPath, datasetType, assemblies);
    }

    preBuildDownloadOptions(dataset, query, cartPath, datasetType, assemblies) {
        this._cartPath = cartPath;
        this._datasetType = datasetType;
        this._assemblies = assemblies || [];
        this._downloadOptionsTemplate = assemblies.length > 0 ? selectedAssemblyTemplate : noSelectedAssemblyTemplate;
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
     * Add the batch download assemblies to the given QueryString object.
     * @param {object} query QueryString object to add assembly terms to
     */
    addAssembliesToQuery(query) {
        this._assemblies.forEach((assembly) => {
            query.addKeyValue('files.assembly', assembly);
        });
    }

    /**
     * Format the default-file download query string.
     */
    formatDefaultFileQuery() {
        const query = this.buildBasicQuery();
        this.addAssembliesToQuery(query);
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
        this.addAssembliesToQuery(query);
        query.addKeyValue('files.analyses.status', 'released');
        this._defaultAnalysisQueryString = query.format();
    }

    /**
     * Format the processed-file download query string, overriding the base class's version.
     */
    formatProcessedQuery() {
        const query = this.buildBasicQuery();
        if (this._assemblies.length > 0) {
            this.addAssembliesToQuery(query);
        } else {
            query.addKeyValue('files.processed', 'true');
        }
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
            .addKeyValue('files.output_category', 'raw data');
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

        // Add the entire options menu. Annotations only have one or two items, while experiments
        // and FCCs have the whole set.
        this._downloadOptions = [];
        if (this._assemblies.length > 0) {
            this._downloadOptions = [
                {
                    ...this._downloadOptionsTemplate[this._downloadOptionsTemplateIndex['default-files']],
                    query: this._defaultFileQueryString,
                },
            ];
        }
        if (this._datasetType !== 'Annotation') {
            if (this._assemblies.length > 0) {
                this._downloadOptions.push(
                    {
                        ...this._downloadOptionsTemplate[this._downloadOptionsTemplateIndex['default-analysis']],
                        query: this._defaultAnalysisQueryString,
                    }
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

        // Build the index of all of all the download options.
        this._downloadOptionsIndex = buildDownloadOptionsIndex(this._downloadOptions);
    }
}
