import React from 'react';
import PropTypes from 'prop-types';
import url from 'url';
import { BrowserSelector } from './objectutils';
import { Panel, PanelBody } from '../libs/bootstrap/panel';
import { FacetList, Listing } from './search';
import { FetchedData, Param } from './fetched';
import * as globals from './globals';


const regionGenomes = [
    { value: 'GRCh37', display: 'hg19' },
    { value: 'GRCh38', display: 'GRCh38' },
    { value: 'GRCm37', display: 'mm9' },
    { value: 'GRCm38', display: 'mm10' },
];


const AutocompleteBox = (props) => {
    const terms = props.auto['@graph']; // List of matching terms from server
    const handleClick = props.handleClick;
    const userTerm = props.userTerm && props.userTerm.toLowerCase(); // Term user entered

    if (!props.hide && userTerm && userTerm.length && terms && terms.length) {
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

        // Set intial React state.
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
        this.closeAutocompleteBox = this.closeAutocompleteBox.bind(this);
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
        this.setState(prevState => ({
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

    closeAutocompleteBox() {
        this.setState({ showAutoSuggest: false });
    }

    tick() {
        if (this.newSearchTerm !== this.state.searchTerm) {
            this.setState({ searchTerm: this.newSearchTerm });
        }
    }

    render() {
        const context = this.props.context;
        const id = url.parse(this.context.location_href, true);
        const region = id.query.region || '';

        if (this.state.genome === '') {
            let assembly = regionGenomes[0].value;
            if (context.assembly) {
                assembly = regionGenomes.find(el =>
                    context.assembly === el.value || context.assembly === el.display
                ).value;
            }
            this.setState({ genome: assembly });
        }

        return (
            <Panel>
                <PanelBody>
                    <form id="panel1" className="adv-search-form" autoComplete="off" aria-labelledby="tab1" onSubmit={this.closeAutocompleteBox} >
                        <input type="hidden" name="annotation" value={this.state.terms.annotation} />
                        <div className="form-group">
                            <label htmlFor="annotation">Enter any one of human Gene name, Symbol, Synonyms, Gene ID, HGNC ID, coordinates, rsid, Ensemble ID</label>
                            <div className="input-group input-group-region-input">
                                <input id="annotation" ref={(input) => { this.annotation = input; }} defaultValue={region} name="region" type="text" className="form-control" onChange={this.handleChange} />
                                {(this.state.showAutoSuggest && this.state.searchTerm) ?
                                    <FetchedData loadingComplete>
                                        <Param name="auto" url={`/suggest/?genome=${this.state.genome}&q=${this.state.searchTerm}`} type="json" />
                                        <AutocompleteBox name="annotation" userTerm={this.state.searchTerm} handleClick={this.handleAutocompleteClick} />
                                    </FetchedData>
                                : null}
                                <div className="input-group-addon input-group-select-addon">
                                    <select value={this.state.genome} name="genome" onFocus={this.closeAutocompleteBox} onChange={this.handleAssemblySelect}>
                                        {regionGenomes.map(genomeId =>
                                            <option key={genomeId.value} value={genomeId.value}>{genomeId.display}</option>
                                        )}
                                    </select>
                                </div>
                                {context.notification ?
                                    <p className="input-region-error">{context.notification}</p>
                                : null}
                            </div>
                        </div>
                        <input type="submit" value="Search" className="btn btn-sm btn-info pull-right" onFocus={this.handleSearchButtonFocus} />
                    </form>
                    {context.coordinates ?
                            <p>Searched coordinates: <strong>{context.coordinates}</strong></p>
                        : null}
                    {context.regulome_score ?
                        <p><strong>RegulomeDB score: {context.regulome_score}</strong></p>
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


class RegionSearch extends React.Component {
    constructor() {
        super();

        // Bind this to non-React methods.
        this.onFilter = this.onFilter.bind(this);
    }

    onFilter(e) {
        if (this.props.onChange) {
            const search = e.currentTarget.getAttribute('href');
            this.props.onChange(search);
            e.stopPropagation();
            e.preventDefault();
        }
    }

    render() {
        const visualizeLimit = 100;
        const context = this.props.context;
        const results = context['@graph'];
        const columns = context.columns;
        const notification = context.notification;
        const searchBase = url.parse(this.context.location_href).search || '';
        const trimmedSearchBase = searchBase.replace(/[?|&]limit=all/, '');
        const filters = context.filters;
        const facets = context.facets;
        const total = context.total;
        const visualizeDisabled = total > visualizeLimit;

        // Get a sorted list of batch hubs keys with case-insensitive sort
        let visualizeKeys = [];
        if (context.visualize_batch && Object.keys(context.visualize_batch).length) {
            visualizeKeys = Object.keys(context.visualize_batch).sort((a, b) => {
                const aLower = a.toLowerCase();
                const bLower = b.toLowerCase();
                return (aLower > bLower) ? 1 : ((aLower < bLower) ? -1 : 0);
            });
        }

        return (
            <div>
                <h2>{context.title}</h2>
                <AdvSearch {...this.props} />
                    {notification.startsWith('Success') ?
                    <div className="panel data-display main-panel">
                        <div className="row">
                            <div className="col-sm-5 col-md-4 col-lg-3">
                                <FacetList
                                    {...this.props}
                                    facets={facets}
                                    filters={filters}
                                    searchBase={searchBase ? `${searchBase}&` : `${searchBase}?`}
                                    onFilter={this.onFilter}
                                />
                            </div>
                            <div className="col-sm-7 col-md-8 col-lg-9">
                                <div>
                                    <h4>
                                        Showing {results.length} of {total}
                                    </h4>
                                    <div className="results-table-control">
                                        {total > results.length && searchBase.indexOf('limit=all') === -1 ?
                                                <a
                                                    rel="nofollow"
                                                    className="btn btn-info btn-sm"
                                                    href={searchBase ? `${searchBase}&limit=all` : '?limit=all'}
                                                    onClick={this.onFilter}
                                                >
                                                    View All
                                                </a>
                                            :
                                            <span>
                                                {results.length > 25 ?
                                                        <a
                                                            className="btn btn-info btn-sm"
                                                            href={trimmedSearchBase || '/region-search/'}
                                                            onClick={this.onFilter}
                                                        >
                                                            View 25
                                                        </a>
                                                : null}
                                            </span>
                                        }

                                        {visualizeKeys && context.visualize_batch ?
                                            <BrowserSelector
                                                visualizeCfg={context.visualize_batch}
                                                disabled={visualizeDisabled}
                                                title={visualizeDisabled ? `Filter to ${visualizeLimit} to visualize` : 'Visualize'}
                                            />
                                        : null}

                                    </div>
                                </div>

                                <hr />
                                <ul className="nav result-table" id="result-table">
                                    {results.map(result => Listing({ context: result, columns, key: result['@id'] }))}
                                </ul>
                            </div>
                        </div>
                    </div>
                : null}
            </div>
        );
    }
}

RegionSearch.propTypes = {
    context: PropTypes.object.isRequired,
    onChange: PropTypes.func,
};

RegionSearch.defaultProps = {
    onChange: null,
};

RegionSearch.contextTypes = {
    location_href: PropTypes.string,
    navigate: PropTypes.func,
};

globals.contentViews.register(RegionSearch, 'region-search');
