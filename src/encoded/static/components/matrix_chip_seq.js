import React from 'react';
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
import { MatrixInternalTags, DisplayAsJson } from './objectutils';
import { SearchFilter } from './matrix';
import { TextFilter } from './search';
import DataTable from './datatable';


const SEARCH_PERFORMED_PUBSUB = 'searchPerformed';
const SEARCH_RESULT_COUNT_PUBSUB = 'searchResultCount';
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

    return {
        chIPSeqData,
        subTabs: subTabs.sort(),
    };
};


/**
 * Get search result-count
 *
 * @param {chIPSeqData} chIPSeqData
 * @returns Number 0 or higher that corresponds to search count
 */
const getSearchResultCount = (chIPSeqData) => {
    const count = chIPSeqData.dataRow
        .reduce((a, b) => [...a, ...b], [])
        .filter(i => !isNaN(i))
        .reduce((a, b) => a + b, 0);

    return count;
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
 * @param {string} selectedSubTab - Sub tab to use
 * @returns {object} DataTable-ready structure.
 */
const convertTargetDataToDataTable = (chIPSeqData, selectedSubTab) => {
    if (!chIPSeqData || !chIPSeqData.headerRow || !chIPSeqData.dataRow) {
        return {
            rows: [],
            rowKeys: [],
            tableCss: 'matrix',
        };
    }

    const dataTable = [];
    const headerRow = chIPSeqData.headerRow.map(x => ({
        header: <a href={`/search/?type=Experiment&status=released&replicates.library.biosample.donor.organism.scientific_name=${chIPSeqData.organismName}&biosample_ontology.term_name=${x}&assay_title=${chIPSeqData.assayTitle}`} title={x}>{x}</a>,
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
                    header: <a href={`/search/?type=Experiment&status=released&target.label=${row[0]}&assay_title=${chIPSeqData.assayTitle}&replicates.library.biosample.donor.organism.scientific_name=${chIPSeqData.organismName}&biosample_ontology.classification=${selectedSubTab}`} title={y}>{y}</a>,
                    style: { borderLeft },
                };
            } else {
                const borderTop = rIndex === 0 ? '1px solid #f0f0f0' : ''; // add border color to topmost rows
                const backgroundColor = y === 0 ? '#FFF' : '#688878'; // determined if box is colored or not
                const borderRight = yIndex === rowLength - 1 ? '1px solid #f0f0f0' : ''; // add border color to right-most rows
                content = {
                    content: <a href={`/search/?type=Experiment&status=released&target.label=${row[0]}&assay_title=${chIPSeqData.assayTitle}&biosample_ontology.term_name=${chIPSeqData.headerRow[yIndex - 1]}&replicates.library.biosample.donor.organism.scientific_name=${chIPSeqData.organismName}&biosample_ontology.classification=${selectedSubTab}`} title={y}>&nbsp;</a>,
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
 * Tab data
 *
 * Note: The server does not return all of this data. So it is hard-coded to make it ever-available.
 */
const tabs = [
    {
        organismName: 'Homo sapiens',
        assayTitle: 'Histone ChIP-seq',
        title: 'Homo sapiens | Histone',
        url: 'replicates.library.biosample.donor.organism.scientific_name=Homo sapiens&assay_title=Histone ChIP-seq',
    }, {
        organismName: 'Homo sapiens',
        assayTitle: 'TF ChIP-seq',
        title: 'Homo sapiens | TF',
        url: 'replicates.library.biosample.donor.organism.scientific_name=Homo sapiens&assay_title=TF ChIP-seq',
    }, {
        organismName: 'Mus musculus',
        assayTitle: 'Histone ChIP-seq',
        title: 'Mus musculus | Histone',
        url: 'replicates.library.biosample.donor.organism.scientific_name=Mus musculus&assay_title=Histone ChIP-seq',
    }, {
        organismName: 'Mus musculus',
        assayTitle: 'TF ChIP-seq',
        title: 'Mus musculus | TF',
        url: 'replicates.library.biosample.donor.organism.scientific_name=Mus musculus&assay_title=TF ChIP-seq',
    },
];

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
 *
 * @class ChIPSeqMatrixHeader
 * @extends {React.Component}
 */
class ChIPSeqMatrixHeader extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            context: this.props.context,
            searchResultCount: this.props.context.total,
        };
        this.setSearchResultCount = this.setSearchResultCount.bind(this);
    }

    componentDidMount() {
        this.searchCount = PubSub.subscribe(SEARCH_RESULT_COUNT_PUBSUB, this.setSearchResultCount);
    }

    componentWillUnmount() {
        PubSub.unsubscribe(this.searchCount);
    }

    setSearchResultCount(message, searchResultCount) {
        this.setState({ searchResultCount });
    }

    render() {
        return (
            <div className="matrix-header">
                <div className="matrix-header__title">
                    <h1>{this.state.context.title}</h1>
                    <div className="matrix-tags">
                        <MatrixInternalTags context={this.state.context} />
                    </div>
                </div>
                <div className="matrix-header__controls">
                    <div className="matrix-header__target-filter-controls">
                        <ChIPSeqMatrixSearch context={this.state.context} />
                    </div>
                    <div className="matrix-header__target-search-controls">
                        <h4>Showing {this.state.searchResultCount} results</h4>
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
    }
}


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
                            <li key={index} role="presentation" aria-controls={tab.title} className={selectedTab === tab.title ? 'active' : ''}>
                                <a href={tab.url ? `${baseUrl}&${tab.url}&status=released` : ''} data-key={index} onClick={handleTabClick} style={{ color: fontColors ? fontColors[index] : 'black' }}>
                                    {tab.title}
                                </a>
                            </li>
                        ))}
                        {moreComponents ? <div className={moreComponentsClasses}>{moreComponents}</div> : null}
                    </ul>
                    {decoration ? <div className={decorationClasses}>{decoration}</div> : null}
                    {tabFlange ? <div className="tab-flange" /> : null}
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
    /** key of tab to select (must provide handleTabClick) too; null for no selection */
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
                {['Homo sapiens', 'Mus musculus'].map((organism, index) =>
                    <a key={index} className={`btn btn-info btn__selector--${organism.replace(/ /g, '-')}`} href={`/chip-seq-matrix/?type=Experiment&replicates.library.biosample.donor.organism.scientific_name=${organism}&assay_title=Histone%20ChIP-seq&status=released`}>{organism}</a>
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
        const assayTitle = query.getKeyValues('assay_title')[0];
        const organismName = query.getKeyValues('replicates.library.biosample.donor.organism.scientific_name')[0];
        const selectedTab = (tabs.find(tab => tab.assayTitle === assayTitle && tab.organismName === organismName) || tabs[0]).title;

        this.subTabs = [];
        this.ChIPSeqMatrixData = [];

        this.state = {
            chIPSeqData: [],
            selectedTab,
            selectedSubTab: null,
            scrolledRight: false,
            showOrganismRequest: false,
            spinnerActive: true,
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
        const storedSelectedSubTab = window.sessionStorage.getItem('encodeSelectedSubTab');
        const selectedSubTab = storedSelectedSubTab && this.subTabs.includes(storedSelectedSubTab) ?
            storedSelectedSubTab :
            this.subTabs.length > 0 ? this.ChIPSeqMatrixData.subTabs[0] : null;

        // sub chIP Seq data to display
        const chIPSeqData = this.ChIPSeqMatrixData ? this.ChIPSeqMatrixData.chIPSeqData[selectedSubTab] : {};
        const matrixUpdate = {
            chIPSeqData,
            selectedSubTab,
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
        const selectedSubTab = this.subTabs[isNaN(index) ? 0 : index];
        window.sessionStorage.setItem('encodeSelectedSubTab', selectedSubTab);
        const chIPSeqData = this.ChIPSeqMatrixData.chIPSeqData[selectedSubTab];
        const count = getSearchResultCount(chIPSeqData);
        PubSub.publish(SEARCH_RESULT_COUNT_PUBSUB, count);

        const isMatrixLarge = isMatrixUpdateLarge(chIPSeqData, this.state.chIPSeqData);

        this.setState({ spinnerActive: true }, () => {
            if (!isMatrixLarge) {
                this.setState({ chIPSeqData: null }, () => { // chIPSeqData set to null to prevent react from doing a diff
                    this.setState({ selectedSubTab, chIPSeqData }, () => {
                        this.setState({ spinnerActive: false });
                    });
                });
            } else {
                // defer is used to allow ending of spinner most likely aferr painting of matrix DOM is complete. It is hacky.
                _.defer(() => {
                    this.setState({ chIPSeqData: null }, () => { // chIPSeqData set to null to prevent react from doing a diff
                        this.setState({ selectedSubTab, chIPSeqData }, () => {
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
        const chIPSeqData = Object.assign({}, this.ChIPSeqMatrixData.chIPSeqData[this.state.selectedSubTab]);
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

        const count = getSearchResultCount(chIPSeqData);
        PubSub.publish(SEARCH_RESULT_COUNT_PUBSUB, count);

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
        const { scrolledRight, chIPSeqData, showOrganismRequest, selectedSubTab, spinnerActive } = this.state;
        const fontColors = globals.biosampleTypeColors.colorList(this.subTabs, { merryGoRoundColors: true });
        const subTabsHeaders = this.subTabs.map(subTab => ({ title: subTab })); // subtabs formatted to for displaying

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
                    <ChIPSeqTabPanel tabList={tabs} selectedTab={this.state.selectedTab} tabPanelCss="matrix__data-wrapper">
                        <ChIPSeqTabPanel tabList={subTabsHeaders} selectedTab={selectedSubTab} tabPanelCss="matrix__data-wrapper" handleTabClick={this.subTabClicked} fontColors={fontColors}>
                            {chIPSeqData && chIPSeqData.headerRow && chIPSeqData.headerRow.length !== 0 && chIPSeqData.dataRow && chIPSeqData.dataRow.length !== 0 ?
                                  <div className="chip_seq_matrix__data" onScroll={this.handleOnScroll} ref={(element) => { this.scrollElement = element; }}>
                                      <DataTable tableData={convertTargetDataToDataTable(chIPSeqData, selectedSubTab)} />
                                  </div>
                              :
                                  <div className="chip_seq_matrix__warning">
                                      { chIPSeqData && Object.keys(chIPSeqData).length === 0 ? 'Select an organism to view data.' : 'No data to display.' }
                                  </div>
                            }
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
