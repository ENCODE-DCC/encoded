import * as globals from './globals';
import React, {useState} from 'react';
import PropTypes from 'prop-types';


const topHitsUrl = '/top-hits-raw/';
const topHitsParams = (
    '&field=description&field=accession' +
    '&field=title&field=summary&field=biosample_summary' +
    '&field=assay_term_name&field=file_type&field=status' +
    '&field=antigen_description' +
    '&format=json'
);


const debounceFunction = (func, delay, timerId) => {
    clearTimeout(timerId);
    return setTimeout(func, delay);
};


class TopHitsQuery {
    constructor(searchTerm) {
        this.searchTerm = searchTerm;
    }

    parseHits(hits) {
        return hits.map(
            (hit) => hit._source.embedded
        );
    }

    parseResults(results) {
        return results.aggregations.types.types.buckets.map(
            (result) => (
                {
                    key: result.key,
                    count: result.doc_count,
                    hits: this.parseHits(result.top_hits.hits.hits)
                }
            )
        );
    }

    makeTopHitsUrl() {
        return `${topHitsUrl}?searchTerm=${this.searchTerm}${topHitsParams}`;
    }

    fetchAndParseTopHits(url) {
        console.log('making request');
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

    getResults() {
        return this.fetchAndParseTopHits(
            this.makeTopHitsUrl()
        );
    }
}


class Hit {
    constructor(item) {
        this.item = item;
    }

    formatName() {
        return this.item.accession || this.item['@id'];
    }

    formatDescription() {
        return (
            this.item.description ||
            this.item.summary ||
            this.item.biosample_summary ||
            this.item.assay_term_name ||
            this.item.title
        );
    }

    formatDetails() {
        return (
            this.item.file_type ||
            this.item.antingen_description
        );
    }

    asString() {
        return [
            this.formatDescription(),
            this.formatDetails(),
            this.formatName(),
            this.item.status
        ].filter(Boolean).join(' - ');
    }
};


const LinkWithHover = (props) => {
    const [isHovered, setIsHovered] = useState(false);
    return (
        <button
          className={isHovered ? props.hoverClass: props.defaultClass}
          onMouseEnter={() => setIsHovered(true)}
          onMouseLeave={() => setIsHovered(false)}
        >
          <a href={props.href}>
            {props.value}
          </a>
        </button>
    );
};


const Title = (props) => {
    return (
        <LinkWithHover
          value={props.value}
          defaultClass={'top-hits-search__suggested-results-title'}
          hoverClass={'top-hits-search__suggested-results-title--selected'}
          href={props.href}
        />
    );
};


const Item = (props) => {
    const hit = new Hit(props.item);
    return (
        <li>
          <LinkWithHover
            value={hit.asString()}
            hoverClass={'top-hits-search__suggested-results--selected'}
            href={props.href}
          />
        </li>
    );
};


const Items = (props) => {
    return (
        <ul>
          {
              props.items.map(
                  item => (
                      <Item
                        key={item["@id"]}
                        item={item}
                        href={item["@id"]}
                      />
                  )
              )
          }
        </ul>
    );
};


const Section = (props) => {
    return (
        <>
          <Title value={props.title} href={props.href}/>
          <Items
            items={props.items}
          />
        </>
    );
};


const TopHitsInput = (props) => {
    return (
        <input
          type="text"
          autoComplete="off"
          name="searchTerm"
          placeholder="Search for top hits by type"
          value={props.value}
          onChange={props.onChange}
        />
    );
};


const TopHitsResults = (props) => {
    const makeTitle = (result) => {
        return `${result.key} (${result.count})`;
    };
    return (
        <div className='top-hits-search__suggested-results'>
          {
              props.results.map(
                  (result) => (
                      <Section
                        key={result.key}
                        title={makeTitle(result)}
                        href={`/search/?type=${result.key}&searchTerm=${props.input}`}
                        items={result.hits}
                      />
                  )
            )}
        </div>
    );
};


const TopHitsSearch = (props) => {
    const [input, setInput] = useState('');
    const [topHits, setTopHits] = useState([]);
    const [displayResults, setDisplayResults] = useState(true);
    const [debounceTimer, setDebounceTimer] = useState(null);
    const debounceTime = 200;

    const makeSearchAndSetTopHits = (searchTerm) => {
        const topHitsQuery = new TopHitsQuery(searchTerm);
        topHitsQuery.getResults().then(
            (results) => setTopHits(results)
        );
    };

    const setDebouncedTopHits = (searchTerm) => {
        setDebounceTimer(
            debounceFunction(
                () => {
                    makeSearchAndSetTopHits(searchTerm);
                },
                debounceTime,
                debounceTimer
            )
        );
    };

    const handleInputChange = (e) => {
        const value = e.target.value;
        setInput(value);
        setDebouncedTopHits(e.target.value);
    };

    return (
        <div className="top-hits-search__input">
          <div className="top-hits-search__input-field">
            <form action="/search/">
              <TopHitsInput input={input} onChange={handleInputChange} />
            </form>
            <TopHitsResults input={input} results={topHits} />
          </div>
        </div>
    );
};


TopHitsSearch.contextTypes = {
    fetch: PropTypes.func
};


globals.contentViews.register(TopHitsSearch, 'TopHitsSearch');
