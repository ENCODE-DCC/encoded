import React from 'react';
import ReactDOMServer from 'react-dom/server';
import PropTypes from 'prop-types';
import url from 'url';
import QueryString from '../libs/query_string';
import * as encoding from '../libs/query_encoding';
import { Panel, PanelBody } from '../libs/ui/panel';
import { svgIcon } from '../libs/svg-icons';
import { tintColor, isLight } from './datacolors';
import * as globals from './globals';
import { MATRIX_VISUALIZE_LIMIT } from './matrix';
import { FacetList, SearchControls } from './search';
import { BodyMapThumbnailAndModal } from './body_map';
import FacetRegistry from './facets/registry';


/** General collection of attributes to exclude in some scenarios */
const excludedAttributes = ['', 'n/a', 'unknown', undefined, null];

/** life stages to display on UI */
const includedLifeStage = ['child', 'embryonic', 'newborn'];

/** Roman mythology equivalent representing gender */
const getGenderMythology = (genderType) => {
    if (genderType === 'male') {
        return 'mars';
    }

    if (genderType === 'female') {
        return 'venus';
    }

    return '';
};

/** Query keys to remove from context's urls */
const removedQueryKeys = ['@id', 'search_base'];

/**
 *  Key/value pairs mapping diseases to css classes
 */
const diseaseCode = {
    'multiple sclerosis': 'multiple-sclerosis-symbol',
    'Alzheimer\'s disease': 'alzheimers-disease-symbol',
    'mild cognitive impairment': 'mild-cognitive-impairment-symbol',
    'Cognitive impairment': 'cognitive-impairment-symbol',
    'amyotrophic lateral sclerosis': 'bamyotrophic-lateral-sclerosis-symbol',
    'nonobstructive coronary artery disease': 'nonobstructive-coronary-artery-symbol',
    'squamous cell carcinoma': 'squamous-cell-carcinoma-symbol',
    'basal cell carcinoma': 'basal-cell-carcinoma-symbol',
};

/**
 * Gets data like age and gender and adds them to the Matrix
 *
 * @param {object} data from a fetch call
 */
const addExtraRowHeaderDataToMatrix = (data, matrixUpdateCallBack) => {
    const graph = data['@graph'].map((g) => {
        let age = '';

        if (g.age) {
            const ageText = `${[g.age].filter((a) => !excludedAttributes.includes(a)).join(', ')}`;
            const formattedAge = `${(ageText || '').replace(' or above', '+')} ${ageText ? g.age_units : ''}${ageText === 1 || ageText === '' ? '' : 's'}`.trim();
            const lifeStageText = g.lifeStage ? ` (${g.lifeStage})` : '';

            age = `${formattedAge}${lifeStageText}`;
        }

        return {
            accession: globals.atIdToAccession(g['@id']),
            age,
            genderMythology: getGenderMythology(g.sex),
            genderType: g.sex,
            lifeStage: includedLifeStage.includes(g.life_stage) ? g.life_stage : '',
        };
    });

    matrixUpdateCallBack(graph);
};

/**
 *  Matrix data from context, to be used to paint the DOM
 *
 * @param {context} context
 */
const getDataTableData = (context) => {
    const { matrix } = context;
    const x = {
        header: matrix.x.assay_title.buckets.map((assayTitle) => assayTitle.key),
    };
    const xLength = x.header.length;
    const y = [];

    matrix.y['replicates.library.biosample.donor.accession'].buckets.forEach((accessionBucket) => {
        const accession = accessionBucket.key;

        // In row, first item is accession. The next are assay number based on the assay in variable - x
        const row = {
            accession,
            assayTotals: [...Array(xLength)].map(() => 0),
            diseases: [],
        };

        accessionBucket.assay_title.buckets.forEach((assayTitleBucket) => {
            const assayTitle = assayTitleBucket.key;
            const assayCount = assayTitleBucket.doc_count;
            const assayIndex = x.header.indexOf(assayTitle);

            row.assayTotals[assayIndex] = assayCount;
            const diseases = assayTitleBucket['replicates.library.biosample.disease_term_name'].buckets.map((disease) => disease.key).filter((disease) => excludedAttributes.includes(disease.key));

            if (diseases.length > 0) {
                row.diseases.push(...diseases);
            }
        });
        row.diseases = [...new Set(row.diseases)];
        y.push(row);
    });

    return { x, y };
};

/**
 * Populate the matrix
 *
 * @param {object} dataTableData Matrix data
 * @param {string} baseUrl Url of the page from context
 * @param {string} searchBaseUrl Search url from context
 * @param {object} graph based on context
 */
const convertToMatrixData = (dataTableData, baseUrl, searchBaseUrl, graph) => {
    const { x, y } = dataTableData;
    const matrixData = [];
    const rowColor = '#fff';
    const firstColumnWidth = '400px'; // changes the default width  in grid matrix

    // header
    const header = {
        type: 'matrixHeader',
        itemKey: 'matrix-header-key',
        items: [{
            content: (
                <div style={{ display: 'flex', flexDirection: 'row', width: firstColumnWidth }} key="matrix-header-key-accession">
                    <div style={{ border: '1px solid #f0f0f0', flex: '0 1 32%', textDecoration: 'none', whiteSpace: 'nowrap', textAlign: 'center' }}>
                        <div className="grid-matrix__header__text">
                                Accession
                        </div>
                    </div>
                    <div style={{ border: '1px solid #f0f0f0', flex: '0 1 40%' }} key="matrix-header-key-age">
                        <div className="grid-matrix__header__text">
                                Age
                        </div>
                    </div>
                    <div style={{ border: '1px solid #f0f0f0', flex: '0 1 8%' }} key="matrix-header-gender">
                        <div className="grid-matrix__header__text">
                                Sex
                        </div>
                    </div>
                    <div style={{ border: '1px solid #f0f0f0', flex: '0 1 20%' }} key="matrix-header-key-disease">
                        <div className="grid-matrix__header__text">
                                Disease
                        </div>
                    </div>
                </div>
            ),
            itemKey: 'matrix-header-key-titles',
        }].concat(dataTableData.x.header.map((xData) => {
            const baseUrlQuery = new QueryString(baseUrl);
            baseUrlQuery.deleteKeyValue('assay_title');
            baseUrlQuery.addKeyValue('assay_title', xData);

            const assayTitleLink = baseUrlQuery.format();

            return {
                content: <a href={`${assayTitleLink.replace('/human-donor-matrix/?type', '/search/?type')}`}>{xData}</a>,
                itemKey: xData.replace(/\s+/g, ''),
            };
        })),
    };

    matrixData.push(header);

    y.forEach((yEntry) => {
        const accessionTextColor = isLight(rowColor) ? '#000' : '#fff';
        const { accession, assayTotals } = yEntry;
        const maxAssayTotal = Math.max(...assayTotals);
        const minAssayTotal = Math.min(...assayTotals);
        const logBase = Math.log(1 + maxAssayTotal + minAssayTotal);

        // change grid matrix default values
        const rowHeaderFirstColStyle = {
            color: accessionTextColor,
            backgroundColor: rowColor,
            width: firstColumnWidth,
        };

        const graphEntry = graph.find((g) => g.accession === accession) || {};
        const icon = !graphEntry.genderMythology ? '' : ReactDOMServer.renderToString((svgIcon(graphEntry.genderMythology)));
        const lifeStageText = graphEntry.lifeStage ? ` (${graphEntry.lifeStage})` : '';
        const age = excludedAttributes.includes(graphEntry.age) ? '' : graphEntry.age;

        const row = {
            type: 'categoryHeader',
            itemKey: accession,
            items: [{
                content: (
                    <span style={rowHeaderFirstColStyle}>
                        <div style={{ display: 'flex', flexDirection: 'row' }} key={`${accession}-accession`}>
                            <div style={{ border: '1px solid #f0f0f0', flex: '0 1 32%' }}>
                                <a id={accession} href={`${baseUrl}&replicates.library.biosample.donor.accession=${accession}`.replace('/human-donor-matrix/?type=', '/matrix/?type=')}>{`${accession}`}</a>
                            </div>
                            <div className={`${accession}-age`} style={{ border: '1px solid #f0f0f0', flex: '0 1 40%' }} key={`${accession}-age`}>
                                { `${age}${lifeStageText}` }
                            </div>
                            <div className={`${accession}-gender`} style={{ border: '1px solid #f0f0f0', flex: '0 1 8%', textAlign: 'center' }} key={`${accession}-gender`}>
                                <div className="gender-symbol" title={`${graphEntry.genderType}`} dangerouslySetInnerHTML={{ __html: icon }} />
                            </div>
                            <div style={{ border: '1px solid #f0f0f0', flex: '0 1 20%' }} key={`${accession}-disease`}>
                                {
                                    yEntry.diseases.map((disease) => <i className={`${diseaseCode[disease]}`} title={`${disease}`} key={`${accession}-${disease}.replace(/s/g, '')`} />)
                                }
                            </div>
                        </div>
                    </span>),
                itemKey: `${accession}-header`,
            }].concat(
                assayTotals.map((assayTotal, assayCountIndex) => {
                    let tintFactor = 0;

                    if (assayTotal > 0) {
                        tintFactor = maxAssayTotal > minAssayTotal ? 1 - (Math.log(1 + (assayTotal - minAssayTotal)) / logBase) : 0.5;
                    }

                    const cellColor = tintColor('#0198C8', tintFactor);
                    const assayCountTextColor = isLight(cellColor) ? '#000' : '#fff';
                    const itemKey = `${accession}-${assayCountIndex}`;
                    const assayTitle = x.header[assayCountIndex];

                    const searchBaseUrlQuery = new QueryString(searchBaseUrl);
                    searchBaseUrlQuery.deleteKeyValue('assay_title');
                    searchBaseUrlQuery.addKeyValue('assay_title', assayTitle);
                    const searchBaseLink = searchBaseUrlQuery.format();

                    return assayTotal === 0
                        ? {
                            content: <span style={{ backgroundColor: '#fff' }} title={assayTitle}> {' '} </span>,
                            itemKey,
                        }
                        : {
                            content: <a href={`${searchBaseLink}&replicates.library.biosample.donor.accession=${accession}`} style={{ color: `${assayCountTextColor}`, backgroundColor: `${cellColor}` }} title={assayTitle}>{assayTotal}</a>,
                            itemKey,
                        };
                })
            ),
        };

        matrixData.push(row);
    });

    return { matrixData };
};

const getExtraRowHeaderData = (context, reactContext, matrixUpdateCallBack) => {
    const searchUrl = '/search/?type=HumanDonor&field=sex&format=json&field=age&field=age_units&field=life_stage&limit=all';

    reactContext.fetch(searchUrl, {
        headers: { Accept: 'application/json' },
    }).then((response) => {
        if (!response.ok) {
            throw response;
        }
        return response.json();
    }).then((data) => {
        addExtraRowHeaderDataToMatrix(data, matrixUpdateCallBack);
    }).catch((e) => {
        console.error('OBJECT LOAD ERROR: %s', e);
    });
};

/**
 * This provides a substrate for building a matrix using css Grid. It receives an array of array where each subarray is a row
 * and uses that to build the array. For example, matrixData can be -
 * [
 *     {
 *          type: 'matrixHeader',
 *          itemKey: 'title-key',
 *          items: [
 *              { content: ['a title'], itemKey: 'a-title-key' }
 *              { content: ['another title'], itemKey: 'b-title-key' }
 *          ]
 *     },
 *     {
 *          type: 'matrixData',
 *          itemKey: 'data-key',
 *          items: [
 *              { content: ['a data point'], itemKey: 'a-data-key' }
 *              { content: ['another data point'], itemKey: 'yet-another-key' }
 *          ]
 *     }
 *
 *  There are three types- matrixHeader (css for header matrix), matrixData (for data) and categoryHeader (for category)
 * ]
 *
 * Each array entry corresponds to a matrix row and each subarray entry corresponds to a field in the matrix.
 * Default css is bare-minimum and only provides a structure. The calling code can either pass in styles via
 * style attribute or override the styles of "grid-matrix__header", "grid-matrix__row-data" and/or
 * "grid-matrix__category" to get desired effect
 *
 * @param {array} matrixData
 * @returns Virtual DOM-part
 */
const GridMatrix = ({ matrixData }) => {
    const rowType = (type) => {
        if (type === 'matrixHeader') {
            return 'grid-matrix__header';
        } if (type === 'matrixData') {
            return 'grid-matrix__row-data';
        } if (type === 'categoryHeader') {
            return 'grid-matrix__category';
        }

        return '';
    };

    return (
        <div className="grid-matrix">
            {
                matrixData.map((data) => (
                    <div key={data.itemKey} className={`${rowType(data.type)} ${data.class || ''}`} style={data.style}>
                        { data?.items?.map((rowItem) => (
                            <React.Fragment key={`${rowItem.itemKey}`}>
                                { rowItem.content }
                            </React.Fragment>
                        ))
                        }
                    </div>
                ))
            }
        </div>
    );
};

GridMatrix.propTypes = {
    /** Whole matrix data */
    matrixData: PropTypes.array.isRequired,
};

/**
 * Render the area above the facets and matrix content.
 *
 *  @param {object} context Page context
 */
const MatrixHeader = ({ context }) => {
    const visualizeDisabledTitle = context.total > MATRIX_VISUALIZE_LIMIT ? `Filter to ${MATRIX_VISUALIZE_LIMIT} to visualize` : '';
    const parsedUrl = url.parse(context['@id'], true);
    parsedUrl.query.format = 'json';
    parsedUrl.search = '';

    // Compose a type title for the page if only one type is included in the query string.
    // Currently, only one type is allowed in the query string or the server returns a 400, so this
    // code exists in case more than one type is allowed in future.
    let type = '';
    if (context.filters && context.filters.length > 0) {
        const typeFilters = context.filters.filter((filter) => filter.field === 'type');
        if (typeFilters.length === 1) {
            type = typeFilters[0].term;
        }
    }

    // If the user has requested an ENCORE matrix, generate a matrix description.
    const query = new QueryString(context.search_base);
    const matrixDescription = query.getKeyValues('internal_tags').includes('ENCORE') ?
        'The ENCORE project aims to study protein-RNA interactions by creating a map of RNA binding proteins (RBPs) encoded in the human genome and identifying the RNA elements that the RBPs bind to.'
    : '';

    return (
        <div className="matrix-header">
            <div className="matrix-header__title">
                <div className="matrix-title-badge">
                    <h1>{type ? `${type} ` : ''}{context.title}</h1>
                </div>
                {matrixDescription ?
                    <div className="matrix-description">
                        <div className="matrix-description__text">{matrixDescription}</div>
                    </div>
                : null}
            </div>
            <div className="matrix-header__controls">
                <div className="matrix-header__search-controls--human-donor">
                    <h4>Showing {context.total} results</h4>
                    <SearchControls context={context} visualizeDisabledTitle={visualizeDisabledTitle} />
                </div>
            </div>
        </div>
    );
};

MatrixHeader.propTypes = {
    /** Matrix search result object */
    context: PropTypes.object.isRequired,
};

const MatrixLegends = ({ context }, reactContext) => {
    const query = new QueryString(context['@id']);
    const biosamples = query.getKeyValues('biosample_ontology.classification');
    const hasTissue = biosamples.includes('tissue');
    const hasPrimaryCell = biosamples.includes('primary cell');

    const navigateToUpdatedBiosampleClassification = (e) => {
        const { value } = e.target;

        query.deleteKeyValue('biosample_ontology.classification');
        query.addKeyValue('config', 'HumanDonorMatrix');

        if (value === 'both') {
            query.addKeyValue('biosample_ontology.classification', 'tissue');
            query.addKeyValue('biosample_ontology.classification', 'primary cell');
        } else {
            query.addKeyValue('biosample_ontology.classification', value);
        }

        reactContext.navigate(query.format());
    };

    return (
        <div className="matrix__legend-region-human-donor">
            <div className="human-donor-legend">
                <div className="human-donor-legend--title">
                    Disease Legend
                </div>
                <div className="human-donor-legend__body">
                    {
                        Object.keys(diseaseCode).map((disease) => (
                            <div key={`${disease}.replace(/s/g, '')`}>
                                <i className={`${diseaseCode[disease]}`} />
                                {' '}
                                <span className="human-donor-legend--disease-text">{disease}</span>
                            </div>
                        ))
                    }
                </div>
            </div>
            <div className="human-donor-biosample">
                <div className="human-donor-biosample__title">
                    Biosample Classification
                </div>
                <div className="human-donor-biosample__body">
                    <div className="human-donor-biosample__body__area">
                        <div className="human-donor-biosample__body__options">
                            <div className="radio-btn">
                                <input type="radio" id="tissue-option" value="tissue" name="biosample-classification" checked={hasTissue && !hasPrimaryCell} onChange={(e) => navigateToUpdatedBiosampleClassification(e)} />
                                <label className="btn btn-default" htmlFor="tissue-option">Tissue</label>
                            </div>
                            <div className="radio-btn">
                                <input type="radio" id="primary-cell-option" value="primary cell" name="biosample-classification" checked={hasPrimaryCell && !hasTissue} onChange={(e) => navigateToUpdatedBiosampleClassification(e)} />
                                <label className="btn btn-default" htmlFor="primary-cell-option">Primary Cell</label>
                            </div>
                            <div className="radio-btn">
                                <input type="radio" id="both-option" value="both" name="biosample-classification" checked={hasTissue && hasPrimaryCell} onChange={(e) => navigateToUpdatedBiosampleClassification(e)} />
                                <label className="btn btn-default" htmlFor="both-option">Both</label>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

MatrixLegends.propTypes = {
    /** Matrix search result object */
    context: PropTypes.object.isRequired,
};

MatrixLegends.contextTypes = {
    navigate: PropTypes.func,
};

/**
 * Render the vertical facets.
 *
 *  @param {object} context Page context
 */
const MatrixVerticalFacets = ({ pageContext }, reactContext) => (
    <div className="human-donor-facets">
        <BodyMapThumbnailAndModal
            context={pageContext}
            location={`${reactContext.location_href}`}
            organism="Homo sapiens"
        />
        <FacetList
            context={pageContext}
            facets={pageContext.facets}
            filters={pageContext.filters}
            addClasses="matrix-facets"
            supressTitle
        />
    </div>
);

MatrixVerticalFacets.propTypes = {
    /** Matrix search result object with urls - @id and searchId having config=HumanDonorMatrix */
    pageContext: PropTypes.object.isRequired,
};

MatrixVerticalFacets.contextTypes = {
    navigate: PropTypes.func,
    location_href: PropTypes.string,
};

/**
 * Display the matrix and associated controls above them.
 */
class MatrixPresentation extends React.Component {
    constructor(props, reactContext) {
        super(props);

        this.state = {
            /** True if matrix scrolled all the way to the right; used for flashing arrow */
            scrolledRight: false,
            /** Data for building the matrix */
            matrixData: [],
        };
        this.reactContext = reactContext;
        this.handleOnScroll = this.handleOnScroll.bind(this);
        this.handleScrollIndicator = this.handleScrollIndicator.bind(this);
        this.matrixUpdateCallBack = this.matrixUpdateCallBack.bind(this);
    }

    componentDidMount() {
        this.handleScrollIndicator(this.scrollElement);

        getExtraRowHeaderData(this.props.context, this.reactContext, this.matrixUpdateCallBack);
    }

    /* eslint-disable react/no-did-update-set-state */
    componentDidUpdate(prevProps) {
        // If URI changed, we need close any expanded rowCategories in case the URI change results
        // in a huge increase in displayed data. Also update the scroll indicator if needed.
        if (prevProps.context['@id'] !== this.props.context['@id']) {
            this.handleScrollIndicator(this.scrollElement);

            getExtraRowHeaderData(this.props.context, this.reactContext, this.matrixUpdateCallBack);
        }
    }
    /* eslint-enable react/no-did-update-set-state */

    /**
     * Called when the user scrolls the matrix horizontally within its div to handle scroll
     * indicators.
     * @param {object} e React synthetic scroll event
     */
    handleOnScroll(e) {
        this.handleScrollIndicator(e.target);
    }

    /**
     * Show a scroll indicator depending on current scrolled position.
     * @param {object} element DOM element to apply shading to
     */
    handleScrollIndicator(element) {
        // Have to use a "roughly equal to" test because of an MS Edge bug mentioned here:
        // https://stackoverflow.com/questions/30900154/workaround-for-issue-with-ie-scrollwidth
        const scrollDiff = Math.abs((element.scrollWidth - element.scrollLeft) - element.clientWidth);
        if (scrollDiff < 2 && !this.state.scrolledRight) {
            // Right edge of matrix scrolled into view.
            this.setState({ scrolledRight: true });
        } else if (scrollDiff >= 2 && this.state.scrolledRight) {
            // Right edge of matrix scrolled out of view.
            this.setState({ scrolledRight: false });
        }
    }

    matrixUpdateCallBack(graph) {
        const { context } = this.props;
        const dataTableData = getDataTableData(context);
        const atIdQuery = new QueryString(context['@id']);
        const searchBaseQuery = new QueryString(context.search_base);

        atIdQuery.deleteKeyValue('config');
        searchBaseQuery.deleteKeyValue('config');

        const { matrixData } = convertToMatrixData(dataTableData, atIdQuery.format(), searchBaseQuery.format(), graph);

        this.setState({ matrixData });
    }

    render() {
        const { context } = this.props;
        const { scrolledRight } = this.state;

        return (
            <div className="matrix__presentation">
                <div className={`matrix__label matrix__label--horz${!scrolledRight ? ' horz-scroll' : ''}`}>
                    <span>{context.matrix.x.label}</span>
                    {svgIcon('largeArrow')}
                </div>
                <div className="matrix__presentation-content">
                    <div className="matrix__label matrix__label--vert"><div>{svgIcon('largeArrow')}{context.matrix.y.label}</div></div>
                    <div className="matrix__data-wrapper">
                        <div className="matrix__data matrix__human-donor" onScroll={this.handleOnScroll} ref={(element) => { this.scrollElement = element; }}>
                            <GridMatrix matrixData={this.state.matrixData} />
                        </div>
                    </div>
                </div>
            </div>
        );
    }
}

MatrixPresentation.propTypes = {
    /** Matrix search result object */
    context: PropTypes.object.isRequired,
};

MatrixPresentation.contextTypes = {
    fetch: PropTypes.func,
    navigate: PropTypes.func,
};

/**
 * Render the vertical facets and the matrix itself.
 */
const MatrixContent = ({ context, pageContext, rowCategoryGetter, rowSubCategoryGetter, mapRowCategoryQueries, mapSubCategoryQueries }) => (
    <div className="matrix__content-human-donor">
        <MatrixVerticalFacets pageContext={pageContext} />
        <MatrixPresentation context={context} rowCategoryGetter={rowCategoryGetter} rowSubCategoryGetter={rowSubCategoryGetter} mapRowCategoryQueries={mapRowCategoryQueries} mapSubCategoryQueries={mapSubCategoryQueries} />
    </div>
);

MatrixContent.propTypes = {
    /** Matrix search result object with urls - @id and searchId not having config=HumanDonorMatrix */
    context: PropTypes.object.isRequired,
    /** Callback to retrieve row categories from matrix data */
    rowCategoryGetter: PropTypes.func.isRequired,
    /** Callback to retrieve subcategories from matrix data */
    rowSubCategoryGetter: PropTypes.func.isRequired,
    /** Callback to map row category query values */
    mapRowCategoryQueries: PropTypes.func.isRequired,
    /** Callback to map subcategory query values */
    mapSubCategoryQueries: PropTypes.func.isRequired,
    /** Matrix search result object with urls - @id and searchId having config=HumanDonorMatrix */
    pageContext: PropTypes.object.isRequired,
};

MatrixContent.contextTypes = {
    navigate: PropTypes.func,
    location_href: PropTypes.string,
};

/**
 * Map query values to a query-string component actually used in experiment matrix row category
 * link queries.
 * @param {string} rowCategory row category value to map
 * @param {object} rowCategoryBucket Matrix search result row bucket object
 *
 * @return {string} mapped row category query
 */
const mapRowCategoryQueriesExperiment = (rowCategory, rowCategoryBucket) => (
    `${rowCategory}=${encoding.encodedURIComponentOLD(rowCategoryBucket.key)}`
);

/**
 * Map query values to a query-string component actually used in experiment matrix subcategory link
 * queries.
 * @param {string} subCategory subcategory value to map
 * @param {string} subCategoryQuery subcategory query value to map
 * @param {object} rowCategoryBucket Matrix search result row bucket object
 *
 * @return {string} mapped subcategory query
 */
const mapSubCategoryQueriesExperiment = (subCategory, subCategoryQuery) => (
    `${subCategory}=${encoding.encodedURIComponentOLD(subCategoryQuery)}`
);

/**
 * View component for the experiment matrix page.
 */
class HumanDonorMatrix extends React.Component {
    constructor() {
        super();
        this.getRowCategories = this.getRowCategories.bind(this);
        this.getRowSubCategories = this.getRowSubCategories.bind(this);
    }

    /**
     * Called to retrieve row category data for the experiment matrix.
     */
    getRowCategories() {
        const rowCategory = this.props.context.matrix.y.group_by[0];
        const rowCategoryData = this.props.context.matrix.y[rowCategory].buckets;
        const rowCategoryColors = globals.biosampleTypeColors.colorList(rowCategoryData.map((rowCategoryDatum) => rowCategoryDatum.key));
        const rowCategoryNames = {};
        rowCategoryData.forEach((datum) => {
            rowCategoryNames[datum.key] = datum.key;
        });
        return {
            rowCategoryData,
            rowCategoryColors,
            rowCategoryNames,
        };
    }

    /**
     * Called to retrieve subcategory data for the experiment matrix.
     */
    getRowSubCategories(rowCategoryBucket) {
        const subCategoryName = this.props.context.matrix.y.group_by[1];
        return rowCategoryBucket[subCategoryName].buckets;
    }

    render() {
        const { context } = this.props;
        const itemClass = globals.itemClass(context, 'view-item');

        const contextKeys = Object.keys(context);
        const formattedContext = {};

        contextKeys.forEach((contextKey) => {
            let value = context[contextKey];

            if (removedQueryKeys.includes(contextKey)) {
                const contextQuery = new QueryString(value);

                contextQuery.deleteKeyValue('config');
                value = contextQuery.format();
            }

            formattedContext[contextKey] = value;
        });

        if (context.total > 0) {
            return (
                <Panel addClasses={itemClass}>
                    <PanelBody>
                        <MatrixHeader context={formattedContext} />
                        <MatrixLegends context={formattedContext} />
                        <MatrixContent context={formattedContext} pageContext={context} rowCategoryGetter={this.getRowCategories} rowSubCategoryGetter={this.getRowSubCategories} mapRowCategoryQueries={mapRowCategoryQueriesExperiment} mapSubCategoryQueries={mapSubCategoryQueriesExperiment} />
                    </PanelBody>
                </Panel>
            );
        }
        return <h4>No results found</h4>;
    }
}

HumanDonorMatrix.propTypes = {
    context: PropTypes.object.isRequired,
};

HumanDonorMatrix.contextTypes = {
    location_href: PropTypes.string,
    navigate: PropTypes.func,
    biosampleTypeColors: PropTypes.object, // DataColor instance for experiment project
};

globals.contentViews.register(HumanDonorMatrix, 'HumanDonorMatrix');


/**
 * Used for all facets that need suppression unconditionally.
 */
const SuppressedFacet = () => null;

FacetRegistry.Facet.register('audit.ERROR.category', SuppressedFacet, 'HumanDonorMatrix');
FacetRegistry.Facet.register('audit.NOT_COMPLIANT.category', SuppressedFacet, 'HumanDonorMatrix');
FacetRegistry.Facet.register('audit.WARNING.category', SuppressedFacet, 'HumanDonorMatrix');
