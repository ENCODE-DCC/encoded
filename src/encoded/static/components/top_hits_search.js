import React, {useState} from 'react';
import * as globals from './globals';
import {InputSuggest} from './home';


const topHitsUrl = '/top-hits-raw/';
const topHitsParams = (
    '&field=description&field=accession' +
    '&field=title&field=biosample_summary' +
    '&format=json'
);


class TopHits {
    constructor() {

    }
}


class Hit extends React.Component {

    asString() {
        const embedded = this.props.embedded;
        return `${embedded.accession || embedded["@id"]} - ${embedded.description || embedded.title || embedded.biosample_summary}`;
    }

    render() {
        return <h5>{this.asString()}</h5>;
    }
}


function Type(props) {
    return <h3>{props.type}</h3>;
}


function Hits(props) {
    return props.hits.map(
        hit => {
            const embedded = hit._source.embedded;
            return <Hit key={embedded["@id"]} embedded={embedded} />
        }
    );
}


function HitsByType(props) {
    return (
        <div>
            <Type type={props.type} />
            <Hits hits={props.hits} />
        </div>
    );
}


export class TopHitsSearch extends React.Component {
    constructor() {
        super();
        this.state = {
            a: null,
            currentSearchTerm: '',
            suggestedSearchTerms: [],
        };
        this.lastSearchTerm = '';
        this.throttlingTimer = null;
        this.handleTimerExpiry = this.handleTimerExpiry.bind(this);
        this.startDelayTimer = this.startDelayTimer.bind(this);
        this.searchTermChange = this.searchTermChange.bind(this);
        this.searchTermClick = this.searchTermClick.bind(this);
        this.termSelectHandler = this.termSelectHandler.bind(this);
        this.inputBlur = this.inputBlur.bind(this);
    }

    componentWillUnmount() {
        if (this.throttlingTimer) {
            clearTimeout(this.throttlingTimer);
            this.throttlingTimer = null;
        }
    }

    parseHits(hits, type) {
        return <HitsByType key={type} hits={hits} type={type} />;
    }

    parseResults(results) {
        let parsedResults = results.aggregations.types.types.buckets.map(
            result => this.parseHits(result.top_hits.hits.hits, result.key)
        );
        return parsedResults;
    }

    makeTopHitsUrl(newSearchTerm) {
        return `${topHitsUrl}?searchTerm=${newSearchTerm}${topHitsParams}`;
    }

    fetchTopHits(url) {
        return fetch(
            url,
            {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                }
            }
        ).then(
            response => (response.ok ? response.json() : [])
        ).then(
            results => {
                return this.parseResults(results);
            }
        );
    }

    updateTopHits(newSearchTerm) {
        this.startDelayTimer();
        this.lastSearchTerm = newSearchTerm;
        const url = this.makeTopHitsUrl(newSearchTerm);
        this.fetchTopHits(url).then(
            results => this.setState(
                {suggestedSearchTerms: results, a: results}
            )
        );
    }

    handleTimerExpiry() {
        this.throttlingTimer = null;
        if (this.state.currentSearchTerm !== this.lastSearchTerm) {
            this.updateTopHits(this.state.currentSearchTerm);
        }
    }

    startDelayTimer() {
        this.throttlingTimer = setTimeout(this.handleTimerExpiry, 1000);
    }

    searchTermChange(newSearchTerm) {
        if (newSearchTerm !== this.currentSearchTerm) {
            this.setState({currentSearchTerm: newSearchTerm});
            if (!this.throttlingTimer) {
                this.updateTopHits(newSearchTerm);
            }
        }
    }

    termSelectHandler(term) {
        this.setState({currentSearchTerm: term, suggestedSearchTerms: []});
    }

    clearTerms () {
        this.setState({suggestedSearchTerms: []});
    }

    searchTermClick() {
        this.clearTerms();
    }

    inputBlur() {
        this.clearTerms();
    }

    render() {
        const context = this.props.context;
        const isSearchDisabled = this.state.currentSearchTerm.length === 0;
        return (
            <div>
            <div className="site-search__screen">
                <form>
                    <fieldset>
                <legend className="sr-only">Top hits search</legend>
                        <div className="site-search__input">
                            <label htmlFor="top-hits-search" id="top-hits-search-label">
                                Search for top hits by type
                            </label>
                            <InputSuggest
                                value={this.state.currentSearchTerm}
                                items={this.state.suggestedSearchTerms}
                                inputId="top-hits-search"
                                labelledById="top-hits-search-label"
                                inputChangeHandler={this.searchTermChange}
                                inputClickHandler={this.searchTermClick}
                                inputBlurHandler={this.inputBlur}
                                itemSelectHandler={this.termSelectHandler}
                            />
                        </div>
                    </fieldset>
                </form>
            </div>
            </div>
        );
    }
}


const Title = (props) => {
    return (
        <li>
          <button className={props.styling}>
            {props.value}
          </button>
        </li>
    );
};


const Item = (props) => {
    return (
        <li>
          <button className={props.styling}>
            {props.value}
          </button>
        </li>
    );
};


const Items = (props) => {
    return (
        <ul className={props.styling}>
          <Title value={props.title} styling={props.titleStyling}/>
          {
              props.items.map(
                  item => (
                      <Item
                        key={item.key}
                        value={item.value}
                        styling={item.styling}
                      />
                  )
              )
          }
        </ul>
    );
};




const TopHitsInput = (props) => {
};


const TopHitsResults = (props) => {
};


const TopHitsMenu = (props) => {
};


const NewTopHitsSearch = (props) => {
    const [input, setInput] = useState('');
    const [topHits, setTopHits] = useState(["a", "b"]);
    const [displayResults, setDisplayResults] = useState(true);

    const styling = {
        selectedItem: 'top-hits-search__suggested-results--selected',
        results: 'top-hits-search__suggested-results',
        title: 'top-hits-search__suggested-results--title'

    };

    const items = [
        {
            key: "abc",
            value: "new item list",
            styling: null
        },
        {
            key: "xyz",
            value: "second item list",
            styling: styling['selectedItem']
        },
    ];
    
    return (
        <div className="top-hits-search__input">
          <div className="top-hits-search__input-field">
            <input
              type="text"
              autoComplete="off"
            />
            <Items
              title="My section"
              items={items}
              styling={styling['results']}
              titleStyling={styling['title']}
            />
          </div>
        </div>
    );
};


globals.contentViews.register(NewTopHitsSearch, 'TopHitsSearch');
