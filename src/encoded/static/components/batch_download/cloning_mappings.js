// libs
import QueryString from '../../libs/query_string';
import { uc } from '../../libs/constants';
// local
import BatchDownloadController, { buildDownloadOptionsIndex } from './base';


/**
 * Batch-download controller for downloads in individual `elements_cloning` and `elements_mappings`
 * file tables.
 * @param {object} dataset `elements_cloning` or `elements_mappings` dataset with files to download
 */
export default class CloningMappingsBatchDownloadController extends BatchDownloadController {
    constructor(dataset) {
        // Just need to reorder the parameters so `preBuildDownloadOptions` can access the
        // parameters beyond `dataset` and `query`.
        super(dataset, new QueryString());
    }

    preBuildDownloadOptions(dataset) {
        this._hasAnalyses = !!(dataset.analyses?.length > 0);
        this._downloadOptionsTemplate = [
            {
                id: 'all-files',
                label: 'Download files',
                title: `All experiment${this._hasAnalyses ? `${uc.rsquo}s analyses` : ''} files`,
                description: `Downloads all files within the experiment${this._hasAnalyses ? `${uc.rsquo}s analyses` : ''}.`,
                query: '',
            },
        ];
        this._downloadOptionsTemplateIndex = buildDownloadOptionsIndex(this._downloadOptionsTemplate);
    }

    /**
     * Format the all-file download query string.
     */
    formatAllFileQuery() {
        const query = this.buildBasicQuery();
        if (this._hasAnalyses) {
            this._dataset.analyses.forEach((analysis) => {
                query.addKeyValue('analyses.@id', analysis['@id']);
            });
        }
        this._allFileQueryString = query.format();
    }

    /**
     * Overrides the base class's method to build all applicable query strings.
     */
    buildQueryStrings() {
        this.formatAllFileQuery();
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
                ...this._downloadOptionsTemplate[this._downloadOptionsTemplateIndex['all-files']],
                query: this._allFileQueryString,
            },
        ];

        // Build the index of this class's custom download options.
        this._downloadOptionsIndex = buildDownloadOptionsIndex(this._downloadOptions);
    }
}
