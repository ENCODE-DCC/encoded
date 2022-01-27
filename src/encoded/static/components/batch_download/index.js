import { BatchDownloadActuator, DefaultBatchDownloadContent } from './base';

/**
 * When you add new batch-download controllers, import them as defaults from their respective
 * files, and export them in the "Batch-download controllers" section of the export list.
 */
import AnalysisBatchDownloadController from './analysis';
import CartBatchDownloadController from './cart';
import CartStaticBatchDownloadController from './cart_static';
import DatasetBatchDownloadController from './dataset';
import RawSequencingBatchDownloadController from './raw_sequencing';
import ReferenceBatchDownloadController from './reference';
import SearchBatchDownloadController from './search';
import ElementsReferencesDownloadController from './elementsReferences';

export {
    // Common batch-download components
    BatchDownloadActuator,
    DefaultBatchDownloadContent,

    // Batch-download controllers
    AnalysisBatchDownloadController,
    CartBatchDownloadController,
    CartStaticBatchDownloadController,
    DatasetBatchDownloadController,
    RawSequencingBatchDownloadController,
    ReferenceBatchDownloadController,
    SearchBatchDownloadController,
    ElementsReferencesDownloadController,
};
