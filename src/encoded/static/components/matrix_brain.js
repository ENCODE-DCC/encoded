import React from 'react';
import PropTypes from 'prop-types';
import _ from 'underscore';
import { svgIcon } from '../libs/svg-icons';
import { Panel, PanelBody } from '../libs/ui/panel';
import * as globals from './globals';
import { DataTable } from './datatable';
import { MatrixBadges } from './objectutils';
import { SearchControls } from './search';

/**
 * All assay columns not included in matrix.
 */
const excludedAssays = [
    'Control ChIP-seq',
    'Control eCLIP',
    'RAMPAGE',
];

/**
 * Order in which assay_titles should appear along the horizontal axis of the matrix. Anything not
 * included gets sorted after these.
 */
const matrixAssaySortOrder = [
    'total RNA-seq',
    'RAMPAGE',
    'long read RNA-seq',
    'small RNA-seq',
    'microRNA-seq',
    'microRNA counts',
    'ATAC-seq',
    'DNase-seq',
    'WGBS',
    'DNAme array',
    'TF ChIP-seq',
    'Histone ChIP-seq',
    'eCLIP',
    'Hi-C',
    'genotyping HTS',
    'genotyping array',
];

/** Circle-sector of disease #1 */
const DISEASE_SECTOR_COLOR_1 = '#27d266';

/** Circle-sector of disease #2 */
const DISEASE_SECTOR_COLOR_2 = '#3c3c9f';

/** Circle-sector of disease #3 */
const DISEASE_SECTOR_COLOR_3 = '#d95252';

/** Circle-sector of when no disease is present */
const NO_DISEASE_SECTOR_COLOR = '#fff';

/** All biosamples in the Brain Matrix */
const BIOSAMPLES = [
    'middle frontal area 46',
    'head of caudate nucleus',
    'posterior cingulate gyrus',
];

/**
 * Maximum number of selected items that can be visualized.
 * @constant
 */
const MATRIX_VISUALIZE_LIMIT = 500;

/**
 * Convert  a text to title case
 *
 * @param {string} title Title
 * @returns Title in title case
 */
const titleize = (title) => title?.toLowerCase().replace(/(^|\s)\S/g, (firstLetter) => firstLetter.toUpperCase());

/**
 * Maps a biosample to a sector color
 *
 * @param {string} biosampleName
 * @returns {string} sector color
 */
const getSectorColor = (biosampleName) => {
    if (biosampleName === BIOSAMPLES[0]) {
        return DISEASE_SECTOR_COLOR_1;
    }

    if (biosampleName === BIOSAMPLES[1]) {
        return DISEASE_SECTOR_COLOR_2;
    }

    if (biosampleName === BIOSAMPLES[2]) {
        return DISEASE_SECTOR_COLOR_3;
    }

    return NO_DISEASE_SECTOR_COLOR;
};

const NO_DISEASE_LABEL = 'No disease';

const DISEASE_GROUPS = [
    [NO_DISEASE_LABEL],
    ['Cognitive impairment', 'mild cognitive impairment'],
    ['Alzheimer\'s disease and Cognitive impairment', 'Alzheimer\'s disease'],
];

const DISEASES = ['Cognitive impairment', 'mild cognitive impairment', 'Alzheimer\'s disease'];

/**
 * Maps a disease (single entry in a array) or diseases (in an array) to a color
 *
 * @param {array} availableDiseases
 * @returns Color
 */
const getDiseaseColorCode = (availableDiseases) => {
    if (!availableDiseases || availableDiseases.length === 0) {
        return 'matrix__row-data--no-disease'; //  No disease
    }

    if (availableDiseases.length > 1) {
        return 'matrix__row-data--multiple-diseases';
    }

    const disease = availableDiseases[0];

    if (disease === 'Alzheimer\'s disease') {
        return 'matrix__row-data--alzheimers-disease';
    }

    if (disease === 'mild cognitive impairment') {
        return 'matrix__row-data-mild-cognitive-impairment';
    }

    if (disease === 'Cognitive impairment') {
        return 'matrix__row-data--cognitive-impairment';
    }

    return 'matrix__row-data--no-disease'; //  No disease
};

/**
 * Get Biosample Legend Markup
 *
 * @param {object} props React's props
 * @returns Biosample Legend
 */
const GetBiosampleLegend = (props) => (
    <div className="brain-legend">
        <div>
            <p className="brain-legend--title">Biosamples</p>
            {
                BIOSAMPLES.map((biosample, index) => {
                    const sectorColor = getSectorColor(biosample);

                    // this is the circle coloring- style
                    const background = `conic-gradient(${index === 0 ? sectorColor : NO_DISEASE_SECTOR_COLOR} 120deg, ${index === 1 ? sectorColor : NO_DISEASE_SECTOR_COLOR} 120deg 240deg, ${index === 2 ? sectorColor : NO_DISEASE_SECTOR_COLOR} 240deg)`;

                    return (
                        <div className="brain-legend__row" key={biosample.replace(/ /g, '')}>
                            <div className="brain-legend__row--circle" style={{ background }} title={biosample} />
                            <div className="brain-legend__row__item brain-legend__row--text">
                                <a href={`${props.context.search_base}&biosample_ontology.term_name=${biosample}`}>{' '}{biosample}</a>
                            </div>
                        </div>
                    );
                })
            }
        </div>
    </div>
);

GetBiosampleLegend.propTypes = {
    /** Matrix search result object */
    context: PropTypes.object.isRequired,
};

/**
 * Get header markup for the Brain Matrix table
 *
 * @param {object} context Context object
 * @returns Header markup
 */
const getHeaderMarkup = (context) => {
    const { x } = context.matrix;

    // get header data
    let headers = x?.assay_title?.buckets?.filter((header) => !excludedAssays.includes(header.key))?.map((bucket) => {
        const assayWithTargetLabel = (bucket['target.label']?.buckets).map((targetBucket) => ({
            key: targetBucket.key,
            docCount: bucket.doc_count,
            assay: bucket.key,
        }));

        return assayWithTargetLabel.some((target) => target.key === 'no_target')
            ? {
                key: bucket.key,
                docCount: bucket.doc_count,
            }
            : assayWithTargetLabel;
    });

    // using headers.flat() gave an error so reverting to underscore.js
    headers = _.flatten(headers);
    headers.sort((a, b) => matrixAssaySortOrder.indexOf(a.assay || a.key) - matrixAssaySortOrder.indexOf(b.assay || b.key));

    const headerRow = {
        css: 'matrix__col-category-header',
        rowContent: [{
            css: 'matrix__brain-corner',
            content: (
                <div />
            ),
        }],
    };

    headers.forEach((header) => {
        const rowItemTitle = header.assay ? `${header.key} ChIP-seq` : `${header.key}`;

        const rowItem = {
            css: '',
            header: header.assay
                ? <a href={`${context.search_base}&assay_title=${header.assay}&target.label=${header.key}`} title={header.docCcount}>{rowItemTitle}</a>
                : <a href={`${context.search_base}&assay_title=${header.key}`} title={header.docCcount}>{rowItemTitle}</a>,
        };

        headerRow.rowContent.push(rowItem);
    });
    return { headers, headerRow };
};

/**
 * Takes matrix data from JSON and generates an object that <DataTable> can use to generate the JSX
 * for the matrix. This is a shim between the incoming matrix data and the object <DataTable>
 * needs.
 * @param {object} context Matrix JSON for the page
 * @return {object} Generated object suitable for passing to <DataTable>
 */
const getDataTableData = (context) => {
    const { y } = context.matrix;

    const { headers } = getHeaderMarkup(context);

    const xKeys = headers.map((header) => header.key);
    const rowLength = headers.length;
    const rowData = [];

    // Gathers the data
    y['replicates.library.biosample.donor.accession'].buckets.forEach((accession) => {
        const rowDataItems = {};
        rowDataItems.rowContent = [...Array(rowLength + 1)].map(() => ({}));

        const assayTitleBuckets = (accession && accession.assay_title && accession.assay_title.buckets
            ? accession.assay_title.buckets
            : [])
            .filter((assayTitle) => !excludedAssays.includes(assayTitle.key))
            .sort((a, b) => matrixAssaySortOrder.indexOf(a.key) - matrixAssaySortOrder.indexOf(b.key));

        let ageData;
        let genderData;
        let biosampleInformation = {};
        let xKey = 1;
        const availableDiseases = new Set();
        const assayTitles = [];

        assayTitleBuckets?.forEach((assayTitleBucket) => {
            if (assayTitleBucket['target.label']?.buckets?.some((a) => a.key === 'no_target')) {
                const { key } = assayTitleBucket;
                const aT1 = assayTitleBucket['target.label'].buckets.map((bucket) => ({
                    key,
                    'replicates.library.biosample.donor.age': bucket['replicates.library.biosample.donor.age'],
                    doc_count: bucket.doc_count,
                }));

                assayTitles.push(...aT1);
            } else {
                const aT2 = assayTitleBucket['target.label'].buckets.map((bucket) => ({
                    doc_count: bucket.doc_count,
                    key: assayTitleBucket.key,
                    'replicates.library.biosample.donor.age': bucket['replicates.library.biosample.donor.age'],
                    'target.label': bucket.key,
                }));
                assayTitles.push(...aT2);
            }
        });

        assayTitles?.forEach((assayTitleBucket) => {
            const assay = assayTitleBucket['target.label'] || assayTitleBucket.key;
            xKey = xKeys.indexOf(assay) + 1;

            const ageBuckets = assayTitleBucket && assayTitleBucket['replicates.library.biosample.donor.age'] && assayTitleBucket['replicates.library.biosample.donor.age'].buckets
                ? assayTitleBucket['replicates.library.biosample.donor.age'].buckets
                : [];

            ageData = ageBuckets.map((age) => age.key).join(', ').replace(' or above', '+');

            ageBuckets.forEach((ageBucket) => {
                const genderBuckets = ageBucket && ageBucket['replicates.library.biosample.donor.sex'] && ageBucket['replicates.library.biosample.donor.sex'].buckets
                    ? ageBucket['replicates.library.biosample.donor.sex'].buckets
                    : [];

                genderData = genderBuckets.map((gender) => gender.key).join(', ');

                genderBuckets?.forEach((genderBucket) => {
                    const biosampleBuckets = genderBucket && genderBucket['replicates.library.biosample.biosample_ontology.term_name'] && genderBucket['replicates.library.biosample.biosample_ontology.term_name'].buckets
                        ? genderBucket['replicates.library.biosample.biosample_ontology.term_name'].buckets
                        : [];

                    biosampleInformation = {};

                    biosampleBuckets?.forEach((biosampleBucket) => {
                        biosampleInformation[biosampleBucket.key] = biosampleBucket.doc_count;

                        const diseaseTermNameBuckets = biosampleBucket && biosampleBucket['replicates.library.biosample.disease_term_name'].buckets
                            ? biosampleBucket['replicates.library.biosample.disease_term_name'].buckets
                            : [];

                        diseaseTermNameBuckets.forEach((diseaseTermNameBucket) => {
                            availableDiseases.add(diseaseTermNameBucket.key);
                        });
                    });
                });
            });

            const availableBiosamples = Object.keys(biosampleInformation);
            const targetLabel = assayTitleBucket['target.label'] ? `&target.label=${assayTitleBucket['target.label']}` : '';
            const assayQuery = `&assay_title=${assayTitleBucket['target.label'] ? assayTitleBucket.key : assay}`;

            if (availableBiosamples.length > 0) {
                const part1 = availableBiosamples.includes(BIOSAMPLES[0]) ? DISEASE_SECTOR_COLOR_1 : NO_DISEASE_SECTOR_COLOR;
                const part2 = availableBiosamples.includes(BIOSAMPLES[1]) ? DISEASE_SECTOR_COLOR_2 : NO_DISEASE_SECTOR_COLOR;
                const part3 = availableBiosamples.includes(BIOSAMPLES[2]) ? DISEASE_SECTOR_COLOR_3 : NO_DISEASE_SECTOR_COLOR;

                rowDataItems.rowContent[xKey] = {
                    accession,
                    targetLabel,
                    assayQuery,
                    assay,
                    part1,
                    part2,
                    part3,
                };
            }
        });

        const uniqueDiseases = Array.from(availableDiseases);
        const genderSymbol = genderData === 'male' ? '♂' : '♀';
        const diseaseColor = uniqueDiseases.length > 0 ? getDiseaseColorCode(uniqueDiseases) : '';

        rowDataItems.diseaseColor = diseaseColor;
        rowDataItems.diseases = uniqueDiseases;

        rowDataItems.rowContent[0] = {
            accession,
            age: ageData,
            genderSymbol,
            genderType: genderData,
        };

        rowData.push(rowDataItems);
    });

    return rowData.reduce((acc, value) => {
        const key = value.diseases.length === 0 || !value.diseases ? NO_DISEASE_LABEL : value.diseases.join(' and ');
        if (!acc[key]) {
            acc[key] = [];
        }

        acc[key].push(value);

        return acc;
    }, {});
};

/**
 * Get the brain table data for a list of diseases
 *
 * @param {object} context Object
 * @param {array} diseaseList List of diseases
 * @returns Data for a list of diseases
 */
const convertContextToDataTable = (context, diseaseList, diseaseGroupIndex = 0) => {
    const rows = [];
    const rowKeys = [];
    const { headerRow } = getHeaderMarkup(context);

    rows.push(headerRow);
    rowKeys.push(`header${diseaseGroupIndex}`);

    diseaseList?.forEach((diseaseInfo) => {
        const disease = Object.keys(diseaseInfo)[0];
        const rowData = diseaseInfo[disease] || [];
        const rowLength = rowData[0]?.rowContent?.length || 1;
        const diseaseColor = rowData[0]?.diseaseColor;
        const replicateUrlPart = disease === NO_DISEASE_LABEL
            ? DISEASES.map((d) => `&replicates.library.biosample.disease_term_name!=${d.trim()}`).join('')
            : disease.split('and').map((d) => `&replicates.library.biosample.disease_term_name=${d.trim()}`).join('');
        const url = `${context.search_base}${replicateUrlPart}`;

        rows.push(
            {
                css: `matrix__row-data ${diseaseColor}`,
                rowContent: [{
                    css: 'text-header',
                    content: (
                        <div className="disease-text">
                            <div>
                                <a href={url}>{titleize(NO_DISEASE_LABEL === disease ? 'No cognitive impairment' : disease)}</a>
                            </div>
                        </div>
                    ),
                    colSpan: rowLength,
                }],
            }
        );

        rowKeys.push(disease.replace(/ /g, ''));

        // Generate markup
        rowData.forEach((rowDataLine, rowDataLineIndex) => {
            const row = [...Array(rowLength)].map(() => ({
                css: 'matrix__row-data',
                content: (
                    <div className="matrix-brain-disease-identifier">
                        <div>&nbsp;</div>
                    </div>
                ),
            }));

            row.css = `${rowDataLineIndex === 0 ? 'matrix__content--brain--first' : ''} matrix__row-data ${diseaseColor}`;
            row.title = rowDataLine.diseases?.length > 0 ? rowDataLine.diseases?.join(', ') : NO_DISEASE_LABEL;
            let rowKey = '';

            rowDataLine.rowContent.forEach((content, index) => {
                if (index === 0) {
                    const { age, genderSymbol, genderType, accession } = content;
                    const key = accession?.key;
                    rowKey = key;
                    const ageText = age ? <span title="age"> {age} years</span> : null;
                    const genderText = genderSymbol ? <div className={`${genderType}-symbol`} title={genderType}> {genderSymbol}</div> : null;

                    row[0].content = (
                        <>
                            <span>
                                <a href={`${context.search_base}&replicates.library.biosample.donor.accession=${key}`} title="Donor">{key}</a>
                            </span>
                            { ageText }
                            { genderText && ageText ? ',' : '' }
                            { genderText }
                        </>
                    );
                } else if (Object.keys(content).length === 0) {
                    row[index].content = (
                        <div className="matrix-brain-disease-identifier">
                            <div>&nbsp;</div>
                        </div>
                    );
                    row[index].css = 'matrix__row-data';
                } else {
                    const { accession, assayQuery, targetLabel, assay, part1, part2, part3 } = content;
                    const key = accession?.key;

                    row[index].content = (
                        <div className="matrix-brain-disease-identifier">
                            <div className="brain-cell">
                                <a
                                    href={`${context.search_base}&replicates.library.biosample.donor.accession=${key}${assayQuery}${targetLabel}`}
                                    title={assay}
                                >
                                    <div
                                        className="brain-matrix-circle"
                                        style={{ background: `conic-gradient(${part1} 120deg, ${part2} 120deg 240deg, ${part3} 240deg)` }}
                                    />
                                </a>
                            </div>
                        </div>
                    );
                }
            });

            rowKeys.push(rowKey);
            rows.push(row);
        });
    });

    return {
        rows,
        rowKeys,
    };
};

/**
 * Render the area above the matrix itself, including the page title.
 */
const MatrixHeader = ({ context }) => {
    const visualizeDisabledTitle = context.total > MATRIX_VISUALIZE_LIMIT ? `Filter to ${MATRIX_VISUALIZE_LIMIT} to visualize` : '';

    return (
        <div className="matrix-header">
            <div className="matrix-header__title">
                <div className="matrix-title-badge">
                    <h1>{context.title}</h1>
                    <MatrixBadges context={context} />
                </div>
                <div className="matrix-description">
                    <div className="matrix-description__text">
                        Human brain samples collection page that includes data from multiple brain regions collected from individuals with various levels of cognitive impairment.
                    </div>
                </div>
            </div>
            <div className="matrix-header__controls">
                <div className="matrix-header__filter-controls matrix__content--brain">
                    <GetBiosampleLegend context={context} />
                </div>
                <div className="matrix-header__search-controls">
                    <h4>Showing {context.total} results</h4>
                    <SearchControls context={context} visualizeDisabledTitle={visualizeDisabledTitle} hideBrowserSelector />
                </div>
            </div>
        </div>);
};

MatrixHeader.propTypes = {
    /** Matrix search result object */
    context: PropTypes.object.isRequired,
};


/**
 * Display the matrix and associated controls above them.
 */
const MatrixPresentation = ({ context }) => {
    const [scrolledRight, setScrolledRight] = React.useState(false);
    const ref = React.useRef(null);

    // Memoized (prevents function creation on every render -- function only gets recreated when
    // `scrolledRight` value changes) callback to calculate whether the ASSAY arrow needs to flash
    // (`scrolledRight` === false) or not (`scrolledRight` === true). Called in response to both
    // "scroll" and "resize" events.
    const handleScroll = React.useCallback((target) => {
        // Have to use a "roughly equal to" test because of an MS Edge bug mentioned here:
        // https://stackoverflow.com/questions/30900154/workaround-for-issue-with-ie-scrollwidth
        const scrollDiff = Math.abs((target.scrollWidth - target.scrollLeft) - target.clientWidth);
        if (scrollDiff < 2 && !scrolledRight) {
            // Right edge of matrix scrolled into view.
            setScrolledRight(true);
        } else if (scrollDiff >= 2 && scrolledRight) {
            // Right edge of matrix scrolled out of view.
            setScrolledRight(false);
        }
    }, [scrolledRight]);

    // Callback called after component mounts to add the "scroll" and "resize" event listeners.
    // Both events can cause a recalculation of `scrolledRight`. People seem to prefer using the
    // "scroll" event listener with hooks as opposed to the onScroll property, but I don't yet know
    // why.
    React.useEffect(() => {
        // Direct callbacks not memoized because of their small size.
        const handleScrollEvent = (event) => handleScroll(event.target);
        const handleResizeEvent = () => handleScroll(ref.current);

        // Cache the reference to the scrollable matrix <div> so that we can remove the "scroll"
        // event handler on unmount, when ref.current might no longer point at this <div>.
        const matrixNode = ref.current;

        // Attach the scroll- and resize- event handlers, then force the initial calculation of
        // `scrolledRight`.
        ref.current.addEventListener('scroll', handleScrollEvent);
        window.addEventListener('resize', handleResizeEvent);
        handleScroll(ref.current);

        // Callback called when unmounting component.
        return () => {
            matrixNode.removeEventListener('scroll', handleScrollEvent);
            window.removeEventListener('resize', handleResizeEvent);
        };
    }, [handleScroll]);

    const dataTableData = getDataTableData(context);
    const matrixConfigs = [];
    let diseaseList = [];

    DISEASE_GROUPS.forEach((diseaseGroup, diseaseGroupIndex) => {
        diseaseList = [];

        diseaseGroup.forEach((disease) => {
            const obj = {};
            obj[disease] = dataTableData[disease];

            if (obj[disease]) {
                diseaseList.push(obj);
            }
        });

        if (diseaseList.length !== 0) {
            // Convert Brain matrix data to a DataTable object. I'd like to memoize this but determining if
            // the incoming, deeply nested matrix data has changed would be very complicated.
            const { rows, rowKeys } = convertContextToDataTable(context, diseaseList, diseaseGroupIndex);
            matrixConfigs.push({
                rows,
                rowKeys,
                key: `rowItemKey${diseaseGroupIndex}`, // hacky but suffices as a key to applease React
            });
        }
    });

    return (
        <div className="matrix__presentation">
            <div className={`matrix__label matrix__label--horz${!scrolledRight ? ' horz-scroll' : ''}`}>
                <span>{context.matrix.x.label}</span>
                {svgIcon('largeArrow')}
            </div>
            <div className="matrix__presentation-content">
                <div className="matrix__label matrix__label--vert"><div>{svgIcon('largeArrow')}{context.matrix.y.label}</div></div>
                <div className="brain-set">
                    {
                        matrixConfigs.map((matrixConfig) => (
                            <div className="brain-set__item" key={matrixConfig.key}>
                                <div className="matrix__data" ref={ref}>
                                    <DataTable tableData={matrixConfig} />
                                </div>
                            </div>
                        ))
                    }
                </div>
            </div>
        </div>
    );
};

MatrixPresentation.propTypes = {
    /** Brain matrix object */
    context: PropTypes.object.isRequired,
};

/**
 * Render the area containing the matrix.
 */
const MatrixContent = ({ context }) => (
    <div className="matrix__content matrix__content--brain">
        <MatrixPresentation context={context} />
    </div>
);

MatrixContent.propTypes = {
    /** Brain matrix object */
    context: PropTypes.object.isRequired,
};


/**
 * View component for the BRAIN matrix page.
 */
const BrainMatrix = ({ context }) => {
    const itemClass = globals.itemClass(context, 'view-item');

    if (context.total > 0) {
        return (
            <Panel addClasses={itemClass}>
                <PanelBody>
                    <MatrixHeader context={context} />
                    <MatrixContent context={context} />
                </PanelBody>
            </Panel>
        );
    }
    return <h4>No results found</h4>;
};

BrainMatrix.propTypes = {
    /** BRAIN matrix object */
    context: PropTypes.object.isRequired,
};

BrainMatrix.contextTypes = {
    location_href: PropTypes.string,
};

globals.contentViews.register(BrainMatrix, 'BrainMatrix');
