import React from 'react';
import PropTypes from 'prop-types';
import _ from 'underscore';
import { Panel, PanelHeading, PanelBody, PanelFooter } from '../libs/ui/panel';
import Tooltip from '../libs/ui/tooltip';
import { CartAddAllElements, CartToggle } from './cart';
import { auditDecor, AuditCounts } from './audit';
import { FilePanelHeader } from './dataset';
import { FetchedItems } from './fetched';
import { DatasetFiles } from './filegallery';
import * as globals from './globals';
import { Breadcrumbs } from './navigation';
import { requestObjects, ItemAccessories, InternalTags } from './objectutils';
import { PickerActions, resultItemClass } from './search';
import Status, { getObjectStatuses, sessionToAccessLevel } from './status';


// Only analysis on selected assembly will be used for QC reporting
const selectedAssembly = ['GRCh38', 'mm10'];

/**
 * Giving an experiment, extract one specific quality metric from its files.
 * Extracted quality metrics are grouped by corresponding biological replicate number.
 * For a specific biological replicate, there could be more than one quality metric
 * values extracted. They are all stored uniquely in an array.
 *
 * @return {object} Quality metrics grouped by biological replicate number.
 */
function getQualityMetricsByReplicate(experiment, field) {
    const qualityMetricsByReplicate = {};
    experiment.files.forEach((f) => {
        f.quality_metrics.forEach((qm) => {
            if (qm[field]) {
                f.biological_replicates.forEach((num) => {
                    if (qualityMetricsByReplicate[num]) {
                        qualityMetricsByReplicate[num].push(qm[field]);
                    } else {
                        qualityMetricsByReplicate[num] = [qm[field]];
                    }
                });
            }
        });
    });
    const qmByRep = {};
    Object.keys(qualityMetricsByReplicate).forEach((rep) => {
        qmByRep[rep] = _.uniq(qualityMetricsByReplicate[rep]);
    });
    return qmByRep;
}

// The hideColorCodedColumns is a collection of conditions determine whether
// corresponding columns, which are all color coded, should be hide or not.
// It will be used by experimentTableColumns thus its key should match keys in
// experimentTableColumns. It will also be used to determine whether color
// legend should be shown or not. So this collection should be color coded
// columns only.
const hideColorCodedColumns = {
    readDepth: series => !_.isEqual(series.assay_term_name, ['ChIP-seq']),
    NRF: series => !_.isEqual(series.assay_term_name, ['ChIP-seq']),
    NSC: series => !_.isEqual(series.assay_term_name, ['ChIP-seq']),
    PBC1: series => !_.isEqual(series.assay_term_name, ['ChIP-seq']),
    PBC2: series => !_.isEqual(series.assay_term_name, ['ChIP-seq']),
    IDR: series => !_.isEqual(series.assay_term_name, ['ChIP-seq']) || series.target.some(target => target.investigated_as.includes('histone')),
};

const experimentTableColumns = {
    accession: {
        title: 'Accession',
        display: (experiment, meta) => <td key="accession" rowSpan={meta.rowCount}><a href={experiment['@id']} title={`View page for experiment ${experiment.accession}`}>{experiment.accession}</a></td>,
    },

    file_assembly: {
        title: 'Assembly',
        getValue: experiment => _.uniq(experiment.files.map(f => f.assembly)),
        hide: series => !_.isEqual(series.assay_term_name, ['ChIP-seq']),
    },

    _biological_replicate_number: {
        title: 'Replicate',
        getValue: (experiment, meta) => meta.bioRepNum,
        replicateSpecific: true,
        hide: series => !_.isEqual(series.assay_term_name, ['ChIP-seq']),
    },

    antibody: {
        title: 'Antibody characterization',
        display: (experiment, meta) => {
            const statuses = [];
            experiment.replicates.forEach((rep) => {
                if (rep.biological_replicate_number === meta.bioRepNum && rep.antibody && rep.library && rep.library.biosample) {
                    const lotReviews = rep.antibody.lot_reviews;
                    const organism = rep.library.biosample.organism['@id'];
                    const biosampleTermId = rep.library.biosample.biosample_ontology.term_id;
                    if (experiment.target && experiment.target.investigated_as.includes('histone')) {
                        lotReviews.forEach((rev) => {
                            if (rev.organisms.includes(organism)) {
                                statuses.push(rev.status);
                            }
                        });
                    } else {
                        lotReviews.forEach((rev) => {
                            if (rev.organisms.includes(organism) && rev.biosample_term_id === biosampleTermId) {
                                statuses.push(rev.status);
                            }
                        });
                    }
                }
            });
            if (statuses.length === 0) {
                statuses.push('awaiting characterization');
            }
            return (
                <td key="antibody">
                    {statuses.map((status, i) => <Status key={i} item={status} inline />)}
                </td>
            );
        },
        replicateSpecific: true,
        hide: series => !_.isEqual(series.assay_term_name, ['ChIP-seq']),
    },

    readDepth: {
        title: <div>Read depth<Tooltip trigger={<i className="icon icon-question-circle" />} tooltipId="qc-report-nrf" css="tooltip-home-info">Number of mapped reads passing quality control filtering. Minimum read depth is 5M. For broad histone marks, acceptable read depth is &gt;35M and recommended read depth is &gt;45M. For other targets, acceptable read depth is &gt;10M and recommended read depth is &gt;20M.</Tooltip></div>,
        display: (experiment, meta) => {
            const low = 5000000;
            let minimal = 10000000;
            let recommended = 20000000;
            if (experiment.target && experiment.target.investigated_as.includes('broad histone mark')) {
                minimal = 35000000;
                recommended = 45000000;
            }
            const filteredFiles = experiment.files.filter(f => f.biological_replicates.includes(meta.bioRepNum));
            const qualityMetrics = filteredFiles.map(f => f.quality_metrics).reduce(
                (flatQualityMetrics, qms) => flatQualityMetrics.concat(qms), []
            );
            let qm = [];
            if (experiment.target && ['H3K9me3-human', 'H3K9me3-mouse'].includes(experiment.target.name)) {
                qm = _.uniq(qualityMetrics.filter(q => q.processing_stage === 'unfiltered').map(q => q.mapped / ((q.read1 && q.read2) ? 2 : 1)).filter(q => q));
            } else {
                qm = _.uniq(qualityMetrics.filter(q => q.processing_stage === 'filtered').map(q => q.total / ((q.read1 && q.read2) ? 2 : 1)).filter(q => q));
            }
            if (qm && qm.length > 1) {
                return <td key="readDepth" className="qc-report">?</td>;
            }
            if (qm && qm.length === 1) {
                let qcClass = 'qc-report';
                if (qm[0] < low) {
                    qcClass = qcClass.concat(' qc-report--error');
                } else if (qm[0] >= low && qm[0] < minimal) {
                    qcClass = qcClass.concat(' qc-report--not-compliant');
                } else if (qm[0] >= minimal && qm[0] < recommended) {
                    qcClass = qcClass.concat(' qc-report--warning');
                } else {
                    qcClass = qcClass.concat(' qc-report--ideal');
                }
                return <td key="readDepth" className={qcClass}>{(qm[0] / 1000000).toFixed(2).concat('M')}</td>;
            }
            return <td key="readDepth" className="qc-report" />;
        },
        replicateSpecific: true,
        hide: series => hideColorCodedColumns.readDepth(series),
    },

    NRF: {
        title: <div>NRF<Tooltip trigger={<i className="icon icon-question-circle" />} tooltipId="qc-report-nrf" css="tooltip-home-info">Non-redundant fraction (indicates library complexity). Number of distinct unique mapping reads (i.e. after removing duplicates) / Total number of reads. Acceptable NRF is &gt;0.5 and recommended NRF is &gt;0.8.</Tooltip></div>,
        display: (experiment, meta) => {
            const qm = getQualityMetricsByReplicate(experiment, 'NRF')[meta.bioRepNum];
            if (qm && qm.length > 1) {
                return <td key="NRF" className="qc-report">?</td>;
            }
            if (qm && qm.length === 1) {
                let qcClass = 'qc-report';
                if (qm[0] < 0.5) {
                    qcClass = qcClass.concat(' qc-report--not-compliant');
                } else if (qm[0] >= 0.5 && qm[0] < 0.8) {
                    qcClass = qcClass.concat(' qc-report--warning');
                } else {
                    qcClass = qcClass.concat(' qc-report--ideal');
                }
                return <td key="NRF" className={qcClass}>{qm[0].toFixed(2)}</td>;
            }
            return <td key="NRF" className="qc-report" />;
        },
        replicateSpecific: true,
        hide: series => hideColorCodedColumns.NRF(series),
    },

    NSC: {
        title: <div>NSC<Tooltip trigger={<i className="icon icon-question-circle" />} tooltipId="qc-report-nrf" css="tooltip-home-info">Normalized strand cross-correlation = FRAGLEN_CC / MIN_CC. Ratio of strand cross-correlation at estimated fragment length to the minimum cross-correlation over all shifts. Acceptable NSC is &gt;1.05 and recommended NSC is &gt;1.1.</Tooltip></div>,
        display: (experiment, meta) => {
            const qm = getQualityMetricsByReplicate(experiment, 'NSC')[meta.bioRepNum];
            if (qm && qm.length > 1) {
                return <td key="NSC" className="qc-report">?</td>;
            }
            if (qm && qm.length === 1) {
                let qcClass = 'qc-report';
                if (qm[0] < 1.05) {
                    qcClass = qcClass.concat(' qc-report--not-compliant');
                } else if (qm[0] >= 1.05 && qm[0] < 1.1) {
                    qcClass = qcClass.concat(' qc-report--warning');
                } else {
                    qcClass = qcClass.concat(' qc-report--ideal');
                }
                return <td key="NSC" className={qcClass}>{qm[0].toFixed(2)}</td>;
            }
            return <td key="NSC" className="qc-report" />;
        },
        replicateSpecific: true,
        hide: series => hideColorCodedColumns.NSC(series),
    },

    PBC1: {
        title: <div>PBC1<Tooltip trigger={<i className="icon icon-question-circle" />} tooltipId="qc-report-nrf" css="tooltip-home-info">PCR Bottlenecking coefficient 1 = M1/M_DISTINCT where M1: number of genomic locations where exactly one read maps uniquely, M_DISTINCT: number of distinct genomic locations to which some read maps uniquely. Acceptable PBC1 is &gt;0.5 and recommended PBC1 is &gt;0.9.</Tooltip></div>,
        display: (experiment, meta) => {
            const qm = getQualityMetricsByReplicate(experiment, 'PBC1')[meta.bioRepNum];
            if (qm && qm.length > 1) {
                return <td key="PBC1" className="qc-report">?</td>;
            }
            if (qm && qm.length === 1) {
                let qcClass = 'qc-report';
                if (qm[0] < 0.5) {
                    qcClass = qcClass.concat(' qc-report--not-compliant');
                } else if (qm[0] >= 0.5 && qm[0] < 0.9) {
                    qcClass = qcClass.concat(' qc-report--warning');
                } else {
                    qcClass = qcClass.concat(' qc-report--ideal');
                }
                return <td key="PBC1" className={qcClass}>{qm[0].toFixed(2)}</td>;
            }
            return <td key="PBC1" className="qc-report" />;
        },
        replicateSpecific: true,
        hide: series => hideColorCodedColumns.PBC1(series),
    },

    PBC2: {
        title: <div>PBC2<Tooltip trigger={<i className="icon icon-question-circle" />} tooltipId="qc-report-nrf" css="tooltip-home-info">PCR Bottlenecking coefficient 2 (indicates library complexity) = M1/M2 where M1: number of genomic locations where only one read maps uniquely and M2: number of genomic locations where 2 reads map uniquely. Acceptable PBC2 is &gt;1 and recommended PBC2 &gt;10.</Tooltip></div>,
        display: (experiment, meta) => {
            const qm = getQualityMetricsByReplicate(experiment, 'PBC2')[meta.bioRepNum];
            if (qm && qm.length > 1) {
                return <td key="PBC2" className="qc-report">?</td>;
            }
            if (qm && qm.length === 1) {
                let qcClass = 'qc-report';
                if (qm[0] < 1) {
                    qcClass = qcClass.concat(' qc-report--not-compliant');
                } else if (qm[0] >= 1 && qm[0] < 10) {
                    qcClass = qcClass.concat(' qc-report--warning');
                } else {
                    qcClass = qcClass.concat(' qc-report--ideal');
                }
                return <td key="PBC2" className={qcClass}>{qm[0].toFixed(2)}</td>;
            }
            return <td key="PBC2" className="qc-report" />;
        },
        replicateSpecific: true,
        hide: series => hideColorCodedColumns.PBC2(series),
    },

    IDR: {
        title: <div>IDR<Tooltip trigger={<i className="icon icon-question-circle" />} tooltipId="qc-report-nrf" css="tooltip-home-info">Irreproducible discovery rate is determined by the self-consistency ratio and the rescue ratio. The self-consistency ratio measures consistency within a single dataset. The rescue ratio measures consistency between datasets when the replicates within a single experiment are not comparable. The IDR test fails if both ratios are &lt;2, and passes if both ratios are &gt;2. Otherwise, IDR is borderline.</Tooltip></div>,
        display: (experiment, meta) => {
            const rescueRatios = getQualityMetricsByReplicate(experiment, 'rescue_ratio')[meta.bioRepNum];
            const selfConsistencyRatios = getQualityMetricsByReplicate(experiment, 'self_consistency_ratio')[meta.bioRepNum];
            if ((rescueRatios && rescueRatios.length > 1) || (selfConsistencyRatios && selfConsistencyRatios.length > 1)) {
                return <td key="IDR" className="qc-report" rowSpan={meta.rowCount}>?</td>;
            }
            if ((rescueRatios && rescueRatios.length === 1) && (selfConsistencyRatios && selfConsistencyRatios.length === 1)) {
                if (rescueRatios[0] > 2 && selfConsistencyRatios[0] > 2) {
                    return <td key="IDR" className="qc-report qc-report--not-compliant" rowSpan={meta.rowCount}>Fail</td>;
                } else if (rescueRatios[0] > 2 || selfConsistencyRatios[0] > 2) {
                    return <td key="IDR" className="qc-report qc-report--warning" rowSpan={meta.rowCount}>Borderline</td>;
                }
                return <td key="IDR" className="qc-report qc-report--ideal" rowSpan={meta.rowCount}>Pass</td>;
            }
            return <td key="IDR" className="qc-report" rowSpan={meta.rowCount} />;
        },
        hide: series => hideColorCodedColumns.IDR(series),
    },

    peakCount: {
        title: <div>Replicated Peak count<Tooltip trigger={<i className="icon icon-question-circle" />} tooltipId="qc-report-nrf" css="tooltip-home-info">The replicated peak count reported here is for replicated experiments only. It is the peak count of either optimal IDR thresholded peaks for TF ChIP or replicated peaks for histone ChIP. Please note that higher peak count does NOT necessarily mean higher quality data.</Tooltip></div>,
        getValue: (experiment, meta) => {
            // ENCODE3 TF and histone ChIP-seq quality metrics modeling
            // Skip peakCount if the experiment has less than 1 replicate
            if (!experiment.replicates || experiment.replicates.length <= 1) {
                return '';
            }
            const optimalPeakCounts = getQualityMetricsByReplicate(experiment, 'N_optimal')[meta.bioRepNum] || getQualityMetricsByReplicate(experiment, 'npeak_overlap')[meta.bioRepNum] || [];
            if (optimalPeakCounts.length === 0) {
                // ENCODE4 ChIP-seq quality metrics modeling
                experiment.files.forEach((f) => {
                    if (f.preferred_default && f.biological_replicates.includes(meta.bioRepNum)) {
                        f.quality_metrics.forEach((qm) => {
                            if (qm.reproducible_peaks) {
                                optimalPeakCounts.push(qm.reproducible_peaks);
                            }
                        });
                    }
                });
            }
            if (optimalPeakCounts.length > 1) {
                return '?';
            }
            if (optimalPeakCounts.length === 1) {
                return optimalPeakCounts[0];
            }
            return '';
        },
        hide: series => !_.isEqual(series.assay_term_name, ['ChIP-seq']),
    },

    status: {
        title: 'Status',
        display: (experiment, meta) => <td key="status" rowSpan={meta.rowCount}><Status item={experiment} badgeSize="small" /></td>,
    },

    date_released: {
        title: 'Date released',
    },

    lab: {
        title: 'Lab',
        getValue: experiment => (experiment.lab ? experiment.lab.title : null),
    },

    award: {
        title: 'RFA',
        getValue: experiment => (experiment.award ? experiment.award.rfa : null),
    },

    audit: {
        title: 'Audit status',
        display: (experiment, meta) => <td key="audit" rowSpan={meta.rowCount}><AuditCounts audits={experiment.audit} isAuthorized={meta.isAuthorized} /></td>,
        sorter: false,
    },

    cart: {
        title: 'Cart',
        display: (experiment, meta) => <td key="cart" rowSpan={meta.rowCount}><CartToggle element={experiment} /></td>,
        sorter: false,
    },
};

// Display the color legend for quality metrics.
const QualityMetricLegend = () => (
    <div className="qc-legend">
        <div className="qc-legend-item qc-report qc-report--ideal">Recommended</div>
        <div className="qc-legend-item qc-report qc-report--warning">Sufficient</div>
        <div className="qc-legend-item qc-report qc-report--not-compliant">Insufficient</div>
        <div className="qc-legend-item qc-report qc-report--error">Error</div>
    </div>
);


/**
 * Experiment statuses we can display at the different access levels. Defined separately from how
 * they're defined in status.js because they're slightly differently from datasetStatuses.
 */
const viewableDatasetStatuses = {
    Dataset: {
        external: [
            'released',
            'archived',
        ],
        consortium: [
            'in progress',
            'submitted',
            'revoked',
        ],
        administrator: [
            'deleted',
            'replaced',
        ],
    },
};


/**
 * Component to display experiment series pages.
 */
class ExperimentSeriesComponent extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            /** Audit objects keyed by dataset @id. Datasets w/o audits included with empty object */
            viewableDatasets: {},
        };
        this.statusFilteredDatasets = this.statusFilteredDatasets.bind(this);
        this.getViewableDatasets = this.getViewableDatasets.bind(this);
    }

    componentDidMount() {
        this.getViewableDatasets();
    }

    componentDidUpdate() {
        const datasetAtIds = Object.keys(this.statusFilteredDatasets());
        const updatedDatasetAtIds = Object.keys(this.state.viewableDatasets);
        const symmDiffAtIds = datasetAtIds.filter(
            i => !updatedDatasetAtIds.includes(i)
        ).concat(
            updatedDatasetAtIds.filter(i => !datasetAtIds.includes(i))
        );
        if (symmDiffAtIds.length > 0) {
            this.getViewableDatasets();
        }
    }

    /**
     * Retrieve viewable datasets and set it to the viewableDatasets state.
     * The viewableDatasets is based on context.related_datasets,
     * filtered based on experiment status and added audit and quality metrics.
     */
    getViewableDatasets() {
        const viewableDatasets = this.statusFilteredDatasets();
        // Collect audit and quality metrics information
        const promises = Object.keys(viewableDatasets).map(datasetAtId => (
            fetch(`${datasetAtId}?frame=audit`, {
                method: 'GET',
                headers: {
                    Accept: 'application/json',
                },
            }).then((response) => {
                // Get response JSON
                if (response.ok) {
                    return response.json();
                }
                return {};
            }).then(data => [data]) // Convert to array to be consistent with the return of requestObjects below
        ));
        promises.push(
            requestObjects(
                Object.keys(viewableDatasets),
                '/search/?type=Experiment&field=replicates.biological_replicate_number&field=replicates.library.biosample.organism.@id&field=replicates.library.biosample.biosample_ontology.term_id&field=replicates.antibody.lot_reviews&field=files.@id&field=files.assembly&field=files.biological_replicates&field=files.quality_metrics&limit=all'
            )
        );
        Promise.all(promises).then((metadataArray) => {
            metadataArray.forEach((metadata) => {
                metadata.forEach((dataset) => {
                    Object.assign(viewableDatasets[dataset['@id']], dataset);
                });
            });
            this.setState({ viewableDatasets });
        });
        return [];
    }

    /**
     * Calculate a list of related_datasets that we can view given our access level and each
     * dataset's status and place this list into this.viewableDatasets.
     *
     * @return {object} All datasets from ExperimentSeries object we can display.
     *                  Keyed on dataset @id. Empty if none.
     */
    statusFilteredDatasets() {
        if (this.props.context.related_datasets.length > 0) {
            const accessLevel = sessionToAccessLevel(this.context.session, this.context.session_properties);
            const viewableStatuses = getObjectStatuses('Dataset', accessLevel, viewableDatasetStatuses);
            const viewableDatasets = {};
            this.props.context.related_datasets.forEach((dataset) => {
                if (viewableStatuses.includes(dataset.status)) {
                    viewableDatasets[dataset['@id']] = dataset;
                }
            });
            return viewableDatasets;
        }
        return {};
    }

    render() {
        const { context, auditDetail, auditIndicators } = this.props;
        const itemClass = globals.itemClass(context, 'view-item');
        const roles = globals.getRoles(this.context.session_properties);
        const isAuthorized = ['admin', 'submitter'].some(role => roles.includes(role));

        // Set up the breadcrumbs.
        const datasetType = context['@type'][1];
        const crumbs = [
            { id: 'Datasets' },
            { id: datasetType, uri: `/search/?type=${datasetType}`, wholeTip: `Search for ${datasetType}` },
            { id: 'Experiment Series', uri: '/search/?type=ExperimentSeries&status=released', wholeTip: 'Search for released experiment series' },
        ];
        const crumbsReleased = (context.status === 'released');

        // Calculate the biosample summary from the organism and the biosample ontology.
        let speciesRender = null;
        if (context.organism && context.organism.length > 0) {
            const speciesList = _.uniq(context.organism.map(organism => organism.scientific_name));
            speciesRender = (
                <span>
                    {speciesList.map((species, i) =>
                        <span key={i}>
                            {i > 0 ? <span> and </span> : null}
                            <i>{species}</i>
                        </span>
                    )}
                </span>
            );
        }

        // Pre-processing dataset metadata
        const seriesObject = this.props.context;
        // Some columns are assay specific, i.e. should only be shown for corresponding experiment series
        const columns = {};
        Object.keys(experimentTableColumns).forEach((columnId) => {
            if (experimentTableColumns[columnId].hide) {
                if (!experimentTableColumns[columnId].hide(seriesObject)) {
                    columns[columnId] = experimentTableColumns[columnId];
                }
            } else {
                columns[columnId] = experimentTableColumns[columnId];
            }
        });
        const showQualityMetricLegend = Object.keys(hideColorCodedColumns).some(
            columnId => !hideColorCodedColumns[columnId](seriesObject)
        );
        let addAllToCartControl;
        let internalTags = [];
        const allRows = [];
        const viewableDatasets = this.state.viewableDatasets;
        if (Object.keys(viewableDatasets).length > 0) {
            // Add the "Add all to cart" button and internal tags from all related datasets.
            const experimentIds = Object.values(viewableDatasets).map(experiment => experiment['@id']);
            addAllToCartControl = (
                <div className="experiment-table__header">
                    <h4 className="experiment-table__title">{`Experiments in experiment series ${context.accession}`}</h4>
                    <CartAddAllElements elements={experimentIds} />
                </div>
            );

            // Collect unique internal_tags from all relevant experiments.
            internalTags = _.uniq(Object.values(viewableDatasets).reduce((allInternalTags, experiment) => (
                experiment.internal_tags && experiment.internal_tags.length > 0 ? allInternalTags.concat(experiment.internal_tags) : allInternalTags
            ), []));

            // Experiment table data
            Object.keys(viewableDatasets).forEach((datasetAtId) => {
                // Select one analysis based on file assembly and file count
                // for extracting quality metrics
                const filesByDesiredAssembly = [];
                viewableDatasets[datasetAtId].files.forEach((f) => {
                    if (selectedAssembly.includes(f.assembly)) {
                        filesByDesiredAssembly.push(f['@id']);
                    }
                });
                const analysisObjects = viewableDatasets[datasetAtId].analysis_objects || [];
                const selectedAnalysis = analysisObjects.filter(
                    analysis => analysis.files.every(f => filesByDesiredAssembly.includes(f))
                ).sort((a, b) => a.length - b.length)[0] || { files: [] };
                viewableDatasets[datasetAtId].files = viewableDatasets[datasetAtId].files.filter(
                    f => selectedAnalysis.files.includes(f['@id'])
                );
                // Number of subrows to be shown corresponds to the number of biological replicates. Show at least one by default.
                let bioRepNums = _.uniq(
                    viewableDatasets[datasetAtId].files.map(f => f.biological_replicates).reduce(
                        (bioRepArray, reps) => bioRepArray.concat(reps), []
                    )
                );
                if (bioRepNums.length === 0) {
                    bioRepNums = [''];
                }
                // Extract experiment metadata
                const rowCount = bioRepNums.length;
                const datasetRows = [];
                bioRepNums.sort((a, b) => a - b).forEach((num, i) => {
                    const cellMeta = { bioRepNum: num, isAuthorized, rowCount };
                    datasetRows.push(
                        <tr key={viewableDatasets[datasetAtId]['@id'].concat('_', num)}>
                            {Object.keys(columns).map((columnId) => {
                                if (columns[columnId].replicateSpecific || i === 0) {
                                    return columns[columnId].display ? columns[columnId].display(viewableDatasets[datasetAtId], cellMeta) : <td key={columnId} rowSpan={columns[columnId].replicateSpecific ? 1 : rowCount}>{columns[columnId].getValue ? columns[columnId].getValue(viewableDatasets[datasetAtId], cellMeta) : viewableDatasets[datasetAtId][columnId]}</td>;
                                }
                                return null;
                            })}
                        </tr>
                    );
                });
                allRows.push(datasetRows);
            });
        }

        return (
            <div className={itemClass}>
                <header>
                    <Breadcrumbs crumbs={crumbs} crumbsReleased={crumbsReleased} />
                    <h1>Summary for experiment series {context.accession}</h1>
                    <ItemAccessories item={context} audit={{ auditIndicators, auditId: 'series-audit' }} />
                </header>
                {auditDetail(context.audit, 'series-audit', { session: this.context.session, sessionProperties: this.context.session_properties })}
                <Panel>
                    <PanelBody addClasses="panel__split">
                        <div className="panel__split-element">
                            <div className="panel__split-heading panel__split-heading--experiment-series">
                                <h4>Summary</h4>
                            </div>
                            <dl className="key-value">
                                <div data-test="status">
                                    <dt>Status</dt>
                                    <dd><Status item={context} inline /></dd>
                                </div>

                                {context.description ?
                                    <div data-test="description">
                                        <dt>Description</dt>
                                        <dd>{context.description}</dd>
                                    </div>
                                : null}

                                {context.assay_term_name && context.assay_term_name.length > 0 ?
                                    <div data-test="description">
                                        <dt>Assay</dt>
                                        <dd>{context.assay_term_name.join(', ')}</dd>
                                    </div>
                                : null}

                                {context.target && context.target.length > 0 ?
                                    <div data-test="target">
                                        <dt>Target</dt>
                                        <dd>
                                            {context.target.map((targetObj, i) => <span key={targetObj['@id']}>{i !== 0 ? ', ' : ''}<a href={targetObj['@id']}>{targetObj.label}{' ('}{targetObj.organism ? <i>{targetObj.organism.scientific_name}</i> : <span>{targetObj.investigated_as[0]}</span>}{')'}</a></span>)}
                                        </dd>
                                    </div>
                                : null}

                                {(context.biosample_summary && context.biosample_summary.length > 0) || speciesRender ?
                                    <div data-test="biosamplesummary">
                                        <dt>Biosample summary</dt>
                                        <dd>
                                            {speciesRender ? <span>{speciesRender}&nbsp;</span> : null}
                                            {context.biosample_summary && context.biosample_summary.length > 0 ? <span>{context.biosample_summary.join(' and ')} </span> : null}
                                        </dd>
                                    </div>
                                : null}

                                {(context.treatment_term_name && context.treatment_term_name.length > 0) ?
                                    <div data-test="treatmenttermname">
                                        <dt>Treatment{context.treatment_term_name.length > 0 ? 's' : ''}</dt>
                                        <dd>
                                            {context.treatment_term_name.join(', ')}
                                        </dd>
                                    </div>
                                : null}
                            </dl>
                        </div>

                        <div className="panel__split-element">
                            <div className="panel__split-heading panel__split-heading--experiment-series">
                                <h4>Attribution</h4>
                            </div>
                            <dl className="key-value">
                                {context.contributors.length > 0 ?
                                    <div data-test="contributors">
                                        <dt>Contributors</dt>
                                        <dd>
                                            {context.contributors.map(contributor => (
                                                <span key={contributor['@id']} className="line-item">
                                                    {contributor.title}
                                                </span>
                                            ))}
                                        </dd>
                                    </div>
                                : null}

                                {context.aliases.length > 0 ?
                                    <div data-test="aliases">
                                        <dt>Aliases</dt>
                                        <dd>{context.aliases.join(', ')}</dd>
                                    </div>
                                : null}

                                {context.submitter_comment ?
                                    <div data-test="submittercomment">
                                        <dt>Submitter comment</dt>
                                        <dd>{context.submitter_comment}</dd>
                                    </div>
                                : null}

                                {internalTags.length > 0 ?
                                    <div className="tag-badges" data-test="tags">
                                        <dt>Tags</dt>
                                        <dd><InternalTags internalTags={internalTags} objectType="Experiment" /></dd>
                                    </div>
                                : null}
                            </dl>
                        </div>
                    </PanelBody>
                </Panel>

                {addAllToCartControl && allRows.length > 0 ?
                    <Panel addClasses="table-panel">
                        <PanelHeading>{addAllToCartControl}</PanelHeading>

                        <div className="table__scrollarea" key="table">
                            <table className="table table__sortable table-raw">
                                <thead>
                                    <tr>
                                        {Object.keys(columns).map(columnId => <th key={columnId}>{columns[columnId].title}</th>)}
                                    </tr>
                                </thead>
                                <tbody>
                                    {allRows}
                                </tbody>
                            </table>
                        </div>
                        {showQualityMetricLegend ? <PanelFooter><QualityMetricLegend /></PanelFooter> : null}
                    </Panel>
                : null}

                <FetchedItems
                    {...this.props}
                    url={`/search/?limit=all&type=File&dataset=${context['@id']}`}
                    Component={DatasetFiles}
                    filePanelHeader={<FilePanelHeader context={context} />}
                    encodevers={globals.encodeVersion(context)}
                    session={this.context.session}
                />
            </div>
        );
    }
}

ExperimentSeriesComponent.propTypes = {
    /** ExperimentSeries object to display */
    context: PropTypes.object.isRequired,
    /** Audit decorator function */
    auditIndicators: PropTypes.func.isRequired,
    /** Audit decorator function */
    auditDetail: PropTypes.func.isRequired,
};

ExperimentSeriesComponent.contextTypes = {
    session: PropTypes.object,
    session_properties: PropTypes.object,
};

const ExperimentSeries = auditDecor(ExperimentSeriesComponent);

globals.contentViews.register(ExperimentSeries, 'ExperimentSeries');


/**
 * Related dataset statuses that get counted in totals, and specified in searches.
 */
const searchableDatasetStatuses = ['released', 'archived'];
const searchableDatasetStatusQuery = searchableDatasetStatuses.reduce((query, status) => `${query}&status=${status}`, '');


const ListingComponent = (props, reactContext) => {
    const result = props.context;
    let targets = [];
    let lifeStages = [];
    let ages = [];

    // Get the biosample info and organism for Series types. Only use if we have precisely one of each.
    const biosampleTerm = (result.biosample_ontology && result.biosample_ontology.length === 1 && result.biosample_ontology[0].term_name) || '';
    const organism = (result.organism && result.organism.length === 1 && result.organism[0].scientific_name) || '';

    // Collect replicates and generate life stage and age display for the search result link. Do
    // not include any where zero or more than one exist.
    const replicates = result.related_datasets.reduce((collectedReplicates, dataset) => (
        dataset.replicates && dataset.replicates.length > 0 ? collectedReplicates.concat(dataset.replicates) : collectedReplicates
    ), []);

    replicates.forEach((replicate) => {
        if (replicate.library && replicate.library.biosample) {
            const biosample = replicate.library.biosample;
            const lifeStage = (biosample.life_stage && biosample.life_stage !== 'unknown') ? biosample.life_stage : '';
            if (lifeStage) {
                lifeStages.push(lifeStage);
            }
            if (biosample.age_display) {
                ages.push(biosample.age_display);
            }
        }
    });
    lifeStages = _.uniq(lifeStages);
    ages = _.uniq(ages);
    const lifeSpec = [lifeStages.length === 1 ? lifeStages[0] : null, ages.length === 1 ? ages[0] : null].filter(Boolean);

    // Get list of target labels.
    if (result.target) {
        targets = _.uniq(result.target.map(target => target.label));
    }

    const contributors = _.uniq(result.contributors.map(lab => lab.title));
    const contributingAwards = _.uniq(result.contributing_awards.map(award => award.project));

    // Work out the count of related datasets
    const totalDatasetCount = result.related_datasets.reduce((datasetCount, dataset) => (searchableDatasetStatuses.includes(dataset.status) ? datasetCount + 1 : datasetCount), 0);

    return (
        <li className={resultItemClass(result)}>
            <div className="result-item">
                <div className="result-item__data">
                    <a href={result['@id']} className="result-item__link">
                        {result.assay_title && result.assay_title.length > 0 ? <span>{result.assay_title.join(', ')} </span> : null}
                        Experiment Series
                        <span>
                            {biosampleTerm ? <span>{` in ${biosampleTerm}`}</span> : null}
                            {lifeSpec.length > 0 ?
                                <span>
                                    {' ('}
                                    {organism ? <i>{organism}</i> : null}
                                    {lifeSpec.length > 0 ? <span>{organism ? ', ' : ''}{lifeSpec.join(', ')}</span> : null}
                                    {')'}
                                </span>
                            : null}
                        </span>
                    </a>
                    <div className="result-item__data-row">
                        {result.dataset_type ? <div><strong>Dataset type: </strong>{result.dataset_type}</div> : null}
                        {targets.length > 0 ? <div><strong>Target: </strong>{targets.join(', ')}</div> : null}
                        <div><strong>Lab: </strong>{contributors.join(', ')}</div>
                        <div><strong>Project: </strong>{contributingAwards.join(', ')}</div>
                    </div>
                </div>
                <div className="result-item__meta">
                    <div className="result-item__meta-title">Experiment Series</div>
                    <div className="result-item__meta-id">{` ${result.accession}`}</div>
                    <div className="result-experiment-series-search">
                        <a href={`/search/?type=Experiment&related_series.@id=${result['@id']}${searchableDatasetStatusQuery}`}>View {totalDatasetCount} datasets</a>
                    </div>
                    <Status item={result.status} badgeSize="small" css="result-table__status" />
                    {props.auditIndicators(result.audit, result['@id'], { session: reactContext.session, sessionProperties: reactContext.session_properties, search: true })}
                </div>
                <PickerActions context={result} />
            </div>
            {props.auditDetail(result.audit, result['@id'], { session: reactContext.session, sessionProperties: reactContext.session_properties })}
        </li>
    );
};

ListingComponent.propTypes = {
    /** ExperimentSeries search results */
    context: PropTypes.object.isRequired,
    /** Audit decorator function */
    auditIndicators: PropTypes.func.isRequired,
    /** Audit decorator function */
    auditDetail: PropTypes.func.isRequired,
};

ListingComponent.contextTypes = {
    session: PropTypes.object,
    session_properties: PropTypes.object,
};

const Listing = auditDecor(ListingComponent);

globals.listingViews.register(Listing, 'ExperimentSeries');
