import BatchDownloadController, { buildDownloadOptionsIndex } from './base';
import { uc } from '../../libs/constants';


/**
 * Download-menu template when the user has selected an assembly.
 */
const defaultFileTemplate = [
    {
        id: 'default-files',
        label: 'Download default files',
        title: 'Default files',
        description: 'Downloads default files within the default analysis for the selected assembly.',
        query: '',
    },
];


/**
 * Download-menu template when the user has not selected an assembly.
 */
const fileViewTemplate = [
    {
        id: 'processed-files',
        label: 'Download processed files',
        title: 'Processed files',
        description: `Download processed files. This includes files outside of this cart${uc.rsquo}s file view.`,
        query: '',
    },
];


/**
 * Controller to handle batch downloads on the cart-view page.
 * @param {string} cartPath @id of the cart with the dataset files to download
 * @param {string} datasetType @type of dataset to select
 * @param {string} assemblies Currently selected assemblies
 * @param {boolean} isFileViewActive True if displaying a file view
 * @param {object} cartQuery QueryString object with facet selections
 */
export default class CartStaticBatchDownloadController extends BatchDownloadController {
    constructor(cartPath, datasetType, assembly, isFileViewActive, cartQuery) {
        // Just need to reorder the parameters so `preBuildDownloadOptions` can access the
        // parameters beyond `dataset` and `query`.
        super(null, cartQuery, cartPath, datasetType, assembly, isFileViewActive);
    }

    preBuildDownloadOptions(dataset, query, cartPath, datasetType, assembly, isFileViewActive) {
        this._cartPath = cartPath;
        this._datasetType = datasetType;
        this._assembly = assembly || '';
        this._isFileViewActive = isFileViewActive;
        this._downloadOptionsTemplate = isFileViewActive ? fileViewTemplate : defaultFileTemplate;
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
        if (this._assembly) {
            query.addKeyValue('files.assembly', this._assembly);
        }
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
     * Format the processed-file download query string, overriding the base class's version.
     */
    formatProcessedQuery() {
        const query = this.buildBasicQuery();
        this.addAssembliesToQuery(query);
        query.addKeyValue('files.processed', 'true');
        this._processedQueryString = query.format();
    }

    /**
     * Build all the query strings based on the cart and query object, overriding the base class's
     * version.
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

        // Add the entire options menu. Annotations only have one or two items, while experiments
        // and FCCs have the whole set.
        this._downloadOptions = [];
        if (this._isFileViewActive) {
            this._downloadOptions = [
                {
                    ...this._downloadOptionsTemplate[this._downloadOptionsTemplateIndex['processed-files']],
                    query: this._processedQueryString,
                },
            ];
        } else {
            this._downloadOptions.push(
                {
                    ...this._downloadOptionsTemplate[this._downloadOptionsTemplateIndex['default-files']],
                    query: this._defaultFileQueryString,
                }
            );
        }

        // Build the index of all of all the download options.
        this._downloadOptionsIndex = buildDownloadOptionsIndex(this._downloadOptions);
    }
}
