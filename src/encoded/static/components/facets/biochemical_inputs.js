import PropTypes from 'prop-types';
import FacetRegistry from './registry';
import QueryString from '../../libs/query_string';


/**
 * Biochemical input facet works just like a regular facet but negating is not allowed, links look more like buttons, and there is an "Any" button to select any possible terms
 */
const BiochemicalInputsFacet = ({ results, facet, queryString }, reactContext) => {
    // Get query terms from url
    const originalQuery = new QueryString(queryString);
    const originalInputs = originalQuery.getKeyValues('advancedQuery');

    // Possible query entries must be hard-coded because the facet object does not always include all terms, plus we want to exclude rDHS
    const facetTerms = ['CTCF', 'DNase-seq', 'H3K27ac', 'H3K4me3'];

    // URl should indicate toggle position, but if not, default is "only"
    let switchState = 'only';
    if (reactContext.location_href.indexOf('#or') > -1) {
        switchState = 'or';
    }
    // If no toggle position is indicated, "or" is the position when an "AND NOT" is present or when search is not biochemical_inputs:*
    if (originalInputs && originalInputs[0]) {
        const defaultOnly = (originalInputs[0] === 'biochemical_inputs:*') || (originalInputs[0].toString().indexOf('AND NOT') > -1);
        if ((reactContext.location_href.indexOf('#') === -1) && !(defaultOnly)) {
            switchState = 'or';
        }
    }

    // Generate array of search parameters, ones selected by AND and de-selected by AND NOT
    let originalInputsArray = [];
    let originalNonincludedArray = [];
    if (originalInputs.length > 0) {
        originalInputsArray = originalInputs[0].toString().replace('biochemical_inputs:(', '').replace(')', '').split(' AND ');
        originalInputsArray = originalInputsArray.filter((input) => input.indexOf('NOT') === -1);
    }
    if (originalInputs[0] === 'biochemical_inputs:*') {
        originalInputsArray = facetTerms;
    }
    originalNonincludedArray = facetTerms.filter((key) => originalInputsArray.indexOf(key) === -1);

    // Generate object which includes url for each button (each button is essentially a link)
    // The object also indicates whether the button is currently selected or not (whether the url will be adding or removing that term)
    const facetObj = {};
    facetTerms.forEach((term) => {
        const query = new QueryString(queryString);
        facetObj[term] = {};
        // Add new term if it does not exist
        if (originalInputsArray.indexOf(term) === -1) {
            const newInputsArray = originalInputsArray.concat([term]);
            const nonincludedArray = originalNonincludedArray.filter((elem) => elem !== term);
            if (switchState === 'only') {
                if (nonincludedArray.length === 0) {
                    query.replaceKeyValue('advancedQuery', 'biochemical_inputs:*');
                } else {
                    query.replaceKeyValue('advancedQuery', `biochemical_inputs:(${(Array.isArray(newInputsArray) && (newInputsArray.length > 0)) ? newInputsArray.join(' AND ') : newInputsArray}${(Array.isArray(nonincludedArray) && (nonincludedArray.length > 0)) ? ` AND NOT ${nonincludedArray.join(' AND NOT ')}` : ''})`);
                }
            } else {
                query.replaceKeyValue('advancedQuery', `biochemical_inputs:(${(Array.isArray(newInputsArray) && (newInputsArray.length > 0)) ? newInputsArray.join(' AND ') : newInputsArray})`);
            }
            facetObj[term].selected = false;
            facetObj[term].link = `?${query.format()}#${switchState.toLowerCase()}`;
        // Remove new term if it does exist
        } else {
            const newInputsArray = originalInputsArray.filter((input) => input !== term);
            const nonincludedArray = originalNonincludedArray.concat([term]);
            if (newInputsArray.length === 0) {
                query.deleteKeyValue('advancedQuery');
            } else if (switchState === 'only') {
                query.replaceKeyValue('advancedQuery', `biochemical_inputs:(${(Array.isArray(newInputsArray) && (newInputsArray.length > 0)) ? newInputsArray.join(' AND ') : newInputsArray}${(Array.isArray(nonincludedArray) && (nonincludedArray.length > 0)) ? ` AND NOT ${nonincludedArray.join(' AND NOT ')}` : ''})`);
            } else {
                query.replaceKeyValue('advancedQuery', `biochemical_inputs:(${(Array.isArray(newInputsArray) && (newInputsArray.length > 0)) ? newInputsArray.join(' AND ') : newInputsArray})`);
            }
            facetObj[term].selected = true;
            facetObj[term].link = `?${query.format()}#${switchState}`;
        }
    });

    // The "Any" / "All" button is special and will:
    // (1) de-select all terms if currently selected
    // (2) "Any" executes the query advancedQuery=biochemical_inputs:*
    // (3) "All" executes the query advancedQuery=biochemical_inputs:(CTCF AND DNase-seq AND H3K27ac AND H3K4me3)
    facetObj.Any = {};
    if (originalInputsArray.length === facetTerms.length) {
        const query = new QueryString(queryString);
        query.deleteKeyValue('advancedQuery');
        facetObj.Any.selected = true;
        facetObj.Any.link = `?${query.format()}#${switchState}`;
    } else {
        const query = new QueryString(queryString);
        let newInputsArray = originalInputsArray;
        facetTerms.forEach((term) => {
            if (originalInputsArray.indexOf(term) === -1) {
                newInputsArray = newInputsArray.concat([term]);
            }
        });
        if (switchState === 'or') {
            query.replaceKeyValue('advancedQuery', `biochemical_inputs:(${facetTerms.join(' AND ')})`);
        } else {
            query.replaceKeyValue('advancedQuery', 'biochemical_inputs:*');
        }
        facetObj.Any.selected = false;
        facetObj.Any.link = `?${query.format()}#${switchState}`;
    }

    // Generate url for toggling "Only" switch
    const toggleSwitchState = () => {
        if (Array.isArray(originalInputsArray) && (originalInputsArray.length > 0)) {
            // Generate href for toggling between "AND" and "OR"
            const switchQuery = new QueryString(queryString);
            let switchQueryLink;
            if (switchState === 'or' && originalInputsArray.length === facetTerms.length) {
                switchQuery.replaceKeyValue('advancedQuery', 'biochemical_inputs:*');
                switchQueryLink = `?${switchQuery.format()}#only`;
            } else if (switchState === 'or') {
                switchQuery.replaceKeyValue('advancedQuery', `biochemical_inputs:(${originalInputsArray.join(' AND ')}${(Array.isArray(originalNonincludedArray) && (originalNonincludedArray.length > 0)) ? ` AND NOT ${originalNonincludedArray.join(' AND NOT ')}` : ''})`);
                switchQueryLink = `?${switchQuery.format()}#only`;
            } else {
                switchQuery.replaceKeyValue('advancedQuery', `biochemical_inputs:(${originalInputsArray.join(' AND ')})`);
                switchQueryLink = `?${switchQuery.format()}#or`;
            }
            reactContext.navigate(switchQueryLink, { noscroll: true });
        } else if (switchState === 'only' && reactContext.location_href.indexOf('#') > -1) {
            reactContext.navigate(reactContext.location_href.replace('#only', '#or'), { noscroll: true });
        } else if (reactContext.location_href.indexOf('#') > -1) {
            reactContext.navigate(reactContext.location_href.replace('#or', '#only'), { noscroll: true });
        } else {
            reactContext.navigate(`${reactContext.location_href}#or`, { noscroll: true });
        }
    };

    // Styles for toggle switch
    const DEFAULT_SWITCH_HEIGHT = 22;
    const DEFAULT_SWITCH_WIDTH = DEFAULT_SWITCH_HEIGHT * 1.6;
    const switchWidth = DEFAULT_SWITCH_WIDTH;
    const switchHeight = DEFAULT_SWITCH_HEIGHT;
    const triggerSize = switchHeight - 4;
    const switchStyles = {
        width: switchWidth,
        height: switchHeight,
        borderRadius: switchHeight / 2,
        backgroundColor: (switchState === 'only') ? '#4183c4' : '#e9e9eb',
    };
    const actuatorStyles = {
        width: triggerSize,
        height: triggerSize,
        borderRadius: (switchHeight / 2) - 2,
        top: 2,
        left: (switchState === 'only') ? (switchWidth - switchHeight) + 2 : 2,
    };


    return (
        <div className={`facet ${results['@type'].indexOf('Encyclopedia') === -1 ? 'hide' : ''}`}>
            <h5>{facet.title}</h5>
            <div className="biochemical-toggle-description">When the toggle is on, your search results will be an exact match for your biochemical inputs selections. When the toggle is off, your selections will appear in your search results and may include additional inputs.</div>
            <label className="boolean-switch">
                <div style={switchStyles} className="boolean-switch__frame">
                    <div style={actuatorStyles} className="boolean-switch__actuator" />
                </div>
                <input type="checkbox" checked={switchState === 'only'} onChange={toggleSwitchState} />
                <div className="boolean-switch__title">Only</div>
            </label>
            <div className="facet__multiselect">
                {(facetObj && Object.keys(facetObj).length === (facetTerms.length + 1)) ?
                    <>
                        {facetTerms.map((term) => (
                            <a href={facetObj[term].link} className={facetObj[term].selected ? 'selected' : ''}>
                                {term}
                            </a>
                        ))}
                        <a href={facetObj.Any.link} className={facetObj.Any.selected ? 'selected anyall' : 'anyall'}>
                            {(switchState === 'only') ?
                                'Any'
                            :
                                'All'
                            }
                        </a>
                    </>
                : null}
            </div>
        </div>
    );
};

BiochemicalInputsFacet.propTypes = {
    /** Complete search-results object */
    results: PropTypes.object.isRequired,
    /** Relevant `facet` object from `facets` array in `results` */
    facet: PropTypes.object.isRequired,
    /** Query-string portion of current URL without initial ? */
    queryString: PropTypes.string,
};

BiochemicalInputsFacet.defaultProps = {
    queryString: '',
};

BiochemicalInputsFacet.contextTypes = {
    navigate: PropTypes.func,
    location_href: PropTypes.string,
};

FacetRegistry.Facet.register('biochemical_inputs', BiochemicalInputsFacet);
