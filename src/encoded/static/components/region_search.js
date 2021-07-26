import React from 'react';
import PropTypes from 'prop-types';
import url from 'url';
import { Panel, PanelBody, TabPanel } from '../libs/ui/panel';
import GenomeBrowser from './genome_browser';
import * as globals from './globals';
import getSeriesData from './series_search.js';
import { FacetList, Listing } from './search';
import { ASSEMBLY_DETAILS, BrowserSelector } from './vis_defines';
import {
    SearchBatchDownloadController,
    BatchDownloadActuator,
} from './batch_download';
import { svgIcon } from '../libs/svg-icons';
import QueryString from '../libs/query_string';
import { FetchedData, Param } from './fetched';

const regionGenomes = [
    { value: 'GRCh37', display: 'hg19' },
    { value: 'GRCh38', display: 'GRCh38' },
    { value: 'GRCm37', display: 'mm9' },
    { value: 'GRCm38', display: 'mm10' },
];

const AutocompleteBox = (props) => {
    const terms = props.auto['@graph']; // List of matching terms from server
    const { handleClick } = props;
    const userTerm = props.userTerm && props.userTerm.toLowerCase(); // Term user entered

    if (!props.hide && userTerm && userTerm.length > 0 && terms && terms.length > 0) {
        return (
            <ul className="adv-search-autocomplete">
                {terms.map((term) => {
                    let matchEnd;
                    let preText;
                    let matchText;
                    let postText;

                    // Boldface matching part of term
                    const matchStart = term.text.toLowerCase().indexOf(userTerm);
                    if (matchStart >= 0) {
                        matchEnd = matchStart + userTerm.length;
                        preText = term.text.substring(0, matchStart);
                        matchText = term.text.substring(matchStart, matchEnd);
                        postText = term.text.substring(matchEnd);
                    } else {
                        preText = term.text;
                    }
                    return (
                        <AutocompleteBoxMenu
                            key={term.text}
                            handleClick={handleClick}
                            term={term}
                            name={props.name}
                            preText={preText}
                            matchText={matchText}
                            postText={postText}
                        />
                    );
                }, this)}
            </ul>
        );
    }

    return null;
};

AutocompleteBox.propTypes = {
    auto: PropTypes.object,
    userTerm: PropTypes.string,
    handleClick: PropTypes.func,
    hide: PropTypes.bool,
    name: PropTypes.string,
};

AutocompleteBox.defaultProps = {
    auto: {}, // Looks required, but because it's built from <Param>, it can fail type checks.
    userTerm: '',
    handleClick: null,
    hide: false,
    name: '',
};


// Draw the autocomplete box drop-down menu.
class AutocompleteBoxMenu extends React.Component {
    constructor() {
        super();

        // Bind this to non-React methods.
        this.handleClick = this.handleClick.bind(this);
    }

    // Handle clicks in the drop-down menu. It just calls the parent's handleClick function, giving
    // it the parameters of the clicked item.
    handleClick() {
        const { term, name } = this.props;
        this.props.handleClick(term.text, term._source.payload.id, name);
    }

    render() {
        const { preText, matchText, postText } = this.props;

        /* eslint-disable jsx-a11y/no-noninteractive-element-interactions, jsx-a11y/no-noninteractive-tabindex, jsx-a11y/click-events-have-key-events */
        return (
            <li tabIndex="0" onClick={this.handleClick}>
                {preText}<b>{matchText}</b>{postText}
            </li>
        );
        /* eslint-enable jsx-a11y/no-noninteractive-element-interactions, jsx-a11y/no-noninteractive-tabindex, jsx-a11y/click-events-have-key-events */
    }
}

AutocompleteBoxMenu.propTypes = {
    handleClick: PropTypes.func.isRequired, // Parent function to handle a click in a drop-down menu item
    term: PropTypes.object.isRequired, // Object for the term being searched
    name: PropTypes.string,
    preText: PropTypes.string, // Text before the matched term in the entered string
    matchText: PropTypes.string, // Matching text in the entered string
    postText: PropTypes.string, // Text after the matched term in the entered string
};

AutocompleteBoxMenu.defaultProps = {
    name: '',
    preText: '',
    matchText: '',
    postText: '',
};


class AdvSearch extends React.Component {
    constructor() {
        super();

        // Set initial React state.
        /* eslint-disable react/no-unused-state */
        // Need to disable this rule because of a bug in eslint-plugin-react.
        // https://github.com/yannickcr/eslint-plugin-react/issues/1484#issuecomment-366590614
        this.state = {
            disclosed: false,
            showAutoSuggest: false,
            searchTerm: '',
            coordinates: '',
            genome: '',
            terms: {},
        };
        /* eslint-enable react/no-unused-state */

        // Bind this to non-React methods.
        this.handleDiscloseClick = this.handleDiscloseClick.bind(this);
        this.handleChange = this.handleChange.bind(this);
        this.handleAutocompleteClick = this.handleAutocompleteClick.bind(this);
        this.handleAssemblySelect = this.handleAssemblySelect.bind(this);
        this.handleOnFocus = this.handleOnFocus.bind(this);
        this.tick = this.tick.bind(this);
    }

    componentDidMount() {
        // Use timer to limit to one request per second
        this.timer = setInterval(this.tick, 1000);
    }

    componentWillUnmount() {
        clearInterval(this.timer);
    }

    handleDiscloseClick() {
        this.setState((prevState) => ({
            disclosed: !prevState.disclosed,
        }));
    }

    handleChange(e) {
        this.setState({ showAutoSuggest: true, terms: {} });
        this.newSearchTerm = e.target.value;
    }

    handleAutocompleteClick(term, id, name) {
        const newTerms = {};
        const inputNode = this.annotation;
        inputNode.value = term;
        newTerms[name] = id;
        this.setState({ terms: newTerms, showAutoSuggest: false });
        inputNode.focus();
        // Now let the timer update the terms state when it gets around to it.
    }

    handleAssemblySelect(event) {
        // Handle click in assembly-selection <select>
        this.setState({ genome: event.target.value });
    }

    handleOnFocus() {
        this.setState({ showAutoSuggest: false });
    }

    tick() {
        if (this.newSearchTerm !== this.state.searchTerm) {
            this.setState({ searchTerm: this.newSearchTerm });
        }
    }

    render() {
        const context = this.props;
        const id = url.parse(this.context.location_href, true);
        const region = id.query.region || '';

        if (this.state.genome === '') {
            let assembly = regionGenomes[0].value;
            if (this.props.assembly) {
                assembly = regionGenomes.find((el) => (
                    this.props.assembly === el.value || this.props.assembly === el.display
                )).value;
            }
            this.setState({ genome: assembly });
        }

        return (
            <Panel>
                <PanelBody>
                    <form id="panel1" className="adv-search-form" autoComplete="off" aria-labelledby="tab1" onSubmit={this.handleOnFocus}>
                        <input type="hidden" name="annotation" value={this.state.terms.annotation} />
                        <label htmlFor="annotation">Enter any one of human Gene name, Symbol, Synonyms, Gene ID, HGNC ID, coordinates, rsid, Ensemble ID</label>
                        <div className="adv-search-form__input">
                            <input id="annotation" ref={(input) => { this.annotation = input; }} defaultValue={region} name="region" type="text" className="form-control" onChange={this.handleChange} />
                            {(this.state.showAutoSuggest && this.state.searchTerm) ?
                                <FetchedData loadingComplete>
                                    <Param name="auto" url={`/suggest/?genome=${this.state.genome}&q=${this.state.searchTerm}`} type="json" />
                                    <AutocompleteBox name="annotation" userTerm={this.state.searchTerm} handleClick={this.handleAutocompleteClick} />
                                </FetchedData>
                            : null}
                            <select value={this.state.genome} name="genome" onFocus={this.closeAutocompleteBox} onChange={this.handleAssemblySelect}>
                                {regionGenomes.map((genomeId) => (
                                    <option key={genomeId.value} value={genomeId.value}>{genomeId.display}</option>
                                ))}
                            </select>
                        </div>
                        {context.notification ?
                            <p className="adv-search-form__notification">{context.notification}</p>
                        : null}
                        <div className="adv-search-form__submit">
                            <input type="submit" value="Search" className="btn btn-info" />
                        </div>
                    </form>
                    {context.coordinates ?
                        <p>Searched coordinates: <strong>{context.coordinates}</strong></p>
                    : null}
                </PanelBody>
            </Panel>
        );
    }
}

AdvSearch.propTypes = {
    context: PropTypes.object.isRequired,
};

AdvSearch.contextTypes = {
    autocompleteTermChosen: PropTypes.bool,
    autocompleteHidden: PropTypes.bool,
    onAutocompleteHiddenChange: PropTypes.func,
    location_href: PropTypes.string,
};

// Default assembly for each organism
const defaultAssemblyByOrganism = {
    'Homo sapiens': 'GRCh38',
    'Mus musculus': 'mm10',
};

// The encyclopedia page displays a table of results corresponding to a selected annotation type
const Encyclopedia = (props, context) => {
    const defaultAssembly = 'GRCh38';
    const defaultFileDownload = 'all';
    const defaultVisualization = 'List View';
    const visualizationOptions = ['List View', 'Genome Browser'];
    const encyclopediaVersion = 'ENCODE v5';
    const searchBase = url.parse(context.location_href).search || '';

    const [selectedVisualization, setSelectedVisualization] = React.useState(defaultVisualization);
    const [selectedAssembly, setAssembly] = React.useState(defaultAssembly);
    const [assemblyList, setAssemblyList] = React.useState([defaultAssembly]);

    var browser_files = [];

    const results = props.context['@graph'];
    results.forEach((res) => {
	res['files'].forEach((file) => {
	    if (file['preferred_default'] && (file['file_format'] == 'bigBed' || file['file_format'] == 'bigWig')) {
		browser_files.push(file);
	    }
	});
    });

    // Data which populates the browser
    const [vizFiles, setVizFiles] = React.useState(browser_files);

    // vizFilesError is true when there are no results for selected filters
    const [vizFilesError, setVizFilesError] = React.useState(false);
    // Number of files available is displayed
    const [totalFiles, setTotalFiles] = React.useState(browser_files.length);

    // Update assembly, organism, browser files, and download link when user clicks on tab
    const handleTabClick = (tab) => {
        setVizFiles([]);
        setAssembly(defaultAssemblyByOrganism[tab]);
    };

    const { columns, notification, filters, facets, total } = props.context;
//    const results = props.context['@graph'];
    const trimmedSearchBase = searchBase.replace(/[?|&]limit=all/, '');
    

    // Maximum number of selected items that can be visualized.
    const VISUALIZE_LIMIT = 100;
    const visualizeDisabledTitle = total > VISUALIZE_LIMIT ? `Filter to ${VISUALIZE_LIMIT} to visualize` : '';

    const onFilter = (e) => {
        if (this.props.onChange) {
            const search = e.currentTarget.getAttribute('href');
            this.props.onChange(search);
            e.stopPropagation();
            e.preventDefault();
        }
    }

    const visualizationTabs = {};
    visualizationOptions.forEach((visualizationName) => {
	visualizationTabs[visualizationName] = <div id={visualizationName} className={`organism-button ${visualizationName.replace(' ', '-')}`}><span>{visualizationName}</span></div>;
    });


    const listView = (
	<Panel>
            <PanelBody>
                            <div className="search-results">
	                        <div className="search-results__facets">
                                    <FacetList
                                        context={props.context}
                                        facets={facets}
                                        filters={filters}
                                        onFilter={onFilter}
                                    />
                                </div>

                                <div className="search-results__result-list">
                                    <h4>
                                        Showing {results.length} of {total}
                                    </h4>
                                    <div className="results-table-control__main">
                                        {total > results.length && searchBase.indexOf('limit=all') === -1 ?
                                                <a
                                                    rel="nofollow"
                                                    className="btn btn-info btn-sm"
                                                    href={searchBase ? `${searchBase}&limit=all` : '?limit=all'}
                                                    onClick={onFilter}
                                                >
                                                    View All
                                                </a>
                                        :
                                            <span>
                                                {results.length > 25 ?
                                                        <a
                                                            className="btn btn-info btn-sm"
                                                            href={trimmedSearchBase || '/region-search/'}
                                                            onClick={onFilter}
                                                        >
                                                            View 25
                                                        </a>
                                                : null}
                                            </span>
                                        }
                                    </div>
                                    <br />
                                    <ul className="nav result-table" id="result-table">
                                        {results.map((result) => Listing({ context: result, columns, key: result['@id'] }))}
                                    </ul>
                                </div>
                            </div>
                       </PanelBody>
                    </Panel>
    );

    const genomeBrowserView = (
	    <div className="outer-tab-container">
                <div className="tab-body">
                    <Panel>
	                <PanelBody>
	                    <div className="search-results">
	                        <div className="search-results__facets">
                                    <FacetList
                                        context={props.context}
                                        facets={facets}
                                        filters={filters}
                                        onFilter={onFilter}
                                    />
                                </div>

                                <div className="search-results__result-list" style={{display: "block"}}>
                                    <GenomeBrowser
                                        files={vizFiles}
                                        label="cart"
//                                        expanded
                                        assembly={selectedAssembly}
                                        annotation="V33"
  //                                      displaySort
                                        maxCharPerLine={30}
                                    />
                                </div>
	                    </div>
                        </PanelBody>
	            </Panel>
                </div>
          </div>
    );

    return (
        <div className="layout">
            <div className="layout__block layout__block--100">
                <div className="block series-search">
                    <div className="encyclopedia-info-wrapper">
                        <div className="badge-container">
                            <h1>Region Search</h1>
                            <span className="encyclopedia-badge">{encyclopediaVersion}</span>
                        </div>
                    </div>

                    <AdvSearch  {...props.context}/>

                    <div className="outer-tab-container">
                        <TabPanel
                            tabs={visualizationTabs}
                            selectedTab={selectedVisualization}
                            handleTabClick={(tab) => setSelectedVisualization(tab)}
                            tabCss="tab-button"
                            tabPanelCss="tab-container encyclopedia-tabs"
                        >
                            { selectedVisualization == 'List View' ? listView  :  genomeBrowserView }
	                </TabPanel>
          </div> 
            </div>
            </div>
	    </div>
    );
};

Encyclopedia.contextTypes = {
    location_href: PropTypes.string,
    navigate: PropTypes.func,
    fetch: PropTypes.func,
};

globals.contentViews.register(Encyclopedia, 'region-search');
