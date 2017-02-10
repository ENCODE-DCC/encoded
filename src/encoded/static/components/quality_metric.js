import React from 'react';
import _ from 'underscore';
import { AttachmentPanel } from './doc';
import globals from './globals';


// For each type of quality metric, make a list of attachment properties. If the quality_metric object has an attachment
// property called `attachment`, it doesn't need to be added here -- this is only for attachment properties with arbitrary names.
// Each property in the list has an associated human-readable description for display on the page.
const qcAttachmentProperties = {
    IDRQualityMetric: [
        { IDR_plot_true: 'IDR dispersion plot for true replicates' },
        { IDR_plot_rep1_pr: 'IDR dispersion plot for replicate 1 pseudo-replicates' },
        { IDR_plot_rep2_pr: 'IDR dispersion plot for replicate 2 pseudo-replicates' },
        { IDR_plot_pool_pr: 'IDR dispersion plot for pool pseudo-replicates' },
        { IDR_parameters_true: 'IDR run parameters for true replicates' },
        { IDR_parameters_rep1_pr: 'IDR run parameters for replicate 1 pseudo-replicates' },
        { IDR_parameters_rep2_pr: 'IDR run parameters for replicate 2 pseudo-replicates' },
        { IDR_parameters_pool_pr: 'IDR run parameters for pool pseudo-replicates' },
    ],
    ChipSeqFilterQualityMetric: [
        { cross_correlation_plot: 'Cross-correlation plot' },
    ],
};


// List of quality metric properties to not display
const qcReservedProperties = ['uuid', 'assay_term_name', 'assay_term_id', 'attachment', 'award', 'lab', 'submitted_by', 'level', 'status', 'date_created', 'step_run', 'schema_version'];


// Display QC metrics of the selected QC sub-node in a file node.
export function qcModalContent(qc, file) {
    let qcPanels = []; // Each QC metric panel to display
    let filesOfMetric = []; // Array of accessions of files that share this metric

    // Make an array of the accessions of files that share this quality metrics object.
    // quality_metric_of is an array of @ids because they're not embedded, and we're trying
    // to avoid embedding where not absolutely needed. So use a regex to extract the files'
    // accessions from the @ids. After generating the array, filter out empty entries.
    if (qc.quality_metric_of && qc.quality_metric_of.length) {
        filesOfMetric = qc.quality_metric_of.map((metricId) => {
            // Extract the file's accession from the @id
            const match = globals.atIdToAccession(metricId);

            // Return matches that *don't* match the file whose QC node we've clicked
            if (match && (match[1] !== file.title)) {
                return match[1];
            }
            return '';
        }).filter(acc => !!acc);
    }

    // Filter out QC metrics properties not to display based on the qcReservedProperties list, as well as those properties with keys
    // beginning with '@'. Sort the list of property keys as well.
    const sortedKeys = Object.keys(qc).filter(key => key[0] !== '@' && qcReservedProperties.indexOf(key) === -1).sort();

    // Get the list of attachment properties for the given qc object @type. and generate the JSX for their display panels.
    // The list of keys for attachment properties to display comes from qcAttachmentProperties. Use the @type for the attachment
    // property as a key to retrieve the list of properties appropriate for that QC type.
    const qcAttachmentPropertyList = qcAttachmentProperties[qc['@type'][0]];
    if (qcAttachmentPropertyList) {
        qcPanels = _(qcAttachmentPropertyList.map((attachmentPropertyInfo) => {
            // Each object in the list has only one key (the metric attachment property name), so get it here.
            const attachmentPropertyName = Object.keys(attachmentPropertyInfo)[0];
            const attachment = qc[attachmentPropertyName];

            // Generate the JSX for the panel. Use the property name as the key to get the corresponding human-readable description for the title
            if (attachment) {
                return (
                    <AttachmentPanel
                        context={qc}
                        attachment={qc[attachmentPropertyName]}
                        title={attachmentPropertyInfo[attachmentPropertyName]}
                        modal
                    />
                );
            }
            return null;
        })).compact();
    }

    // Convert the QC metric object @id to a displayable string
    let qcName = qc['@id'].match(/^\/([a-z0-9-]*)\/.*$/i);
    if (qcName && qcName[1]) {
        qcName = qcName[1].replace(/-/g, ' ');
        qcName = qcName[0].toUpperCase() + qcName.substring(1);
    }

    const header = (
        <div className="details-view-info">
            <h4>{qcName} of {file.title}</h4>
            {filesOfMetric.length ? <h5>Shared with {filesOfMetric.join(', ')}</h5> : null}
        </div>
    );
    const body = (
        <div>
            <div className="row">
                <div className="col-md-4 col-sm-6 col-xs-12">
                    <dl className="key-value">
                        {sortedKeys.map(key =>
                            ((typeof qc[key] === 'string' || typeof qc[key] === 'number') ?
                                <div data-test={key} key={key}>
                                    <dt>{key}</dt>
                                    <dd>{qc[key]}</dd>
                                </div>
                            : null)
                        )}
                    </dl>
                </div>

                {(qcPanels && qcPanels.length) || qc.attachment ?
                    <div className="col-md-8 col-sm-12 quality-metrics-attachments">
                        <div className="row">
                            <h5>Quality metric attachments</h5>
                            <div className="flexrow attachment-panel-inner">
                                {/* If the metrics object has an `attachment` property, display that first, then display the properties
                                    not named `attachment` but which have their own schema attribute, `attachment`, set to true */}
                                {qc.attachment ?
                                    <AttachmentPanel context={qc} attachment={qc.attachment} title="Attachment" modal />
                                : null}
                                {qcPanels}
                            </div>
                        </div>
                    </div>
                : null}
            </div>
        </div>
    );
    return { header: header, body: body };
}
