import BatchDownloadController, { buildDownloadOptionsIndex } from './base';


/**
 * Batch-download controller for downloads in individual sections within a file table of the file
 * gallery. It only offers one download options.
 * @param {object} dataset Contains dataset with files to download
 * @param {object} query QueryString of currently selected file facet terms
 */
export default class ElementsReferencesDownloadController extends BatchDownloadController {
    preBuildDownloadOptions(dataset, query) {
        this._elementsReferences = dataset.elements_references;
        this._query = query;
        this._downloadOptionsTemplate = [
            {
                id: 'elements-references',
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
        this._query.addKeyValue('type', 'Reference');
        this._elementsReferences?.forEach((elementsReference) => {
            this._query.addKeyValue('@id', elementsReference['@id']);
        });

        this._referenceFileQueryString = this._query.format();
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
                ...this._downloadOptionsTemplate[this._downloadOptionsTemplateIndex['elements-references']],
                query: this._referenceFileQueryString,
            },
        ];

        // Build the index of this class's custom download options.
        this._downloadOptionsIndex = buildDownloadOptionsIndex(this._downloadOptions);
    }
}
