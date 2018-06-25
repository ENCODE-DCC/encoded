import React from 'react';
import PropTypes from 'prop-types';
import _ from 'underscore';
import moment from 'moment';
import { FetchedData, FetchedItems, Param } from './fetched';
import * as globals from './globals';
import { Panel, PanelBody } from '../libs/bootstrap/panel';
import Tooltip from '../libs/bootstrap/tooltip';


const newsUri = '/search/?type=Page&news=true&status=released';


// Convert the selected organisms and assays into an encoded query.
function generateQuery(selectedOrganisms, selectedAssayCategory) {
    // Make the base query.
    let query = selectedAssayCategory === 'COMPPRED' ? '?type=Annotation&encyclopedia_version=4' : '?type=Experiment&status=released';

    // Add the selected assay category, if any (doesn't apply to Computational Predictions).
    if (selectedAssayCategory && selectedAssayCategory !== 'COMPPRED') {
        query += `&assay_slims=${selectedAssayCategory}`;
    }

    // Add all the selected organisms, if any
    if (selectedOrganisms.length) {
        const organismSpec = selectedAssayCategory === 'COMPPRED' ? 'organism.scientific_name=' : 'replicates.library.biosample.donor.organism.scientific_name=';
        const queryStrings = {
            HUMAN: `${organismSpec}Homo+sapiens`, // human
            MOUSE: `${organismSpec}Mus+musculus`, // mouse
            WORM: `${organismSpec}Caenorhabditis+elegans`, // worm
            FLY: `${organismSpec}Drosophila+melanogaster&${organismSpec}Drosophila+pseudoobscura&${organismSpec}Drosophila+simulans&${organismSpec}Drosophila+mojavensis&${organismSpec}Drosophila+ananassae&${organismSpec}Drosophila+virilis&${organismSpec}Drosophila+yakuba`,
        };
        const organismQueries = selectedOrganisms.map(organism => queryStrings[organism]);
        query += `&${organismQueries.join('&')}`;
    }

    return query;
}


// Buttons to introduce people to ENCODE.
const IntroControls = () => (
    <div className="intro-controls">
        <a href="/about/contributors/" role="button" className="intro-controls__element intro-controls__element--33-width">About</a>
        <a href="/help/getting-started/" role="button" className="intro-controls__element intro-controls__element--33-width">Get Started</a>
        <a href="/help/rest-api/" role="button" className="intro-controls__element intro-controls__element--33-width">REST API</a>
        <a href="/matrix/?type=Experiment&status=released" role="button" className="intro-controls__element intro-controls__element--50-width">Data Matrix</a>
        <a href="/matrix/?type=Annotation&encyclopedia_version=4" role="button" className="intro-controls__element intro-controls__element--50-width">Encyclopedia Matrix</a>
    </div>
);


// Home-page-only ENCODE search form.
class EncodeSearch extends React.Component {
    constructor() {
        super();
        this.state = {
            inputText: '', // Text value in controlled <input>
            disabledSearch: true, // True to disable search button
        };
        this.handleOnChange = this.handleOnChange.bind(this);
    }

    handleOnChange(e) {
        // Called when user changes the contents of the input field.
        const newInputText = e.target.value;
        this.setState({ inputText: newInputText, disabledSearch: newInputText.length === 0 });
    }

    render() {
        return (
            <form action="/search/">
                <fieldset className="site-search__encode">
                    <legend className="sr-only">Encode search</legend>
                    <div className="site-search__input">
                        <label htmlFor="encode-search">Search ENCODE portal</label>
                        <Tooltip trigger={<i className="icon icon-info-circle" />} tooltipId="search-encode" css="tooltip-home-info">
                            Search the entire ENCODE portal by using terms like &ldquo;skin,&rdquo; &ldquo;ChIP-seq,&rdquo; or &ldquo;CTCF.&rdquo;
                        </Tooltip>
                        <input id="encode-search" className="form-control" value={this.state.inputText} name="searchTerm" type="text" onChange={this.handleOnChange} />
                    </div>
                    <div className="site-search__submit">
                        <button type="submit" aria-label="ENCODE portal search" title="ENCODE portal search" disabled={this.state.disabledSearch} className="btn btn-info">ENCODE <i className="icon icon-search" /></button>
                    </div>
                </fieldset>
            </form>
        );
    }
}


// Display one term in the SCREEN search suggestions list. If the user clicks on this item or moves
// the mouse into it, this component alerts the parent list component so it can react. This
// component's purpose is to tie specific list items to events that select it.
class SearchSuggestionsItem extends React.Component {
    constructor() {
        super();
        this.itemClickHandler = this.itemClickHandler.bind(this);
        this.itemMouseEnter = this.itemMouseEnter.bind(this);
    }

    itemClickHandler(e) {
        e.preventDefault();
        e.stopPropagation();
        this.props.listClickHandler(this.props.item);
    }

    itemMouseEnter() {
        this.props.listMouseEnter(this.props.item);
    }

    render() {
        return <li><button className={this.props.selected ? 'site-search__suggested-results--selected' : ''} onMouseDown={this.itemClickHandler} onMouseEnter={this.itemMouseEnter}>{this.props.item}</button></li>;
    }
}

SearchSuggestionsItem.propTypes = {
    item: PropTypes.string.isRequired, // Suggestion item to display
    selected: PropTypes.bool, // True to display selected
    listClickHandler: PropTypes.func.isRequired, // Click handler for entire suggestion list
    listMouseEnter: PropTypes.func.isRequired, // Handler for mouseenter event for this item
};

SearchSuggestionsItem.defaultProps = {
    selected: false,
};


// Display a list of search suggestions from SCREEN in a drop-down list below the search field.
class SearchSuggestionsPicker extends React.Component {
    constructor() {
        super();
        this.listClickHandler = this.listClickHandler.bind(this);
        this.listMouseEnter = this.listMouseEnter.bind(this);
    }

    listClickHandler(term) {
        if (this.props.itemSelectHandler) {
            this.props.itemSelectHandler(term);
        }
    }

    listMouseEnter(term) {
        if (this.props.itemMouseEnterHandler) {
            this.props.itemMouseEnterHandler(term);
        }
    }

    render() {
        return (
            <ul className="site-search__suggested-results" id={this.props.controlId}>
                {this.props.suggestedSearchItems.map((item, i) => (
                    <SearchSuggestionsItem key={item} item={item} selected={i === this.props.selectedItemIndex} listClickHandler={this.listClickHandler} listMouseEnter={this.listMouseEnter} />
                ))}
            </ul>
        );
    }
}

SearchSuggestionsPicker.propTypes = {
    suggestedSearchItems: PropTypes.array.isRequired, // Array of terms to display and choose from
    selectedItemIndex: PropTypes.number, // Item to display as selected
    controlId: PropTypes.string, // HTML ID to assign to <ul>; for arias
    itemSelectHandler: PropTypes.func, // Callback when user chooses a suggested term
    itemMouseEnterHandler: PropTypes.func, // Callback when mouse enters a suggested term
};

SearchSuggestionsPicker.defaultProps = {
    selectedItemIndex: -1,
    controlId: 'site-search-suggestions-picker',
    itemSelectHandler: null,
    itemMouseEnterHandler: null,
};


// https://developer.mozilla.org/en-US/docs/Web/API/KeyboardEvent/keyCode
const KEYCODE_UP_ARROW = 38;
const KEYCODE_DOWN_ARROW = 40;
const KEYCODE_ENTER = 13;
const KEYCODE_ESC = 27;


// Combination input and drop-down suggestions form control. Handles both mouse and keyboard
// control of the suggestions list.
class InputSuggest extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            inputText: props.value, // Current contents of <input>
            selectedItemIndex: -1, // Index of currently selected item in `item` array
            hideSuggestions: false, // True to hide items even if parent passes items in
        };
        this.handleOnChange = this.handleOnChange.bind(this);
        this.handleOnClick = this.handleOnClick.bind(this);
        this.handleItemSelectClick = this.handleItemSelectClick.bind(this);
        this.handleOnBlur = this.handleOnBlur.bind(this);
        this.handleKeyDown = this.handleKeyDown.bind(this);
        this.handleMouseEnter = this.handleMouseEnter.bind(this);
    }

    componentDidUpdate(prevProps) {
        // React to new <input> text contents controlled by parent form component.
        if (prevProps.value !== this.props.value) {
            this.setState({
                inputText: this.props.value,
                selectedItemIndex: -1,
                hideSuggestions: false,
            });
        }
    }

    handleOnChange(e) {
        // Called when user changes the contents of the controlled <input> field.
        const newInputText = e.target.value;
        this.setState({ inputText: newInputText });
        if (this.props.inputChangeHandler) {
            this.props.inputChangeHandler(newInputText);
        }
    }

    handleOnClick() {
        // Called when user clicks in the <input> field.
        if (this.props.inputClickHandler) {
            this.props.inputClickHandler();
        }
    }

    handleItemSelectClick(selectedItem) {
        // Called when the user clicks on an item on the suggestion list.
        if (this.props.itemSelectHandler) {
            this.props.itemSelectHandler(selectedItem);
        }
    }

    handleOnBlur() {
        // Called when the user moves focus outside the <input> field.
        if (this.props.inputBlurHandler) {
            this.props.inputBlurHandler();
        }
    }

    handleKeyDown(e) {
        // Handle keyboard usage of the suggestion list.
        if (e.keyCode === KEYCODE_UP_ARROW) {
            e.preventDefault();
            this.setState((prevState) => {
                let newIndex = -1;
                if (prevState.selectedItemIndex > 0) {
                    // Select item above the currently selected one.
                    newIndex = prevState.selectedItemIndex - 1;
                } else if (prevState.selectedItemIndex === -1) {
                    // No item selected, so select the last item.
                    newIndex = this.props.items.length - 1;
                } else if (prevState.selectedItemIndex === 0) {
                    // First item selected, so stay on that item.
                    newIndex = prevState.selectedItemIndex;
                }
                return { selectedItemIndex: newIndex };
            });
        } else if (e.keyCode === KEYCODE_DOWN_ARROW) {
            e.preventDefault();

            // Select the next item in the list, or stay on the item if the current item is the
            // last one.
            this.setState(prevState => ({ selectedItemIndex: prevState.selectedItemIndex < this.props.items.length - 1 ? prevState.selectedItemIndex + 1 : prevState.selectedItemIndex }));
        } else if (e.keyCode === KEYCODE_ENTER && this.state.selectedItemIndex > -1 && this.props.itemSelectHandler) {
            this.props.itemSelectHandler(this.props.items[this.state.selectedItemIndex]);
        } else if (e.keyCode === KEYCODE_ESC) {
            // Hide the suggestions list even if the parent component sends items to display. That
            // way the parent doesn't need to handle the ESC key itself.
            e.preventDefault();
            this.setState({ hideSuggestions: true });
        }
    }

    handleMouseEnter(term) {
        // Mouse entering a suggestion item selects it, and deselects anything else.
        const termIndex = this.props.items.indexOf(term);
        if (termIndex > -1) {
            this.setState({ selectedItemIndex: termIndex });
        }
    }

    render() {
        const { items, inputId, placeholder } = this.props;
        const controlId = `${inputId}-list`;
        const activeDescendant = (this.props.items.length && this.state.selectedItemIndex > -1) ? this.props.items[this.state.selectedItemIndex] : '';
        return (
            <div className="site-search__input-field" role="combobox" aria-haspopup="listbox" aria-expanded={items.length > 0} aria-controls={controlId} aria-owns={controlId}>
                <input
                    id={inputId}
                    className="form-control"
                    placeholder={placeholder}
                    type="text"
                    autoComplete="off"
                    aria-autocomplete="list"
                    aria-activedescendant={activeDescendant}
                    aria-labelledby={this.props.labelledById}
                    value={this.state.inputText}
                    onChange={this.handleOnChange}
                    onClick={this.handleOnClick}
                    onBlur={this.handleOnBlur}
                    onKeyDown={this.handleKeyDown}
                />
                {items.length > 0 && !this.state.hideSuggestions ?
                    <SearchSuggestionsPicker
                        suggestedSearchItems={this.props.items}
                        selectedItemIndex={this.state.selectedItemIndex}
                        controlId={controlId}
                        itemSelectHandler={this.handleItemSelectClick}
                        itemMouseEnterHandler={this.handleMouseEnter}
                    />
                : null}
            </div>
        );
    }
}

InputSuggest.propTypes = {
    items: PropTypes.array, // Array of strings to display in menu
    value: PropTypes.string, // Initial value of text in <input>
    inputId: PropTypes.string.isRequired, // HTML id to assign to <input>
    labelledById: PropTypes.string, // ID of label for <input>
    placeholder: PropTypes.string, // Placeholder text for <input>
    inputChangeHandler: PropTypes.func, // Callback to handle <input> text content change
    inputClickHandler: PropTypes.func, // Callback to handle clicks in <input>
    inputBlurHandler: PropTypes.func, // Callback to handle <input> blurring
    itemSelectHandler: PropTypes.func, // Callback to handle click in dropdown item
};

InputSuggest.defaultProps = {
    items: [],
    value: '',
    placeholder: '',
    labelledById: '',
    inputChangeHandler: null,
    inputClickHandler: null,
    inputBlurHandler: null,
    itemSelectHandler: null,
};


// URLS to work the SCREEN site, both for a suggestion list and searches.
const screenSuggestionsUrl = 'https://api.wenglab.org/screenv10_python_beta/autows/suggestions';
const screenSearchUrl = 'http://screen.encodeproject.org/api/autows/search';


// Render the search form for SCREEN searches, including the search field, search buttons, and
// drop-down suggestions from the SCREEN server. To prevent fast typers from overwhelming the
// SCREEN server with suggestion requests, a timer prevents more than one suggestion request per
// second.
class ScreenSearch extends React.Component {
    constructor() {
        super();
        this.state = {
            currSearchTerm: '', // Text currently entered in SCREEN search field
            suggestedSearchTerms: [], // Suggested search terms from SCREEN
        };

        this.lastSearchTerm = ''; // Last text we requested suggestions for
        this.throttlingTimer = null; // Tracks delay timer; null when not running

        this.getScreenSuggestions = this.getScreenSuggestions.bind(this);
        this.handleTimerExpiry = this.handleTimerExpiry.bind(this);
        this.startDelayTimer = this.startDelayTimer.bind(this);
        this.searchTermChange = this.searchTermChange.bind(this);
        this.searchTermClick = this.searchTermClick.bind(this);
        this.submitScreenSearch = this.submitScreenSearch.bind(this);
        this.termSelectHandler = this.termSelectHandler.bind(this);
        this.inputBlur = this.inputBlur.bind(this);
    }

    componentWillUnmount() {
        if (this.throttlingTimer) {
            clearTimeout(this.throttlingTimer);
            this.throttlingTimer = null;
        }
    }

    getScreenSuggestions(newSearchTerm) {
        // Retrieve a list of term suggestions from the SCREEN REST API based on `newSearchTerm`.
        this.startDelayTimer();
        this.lastSearchTerm = newSearchTerm;
        fetch(screenSuggestionsUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ userQuery: newSearchTerm.trim() }),
        }).then(response => (
            // If we get an error response from the SCREEN server, just don't display a suggestions
            // drop down.
            response.ok ? response.json() : []
        )).then((results) => {
            let dedupedSearchTerms = [];
            if (results.length > 0) {
                dedupedSearchTerms = _.chain(results.map(term => term.trim())).uniq().compact().value();
            }
            this.setState({ suggestedSearchTerms: dedupedSearchTerms });
            return results;
        });
    }

    handleTimerExpiry() {
        // Called when the timer expires. If the last term requested for suggestions is different
        // from what's in the input field, request new suggestions.
        this.throttlingTimer = null;
        if (this.state.currSearchTerm !== this.lastSearchTerm) {
            this.getScreenSuggestions(this.state.currSearchTerm);
        }
    }

    startDelayTimer() {
        this.throttlingTimer = setTimeout(this.handleTimerExpiry, 1000);
    }

    searchTermChange(newSearchTerm) {
        // Called when user changed the contents of the search input field.
        if (newSearchTerm !== this.currSearchTerm) {
            this.setState({ currSearchTerm: newSearchTerm });

            // Only request a search suggestion if the timer isn't running.
            if (!this.throttlingTimer) {
                this.getScreenSuggestions(newSearchTerm);
            }
        }
    }

    submitScreenSearch() {
        // Request search results from SCREEN.
        fetch(screenSearchUrl, {
            method: 'POST',
            headers: {
                Accept: 'application/json',
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                assembly: 'hg19',
                userQuery: this.state.currSearchTerm,
                uuid: '0',
            }),
        }).then(response => (
            response.ok ? response.json() : null
        ));
    }

    termSelectHandler(term) {
        // Called when user clicks on a term in the drop-down suggestion list.
        this.setState({ currSearchTerm: term, suggestedSearchTerms: [] });
    }

    searchTermClick() {
        // Called when the user clicks in the SCREEN search edit field so that the drop-down
        // suggestion list disappears so that we don't hide the search buttons.
        this.setState({ suggestedSearchTerms: [] });
    }

    inputBlur() {
        // Called input focus moves away from the search input component.
        this.setState({ suggestedSearchTerms: [] });
    }

    render() {
        const disabledSearch = this.state.currSearchTerm.length === 0;
        return (
            <form>
                <fieldset className="site-search__screen">
                    <legend className="sr-only">Screen search</legend>
                    <div className="site-search__input">
                        <label htmlFor="screen-search" id="screen-search-label">
                            Search for Candidate Regulatory Elements
                            <Tooltip trigger={<i className="icon icon-info-circle" />} tooltipId="search-screen" css="tooltip-home-info">
                                Search for candidate regulatory elements by entering a gene name or alias, SNP rsID, ccRE accession, or genomic region in the form chr:start-end; or enter a cell type to filter results e.g. &ldquo;chr11:5226493-5403124&rdquo; or &ldquo;rs4846913.&rdquo;
                            </Tooltip>
                            <br />
                            <span className="site-search__note">Hosted by <a href="http://screen.encodeproject.org/">SCREEN</a></span>
                        </label>
                        <InputSuggest
                            value={this.state.currSearchTerm}
                            items={this.state.suggestedSearchTerms}
                            inputId="screen-search"
                            labelledById="screen-search-label"
                            inputChangeHandler={this.searchTermChange}
                            inputClickHandler={this.searchTermClick}
                            inputBlurHandler={this.inputBlur}
                            itemSelectHandler={this.termSelectHandler}
                        />
                    </div>
                    <div className="site-search__submit">
                        <a disabled={disabledSearch} aria-label="Human hg19 search" title="Human hg19 search" className="btn btn-info" role="button" href={`http://screen.encodeproject.org/search/?q=${this.state.currSearchTerm}&uuid=0&assembly=hg19`}>Human hg19 <i className="icon icon-search" /></a>
                        <a disabled={disabledSearch} aria-label="Mouse mm10 search" title="Mouse mm10 search" className="btn btn-info" role="button" href={`http://screen.encodeproject.org/search/?q=${this.state.currSearchTerm}&uuid=0&assembly=mm10`}>Mouse mm10 <i className="icon icon-search" /></a>
                    </div>
                </fieldset>
            </form>
        );
    }
}


const SiteSearch = () => (
    <div className="site-search">
        <EncodeSearch />
        <ScreenSearch />
    </div>
);


// Main page component to render the home page
export default class Home extends React.Component {
    constructor(props) {
        super(props);

        // Set initial React state.
        this.state = {
            organisms: [], // create empty array of selected tabs
            assayCategory: '',
            socialHeight: 0,
        };

        // Required binding of `this` to component methods or else they can't see `this`.
        this.handleAssayCategoryClick = this.handleAssayCategoryClick.bind(this);
        this.handleTabClick = this.handleTabClick.bind(this);
        this.newsLoaded = this.newsLoaded.bind(this);
    }

    handleAssayCategoryClick(assayCategory) {
        if (this.state.assayCategory === assayCategory) {
            this.setState({ assayCategory: '' });
        } else {
            this.setState({ assayCategory });
        }
    }

    handleTabClick(selectedTab) {
        // Create a copy of this.state.newtabs so we can manipulate it in peace.
        const tempArray = _.clone(this.state.organisms);
        if (tempArray.indexOf(selectedTab) === -1) {
            // if tab isn't already in array, then add it
            tempArray.push(selectedTab);
        } else {
            // otherwise if it is in array, remove it from array and from link
            const indexToRemoveArray = tempArray.indexOf(selectedTab);
            tempArray.splice(indexToRemoveArray, 1);
        }

        // Update the list of user-selected organisms.
        this.setState({ organisms: tempArray });
    }

    // Called when the news content loads so that we can get its height. That lets us match up the
    // height of <TwitterWidget>. If we don't have any news items, nodeRef has `undefined` and we
    // just hard-code the height at 600 so that the Twitter widget has some space.
    newsLoaded(nodeRef) {
        this.setState({ socialHeight: nodeRef ? nodeRef.clientHeight : 600 });
    }

    render() {
        // Based on the currently selected organisms and assay category, generate a query string
        // for the GET request to retrieve chart data.
        const currentQuery = generateQuery(this.state.organisms, this.state.assayCategory);

        return (
            <div className="whole-page">
                <div className="row">
                    <div className="col-xs-12">
                        <Panel>
                            <AssayClicking assayCategory={this.state.assayCategory} handleAssayCategoryClick={this.handleAssayCategoryClick} />
                            <div className="organism-tabs">
                                <TabClicking organisms={this.state.organisms} handleTabClick={this.handleTabClick} />
                            </div>
                            <div className="graphs">
                                <div className="row">
                                    <HomepageChartLoader organisms={this.state.organisms} assayCategory={this.state.assayCategory} query={currentQuery} />
                                </div>
                            </div>
                            <div className="social">
                                <div className="social-news">
                                    <div className="news-header">
                                        <h2>News <a href="/news/" title="More ENCODE news" className="twitter-ref">More ENCODE news</a></h2>
                                    </div>
                                    <NewsLoader newsLoaded={this.newsLoaded} />
                                </div>
                                <div className="social-twitter">
                                    <TwitterWidget height={this.state.socialHeight} />
                                </div>
                            </div>
                        </Panel>
                    </div>
                </div>
            </div>
        );
    }
}


// Given retrieved data, draw all home-page charts.
const ChartGallery = props => (
    <PanelBody>
        <div className="view-all">
            <a href={`/matrix/${props.query}`} className="view-all-button btn btn-info btn-sm" role="button">
                {props.assayCategory !== '' || props.organisms.length > 0 ? 'Filtered ' : ''}
                Data Matrix
            </a>
        </div>
        <div className="chart-gallery">
            <div className="chart-single">
                <HomepageChart {...props} />
            </div>
            <div className="chart-single">
                <HomepageChart2 {...props} />
            </div>
            <div className="chart-single">
                <HomepageChart3 {...props} />
            </div>
        </div>
    </PanelBody>
);

ChartGallery.propTypes = {
    assayCategory: PropTypes.string, // Selected assay cateogry from classic image buttons
    organisms: PropTypes.array, // Contains selected organism strings
    query: PropTypes.string, // Query string to add to /matrix/ URI
};

ChartGallery.defaultProps = {
    assayCategory: '',
    organisms: [],
    query: null,
};


// Component to allow clicking boxes on classic image
class AssayClicking extends React.Component {
    constructor(props) {
        super(props);

        // Required binding of `this` to component methods or else they can't see `this`.
        this.sortByAssay = this.sortByAssay.bind(this);
    }

    // Properly adds or removes assay category from link
    sortByAssay(category, e) {
        function handleClick(cat, ctx) {
            // Call the Home component's function to record the new assay cateogry
            ctx.props.handleAssayCategoryClick(cat); // handles assay category click
        }

        if (e.type === 'touchend') {
            handleClick(category, this);
            this.assayClickHandled = true;
        } else if (e.type === 'click' && !this.assayClickHandled) {
            handleClick(category, this);
        } else {
            this.assayClickHandled = false;
        }
    }

    // Renders classic image and svg rectangles
    render() {
        const assayList = [
            '3D+chromatin+structure',
            'DNA+accessibility',
            'DNA+binding',
            'DNA+methylation',
            'COMPPRED',
            'Transcription',
            'RNA+binding',
        ];
        const assayCategory = this.props.assayCategory;

        return (
            <div>
                <div className="overall-classic">

                    <h1>ENCODE: Encyclopedia of DNA Elements</h1>

                    <div className="site-banner">
                        <div className="site-banner-img">
                            <img src="static/img/classic-image.jpg" alt="ENCODE representational diagram with embedded assay selection buttons" />

                            <svg id="site-banner-overlay" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2260 1450" className="classic-svg">
                                <BannerOverlayButton item={assayList[0]} x="101.03" y="645.8" width="257.47" height="230.95" selected={assayCategory === assayList[0]} clickHandler={this.sortByAssay} />
                                <BannerOverlayButton item={assayList[1]} x="386.6" y="645.8" width="276.06" height="230.95" selected={assayCategory === assayList[1]} clickHandler={this.sortByAssay} />
                                <BannerOverlayButton item={assayList[2]} x="688.7" y="645.8" width="237.33" height="230.95" selected={assayCategory === assayList[2]} clickHandler={this.sortByAssay} />
                                <BannerOverlayButton item={assayList[3]} x="950.83" y="645.8" width="294.65" height="230.95" selected={assayCategory === assayList[3]} clickHandler={this.sortByAssay} />
                                <BannerOverlayButton item={assayList[4]} x="1273.07" y="645.8" width="373.37" height="230.95" selected={assayCategory === assayList[4]} clickHandler={this.sortByAssay} />
                                <BannerOverlayButton item={assayList[5]} x="1674.06" y="645.8" width="236.05" height="230.95" selected={assayCategory === assayList[5]} clickHandler={this.sortByAssay} />
                                <BannerOverlayButton item={assayList[6]} x="1937.74" y="645.8" width="227.38" height="230.95" selected={assayCategory === assayList[6]} clickHandler={this.sortByAssay} />
                            </svg>
                        </div>

                        <div className="site-banner-intro">
                            <div className="site-banner-intro-content">
                                <IntroControls />
                                <SiteSearch />
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        );
    }
}

AssayClicking.propTypes = {
    assayCategory: PropTypes.string.isRequired, // Test to display in each audit's detail, possibly containing @ids that this component turns into links automatically
};


// Draw an overlay button on the ENCODE banner.
const BannerOverlayButton = (props) => {
    const { item, x, y, width, height, selected, clickHandler } = props;

    return (
        <rect
            id={item}
            x={x}
            y={y}
            width={width}
            height={height}
            className={`rectangle-box${selected ? ' selected' : ''}`}
            onClick={(e) => { clickHandler(item, e); }}
        />
    );
};

BannerOverlayButton.propTypes = {
    item: PropTypes.string, // ID of button being clicked
    x: PropTypes.string, // X coordinate of button
    y: PropTypes.string, // Y coordinate of button
    width: PropTypes.string, // Width of button in pixels
    height: PropTypes.string, // Height of button in pixels
    selected: PropTypes.bool, // `true` if button is selected
    clickHandler: PropTypes.func.isRequired, // Function to call when the button is clicked
};

BannerOverlayButton.defaultProps = {
    item: '',
    x: '0',
    y: '0',
    width: '0',
    height: '0',
    selected: false,
};


// Passes in tab to handleTabClick
/* eslint-disable react/prefer-stateless-function */
class TabClicking extends React.Component {
    render() {
        const { organisms, handleTabClick } = this.props;
        return (
            <div>
                <div className="organism-selector">
                    <OrganismSelector organism="Human" selected={organisms.indexOf('HUMAN') !== -1} clickHandler={handleTabClick} />
                    <OrganismSelector organism="Mouse" selected={organisms.indexOf('MOUSE') !== -1} clickHandler={handleTabClick} />
                    <OrganismSelector organism="Worm" selected={organisms.indexOf('WORM') !== -1} clickHandler={handleTabClick} />
                    <OrganismSelector organism="Fly" selected={organisms.indexOf('FLY') !== -1} clickHandler={handleTabClick} />
                </div>
            </div>
        );
    }
}
/* eslint-enable react/prefer-stateless-function */

TabClicking.propTypes = {
    organisms: PropTypes.array, // Array of currently selected tabs
    handleTabClick: PropTypes.func.isRequired, // Function to call when a tab is clicked
};

TabClicking.defaultProps = {
    organisms: [],
};


const OrganismSelector = (props) => {
    const { organism, selected, clickHandler } = props;

    return (
        <button className={`organism-selector__tab${selected ? ' organism-selector--selected' : ''}`} onClick={() => { clickHandler(organism.toUpperCase(organism)); }}>
            {organism}
        </button>
    );
};

OrganismSelector.propTypes = {
    organism: PropTypes.string, // Organism this selector represents
    selected: PropTypes.bool, // `true` if selector is selected
    clickHandler: PropTypes.func.isRequired, // Function to call to handle a selector click
};

OrganismSelector.defaultProps = {
    organism: '',
    selected: false,
};


// Initiates the GET request to search for experiments, and then pass the data to the HomepageChart
// component to draw the resulting chart.
const HomepageChartLoader = (props) => {
    const { query, organisms, assayCategory } = props;

    return (
        <FetchedData>
            <Param name="data" url={`/search/${query}`} />
            <ChartGallery organisms={organisms} assayCategory={assayCategory} query={query} />
        </FetchedData>
    );
};

HomepageChartLoader.propTypes = {
    query: PropTypes.string, // Current search URI based on selected assayCategory
    organisms: PropTypes.array, // Array of selected organism strings
    assayCategory: PropTypes.string, // Selected assay category
};

HomepageChartLoader.defaultProps = {
    query: '',
    organisms: [],
    assayCategory: '',
};


// Draw the total chart count in the middle of the donut.
function drawDonutCenter(chart) {
    const canvasId = chart.chart.canvas.id;
    const width = chart.chart.width;
    const height = chart.chart.height;
    const ctx = chart.chart.ctx;

    ctx.fillStyle = '#000000';
    ctx.restore();
    const fontSize = (height / 114).toFixed(2);
    ctx.font = `${fontSize}em sans-serif`;
    ctx.textBaseline = 'middle';

    if (canvasId === 'myChart' || canvasId === 'myChart2') {
        const data = chart.data.datasets[0].data;
        const total = data.reduce((prev, curr) => prev + curr);
        const textX = Math.round((width - ctx.measureText(total).width) / 2);
        const textY = height / 2;

        ctx.clearRect(0, 0, width, height);
        ctx.fillText(total, textX, textY);
        ctx.save();
    } else {
        ctx.clearRect(0, 0, width, height);
    }
}


// Component to display the D3-based chart for Project
class HomepageChart extends React.Component {
    constructor(props) {
        super(props);
        this.wrapperHeight = 200;
        this.createChart = this.createChart.bind(this);
        this.updateChart = this.updateChart.bind(this);
    }

    componentDidMount() {
        // Create the chart, and assign the chart to this.myPieChart when the process finishes.
        if (document.getElementById('myChart')) {
            this.createChart(this.facetData);
        }
    }

    componentDidUpdate() {
        if (this.myPieChart) {
            // Existing data updated
            this.updateChart(this.myPieChart, this.facetData);
        } else if (this.facetData.length) {
            // Chart existed but was destroyed for lack of data. Rebuild the chart.
            this.createChart(this.facetData);
        }
    }

    // Draw the Project chart, for initial load, or when the previous load had no data for this
    // chart.
    createChart(facetData) {
        require.ensure(['chart.js'], (require) => {
            const Chart = require('chart.js');

            // for each item, set doc count, add to total doc count, add proper label, and assign color.
            const colors = globals.projectColors.colorList(facetData.map(term => term.key), { shade: 10 });
            const data = [];
            const labels = [];

            // Convert facet data to chart data.
            facetData.forEach((term, i) => {
                data[i] = term.doc_count;
                labels[i] = term.key;
            });

            // adding total doc count to middle of donut
            // http://stackoverflow.com/questions/20966817/how-to-add-text-inside-the-doughnut-chart-using-chart-js/24671908
            Chart.pluginService.register({
                beforeDraw: drawDonutCenter,
            });

            // Pass the assay_title counts to the charting library to render it.
            const canvas = document.getElementById('myChart');
            if (canvas) {
                const ctx = canvas.getContext('2d');
                this.myPieChart = new Chart(ctx, {
                    type: 'doughnut',
                    data: {
                        labels,
                        datasets: [{
                            data,
                            backgroundColor: colors,
                        }],
                    },

                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        legend: {
                            display: false, // Hide automatically generated legend; we draw it ourselves
                        },
                        animation: {
                            duration: 200,
                        },
                        legendCallback: (chart) => { // allows for legend clicking
                            const chartData = chart.data.datasets[0].data;
                            const text = [];
                            text.push('<ul>');
                            for (let i = 0; i < chartData.length; i += 1) {
                                if (chartData[i]) {
                                    text.push('<li>');
                                    text.push(`<a href="/matrix/${this.props.query}&award.project=${chart.data.labels[i]}">`); // go to matrix view when clicked
                                    text.push(`<span class="chart-legend-chip" style="background-color:${chart.data.datasets[0].backgroundColor[i]}"></span>`);
                                    if (chart.data.labels[i]) {
                                        text.push(`<span class="chart-legend-label">${chart.data.labels[i]}</span>`);
                                    }
                                    text.push('</a></li>');
                                }
                            }
                            text.push('</ul>');
                            return text.join('');
                        },
                        onClick: (e) => {
                            // React to clicks on pie sections
                            const activePoints = this.myPieChart.getElementAtEvent(e);

                            if (activePoints[0]) { // if click on wrong area, do nothing
                                const clickedElementIndex = activePoints[0]._index;
                                const term = this.myPieChart.data.labels[clickedElementIndex];
                                this.context.navigate(`/matrix/${this.props.query}&award.project=${term}`);
                            }
                        },
                    },
                });

                // Have chartjs draw the legend into the DOM.
                document.getElementById('chart-legend').innerHTML = this.myPieChart.generateLegend();

                // Save the chart <div> height so we can set it to that value when no data's available.
                const chartWrapperDiv = document.getElementById('chart-wrapper-1');
                this.wrapperHeight = chartWrapperDiv.clientHeight;
            }
        });
    }

    // Update existing chart with new data.
    /* eslint-disable class-methods-use-this */
    updateChart(Chart, facetData) {
        // for each item, set doc count, add to total doc count, add proper label, and assign color.
        const colors = globals.projectColors.colorList(facetData.map(term => term.key), { shade: 10 });
        const data = [];
        const labels = [];

        // Convert facet data to chart data.
        facetData.forEach((term, i) => {
            data[i] = term.doc_count;
            labels[i] = term.key;
        });

        // Update chart data and redraw with the new data
        Chart.data.datasets[0].data = data;
        Chart.data.datasets[0].backgroundColor = colors;
        Chart.data.labels = labels;
        Chart.update();

        // Redraw the updated legend
        document.getElementById('chart-legend').innerHTML = Chart.generateLegend();
    }
    /* eslint-enable class-methods-use-this */

    render() {
        const facets = this.props.data && this.props.data.facets;
        let total;

        // Get all project facets, or an empty array if none.
        if (facets) {
            const projectFacet = facets.find(facet => facet.field === 'award.project');
            this.facetData = projectFacet ? projectFacet.terms : [];
            const docCounts = this.facetData.length ? this.facetData.map(data => data.doc_count) : [];
            total = docCounts.length ? docCounts.reduce((prev, curr) => prev + curr) : 0;

            // No data with the current selection, but we used to? Destroy the existing chart so we can
            // display a no-data message instead.
            if ((this.facetData.length === 0 || total === 0) && this.myPieChart) {
                this.myPieChart.destroy();
                this.myPieChart = null;
            }
        } else {
            this.facets = null;
            if (this.myPieChart) {
                this.myPieChart.destroy();
                this.myPiechart = null;
            }
        }

        return (
            <div>
                <div className="title">
                    Project
                    <center><hr width="80%" color="blue" /></center>
                </div>
                {this.facetData.length && total ?
                    <div id="chart-wrapper-1" className="chart-wrapper">
                        <div className="chart-container">
                            <canvas id="myChart" />
                        </div>
                        <div id="chart-legend" className="chart-legend" />
                    </div>
                    :
                    <div className="chart-no-data" style={{ height: this.wrapperHeight }}><p>No data to display</p></div>
                }
            </div>
        );
    }
}

HomepageChart.propTypes = {
    query: PropTypes.string.isRequired,
    data: PropTypes.object,
};

HomepageChart.defaultProps = {
    data: null,
};

HomepageChart.contextTypes = {
    navigate: PropTypes.func,
    projectColors: PropTypes.object, // DataColor instance for experiment project
};


// Component to display the D3-based chart for Biosample
class HomepageChart2 extends React.Component {
    constructor(props) {
        super(props);
        this.wrapperHeight = 200;
        this.createChart = this.createChart.bind(this);
        this.updateChart = this.updateChart.bind(this);
    }

    componentDidMount() {
        if (document.getElementById('myChart2')) {
            this.createChart(this.facetData);
        }
    }

    componentDidUpdate() {
        if (this.myPieChart) {
            // Existing data updated
            this.updateChart(this.myPieChart, this.facetData);
        } else if (this.facetData.length) {
            // Chart existed but was destroyed for lack of data. Rebuild the chart.
            this.createChart(this.facetData);
        }
    }

    createChart(facetData) {
        // Draw the chart of search results given in this.props.data.facets. Since D3 doesn't work
        // with the React virtual DOM, we have to load it separately using the webpack .ensure
        // mechanism. Once the callback is called, it's loaded and can be referenced through
        // require.
        require.ensure(['chart.js'], (require) => {
            const Chart = require('chart.js');
            const colors = globals.biosampleTypeColors.colorList(facetData.map(term => term.key), { shade: 10 });
            const data = [];
            const labels = [];

            facetData.forEach((term, i) => {
                data[i] = term.doc_count;
                labels[i] = term.key;
            });

            // adding total doc count to middle of donut
            // http://stackoverflow.com/questions/20966817/how-to-add-text-inside-the-doughnut-chart-using-chart-js/24671908
            Chart.pluginService.register({
                beforeDraw: drawDonutCenter,
            });

            // Pass the assay_title counts to the charting library to render it.
            const canvas = document.getElementById('myChart2');
            if (canvas) {
                const ctx = canvas.getContext('2d');
                this.myPieChart = new Chart(ctx, {
                    type: 'doughnut',
                    data: {
                        labels,
                        datasets: [{
                            data,
                            backgroundColor: colors,
                        }],
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        legend: {
                            display: false, // hiding automatically generated legend
                        },
                        animation: {
                            duration: 200,
                        },
                        legendCallback: (chart) => { // allows for legend clicking
                            const chartData = chart.data.datasets[0].data;
                            const text = [];
                            text.push('<ul>');
                            for (let i = 0; i < chartData.length; i += 1) {
                                if (chartData[i]) {
                                    text.push('<li>');
                                    text.push(`<a href="/matrix/${this.props.query}&biosample_type=${chart.data.labels[i]}">`); // go to matrix view when clicked
                                    text.push(`<span class="chart-legend-chip" style="background-color:${chart.data.datasets[0].backgroundColor[i]}"></span>`);
                                    if (chart.data.labels[i]) {
                                        text.push(`<span class="chart-legend-label">${chart.data.labels[i]}</span>`);
                                    }
                                    text.push('</a></li>');
                                }
                            }
                            text.push('</ul>');
                            return text.join('');
                        },
                        onClick: (e) => {
                            // React to clicks on pie sections
                            const activePoints = this.myPieChart.getElementAtEvent(e);
                            if (activePoints[0]) {
                                const clickedElementIndex = activePoints[0]._index;
                                const term = this.myPieChart.data.labels[clickedElementIndex];
                                this.context.navigate(`/matrix/${this.props.query}&biosample_type=${term}`); // go to matrix view
                            }
                        },
                    },
                });
            } else {
                this.myPieChart = null;
            }

            // Have chartjs draw the legend into the DOM.
            const legendElement = document.getElementById('chart-legend-2');
            if (legendElement) {
                legendElement.innerHTML = this.myPieChart.generateLegend();
            }

            // Save the chart <div> height so we can set it to that value when no data's available.
            const chartWrapperDiv = document.getElementById('chart-wrapper-2');
            if (chartWrapperDiv) {
                this.wrapperHeight = chartWrapperDiv.clientHeight;
            }
        });
    }

    /* eslint-disable class-methods-use-this */
    updateChart(Chart, facetData) {
        // for each item, set doc count, add to total doc count, add proper label, and assign color.
        const colors = globals.biosampleTypeColors.colorList(facetData.map(term => term.key), { shade: 10 });
        const data = [];
        const labels = [];

        // Convert facet data to chart data.
        facetData.forEach((term, i) => {
            data[i] = term.doc_count;
            labels[i] = term.key;
        });

        // Update chart data and redraw with the new data
        Chart.data.datasets[0].data = data;
        Chart.data.datasets[0].backgroundColor = colors;
        Chart.data.labels = labels;
        Chart.update();

        // Redraw the updated legend
        document.getElementById('chart-legend-2').innerHTML = Chart.generateLegend(); // generates legend
    }
    /* eslint-enable class-methods-use-this */

    render() {
        const facets = this.props.data && this.props.data.facets;
        let total;

        // Our data source will be different for computational predictions
        if (facets) {
            this.computationalPredictions = this.props.assayCategory === 'COMPPRED';
            const assayFacet = facets.find(facet => facet.field === 'biosample_type');
            this.facetData = assayFacet ? assayFacet.terms : [];
            const docCounts = this.facetData.length ? this.facetData.map(data => data.doc_count) : [];
            total = docCounts.length ? docCounts.reduce((prev, curr) => prev + curr) : 0;

            // No data with the current selection, but we used to destroy the existing chart so we can
            // display a no-data message instead.
            if ((this.facetData.length === 0 || total === 0) && this.myPieChart) {
                this.myPieChart.destroy();
                this.myPieChart = null;
            }
        } else {
            this.facets = null;
            if (this.myPieChart) {
                this.myPieChart.destroy();
                this.myPiechart = null;
            }
        }

        return (
            <div>
                <div className="title">
                    Biosample Type
                    <center><hr width="80%" color="blue" /></center>
                </div>
                {this.facetData.length && total ?
                    <div id="chart-wrapper-2" className="chart-wrapper">
                        <div className="chart-container">
                            <canvas id="myChart2" />
                        </div>
                        <div id="chart-legend-2" className="chart-legend" />
                    </div>
                    :
                    <div className="chart-no-data" style={{ height: this.wrapperHeight }}>No data to display</div>
                }
            </div>
        );
    }
}

HomepageChart2.propTypes = {
    query: PropTypes.string.isRequired,
    data: PropTypes.object,
    assayCategory: PropTypes.string,
};

HomepageChart2.defaultProps = {
    data: null,
    assayCategory: '',
};

HomepageChart2.contextTypes = {
    navigate: PropTypes.func,
    biosampleTypeColors: PropTypes.object, // DataColor instance for experiment project
};


// Draw the small triangle above the selected assay in the "Assay Categories" chart if the user has
// selected an assay from the classic image.
function drawColumnSelects(currentAssay, ctx, data) {
    // Adapted from https://github.com/chartjs/Chart.js/issues/2477#issuecomment-255042267
    if (currentAssay) {
        ctx.fillStyle = '#2138B2';

        // Find the data with a label matching the currently selected assay.
        const currentColumn = data.labels.indexOf(currentAssay);
        if (currentColumn !== -1) {
            // Get information on the matching column's coordinates so we know where to draw the
            // triangle.
            const dataset = data.datasets[0];
            const model = dataset._meta[Object.keys(dataset._meta)[0]].data[currentColumn]._model;

            // Draw the triangle into the HTML5 <canvas> element.
            ctx.beginPath();
            ctx.moveTo(model.x - 5, model.y - 8);
            ctx.lineTo(model.x, model.y - 3);
            ctx.lineTo(model.x + 5, model.y - 8);
            ctx.fill();
        }
    }
}


// Component to display the D3-based chart for Biosample
class HomepageChart3 extends React.Component {
    constructor(props) {
        super(props);
        this.wrapperHeight = 200;
        this.createChart = this.createChart.bind(this);
        this.updateChart = this.updateChart.bind(this);
    }

    componentDidMount() {
        if (document.getElementById('myChart3')) {
            this.createChart(this.facetData);
        }
    }

    componentDidUpdate() {
        if (this.myPieChart) {
            // Existing data updated
            this.updateChart(this.myPieChart, this.facetData);
        } else if (this.facetData.length) {
            // Chart existed but was destroyed for lack of data. Rebuild the chart.
            this.createChart(this.facetData);
        }
    }

    createChart(facetData) {
        // Draw the chart of search results given in this.props.data.facets. Since D3 doesn't work
        // with the React virtual DOM, we have to load it separately using the webpack .ensure
        // mechanism. Once the callback is called, it's loaded and can be referenced through
        // require.
        require.ensure(['chart.js'], (require) => {
            const Chart = require('chart.js');
            const colors = [];
            const data = [];
            const labels = [];
            const selectedAssay = (this.props.assayCategory && this.props.assayCategory !== 'COMPPRED') ? this.props.assayCategory.replace(/\+/g, ' ') : '';

            // For each item, set doc count, add to total doc count, add proper label, and assign
            // color.
            facetData.forEach((term, i) => {
                data[i] = term.doc_count;
                labels[i] = term.key;
                colors[i] = selectedAssay ? (term.key === selectedAssay ? 'rgb(255,217,98)' : 'rgba(255,217,98,.4)') : '#FFD962';
            });

            // Pass the counts to the charting library to render it.
            const canvas = document.getElementById('myChart3');
            if (canvas) {
                const ctx = canvas.getContext('2d');
                this.myPieChart = new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels, // full labels
                        datasets: [{
                            data,
                            backgroundColor: colors,
                        }],
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        legend: {
                            display: false, // hiding automatically generated legend
                        },
                        hover: {
                            mode: false,
                        },
                        animation: {
                            duration: 0,
                            onProgress: function onProgress() { drawColumnSelects(selectedAssay, this.chart.ctx, this.data); },
                            onComplete: function onComplete() { drawColumnSelects(selectedAssay, this.chart.ctx, this.data); },
                        },
                        scales: {
                            xAxes: [{
                                gridLines: {
                                    display: false,
                                },
                                ticks: {
                                    autoSkip: false,
                                },
                            }],
                        },
                        layout: {
                            padding: {
                                top: 10,
                            },
                        },
                        onClick: (e) => {
                            // React to clicks on pie sections
                            const query = 'assay_slims=';
                            const activePoints = this.myPieChart.getElementAtEvent(e);
                            if (activePoints[0]) {
                                const clickedElementIndex = activePoints[0]._index;
                                const term = this.myPieChart.data.labels[clickedElementIndex];
                                this.context.navigate(`/matrix/${this.props.query}&${query}${term}`); // go to matrix view
                            }
                        },
                    },
                });

                // Save height of wrapper div.
                const chartWrapperDiv = document.getElementById('chart-wrapper-3');
                this.wrapperHeight = chartWrapperDiv.clientHeight;
            }
        });
    }

    updateChart(Chart, facetData) {
        // for each item, set doc count, add to total doc count, add proper label, and assign color.
        const data = [];
        const labels = [];
        const colors = [];

        // Convert facet data to chart data.
        const selectedAssay = (this.props.assayCategory && this.props.assayCategory !== 'COMPPRED') ? this.props.assayCategory.replace(/\+/g, ' ') : '';
        facetData.forEach((term, i) => {
            data[i] = term.doc_count;
            labels[i] = term.key;
            colors[i] = selectedAssay ? (term.key === selectedAssay ? 'rgb(255,217,98)' : 'rgba(255,217,98,.4)') : '#FFD962';
        });

        // Update chart data and redraw with the new data
        Chart.data.datasets[0].data = data;
        Chart.data.labels = labels;
        Chart.data.datasets[0].backgroundColor = colors;
        Chart.options.hover.mode = false;
        Chart.options.animation.onProgress = function onProgress() { drawColumnSelects(selectedAssay, this.chart.ctx, this.data); };
        Chart.options.animation.onComplete = function onComplete() { drawColumnSelects(selectedAssay, this.chart.ctx, this.data); };
        Chart.update();
    }

    render() {
        const facets = this.props.data && this.props.data.facets;
        let total;

        // Get all assay category facets, or an empty array if none
        if (facets) {
            const projectFacet = facets.find(facet => facet.field === 'assay_slims');
            this.facetData = projectFacet ? projectFacet.terms : [];
            const docCounts = this.facetData.length ? this.facetData.map(data => data.doc_count) : [];
            total = docCounts.length ? docCounts.reduce((prev, curr) => prev + curr) : 0;

            // No data with the current selection, but we used to? Destroy the existing chart so we can
            // display a no-data message instead.
            if ((this.facetData.length === 0 || total === 0) && this.myPieChart) {
                this.myPieChart.destroy();
                this.myPieChart = null;
            }
        } else {
            this.facets = null;
            if (this.myPieChart) {
                this.myPieChart.destroy();
                this.myPiechart = null;
            }
        }

        return (
            <div>
                <div className="title">
                    Assay Categories
                    <center><hr width="80%" color="blue" /></center>
                </div>
                {this.facetData.length && total ?
                    <div id="chart-wrapper-3" className="chart-wrapper">
                        <div className="chart-container-assaycat">
                            <canvas id="myChart3" />
                        </div>
                    </div>
                    :
                    <div className="chart-no-data" style={{ height: this.wrapperHeight }}>No data to display</div>
                }
            </div>
        );
    }
}

HomepageChart3.propTypes = {
    assayCategory: PropTypes.string,
    query: PropTypes.string.isRequired,
    data: PropTypes.object,
};

HomepageChart3.defaultProps = {
    assayCategory: '',
    data: null,
};

HomepageChart3.contextTypes = {
    navigate: PropTypes.func,
};


// Render the most recent five news posts
class News extends React.Component {
    componentDidMount() {
        this.props.newsLoaded(this.nodeRef);
    }

    render() {
        const { items } = this.props;
        if (items && items.length) {
            return (
                <div ref={(node) => { this.nodeRef = node; }} className="news-listing">
                    {items.map(item =>
                        <div key={item['@id']} className="news-listing-item">
                            <h3>{item.title}</h3>
                            <h4>{moment.utc(item.date_created).format('MMMM D, YYYY')}</h4>
                            <div className="news-excerpt">{item.news_excerpt}</div>
                            <div className="news-listing-readmore">
                                <a className="btn btn-info btn-sm" href={item['@id']} title={`View news post for ${item.title}`} key={item['@id']}>Read more</a>
                            </div>
                        </div>
                    )}
                </div>
            );
        }
        return <div className="news-empty">No news available at this time</div>;
    }
}

News.propTypes = {
    items: PropTypes.array,
    newsLoaded: PropTypes.func.isRequired, // Called parent once the news is loaded
};

News.defaultProps = {
    items: null,
};


// Send a GET request for the most recent five news posts. Don't make this a stateless component
// because we attach `ref` to this, and stateless components don't support that.
/* eslint-disable react/prefer-stateless-function */
class NewsLoader extends React.Component {
    render() {
        return <FetchedItems {...this.props} url={`${newsUri}&limit=5`} Component={News} newsLoaded={this.props.newsLoaded} />;
    }
}
/* eslint-enable react/prefer-stateless-function */

NewsLoader.propTypes = {
    newsLoaded: PropTypes.func.isRequired, // Called parent once the news is loaded
};


class TwitterWidget extends React.Component {
    constructor(props) {
        super(props);
        this.initialized = false;
        this.injectTwitter = this.injectTwitter.bind(this);
    }

    componentDidMount() {
        if (!this.initialized && this.props.height) {
            this.injectTwitter();
        }
    }

    componentDidUpdate() {
        if (!this.initialized && this.props.height) {
            this.injectTwitter();
        }
    }

    injectTwitter() {
        if (!this.initialized) {
            const link = this.anchor;
            this.initialized = true;
            const js = document.createElement('script');
            js.id = 'twitter-wjs';
            js.src = '//platform.twitter.com/widgets.js';
            return link.parentNode.appendChild(js);
        }
        return null;
    }

    render() {
        return (
            <div>
                <div className="twitter-header">
                    <h2>Twitter <a href="https://twitter.com/EncodeDCC" title="ENCODE DCC Twitter page in a new window or tab" target="_blank" rel="noopener noreferrer"className="twitter-ref">@EncodeDCC</a></h2>
                </div>
                {this.props.height ?
                    <a
                        ref={(anchor) => { this.anchor = anchor; }}
                        className="twitter-timeline"
                        href="https://twitter.com/encodedcc" // from encodedcc twitter
                        data-chrome="noheader"
                        data-screen-name="EncodeDCC"
                        data-height={this.props.height.toString()} // height so it matches with rest of site
                    >
                        @EncodeDCC
                    </a>
                : null}
            </div>
        );
    }
}

TwitterWidget.propTypes = {
    height: PropTypes.number.isRequired, // Number of pixels tall to make widget
};
