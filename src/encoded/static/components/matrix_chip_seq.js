import React, { useState } from 'react';
import PropTypes from 'prop-types';
import pluralize from 'pluralize';
import url from 'url';
import PubSub from 'pubsub-js';
import _ from 'underscore';
import QueryString from '../libs/query_string';
import { Panel, PanelBody, TabPanelPane } from '../libs/ui/panel';
import { Modal, ModalHeader, ModalBody } from '../libs/ui/modal';
import { svgIcon } from '../libs/svg-icons';
import * as globals from './globals';
import { MatrixBadges, DisplayAsJson } from './objectutils';
import { SearchFilter } from './matrix';
import { TextFilter } from './search';
import DataTable from './datatable';


const SEARCH_PERFORMED_PUBSUB = 'searchPerformed';
const CLEAR_SEARCH_BOX_PUBSUB = 'clearSearchBox';
const LARGE_MATRIX_MIN_SIZE = 150;

/**
 * Tranform context to a form where easier to fetch information
 *
 * @param {context} context - Context from react
 * @param {string} assayTitle - Assay Title
 * @param {string} organismName - Organism Name
 * @returns {object} - Object with structure - { chIPSeqData, subTabs };
 *
 *      chIPSeqData is an object where:
 *          key is a sub Tab
 *          value is of structure - { headerRow, dataRow, assayTitle, organismName };
 *              headerRow - header content-list
 *              dataRow - array of non-header content
 *                  key: biosample ontology classification
 *                  value: array containing counts
 *              assayTitle - Assay title
 *              organismName- Organism name
 *      subTabs: List of subTabs for easy access
 */
const getChIPSeqData = (context, assayTitle, organismName) => {
    if (!context || !context.matrix || !context.matrix.x || !context.matrix.y || !assayTitle || !organismName) {
        return null;
    }

    const subTabSource = 'biosample_ontology.classification';

    const subTabs = context.matrix.x[subTabSource].buckets.map(x => x.key);
    const chIPSeqData = {};

    subTabs.forEach((subTab) => {
        const xGroupBy1 = context.matrix.x.group_by[0];
        const xGroupBy2 = context.matrix.x.group_by[1];
        const headerRow = context.matrix.x[xGroupBy1].buckets.find(f => f.key === subTab)[xGroupBy2]
            .buckets
            .reduce((a, b) => a.concat(b), [])
            .map(x => x.key);
        const headerRowIndex = headerRow.reduce((x, y, z) => { x[y] = z; return x; }, []);
        const headerRowLength = headerRow.length;
        const yGroupBy1 = context.matrix.y.group_by[0];
        const yGroupBy2 = context.matrix.y.group_by[1];

        const yData = context.matrix.y[yGroupBy1].buckets
            .find(rBucket => rBucket.key === organismName)[yGroupBy2].buckets
            .reduce((a, b) => {
                const m = {};
                m[b.key] = b[xGroupBy1].buckets
                    .filter(f => f.key === subTab)
                    .reduce((x, y) => {
                        x.push([...y[xGroupBy2].buckets]
                            .reduce((i, j) => i.concat(j), []));
                        return x;
                    }, []);
                return a.concat(m);
            }, []);

        const dataRowT = {};

        yData.forEach((y) => {
            const yKey = Object.keys(y)[0];
            dataRowT[yKey] = dataRowT[yKey] || Array(headerRowLength + 1).fill(0);
            dataRowT[yKey][0] = yKey;

            const keyDocCountPair = y[yKey].reduce((a, b) => a.concat(b), []);

            keyDocCountPair.forEach((kp) => {
                const key = kp.key;
                const docCount = kp.doc_count;
                const index = headerRowIndex[key];
                dataRowT[yKey][index + 1] = docCount;
            });
        });

        let dataRow = [];
        const keys = Object.keys(dataRowT);

        // move biosample ontology classifications to dataRow-group
        keys.forEach((key) => {
            dataRow.push(dataRowT[key]);
        });

        // remove all rows with all 0's
        // Note- First entry is biosample ontology classification, does not count against 0's-row and is weedy out in the statement
        dataRow = dataRow.filter(data => data.some((content, index) => (content !== 0 && index !== 0)));

        chIPSeqData[subTab] = { headerRow, dataRow, assayTitle, organismName };
    });

    const subTabsSorted = subTabs.sort();

    // whole organisms should be moved to the front
    return {
        chIPSeqData,
        subTabs: [
            subTabsSorted.find(item => item === 'whole organisms'),
            ...subTabsSorted.filter(tab => tab !== 'whole organisms'),
        ].filter(tab => tab !== undefined),
    };
};


/**
 * Determines if the matrix update is large
 *
 * @param {*} currentChIPSeqData
 * @param {*} newChIPSeqData
 * @returns
 * Note- This is hacky and needs to be reconsidered
 */
const isMatrixUpdateLarge = (currentChIPSeqData, newChIPSeqData) => {
    const isCurrentMatrixLarge = currentChIPSeqData && currentChIPSeqData.dataRow && (currentChIPSeqData.dataRow.length > LARGE_MATRIX_MIN_SIZE);
    const isNewMatrixLarge = newChIPSeqData && newChIPSeqData.dataRow && (newChIPSeqData.dataRow.length > LARGE_MATRIX_MIN_SIZE);

    return isCurrentMatrixLarge || isNewMatrixLarge;
};

/**
 * Transform chIP Seq data to a form DataTable-object can understand.
 *
 * @param {chIPSeqData} chIPSeqData
 * @param {string} selectedTabLevel3 - Sub tab to use
 * @returns {object} DataTable-ready structure.
 */
const convertTargetDataToDataTable = (chIPSeqData, selectedTabLevel3) => {
    if (!chIPSeqData || !chIPSeqData.headerRow || !chIPSeqData.dataRow) {
        return {
            rows: [],
            rowKeys: [],
            tableCss: 'matrix',
        };
    }

    // add assay_title = Mint chip-seq if the assay selected in Histone chip-seq
    const isAssayTitleHistone = chIPSeqData.assayTitle === 'Histone ChIP-seq';

    const dataTable = [];
    const headerRow = chIPSeqData.headerRow.map(x => ({
        header: <a href={`/search/?type=Experiment&status=released&replicates.library.biosample.donor.organism.scientific_name=${chIPSeqData.organismName}&biosample_ontology.term_name=${x}&assay_title=${chIPSeqData.assayTitle}${isAssayTitleHistone ? '&assay_title=Mint-ChIP-seq' : ''}`} title={x}>{x}</a>,
    }));

    dataTable.push({
        rowContent: [{ header: null }, ...headerRow],
        css: 'matrix__col-category-header',
    });

    const rowLength = chIPSeqData.dataRow.length > 0 ? chIPSeqData.dataRow[0].length : 0;

    const rowData = chIPSeqData.dataRow.map((row, rIndex) => {
        const rowContent = row.map((y, yIndex) => {
            let content;

            if (yIndex === 0) {
                const borderLeft = '1px solid #fff'; // make left-most side border white
                content = {
                    header: <a href={`/search/?type=Experiment&status=released&target.label=${row[0]}&assay_title=${chIPSeqData.assayTitle}${isAssayTitleHistone ? '&assay_title=Mint-ChIP-seq' : ''}&replicates.library.biosample.donor.organism.scientific_name=${chIPSeqData.organismName}&biosample_ontology.classification=${selectedTabLevel3}`} title={y}>{y}</a>,
                    style: { borderLeft },
                };
            } else {
                const borderTop = rIndex === 0 ? '1px solid #f0f0f0' : ''; // add border color to topmost rows
                const backgroundColor = y === 0 ? '#FFF' : '#688878'; // determined if box is colored or not
                const borderRight = yIndex === rowLength - 1 ? '1px solid #f0f0f0' : ''; // add border color to right-most rows
                content = {
                    content: <a href={`/search/?type=Experiment&status=released&target.label=${row[0]}&assay_title=${chIPSeqData.assayTitle}${isAssayTitleHistone ? '&assay_title=Mint-ChIP-seq' : ''}&biosample_ontology.term_name=${chIPSeqData.headerRow[yIndex - 1]}&replicates.library.biosample.donor.organism.scientific_name=${chIPSeqData.organismName}&biosample_ontology.classification=${selectedTabLevel3}`} title={y}>&nbsp;</a>,
                    style: { backgroundColor, borderTop, borderRight },
                };
            }
            return content;
        });
        const css = 'matrix__row-data';

        return { rowContent, css };
    });

    dataTable.push(...rowData);

    const matrixConfig = {
        rows: dataTable,
        tableCss: 'matrix',
    };

    return matrixConfig;
};

/**
* First row of Tab- Organism
*
* id: Server name
* header: Name shown to user
* headerImage: Image shown beside header
* url: hyperlink (set by array's consumer)
*/
const tabLevel1 = [
    {
        id: 'Homo sapiens',
        header: 'Homo sapiens',
        headerImage: '/static/img/bodyMap/organisms/Homo-sapiens.svg',
        url: '',
    },
    {
        id: 'Mus musculus',
        header: 'Mus musculus',
        headerImage: '/static/img/bodyMap/organisms/Mus-musculus.svg',
        url: '',
    },
    {
        id: 'Caenorhabditis elegans',
        header: 'Caenorhabditis elegans',
        headerImage: '/static/img/bodyMap/organisms/Caenorhabditis-elegans.svg',
        url: '',
    },
    {
        id: 'Drosophila melanogaster',
        header: 'Drosophila melanogaster',
        headerImage: '/static/img/bodyMap/organisms/Drosophila-melanogaster.svg',
        url: '',
    },
];

/**
 * Second tab- Assay title
 *
 * id: Server name
 * header: Name shown to user
 * url: hyperlink (set by array's consumer)
 */
const tabLevel2 = [
    {
        id: 'Histone ChIP-seq',
        header: 'Histone',
        url: '',
    },
    {
        id: 'TF ChIP-seq',
        header: 'Transcription Factor',
        url: '',
    },
];


const assayTitlesOptions = tabLevel2.map(tab => tab.id);

/**
 *  Files (Drosophila melanogaster) and worms (Caenorhabditis elegans) exclude the Histone tab
 */
const organismsWithHiddenHistoneAssay = ['Drosophila melanogaster', 'Caenorhabditis elegans'];


const Spinner = ({ isActive }) => (
    <>
        {isActive ?
            <div className="communicating--centered">
                <div className="loading-spinner--centered">
                    <div className="loading-spinner-circle--centered" />
                </div>
            </div>
        : null}
    </>
);

Spinner.propTypes = {
    isActive: PropTypes.bool,
};

Spinner.defaultProps = {
    isActive: false,
};


/**
 * ChIP-Seq Matrix text filter.
 *
 *  Important to extend TextFilter because this class has functionality it lacks like
 *  knowing when to clear text book via Pubsub subscription
 *
 * @class ChIPSeqMatrixTextFilter
 * @extends {TextFilter}
 */
class ChIPSeqMatrixTextFilter extends TextFilter {
    constructor() {
        super();

        this.handleChange = this.handleChange.bind(this);
        this.clearSearch = this.clearSearch.bind(this);

        this.state = { searchOption: 'biosample' };
        this.searchBox = React.createRef();
    }

    componentDidMount() {
        this.clearSearchPubSub = PubSub.subscribe(CLEAR_SEARCH_BOX_PUBSUB, this.clearSearch);
    }

    componentWillUnmount() {
        PubSub.unsubscribe(this.clearSearchPubSub);
    }

    clearSearch() {
        if (this.searchBox && this.searchBox.current) {
            this.searchBox.current.value = '';
        }
    }

    onKeyDown(e) {
        if (e.keyCode === 13) {
            e.preventDefault();
            PubSub.publish(SEARCH_PERFORMED_PUBSUB, {
                text: e.target.value,
                option: this.state.searchOption,
            });
        }
    }

    handleChange(e) {
        this.setState({ searchOption: e.target.value });
    }

    render() {
        const filterText = this.state.searchOption === 'biosample' ?
            'Enter any text string such as lung or musc or H9 to filter biosample' :
            'Enter any text string such as ac or H3 to filter ChIP target';

        return (
            <div className="facet chip_seq_matrix-search">
                <input
                    type="search"
                    className="search-query"
                    placeholder={filterText}
                    defaultValue={this.getValue(this.props)}
                    onKeyDown={this.onKeyDown}
                    data-test="filter-search-box"
                    ref={this.searchBox}
                />
                <select name="searchOption" onChange={this.handleChange}>
                    <option value="biosample">Biosample</option>
                    <option value="target">Target</option>
                </select>
            </div>
        );
    }
}

/**
 * Hold code and markup for search
 *
 * SearchFilter extended rather than used because this class has function is does not like use
 * of ChIPSeqMatrixTextFilter
 *
 * @class ChIPSeqMatrixSearch
 * @extends {SearchFilter}
 */
class ChIPSeqMatrixSearch extends SearchFilter {
    render() {
        const { context } = this.props;
        const parsedUrl = url.parse(this.context.location_href);
        const matrixBase = parsedUrl.search || '';
        const matrixSearch = matrixBase + (matrixBase ? '&' : '?');
        const parsed = url.parse(matrixBase, true);
        const queryStringType = parsed.query.type || '';
        const type = pluralize(queryStringType.toLocaleLowerCase());
        return (
            <div className="matrix-general-search">
                <p>Enter filter terms to filter the {type} included in the matrix.</p>
                <div className="general-search-entry">
                    <i className="icon icon-filter" />
                    <div className="searchform">
                        <ChIPSeqMatrixTextFilter filters={context.filters} searchBase={matrixSearch} onChange={this.onChange} />
                    </div>
                </div>
            </div>
        );
    }
}

/**
* Render the area above the matrix itself, including the page title.
*/
const ChIPSeqMatrixHeader = (props) => {
    const [context] = useState(props.context);

    return (
        <div className="matrix-header">
            <div className="matrix-header__title">
                <div className="matrix-title-badge">
                    <h1>{context.title}</h1>
                    <MatrixBadges context={context} type="ChIPseq" />
                </div>
            </div>
            <div className="matrix-header__controls">
                <div className="matrix-header__target-filter-controls">
                    <ChIPSeqMatrixSearch context={context} />
                </div>
                <div className="matrix-header__target-search-controls">
                    <div className="results-table-control">
                        <div className="results-table-control__main">&nbsp;</div>
                        <div className="results-table-control__json">
                            <DisplayAsJson />
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

ChIPSeqMatrixHeader.propTypes = {
    context: PropTypes.object.isRequired,
};

const ChIPSeqMatrixContent = ({ context }) => (
    <div className="matrix__content matrix__content--target">
        <ChIPSeqMatrixPresentation context={context} />
    </div>
);

ChIPSeqMatrixContent.propTypes = {
    context: PropTypes.object.isRequired,
};

/**
 * Component for creating tab-markup.
 *
 * @class ChIPSeqTabPanel
 * @extends {React.Component}
 */
class ChIPSeqTabPanel extends React.Component {
    render() {
        const { tabList, navCss, moreComponents, moreComponentsClasses, tabFlange, decoration, decorationClasses, selectedTab, handleTabClick, fontColors } = this.props;
        let children = [];
        let firstPaneIndex = -1; // React.Children.map index of first <TabPanelPane> component

        // We expect to find <TabPanelPane> child elements inside <TabPanel>. For any we find, get
        // the React `key` value and copy it to an `id` value that we add to each child component.
        // That lets each child get an HTML ID matching `key` without having to pass both a key and
        // id with the same value. We also set the `active` property in the TabPanelPane component
        // here too so that each pane knows whether it's the active one or not. ### React14
        if (this.props.children) {
            children = React.Children.map(this.props.children, (child, i) => {
                if (child.type === TabPanelPane) {
                    firstPaneIndex = firstPaneIndex === -1 ? i : firstPaneIndex;

                    // Replace the existing child <TabPanelPane> component
                    const active = this.getCurrentTab() === child.key;
                    return React.cloneElement(child, { id: child.key, active });
                }
                return child;
            });
        }

        const baseUrl = '/chip-seq-matrix/?type=Experiment';

        return (
            <div className="chip_seq_matrix__data-wrapper">
                <div className="tab-nav">
                    <ul className={`nav-tabs${navCss ? ` ${navCss}` : ''}`} role="tablist">
                        {tabList.map((tab, index) => (
                            <li key={index} role="presentation" aria-controls={tab.id} className={selectedTab === tab.id ? 'active' : ''} title={tab.header}>
                                <a href={tab.url ? `${baseUrl}&${tab.url}&status=released` : ''} data-key={index} onClick={handleTabClick} style={{ color: fontColors ? fontColors[index] : 'black' }}>
                                    {tab.headerImage ? <img src={tab.headerImage} alt={tab.header} /> : '' }
                                    {tab.header}
                                </a>
                            </li>
                        ))}
                        {moreComponents ? <div className={moreComponentsClasses}>{moreComponents}</div> : null}
                    </ul>
                    {decoration ? <div className={decorationClasses}>{decoration}</div> : null}
                    {tabFlange ? <div className="tab-flange" /> : null}
                    <div className="tab-border" />
                </div>
                <div className="tab-content">
                    {children}
                </div>
            </div>
        );
    }
}

ChIPSeqTabPanel.propTypes = {
    /** Object with tab=>pane specifications */
    tabList: PropTypes.array.isRequired,
    /** key of tab to select; it's null for no-selection */
    selectedTab: PropTypes.string,
    /** Classes to add to navigation <ul> */
    navCss: PropTypes.string,
    /** Other components to render in the tab bar */
    moreComponents: PropTypes.object,
    /** Classes to add to moreComponents wrapper <div> */
    moreComponentsClasses: PropTypes.string,
    /** True to show a small full-width strip under active tab */
    tabFlange: PropTypes.bool,
    /** Component to render in the tab bar */
    decoration: PropTypes.object,
    /** CSS classes to wrap decoration in */
    decorationClasses: PropTypes.string,
    /** If selectedTab is provided, then parent must keep track of it */
    handleTabClick: PropTypes.func,
    children: PropTypes.node,
    /** Colors of the fonts */
    fontColors: PropTypes.array,
};

ChIPSeqTabPanel.contextTypes = {
    location_href: PropTypes.string,
    navigate: PropTypes.func,
};

ChIPSeqTabPanel.defaultProps = {
    fontColors: null,
    selectedTab: '',
    navCss: null,
    moreComponents: null,
    moreComponentsClasses: '',
    tabFlange: false,
    decoration: null,
    decorationClasses: null,
    handleTabClick: null,
    children: null,
};


/**
 * Used for creating modal pop up that gathers information on what organism a user wants to view.
 *
 */
const SelectOrganismModal = () => (
    <Modal>
        <ModalHeader closeModal={false} addCss="matrix__modal-header">
            <h2>ChIP-Seq Matrix &mdash; choose organism</h2>
        </ModalHeader>
        <ModalBody addCss="chip_seq_matrix__organism-selector">
            <div>Organism to view in matrix:</div>
            <div className="selectors">
                {tabLevel1.map((tab, index) =>
                    <a key={index} className={`btn btn-info btn__selector--${tab.id.replace(/ /g, '-')}`} href={`/chip-seq-matrix/?type=Experiment&replicates.library.biosample.donor.organism.scientific_name=${tab.id}&assay_title=Histone%20ChIP-seq&assay_title=Mint-ChIP-seq&status=released`}>{tab.header}</a>
                )}
            </div>
        </ModalBody>
    </Modal>);

/**
 * Container for ChIP-Seq Matrix page's content.
 *
 * @class ChIPSeqMatrixPresentation
 * @extends {React.Component}
 * @listens PubSub - SEARCH_PERFORMED_PUBSUB
 */
class ChIPSeqMatrixPresentation extends React.Component {
    constructor(props) {
        super(props);

        this.subTabClicked = this.subTabClicked.bind(this);
        this.performSearch = this.performSearch.bind(this);
        this.handleOnScroll = this.handleOnScroll.bind(this);
        this.handleScrollIndicator = this.handleScrollIndicator.bind(this);

        const { context } = this.props;
        const link = context['@id'];
        const query = new QueryString(link);
        const assayTitle = assayTitlesOptions.filter(tab => query.getKeyValues('assay_title').includes(tab))[0];
        const organismName = query.getKeyValues('replicates.library.biosample.donor.organism.scientific_name')[0];
        const selectedTabLevel1 = (tabLevel1.find(tab => tab.id === organismName) || tabLevel1[0]).id;
        const selectedTabLevel2 = (tabLevel2.find(tab => tab.id === assayTitle) || tabLevel2[0]).id;

        this.subTabs = [];
        this.ChIPSeqMatrixData = [];

        this.state = {
            chIPSeqData: [],
            scrolledRight: false,
            showOrganismRequest: false,
            spinnerActive: true,
            organismName,
            selectedTabLevel1,
            selectedTabLevel2,
        };
    }

    componentDidMount() {
        this.handleScrollIndicator(this.scrollElement);

        // extract ChIP-Seq Matrix data and get relevant values out
        const { context } = this.props;
        const link = context['@id'];
        const query = new QueryString(link);
        const assayTitle = query.getKeyValues('assay_title')[0];
        const organismName = query.getKeyValues('replicates.library.biosample.donor.organism.scientific_name')[0];
        const showOrganismRequest = !(assayTitle && organismName);

        // ALL ChIP-Seq Matrix data
        this.ChIPSeqMatrixData = getChIPSeqData(context, assayTitle, organismName);

        // sub tabs
        this.subTabs = this.ChIPSeqMatrixData ? this.ChIPSeqMatrixData.subTabs : [];

        // subtab may be in the url #, get it if it is there or default to first subtabs list value
        const storedSelectedTabLevel3 = window.sessionStorage.getItem('encodeSelectedTabLevel3');
        const selectedTabLevel3 = storedSelectedTabLevel3 && this.subTabs.includes(storedSelectedTabLevel3) ?
            storedSelectedTabLevel3 :
            this.subTabs.length > 0 ? this.ChIPSeqMatrixData.subTabs[0] : null;

        // Note: Hacky. If assay title is Histone and the organism is worm or fly, direct the user to TF assay title
        if (assayTitle === 'Histone ChIP-seq' && organismsWithHiddenHistoneAssay.includes(organismName)) {
            const tfUrl = link.replace('assay_title=Histone%20ChIP-seq', 'assay_title=TF ChIP-seq').replace('assay_title=Histone ChIP-seq', 'assay_title=TF ChIP-seq');
            this.context.navigate(tfUrl);
        }

        // sub chIP Seq data to display
        const chIPSeqData = this.ChIPSeqMatrixData ? this.ChIPSeqMatrixData.chIPSeqData[selectedTabLevel3] : {};
        const matrixUpdate = {
            chIPSeqData,
            selectedTabLevel3,
            showOrganismRequest, // determines if organism modal shows
        };

        const isMatrixLarge = isMatrixUpdateLarge(chIPSeqData, this.state.chIPSeqData);

        this.setState({ spinnerActive: true }, () => {
            if (!isMatrixLarge) {
                this.setState(matrixUpdate);
                this.setState({ spinnerActive: false });
            } else {
                // defer is used to allow ending of spinnner most likely after matrix is drawn. It is hacky.
                _.defer(() => {
                    this.setState(matrixUpdate, () => {
                        _.defer(() => {
                            this.setState({ spinnerActive: false });
                        });
                    });
                });
            }
        });

        this.searchSubcription = PubSub.subscribe(SEARCH_PERFORMED_PUBSUB, this.performSearch);
    }

    componentDidUpdate() {
        // Updates only happen for scrolling on this page. Every other update causes an
        // unmount/mount sequence.
        this.handleScrollIndicator(this.scrollElement);
    }

    // these are important to reset if code blows up
    componentDidCatch() {
        this.setState({ showOrganismRequest: false, spinnerActive: false });
    }

    componentWillUnmount() {
        PubSub.unsubscribe(this.searchSubcription);
    }

    /**
     * A subtab is clicked.
     *
     *  Its mains job is to extract required data from chIPSeqData object. This is computationally cheaper than
     *  refetching a new context and going off that.
     *
     * @param {object} e - event object
     * @memberof ChIPSeqMatrixPresentation
     */
    subTabClicked(e) {
        PubSub.publish(CLEAR_SEARCH_BOX_PUBSUB, {});
        const index = Number(e.target.dataset.key);
        const selectedTabLevel3 = this.subTabs[isNaN(index) ? 0 : index];
        window.sessionStorage.setItem('encodeSelectedTabLevel3', selectedTabLevel3);
        const chIPSeqData = this.ChIPSeqMatrixData.chIPSeqData[selectedTabLevel3];


        const isMatrixLarge = isMatrixUpdateLarge(chIPSeqData, this.state.chIPSeqData);

        this.setState({ spinnerActive: true }, () => {
            if (!isMatrixLarge) {
                this.setState({ chIPSeqData: null }, () => { // chIPSeqData set to null to prevent react from doing a diff
                    this.setState({ selectedTabLevel3, chIPSeqData }, () => {
                        this.setState({ spinnerActive: false });
                    });
                });
            } else {
                // defer is used to allow ending of spinner most likely aferr painting of matrix DOM is complete. It is hacky.
                _.defer(() => {
                    this.setState({ chIPSeqData: null }, () => { // chIPSeqData set to null to prevent react from doing a diff
                        this.setState({ selectedTabLevel3, chIPSeqData }, () => {
                            _.defer(() => {
                                this.setState({ spinnerActive: false });
                            });
                        });
                    });
                });
            }
        });
    }

    /**
     * User is searching
     *
     * PubSub used because it is easier to let anyone clear search box and/or get search data
     *
     * @param {string} message - Message from PubSub
     * @param {object} searchData - Information on what search user is doing
     * @memberof ChIPSeqMatrixPresentation
     */
    performSearch(message, searchData) {
        const searchText = searchData.text.toLocaleLowerCase().trim();
        const chIPSeqData = Object.assign({}, this.ChIPSeqMatrixData.chIPSeqData[this.state.selectedTabLevel3]);
        let dataRow = [];
        let headerRow = [];

        if (searchText) {
            const searchField = searchData.option === 'biosample' ? 'headerRow' : 'dataRow';
            const selectedAxis = chIPSeqData[searchField] || [];

            // searching biosample
            if (searchField === 'headerRow') {
                const filterResultIndexes = selectedAxis.map((m, i) => {
                    if (m.toLocaleLowerCase().indexOf(searchText) !== -1) {
                        return i;
                    }
                    return null;
                }).filter(m => m !== null);

                const dataRowLength = chIPSeqData.dataRow.length;

                // .fill([]) duplicate the same array reference rather than create a new array
                // so map was used
                dataRow = [...Array(dataRowLength)].map(() => []);

                headerRow = [];

                filterResultIndexes.forEach((i) => {
                    headerRow.push(chIPSeqData.headerRow[i]);
                });

                for (let j = 0; j < dataRowLength; j += 1) {
                    // get text of first entry
                    dataRow[j].push(chIPSeqData.dataRow[j][0]);

                    // get entries other than the first
                    for (let k = 0; k < filterResultIndexes.length; k += 1) {
                        // header row is offset by 1 compared to data row
                        dataRow[j].push(chIPSeqData.dataRow[j][filterResultIndexes[k] + 1]);
                    }
                }
            } else { // searching target
                dataRow = selectedAxis.map(y => (y[0].trim().toLocaleLowerCase().indexOf(searchText) !== -1 ? y : null)).filter(f => f !== null);
                headerRow = chIPSeqData.headerRow;
            }

            // clear data if both data or header row if either is empty, so show no-data message
            if (headerRow.length === 0) {
                dataRow = [];
            } else if (dataRow.length === 0) {
                headerRow = [];
            }

            chIPSeqData.headerRow = headerRow;
            chIPSeqData.dataRow = dataRow;
        }

        const isMatrixLarge = isMatrixUpdateLarge(chIPSeqData, this.state.chIPSeqData);

        this.setState({ spinnerActive: true }, () => {
            if (!isMatrixLarge) {
                this.setState({ chIPSeqData: null }, () => {
                    this.setState({ chIPSeqData }, () => {
                        this.setState({ spinnerActive: false });
                    });
                });
            } else {
                // defer is used to allow painting of DOM after matrix is drawn. It is hacky.
                _.defer(() => {
                    this.setState({ chIPSeqData: null }, () => {
                        this.setState({ chIPSeqData }, () => {
                            _.defer(() => {
                                this.setState({ spinnerActive: false });
                            });
                        });
                    });
                });
            }
        });
    }


    /**
     * Called when the user scrolls the matrix horizontally within its div to handle scroll
     * indicators
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
        if (element) {
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
        } else if (!this.state.scrolledRight) {
            this.setState({ scrolledRight: true });
        }
    }

    render() {
        const { context } = this.props;
        const { scrolledRight, chIPSeqData, showOrganismRequest, selectedTabLevel1, selectedTabLevel2, selectedTabLevel3, spinnerActive, organismName } = this.state;
        const subTabsHeaders = this.subTabs.map((subTab, index) => ({ // subtabs formatted to for displaying
            id: (subTab || index.toString()).trim(' '),
            header: subTab,
        }));

        // NOTE: In fly (Drosophila melanogaster) and worm (Caenorhabditis elegans), Histone ChIP-seq are hidden
        const hideAssayTitle = selectedTabLevel1 && organismsWithHiddenHistoneAssay.includes(selectedTabLevel1);
        const filteredTabLevel2 = hideAssayTitle ?
            tabLevel2.filter(tab => tab.id !== 'Histone ChIP-seq') :
            tabLevel2;

        for (let i = 0; i < tabLevel1.length; i += 1) {
            const tab1 = tabLevel1[i];
            tab1.url = `replicates.library.biosample.donor.organism.scientific_name=${tab1.id}&assay_title=${selectedTabLevel2}${selectedTabLevel2 === 'Histone ChIP-seq' ? '&assay_title=Mint-ChIP-seq' : ''}`;
        }

        for (let i = 0; i < tabLevel2.length; i += 1) {
            const assay = tabLevel2[i].id;
            tabLevel2[i].url = `replicates.library.biosample.donor.organism.scientific_name=${organismName}&assay_title=${assay}${assay === 'Histone ChIP-seq' ? '&assay_title=Mint-ChIP-seq' : ''}`;
        }

        return (
            <div className="matrix__presentation">
                <Spinner isActive={spinnerActive} />
                <div className={`matrix__label matrix__label--horz${!scrolledRight ? ' horz-scroll' : ''}`}>
                    <span>biosample</span>
                    {svgIcon('largeArrow')}
                </div>
                <div className="matrix__presentation-content">
                    <div className="matrix__label matrix__label--vert"><div>{svgIcon('largeArrow')}{context.matrix.y.label}</div></div>
                    {showOrganismRequest ? <SelectOrganismModal /> : null }
                    <ChIPSeqTabPanel tabList={tabLevel1} selectedTab={selectedTabLevel1} navCss="organism-tab">
                        <ChIPSeqTabPanel tabList={filteredTabLevel2} selectedTab={selectedTabLevel2}>
                            <ChIPSeqTabPanel tabList={subTabsHeaders} selectedTab={selectedTabLevel3} handleTabClick={this.subTabClicked}>
                                {chIPSeqData && chIPSeqData.headerRow && chIPSeqData.headerRow.length !== 0 && chIPSeqData.dataRow && chIPSeqData.dataRow.length !== 0 ?
                                      <div className="chip_seq_matrix__data" onScroll={this.handleOnScroll} ref={(element) => { this.scrollElement = element; }}>
                                          <DataTable tableData={convertTargetDataToDataTable(chIPSeqData, selectedTabLevel3)} />
                                      </div>
                                  :
                                      <div className="chip_seq_matrix__warning">
                                          { chIPSeqData && Object.keys(chIPSeqData).length === 0 ? 'Select an organism to view data.' : 'No data to display.' }
                                      </div>
                                }
                            </ChIPSeqTabPanel>
                        </ChIPSeqTabPanel>
                    </ChIPSeqTabPanel>
                </div>
            </div>);
    }
}

ChIPSeqMatrixPresentation.propTypes = {
    context: PropTypes.object.isRequired,
};

ChIPSeqMatrixPresentation.contextTypes = {
    navigate: PropTypes.func,
    location_href: PropTypes.string,
    session: PropTypes.object,
    session_properties: PropTypes.object,
};


/**
 * Container for ChIP-Seq Matrix page.
 *
 * @param {context}  context - Context object
 * @returns
 */
const ChIPSeqMatrix = ({ context }) => {
    const itemClass = globals.itemClass(context, 'view-item');

    return (
        <Panel addClasses={itemClass}>
            <PanelBody>
                <ChIPSeqMatrixHeader context={context} />
                <ChIPSeqMatrixContent context={context} />
            </PanelBody>
        </Panel>
    );
};

ChIPSeqMatrix.propTypes = {
    context: PropTypes.object.isRequired,
};

ChIPSeqMatrix.contextTypes = {
    location_href: PropTypes.string,
    navigate: PropTypes.func,
    biosampleTypeColors: PropTypes.object, // DataColor instance for experiment project
};

globals.contentViews.register(ChIPSeqMatrix, 'ChipSeqMatrix');
