import React from 'react';
import PropTypes from 'prop-types';
import url from 'url';
import { Panel, PanelBody, TabPanel } from '../libs/ui/panel';
import GenomeBrowser from './genome_browser';
import * as globals from './globals';
import { FacetList, Listing } from './search';
import { FetchedData, Param } from './fetched';
import { makeSearchUrl } from './gene_search/search';

const AutocompleteBoxMenu = (props) => {
    const handleClick = () => {
        const { term, name } = props;
        props.handleClick(term.title, term.locations, name);
    };

    const { preText, matchText, postText } = props;

    /* eslint-disable jsx-a11y/no-noninteractive-element-interactions, jsx-a11y/no-noninteractive-tabindex, jsx-a11y/click-events-have-key-events */
    return (
        <li tabIndex="0" onClick={handleClick}>
            {preText}<b>{matchText}</b>{postText}
        </li>
    );
    /* eslint-enable jsx-a11y/no-noninteractive-element-interactions, jsx-a11y/no-noninteractive-tabindex, jsx-a11y/click-events-have-key-events */
};

AutocompleteBoxMenu.defaultProps = {
    preText: '',
    postText: '',
};

AutocompleteBoxMenu.propTypes = {
    handleClick: PropTypes.func.isRequired,
    term: PropTypes.object.isRequired,
    name: PropTypes.object.isRequired,
    preText: PropTypes.string,
    matchText: PropTypes.string.isRequired,
    postText: PropTypes.string,
};


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
                    const matchStart = term.title.toLowerCase().indexOf(userTerm);
                    if (matchStart >= 0) {
                        matchEnd = matchStart + userTerm.length;
                        preText = term.title.substring(0, matchStart);
                        matchText = term.title.substring(matchStart, matchEnd);
                        postText = term.title.substring(matchEnd);
                    } else {
                        preText = term.title;
                    }
                    return (
                        <AutocompleteBoxMenu
                            key={term.title}
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


class SearchBox extends React.Component {
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

    handleAutocompleteClick(term, locations, name) {
        const coordinates = locations.filter((location) => location.assembly === this.state.genome)[0];
        const query = `${coordinates.chromosome}:${coordinates.start}-${coordinates.end}`;

        const newTerms = {};
        const inputNode = this.annotation;
        inputNode.value = term;
        newTerms[name] = query;
        this.setState({ terms: newTerms, showAutoSuggest: false });
        inputNode.focus();
        // Now let the timer update the terms state when it gets around to it.
    }

    handleAssemblySelect(event) {
        // Handle click in assembly-selection <select>
        this.setState({ genome: event.target.value });
    }

    handleOnFocus(e) {
        this.setState({ showAutoSuggest: false });

        const query = e.currentTarget.getElementsByClassName('form-control')[0].value;
        const annotation = e.currentTarget.elements.annotation[0].value;
        const assembly = this.state.genome;
        this.props.handleSearch(query, annotation, assembly);

        e.stopPropagation();
        e.preventDefault();
    }

    tick() {
        if (this.newSearchTerm !== this.state.searchTerm) {
            this.setState({ searchTerm: this.newSearchTerm });
        }
    }

    render() {
        const regionGenomes = ['GRCh38', 'mm10'];
        const defaultAssembly = regionGenomes[0];

        const context = this.props;
        const id = url.parse(this.context.location_href, true);

        if (this.state.genome === '') {
            const assembly = this.props.assembly || id.query.genome || defaultAssembly;

            if (regionGenomes.indexOf(assembly) !== -1) {
                this.setState({ genome: assembly });
            } else {
                this.setState({ genome: defaultAssembly });
            }
        }

        const suggest = `https://www.encodeproject.org${makeSearchUrl(this.state.searchTerm, this.state.genome)}`;

        return (
            <Panel>
                <PanelBody>
                    <form id="panel1" className="adv-search-form" autoComplete="off" aria-labelledby="tab1" onSubmit={this.handleOnFocus}>
                        <input type="hidden" name="annotation" value={this.state.terms.annotation} />
                        <label htmlFor="annotation">Enter any one of human Gene name, Symbol, Synonyms, Gene ID, HGNC ID, coordinates, rsid, Ensemble ID</label>
                        <div className="adv-search-form__input">
                            <input id="annotation" ref={(input) => { this.annotation = input; }} name="region" type="text" className="form-control" onChange={this.handleChange} />
                            {(this.state.showAutoSuggest && this.state.searchTerm) ?
                                <FetchedData loadingComplete>
                                    <Param name="auto" url={suggest} type="json" />
                                    <AutocompleteBox name="annotation" userTerm={this.state.searchTerm} handleClick={this.handleAutocompleteClick} />
                                </FetchedData>
                            : null}
                            <select value={this.state.genome} name="genome" onFocus={this.closeAutocompleteBox} onChange={this.handleAssemblySelect}>
                                {regionGenomes.map((genome) => (
                                    <option key={genome} value={genome}>{genome}</option>
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

SearchBox.defaultProps = {
    assembly: 'GRCh38',
    notification: '',
    coordinates: '',
};

SearchBox.propTypes = {
    assembly: PropTypes.string,
    handleSearch: PropTypes.func.isRequired,
    notification: PropTypes.string,
    coordinates: PropTypes.string,
};

SearchBox.contextTypes = {
    autocompleteTermChosen: PropTypes.bool,
    autocompleteHidden: PropTypes.bool,
    onAutocompleteHiddenChange: PropTypes.func,
    location_href: PropTypes.string,
};

const RegionSearch = (props, context) => {
    const defaultAssembly = 'GRCh38';
    const encyclopediaVersion = 'ENCODE v5';
    const visualizationOptions = ['Datasets', 'Genome Browser'];
    const defaultVisualization = 'Datasets';
    const supportedFileTypes = ['bigWig', 'bigBed'];

    const initialGBrowserFiles = (props.context.gbrowser || []).filter((file) => supportedFileTypes.indexOf(file.file_format) > -1);
    const availableFileTypes = [...new Set(initialGBrowserFiles.map((file) => file.file_format))];

    const [selectedVisualization, setSelectedVisualization] = React.useState(defaultVisualization);
    const [selectedFileTypes, setSelectedFileTypes] = React.useState(availableFileTypes);
    const [gBrowserFiles, setGBrowserFiles] = React.useState(initialGBrowserFiles);
    const selectedAssembly = url.parse(context.location_href, true).query.genome || defaultAssembly;

    const searchBase = url.parse(context.location_href).search || '';
    const trimmedSearchBase = searchBase.replace(/[?|&]limit=all/, '');

    const results = props.context['@graph'];

    const { columns, filters, facets, total } = props.context;

    const chooseFileType = (e) => {
        const type = e.currentTarget.getAttribute('name');

        if (supportedFileTypes.indexOf(type) === -1) {
            return;
        }

        const newSelectedTypes = [...selectedFileTypes];
        const index = newSelectedTypes.indexOf(type);

        if (index === -1) {
            newSelectedTypes.push(type);
        } else {
            newSelectedTypes.splice(index, 1);
        }

        setSelectedFileTypes(newSelectedTypes);

        e.stopPropagation();
        e.preventDefault();
    };

    React.useEffect(() => {
        const newGBrowserFiles = (props.context.gbrowser || []).filter((file) => selectedFileTypes.indexOf(file.file_format) > -1);
        setGBrowserFiles(newGBrowserFiles);
    }, [selectedFileTypes]);

    const onFilter = (e) => {
        if (props.onChange) {
            const search = e.currentTarget.getAttribute('href');
            props.onChange(search);
            e.stopPropagation();
            e.preventDefault();
        }
    };

    const visualizationTabs = {};
    visualizationOptions.forEach((visualizationName) => {
        visualizationTabs[visualizationName] = <div id={visualizationName} className={`organism-button ${visualizationName.replace(' ', '-')}`}><span>{visualizationName}</span></div>;
    });

    const handleSearch = (query, annotation, assembly) => {
        window.location = `/region-search/?region=${encodeURIComponent(query)}&annotation=${annotation}&genome=${assembly}`;
    };

    const handlePagination = (e) => {
        e.preventDefault();
        e.stopPropagation();

        window.location = e.currentTarget.getAttribute('href');
    };

    const resultsList = (
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
                        <h4>Showing {results.length} of {total}</h4>
                        <div className="results-table-control__main">
                            {total > results.length && searchBase.indexOf('limit=all') === -1 ?
                            <a
                                rel="nofollow"
                                className="btn btn-info btn-sm"
                                href={searchBase ? `${searchBase}&limit=all` : '?limit=all'}
                                onClick={handlePagination}
                            >
                                View All
                            </a>
                            :
                            <span>
                                {results.length > 25 ?
                                    <a
                                        className="btn btn-info btn-sm"
                                        href={trimmedSearchBase || '/region-search/'}
                                        onClick={handlePagination}
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
                                    additionalFacet={
                                        <>
                                            <div className="facet ">
                                                <h5>File Type</h5>
                                                {availableFileTypes.map((type) => (
                                                    <button type="button" name={type} className="facet-term annotation-type" onClick={chooseFileType}>
                                                        {(selectedFileTypes.indexOf(type) > -1) ?
                                                            <span className="full-dot dot" />
                                                        :
                                                            <span className="empty-dot dot" />
                                                        }
                                                        <div className="facet-term__text">
                                                            {type}
                                                        </div>
                                                    </button>
                                                ))}
                                            </div>
                                        </>
                                    }
                                />
                            </div>

                            <div className="search-results__result-list" style={{ display: 'block' }}>
                                <GenomeBrowser
                                    files={gBrowserFiles}
                                    label="cart"
                                    assembly={selectedAssembly}
                                    expanded
                                    annotation="V33"
                                    displaySort
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

                    <SearchBox {...props.context} handleSearch={handleSearch} />

                    { results.length > 0 ?
                    <div className="outer-tab-container">
                        <TabPanel
                            tabs={visualizationTabs}
                            selectedTab={selectedVisualization}
                            handleTabClick={(tab) => setSelectedVisualization(tab)}
                            tabCss="tab-button"
                            tabPanelCss="tab-container encyclopedia-tabs"
                        >
                            { selectedVisualization === 'Datasets' ? resultsList : genomeBrowserView }
                        </TabPanel>
                    </div> : null }
                </div>
            </div>
        </div>
    );
};

RegionSearch.defaultProps = {
    onChange: () => {},
};

RegionSearch.propTypes = {
    context: PropTypes.object.isRequired,
    onChange: PropTypes.func,
};

RegionSearch.contextTypes = {
    location_href: PropTypes.string,
    navigate: PropTypes.func,
    fetch: PropTypes.func,
};

globals.contentViews.register(RegionSearch, 'region-search');
