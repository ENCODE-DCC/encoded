/**
 * Pager controls for each tab.
 */
/** Number of dataset elements to display per page */
export const PAGE_ELEMENT_COUNT = 25;
/** Number of genome-browser tracks to display per page */
export const PAGE_TRACK_COUNT = 20;
/** Number of files to display per page */
export const PAGE_FILE_COUNT = 25;
/** Number of datasets to display at a time in series manager modal */
export const SERIES_MANAGER_DATASET_COUNT = 6;


/**
 * Series types that don't allow their related datasets to be removed from the cart independently
 * of the series.
 */
export const obligateSeriesTypes = ['SingleCellRnaSeries', 'FunctionalCharacterizationSeries'];
