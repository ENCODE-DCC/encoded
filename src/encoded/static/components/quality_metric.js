import React from 'react';
import PropTypes from 'prop-types';
import _ from 'underscore';
import { Modal, ModalHeader, ModalBody, ModalFooter } from '../libs/ui/modal';
import { Panel, PanelHeading, PanelBody } from '../libs/ui/panel';
import { collapseIcon } from '../libs/svg-icons';
import { AttachmentPanel } from './doc';
import { FetchedData, Param } from './fetched';
import * as globals from './globals';


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
    ChipAlignmentEnrichmentQualityMetric: [
        { cross_correlation_plot: 'Cross-correlation plot' },
        { jsd_plot: 'Jensen-Shannon distance plot' },
        { gc_bias_plot: 'GC bias plot' },
    ],
    ChipReplicationQualityMetric: [
        { IDR_dispersion_plot: 'IDR dispersion plot' },
    ],
    AtacAlignmentEnrichmentQualityMetric: [
        { cross_correlation_plot: 'Cross-correlation plot' },
        { jsd_plot: 'Jensen-Shannon distance plot' },
        { gc_bias_plot: 'GC bias plot' },
        { tss_enrichment_plot: 'TSS enrichment plot' },
    ],
    AtacLibraryQualityMetric: [
        { fragment_length_distribution_plot: 'Fragment length distribution plot' },
    ],
    AtacPeakEnrichmentQualityMetric: [
        { peak_width_distribution_plot: 'Peak width distribution plot' },
    ],
    AtacReplicationQualityMetric: [
        { idr_dispersion_plot: 'IDR dispersion plot' },
    ],
    GembsAlignmentQualityMetric: [
        { mapq_plot: 'MAPQ plot' },
        { insert_size_plot: 'Insert size plot' },
    ],
    DnaseFootprintingQualityMetric: [
        { dispersion_model: 'Dispersion model' },
    ],
    DnaseAlignmentQualityMetric: [
        { insert_size_histogram: 'Insert size histogram' },
        { insert_size_metric: 'Insert size metric file' },
        { nuclear_preseq: 'Total read metric file' },
        { nuclear_preseq_targets: 'Sequencing depths file' },
    ],
    ScAtacAlignmentQualityMetric: [
        { mito_stats: 'Mitochondrial read statistics' },
        { samstats: 'SAMstats QC' },
    ],
    ScAtacReadQualityMetric: [
        { barcode_matching_stats: 'Barcode matching QC' },
        { adapter_trimming_stats: 'Adapter trimming QC' },
        { barcode_revcomp_stats: 'Barcode reverse complement detection QC' },
    ],
    ScAtacMultipletQualityMetric: [
        { multiplet_stats: 'Multiplet detection statistics file' },
        { barcodes_status: 'Per-barcode multiplet status' },
        { barcode_pairs_multiplets: 'Multiplet barcode pair statistics' },
        { barcode_pairs_expanded: 'Total barcode pair statistics' },
        { multiplet_threshold_plot: 'Plot illustrating multiplet Jaccard distance threshold' },
    ],
    ScAtacLibraryComplexityQualityMetric: [
        { picard_markdup_stats: 'Picard MarkDup statistics' },
        { pbc_stats: 'PBC statistics' },
    ],
    ScAtacAnalysisQualityMetric: [
        { archr_doublet_summary_figure: 'ArchR doublet summary' },
        { archr_fragment_size_distribution: 'ArchR fragment size distribution' },
        { archr_tss_by_unique_frags: 'ArchR TSS-by-fragment plot' },
        { archr_doublet_summary_text: 'ArchR doublet data' },
        { archr_pre_filter_metadata: 'ArchR pre-filter metadata' },
    ],
    StarSoloQualityMetric: [
        { barcode_rank_plot: 'Barcode rank plot' },
        { sequencing_saturation_plot: 'Sequencing saturation plot' },
    ],
    ScrnaSeqCountsSummaryQualityMetric: [
        { total_counts_vs_pct_mitochondria: 'Total counts vs pct mitochondria' },
        { total_counts_vs_genes_by_count: 'Total counts vs genes by count' },
        { counts_violin_plot: 'Counts violin plot' },
    ],
    SegwayQualityMetric: [
        { trackname_assay: 'Trackname assay' },
        { feature_aggregation_tab: 'Feature aggregation tab' },
        { signal_distribution_tab: 'Signal distribution tab' },
        { segment_sizes_tab: 'Segment sizes tab' },
        { length_distribution_tab: 'Length distribution tab' },
    ],
};


// Display QC metrics of the selected QC sub-node in a file node.
function qcModalContent(qc, file, qcSchema, genericQCSchema) {
    let qcPanels = []; // Each QC metric panel to display
    let filesOfMetric = []; // Array of accessions of files that share this metric

    // Make an array of the accessions of files that share this quality metrics object.
    // quality_metric_of is an array of @ids because they're not embedded, and we're trying
    // to avoid embedding where not absolutely needed. So use a regex to extract the files'
    // accessions from the @ids. After generating the array, filter out empty entries.
    if (qc.quality_metric_of && qc.quality_metric_of.length > 0) {
        filesOfMetric = qc.quality_metric_of.map((metricId) => {
            // Extract the file's accession from the @id
            const match = globals.atIdToAccession(metricId);

            // Return matches that *don't* match the file whose QC node we've clicked
            if (match !== file.title) {
                return match;
            }
            return '';
        }).filter((acc) => !!acc);
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
        <div className="graph-modal-header__content">
            <h2>{qcName} of {file.title}</h2>
            {filesOfMetric.length > 0 ? <h5>Shared with {filesOfMetric.join(', ')}</h5> : null}
        </div>
    );
    const body = (
        <div className="quality-metrics-modal">
            <QCDataDisplay qcMetric={qc} qcSchema={qcSchema} genericQCSchema={genericQCSchema} />
            {(qcPanels && qcPanels.length > 0) || qc.attachment ?
                <div className="quality-metrics-modal__attachments">
                    <h5>Quality metric attachments</h5>
                    <div className="attachment-list">
                        {/* If the metrics object has an `attachment` property, display that first, then display the properties
                            not named `attachment` but which have their own schema attribute, `attachment`, set to true */}
                        {qc.attachment ?
                            <AttachmentPanel context={qc} attachment={qc.attachment} title="Attachment" modal />
                        : null}
                        {qcPanels}
                    </div>
                </div>
            : null}
        </div>
    );
    return { header, body };
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
const QualityMetricsModal = (props) => {
    const { qc, file, qcSchema, genericQCSchema } = props;
    const meta = qcModalContent(qc, file, qcSchema, genericQCSchema);

    /* eslint-disable jsx-a11y/anchor-is-valid */
    return (
        <Modal
            actuator={
                <button type="button" className="btn btn-info qc-individual-panel__modal-actuator" title="View data and attachments for this quality metric">
                    <i className="icon icon-info-circle" />
                </button>
            }
        >
            <ModalHeader closeModal addCss="graph-modal-quality-metric">
                {meta ? meta.header : null}
            </ModalHeader>
            <ModalBody>
                {meta ? meta.body : null}
            </ModalBody>
            <ModalFooter closeModal={<a className="btn btn-info btn-sm">Close</a>} />
        </Modal>
    );
    /* eslint-enable jsx-a11y/anchor-is-valid */
};

QualityMetricsModal.propTypes = {
    qc: PropTypes.object.isRequired, // QC object we're displaying
    file: PropTypes.object.isRequired, // File this QC object belongs to
    qcSchema: PropTypes.object.isRequired, // Schema specifically for the given qc object
    genericQCSchema: PropTypes.object.isRequired, // Generic quality metrics schema
};


// Top-level component to display the panel containing QC metrics panels. It initiates the GET
// request to retrieve the system-wide schemas so that we can extract the QC property titles
// from it, then renders the resulting QC panel.
export const QualityMetricsPanel = (props) => (
    <FetchedData>
        <Param name="schemas" url="/profiles/" />
        <QualityMetricsPanelRenderer qcMetrics={props.qcMetrics} file={props.file} />
    </FetchedData>
);

QualityMetricsPanel.propTypes = {
    qcMetrics: PropTypes.array.isRequired, // Array of quality metrics objects to display
    file: PropTypes.object.isRequired, // File whose QC objects are being displayed
};


// Draw the collapse trigger at the bottom of the QC panel
class ExpandTrigger extends React.Component {
    constructor() {
        super();

        // Bind this to non-React methods.
        this.handleClick = this.handleClick.bind(this);
    }

    // Handle a click anywhere in the trigger button.
    handleClick() {
        this.props.clickHandler();
    }

    render() {
        const { expanded, id } = this.props;
        return (
            <button type="button" className="qc-individual-panel__expand-trigger" onClick={this.handleClick} aria-controls={id} title={expanded ? 'Collapse this panel to a smaller size' : 'Expand this panel to show all data'}>
                {collapseIcon(!expanded)}
            </button>
        );
    }
}

ExpandTrigger.propTypes = {
    expanded: PropTypes.bool.isRequired, // True if the panel this trigger controls is expanded
    clickHandler: PropTypes.func.isRequired, // Function to call to handle a click in the trigger
    id: PropTypes.string.isRequired, // ID of the panel this trigger controls
};


/** Renderable schema property types */
const renderableSchemaTypes = ['number', 'string', 'integer', 'boolean'];
/** Javascript types for QC properties we can render */
const renderableTypes = ['number', 'string', 'boolean'];

/**
 * Determine whether a QC metric property can be rendered or not. This function isn't intended to
 * be used outside this module, but it gets exported for Jest testing.
 * @param {string} propName Name of the QC property we're evaluating for rendering
 * @param {object} qcMetric QC metric being rendered
 * @param {object} qcSchema Schema for this QC metric object
 *
 * @return {bool} True if QC metric property can be rendered
 */
export const isRenderableProp = (propName, qcMetric, qcSchema) => {
    // The type of the QC property must be renderable before anything else.
    if (renderableTypes.indexOf(typeof qcMetric[propName]) !== -1) {
        const schemaProperty = qcSchema.properties[propName];
        if (typeof schemaProperty.type === 'object' && Array.isArray(schemaProperty.type) && schemaProperty.type.length > 0) {
            // Schema has more than one possible type for this property. Determine if we can
            // render any of them.
            return schemaProperty.type.some((schemaPropType) => (
                renderableSchemaTypes.indexOf(schemaPropType) !== -1
            ));
        }

        // Schema specifies only type type for this property. Determine if we can render it.
        return renderableSchemaTypes.indexOf(schemaProperty.type) !== -1;
    }
    return false;
};


// Display the data for a QC object as a <dl>
const QCDataDisplay = (props) => {
    const { qcMetric, qcSchema, genericQCSchema } = props;

    // Make a list of QC metric object keys to display. Filter to only display strings and
    // numbers -- not objects which are usually attachments that we only display in the modals.
    // Also filter out anything in the generic QC schema, as those properties (@id, uuid, etc.)
    // aren't interesting for the QC panel.
    // Key order will stay the same as how they are defined in schema
    const categories = {};
    Object.keys(qcSchema.properties).forEach((prop) => {
        if (
            genericQCSchema.properties[prop]
            || !isRenderableProp(prop, qcMetric, qcSchema)
        ) {
            return;
        }
        const category = qcSchema.properties[prop].category || 'unknown';
        if (!categories[category]) {
            categories[category] = [];
        }
        categories[category].push(prop);
    });

    return (
        <div className="quality-metrics-modal__data">
            <dl className="key-value">
                {Object.keys(categories).map((category, i) => (
                    <div key={category}>
                        {category !== 'unknown' ?
                            <h4>{category}</h4>
                        : null}
                        {categories[category].map((key) => (
                            <div key={key} data-test={key}>
                                <dt className="sentence-case">{qcSchema.properties[key].title}</dt>
                                <dd>{typeof qcMetric[key] === 'boolean' ? qcMetric[key].toString() : qcMetric[key]}</dd>
                            </div>
                        ))}
                        {i !== Object.keys(categories).length - 1 ? <hr /> : null}
                    </div>
                ))}
            </dl>
        </div>
    );
};

QCDataDisplay.propTypes = {
    qcMetric: PropTypes.object, // QC metric object whose data we're displaying here
    qcSchema: PropTypes.object.isRequired, // Schema that applies to the given qcMetric object
    genericQCSchema: PropTypes.object.isRequired, // Generic quality metric schema
};

QCDataDisplay.defaultProps = {
    qcMetric: null,
};


// Render a panel for an individual quality metric object.
class QCIndividualPanel extends React.Component {
    constructor() {
        super();

        // Set initial React state.
        this.state = {
            expanded: false, // True if panel is collapsed to its smaller size
            triggerVisible: true, // `true` if ExpandTrigger should be visible; `false` if data too short for ExpandTrigger to be needed
        };

        // Bind this to non-React methods.
        this.expandClick = this.expandClick.bind(this);
    }

    componentDidMount() {
        // If the body of the panel is shorter than the collapsed height of the panel, we don't
        // need the trigger.
        if (this.qcHeading && this.qcBody && (this.qcHeading.clientHeight + this.qcBody.clientHeight <= collapsedHeight)) {
            this.setState({ triggerVisible: false });
        }
    }

    expandClick() {
        // Toggle the expanded state of the QC panel in response to a click in ExpandTrigger.
        this.setState((prevState) => ({
            expanded: !prevState.expanded,
        }));
    }

    render() {
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
    }
}

QCIndividualPanel.propTypes = {
    qcMetric: PropTypes.object.isRequired, // QC metric object whose properties we're displaying
    qcSchema: PropTypes.object.isRequired, // Schema that applies to the given qcMetric object
    genericQCSchema: PropTypes.object.isRequired, // Generic quality metric schema
    file: PropTypes.object.isRequired, // File whose QC object is being displayed
};


// Display a panel of an array of quality metrics objects.
const QualityMetricsPanelRenderer = (props) => {
    const { qcMetrics, schemas, file } = props;

    // Extract the GenericQualityMetric schema. We don't display properties that exist in this
    // schema because they're generic properties, not interesting QC properties.
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
};

QualityMetricsPanelRenderer.propTypes = {
    qcMetrics: PropTypes.array.isRequired, // Array of quality metrics objects to display
    file: PropTypes.object.isRequired, // File whose QC objects we're displaying
    schemas: PropTypes.object, // All schemas in the system keyed by @type; used to get QC titles
};

QualityMetricsPanelRenderer.defaultProps = {
    schemas: null,
};


// Display the metadata of the selected file in the graph
const QCDetailView = function QCDetailView(node) {
    // The node is for a file
    const selectedQc = node.ref;
    let modalContent = {};

    if (selectedQc && Object.keys(selectedQc).length > 0) {
        const { schemas } = node;
        const genericQCSchema = schemas.GenericQualityMetric;
        const qcSchema = schemas[selectedQc['@type'][0]];
        modalContent = qcModalContent(selectedQc, node.parent, qcSchema, genericQCSchema);
        modalContent.type = 'QualityMetric';
    }

    return modalContent;
};

globals.graphDetail.register(QCDetailView, 'QualityMetric');
