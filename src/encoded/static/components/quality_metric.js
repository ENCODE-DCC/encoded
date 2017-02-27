import React from 'react';
import _ from 'underscore';
import { Modal, ModalHeader, ModalBody, ModalFooter } from '../libs/bootstrap/modal';
import { Panel, PanelHeading, PanelBody } from '../libs/bootstrap/panel';
import { collapseIcon } from '../libs/svg-icons';
import { AttachmentPanel } from './doc';
import { FetchedData, Param } from './fetched';
import globals from './globals';


const collapsedHeight = 200; // Match collapsed-height from _quality_metrics.scss


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


// Display QC metrics of the selected QC sub-node in a file node.
export function qcModalContent(qc, file, qcSchema, genericQCSchema) {
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
            if (match !== file.title) {
                return match;
            }
            return '';
        }).filter(acc => !!acc);
    }

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
                        key={attachmentPropertyName}
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
                    <QCDataDisplay qcMetric={qc} qcSchema={qcSchema} genericQCSchema={genericQCSchema} />
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


// Extract a displayable string from a QualityMetric object passed in the `qc` parameter.
export function qcIdToDisplay(qc) {
    let qcName = qc['@id'].match(/^\/([a-z0-9-]*)\/.*$/i);
    if (qcName && qcName[1]) {
        qcName = qcName[1].replace(/-/g, ' ');
        qcName = qcName[0].toUpperCase() + qcName.substring(1);
        return qcName;
    }
    return '';
}


// The modal and actuator for the quality metrics modal.
const QualityMetricsModal = React.createClass({
    propTypes: {
        qc: React.PropTypes.object, // QC object we're displaying
        file: React.PropTypes.object, // File this QC object belongs to
        qcSchema: React.PropTypes.object, // Schema specifically for the given qc object
        genericQCSchema: React.PropTypes.object, // Generic quality metrics schema
    },

    render: function () {
        const { qc, file, qcSchema, genericQCSchema } = this.props;
        const meta = qcModalContent(qc, file, qcSchema, genericQCSchema);

        return (
            <Modal actuator={<button className="btn btn-info qc-individual-panel__modal-actuator" title="View data and attachments for this quality metric"><i className="icon icon-info-circle" /></button>}>
                <ModalHeader closeModal addCss="graph-modal-quality-metric">
                    {meta ? meta.header : null}
                </ModalHeader>
                <ModalBody>
                    {meta ? meta.body : null}
                </ModalBody>
                <ModalFooter closeModal={<a className="btn btn-info btn-sm">Close</a>} />
            </Modal>
        );
    },
});


// Top-level component to display the panel containing QC metrics panels. It initiates the GET
// request to retrieve the system-wide schemas so that we can extract the QC property titles
// from it, then renders the resulting QC panel.
export const QualityMetricsPanel = React.createClass({
    propTypes: {
        qcMetrics: React.PropTypes.array.isRequired, // Array of quality metrics objects to display
        file: React.PropTypes.object.isRequired, // File whose QC objects are being displayed
    },

    render: function () {
        return (
            <FetchedData>
                <Param name="schemas" url="/profiles/" />
                <QualityMetricsPanelRenderer qcMetrics={this.props.qcMetrics} file={this.props.file} />
            </FetchedData>
        );
    },
});


// Draw the collapse trigger at the bottom of the QC panel
const ExpandTrigger = React.createClass({
    propTypes: {
        expanded: React.PropTypes.bool.isRequired, // True if the panel this trigger controls is expanded
        clickHandler: React.PropTypes.func.isRequired, // Function to call to handle a click in the trigger
        id: React.PropTypes.string.isRequired, // ID of the panel this trigger controls
    },

    // Handle a click anywhere in the trigger button.
    handleClick: function () {
        this.props.clickHandler();
    },

    render: function () {
        const { expanded, id } = this.props;
        return (
            <button className="qc-individual-panel__expand-trigger" onClick={this.handleClick} aria-controls={id} title={expanded ? 'Collapse this panel to a smaller size' : 'Expand this panel to show all data'}>
                {collapseIcon(!expanded)}
            </button>
        );
    },
});


// Display the data for a QC object as a <dl>
const QCDataDisplay = React.createClass({
    propTypes: {
        qcMetric: React.PropTypes.object, // QC metric object whose data we're displaying here
        qcSchema: React.PropTypes.object.isRequired, // Schema that applies to the given qcMetric object
        genericQCSchema: React.PropTypes.object.isRequired, // Generic quality metric schema
    },

    render: function () {
        const { qcMetric, qcSchema, genericQCSchema } = this.props;

        // Make a list of QC metric object keys to display. Filter to only display strings and
        // numbers -- not objects which are usually attachments that we only display in the modals.
        // Also filter out anything in the generic QC schema, as those properties (@id, uuid, etc.)
        // aren't interesting for the QC panel. Also sort the keys case insensitively.
        const displayKeys = Object.keys(qcMetric).filter((key) => {
            const schemaProperty = qcSchema.properties[key];
            return !genericQCSchema.properties[key] && (schemaProperty.type === 'number' || schemaProperty.type === 'string');
        }).sort((a, b) => {
            const aUp = a.toUpperCase();
            const bUp = b.toUpperCase();
            return aUp < bUp ? -1 : (aUp > bUp ? 1 : 0);
        });

        return (
            <dl className="key-value">
                {displayKeys.map(key =>
                    <div key={key} data-test={key}>
                        <dt className="sentence-case">{qcSchema.properties[key].title}</dt>
                        <dd>{qcMetric[key]}</dd>
                    </div>
                )}
            </dl>
        );
    },
});


// Render a panel for an individual quality metric object.
const QCIndividualPanel = React.createClass({
    propTypes: {
        qcMetric: React.PropTypes.object.isRequired, // QC metric object whose properties we're displaying
        qcSchema: React.PropTypes.object.isRequired, // Schema that applies to the given qcMetric object
        genericQCSchema: React.PropTypes.object.isRequired, // Generic quality metric schema
        file: React.PropTypes.object.isRequired, // FIle whose QC object is being displayed
    },

    getInitialState: function () {
        return {
            expanded: false, // True if panel is collapsed to its smaller size
            triggerVisible: true, // `true` if ExpandTrigger should be visible; `false` if data too short for ExpandTrigger to be needed
        };
    },

    componentDidMount: function () {
        // If the body of the panel is shorter than the collapsed height of the panel, we don't
        // need the trigger.
        if (this.qcHeading && this.qcBody && (this.qcHeading.clientHeight + this.qcBody.clientHeight <= collapsedHeight)) {
            this.setState({ triggerVisible: false });
        }
    },

    expandClick: function () {
        // Toggle the expanded state of the QC panel in response to a click in ExpandTrigger.
        this.setState({ expanded: !this.state.expanded });
    },

    render: function () {
        const { qcMetric, qcSchema, genericQCSchema, file } = this.props;

        // Calculate the classes for the individual panel.
        const panelClasses = `qc-individual-panel${this.state.expanded ? ' expanded' : ''}`;

        // Got a matching schema, so render it with full titles.
        return (
            <div className="qc-individual-panel__wrapper">
                <Panel id={qcMetric.uuid} addClasses={panelClasses} aria-expanded={this.state.expanded} aria-labelledby={`${qcMetric.uuid}-label`}>
                    <PanelHeading addClasses="qc-individual-panel__heading">
                        <div className="qc-individual-panel__heading-inner" ref={(comp) => { this.qcHeading = comp; }}>
                            <h4 id={`${qcMetric.uuid}-label`} className="qc-individual-panel__title">{qcIdToDisplay(qcMetric)}</h4>
                            <QualityMetricsModal qc={qcMetric} file={file} qcSchema={qcSchema} genericQCSchema={genericQCSchema} />
                        </div>
                    </PanelHeading>
                    <PanelBody>
                        <div ref={(comp) => { this.qcBody = comp; }}>
                            <QCDataDisplay qcMetric={qcMetric} qcSchema={qcSchema} genericQCSchema={genericQCSchema} />
                        </div>
                    </PanelBody>
                    {this.state.triggerVisible ?
                        <ExpandTrigger expanded={this.state.expanded} clickHandler={this.expandClick} id={qcMetric.uuid} />
                    : null}
                </Panel>
            </div>
        );
    },
});


// Display a panel of an array of quality metrics objects.
const QualityMetricsPanelRenderer = React.createClass({
    propTypes: {
        qcMetrics: React.PropTypes.array.isRequired, // Array of quality metrics objects to display
        file: React.PropTypes.object.isRequired, // File whose QC objects we're displaying
        schemas: React.PropTypes.object, // All schemas in the system keyed by @type; used to get QC titles
    },

    getDefaultProps: function () {
        return {
            schemas: null,
        };
    },

    render: function () {
        const { qcMetrics, schemas, file } = this.props;

        // Extract the GenericQualityMetric schema. We don't display properties that exist in this
        // schema because they're generic properties, not interesting QC proeprties.
        const genericQCSchema = schemas.GenericQualityMetric;
        if (!genericQCSchema) {
            // Not having this schema would be very weird, but just in case...
            return null;
        }

        return (
            <Panel>
                <PanelHeading>
                    <h4>Quality metrics</h4>
                </PanelHeading>
                <PanelBody addClasses="qc-panel">
                    {qcMetrics.map((qcMetric) => {
                        // Get the schema specific for this quality metric, as identified by the
                        // first @type in this QC metric.
                        const qcSchema = schemas && schemas[qcMetric['@type'][0]];
                        if (qcSchema && qcSchema.properties) {
                            return <QCIndividualPanel key={qcMetric.uuid} qcMetric={qcMetric} qcSchema={qcSchema} genericQCSchema={genericQCSchema} file={file} />;
                        }

                        // Weirdly, no matching schema. Render properties generically.
                        return null;
                    })}
                </PanelBody>
            </Panel>
        );
    },
});
