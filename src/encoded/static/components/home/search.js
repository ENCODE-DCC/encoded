// node_modules
import React from 'react';
import PropTypes from 'prop-types';
import { AnimatePresence, motion } from 'framer-motion';
// libs
import { svgIcon } from '../../libs/svg-icons';
import Timeout from '../../libs/timeout';
// libs/ui
import BooleanToggle from '../../libs/ui/boolean-toggle';
import Tooltip from '../../libs/ui/tooltip';
// components
import { useMount, useSessionStorage } from '../hooks';
// local
import {
    NATIVE_ICON,
    SCREEN_ICON,
    SEARCH_INPUT_ID_NATIVE,
    SEARCH_INPUT_ID_SCREEN,
    SEARCH_MODE_ICON_SIZE,
    SEARCH_TIMEOUT_NATIVE,
    SEARCH_TIMEOUT_SCREEN,
} from './constants';
import { requestCollectionsAndTypeHits, requestScreenSuggestions } from './request';
import { ScreenSuggestionsMenu, ScreenSupplement } from './screen';


/**
 * Controls the search text input field for both SCREEN- and ENCODE-mode searches. Once the user
 * stops typing their search term, send a request to the server to retrieve the corresponding
 * collection titles and return them, or the SCREEN suggestions.
 */
const SearchInput = ({
    searchTerm,
    isNativeMode,
    onSearchTermChange,
    onReceiveCollectionsAndTypeHits,
    onReceiveScreenSuggestions,
}) => {
    /** True if search request to server is in flight */
    const [isSearchInProgress, setIsSearchInProgress] = React.useState(false);
    /** References the Timeout object; set once user starts typing */
    const timeout = React.useRef(null);
    /** Ref to focus search input */
    const searchInputRef = React.useRef(null);
    /** Refs to avoid stale closures in callbacks */
    const searchTermForRequest = React.useRef();
    searchTermForRequest.current = searchTerm;
    const isNativeModeForRequest = React.useRef();
    isNativeModeForRequest.current = isNativeMode;

    const textInputId = isNativeMode ? SEARCH_INPUT_ID_NATIVE : SEARCH_INPUT_ID_SCREEN;

    /**
     * Called when the request timeout has expired. In native search mode, we then send a request
     * for collections matching the user's search text. In SCREEN search mode, we send a request
     * for terms matching the search term. Once we receive the response, pass the results to the
     * parent component.
     */
    const onRequestTimeoutExpired = () => {
        if (isNativeModeForRequest.current) {
            // Native collections search.
            setIsSearchInProgress(true);
            requestCollectionsAndTypeHits(searchTermForRequest.current).then(({ collectionTitles, typeHits }) => {
                setIsSearchInProgress(false);
                onReceiveCollectionsAndTypeHits(collectionTitles, typeHits, searchTermForRequest.current);
            });
        } else {
            // SCREEN suggestions search.
            requestScreenSuggestions(searchTermForRequest.current).then((suggestions) => {
                onReceiveScreenSuggestions(suggestions, searchTermForRequest.current);
            });
        }
    };

    /**
     * Call this to get a reference to the Timeout object instead of using a variable.
     * @param {boolean} createNewTimeout - True to stop any existing Timeout and start a new one.
     */
    const getRequestTimeout = (createNewTimeout) => {
        // Stop and clear any existing Timeout if requested to create a new timer unconditionally.
        if (createNewTimeout && timeout.current) {
            timeout.current.stop();
            timeout.current = null;
        }

        // Create a new Timeout if none exists.
        if (!timeout.current) {
            timeout.current = new Timeout(
                onRequestTimeoutExpired,
                isNativeModeForRequest.current ? SEARCH_TIMEOUT_NATIVE : SEARCH_TIMEOUT_SCREEN,
            );
        }
        return timeout.current;
    };

    /**
     * Called when the user changes the input text. Sets the new value in state and restarts the
     * request timer.
     * @param {string} value Current value in input field
     */
    const onTextInputChange = (value) => {
        onSearchTermChange(value);
        getRequestTimeout().restart();
    };

    /**
     * Call to clear the search term and focus the search input field when the user clicks the
     * button to clear the search box.
     */
    const clearSearchTerm = () => {
        getRequestTimeout(true);
        onSearchTermChange('');
        onReceiveCollectionsAndTypeHits({}, [], '');
        searchInputRef.current.focus();
    };

    React.useEffect(() => {
        // If the native mode changes, clear the timeout so we can use a different timeout value
        // for the new mode.
        getRequestTimeout(true);
    }, [isNativeMode]);

    useMount(() => {
        // If we already have a search term on mount, it probably came from session storage so
        // perform a search immediately.
        if (searchTerm) {
            onRequestTimeoutExpired();
        }
    });

    return (
        <div className="home-search-input">
            <input
                ref={searchInputRef}
                id={textInputId}
                name={textInputId}
                type="text"
                value={searchTerm}
                onChange={(e) => onTextInputChange(e.target.value)}
            />
            {isSearchInProgress
                ? <div className="home-search-input__spinner">{svgIcon('spinner')}</div>
                : (
                    <button
                        type="button"
                        onClick={clearSearchTerm}
                        aria-label={searchTerm ? 'Clear search term' : 'Search'}
                    >
                        {svgIcon(searchTerm ? 'multiplication' : 'magnifyingGlass')}
                    </button>
                )
            }
        </div>
    );
};

SearchInput.propTypes = {
    /** Current entry in the search text field */
    searchTerm: PropTypes.string.isRequired,
    /** True if user has selected native ENCODE search; false for SCREEN */
    isNativeMode: PropTypes.bool.isRequired,
    /** Called when the user changes the contents of the search text field */
    onSearchTermChange: PropTypes.func.isRequired,
    /** Called once the collection titles and top hits that have been received from the server */
    onReceiveCollectionsAndTypeHits: PropTypes.func.isRequired,
    /** Called once the SCREEN suggestions have been received from the server */
    onReceiveScreenSuggestions: PropTypes.func.isRequired,
};


/**
 * Displays the toggle to switch between SCREEN and ENCODE mode.
 */
const SearchModeSelector = ({ isNativeMode, onNativeModeSet }) => (
    <div className="home-search-section__selector">
        <button
            type="button"
            aria-label="Enable ENCODE site search"
            name="search-mode-select-native"
            onClick={() => onNativeModeSet(true)}
        >
            ENCODE
        </button>
        <BooleanToggle
            id="search-selector"
            state={!isNativeMode}
            title=""
            voice={`Search selector set to ${isNativeMode ? 'ENCODE' : 'SCREEN'}`}
            triggerHandler={(e) => onNativeModeSet(!e.target.checked)}
            options={{
                switchBackgroundColor: {
                    on: '#707070',
                    off: '#909090',
                },
            }}
        />
        <button
            type="button"
            aria-label="Enable SCREEN site search"
            name="search-mode-select-screen"
            onClick={() => onNativeModeSet(false)}
        >
            SCREEN
        </button>
    </div>
);

SearchModeSelector.propTypes = {
    /** True if the search is in native ENCODE mode */
    isNativeMode: PropTypes.bool.isRequired,
    /** Called when the user changes the search mode */
    onNativeModeSet: PropTypes.func.isRequired,
};


/**
 * Shows the top-hits results as buttons to corresponding searches
 */
const NativeSupplement = ({ typeHits, searchedTerm }) => {
    if (typeHits.length > 0) {
        return (
            <div className="home-search-section__supplement home-search-section__supplement--native">
                {typeHits.map((hit) => {
                    const hitUri = `/search/?type=${hit.key}&searchTerm=${searchedTerm}`;
                    return (
                        <a
                            key={hit.key}
                            href={hitUri}
                            className="btn btn-success btn-xs native-top-hit"
                            aria-label={`List view for type ${hit.key} with ${hit.doc_count} ${hit.doc_count === 1 ? 'match' : 'matches'} for ${searchedTerm}`}
                        >
                            {hit.key}
                            <div className="native-top-hit__count">{hit.doc_count}</div>
                        </a>
                    );
                })}
            </div>
        );
    }
    return null;
};

NativeSupplement.propTypes = {
    /** Hits for the relevant types from the ENCODE collections search */
    typeHits: PropTypes.arrayOf(PropTypes.shape({
        key: PropTypes.string.isRequired,
        doc_count: PropTypes.number.isRequired,
    })).isRequired,
    /** User-entered search term that generated these top hits */
    searchedTerm: PropTypes.string.isRequired,
};


/**
 * Displays the icons corresponding to the current search mode.
 */
const SearchModeIcon = ({ isNativeMode }) => (
    <div className="home-search-mode-icon">
        <img src={isNativeMode ? NATIVE_ICON : SCREEN_ICON} width={SEARCH_MODE_ICON_SIZE} height={SEARCH_MODE_ICON_SIZE} alt="Search icon" />
    </div>
);

SearchModeIcon.propTypes = {
    /** True if the search is in native ENCODE mode */
    isNativeMode: PropTypes.bool.isRequired,
};


/**
 * Variants and transitions for the search title animations.
 */
const TRANSITION_DISTANCE = 300;

const nativeVariants = {
    enter: (isNativeMode) => (
        {
            x: isNativeMode ? -TRANSITION_DISTANCE : TRANSITION_DISTANCE,
            opacity: 0,
        }
    ),
    center: {
        x: 0,
        opacity: 1,
    },
    exit: (isNativeMode) => (
        {
            x: isNativeMode ? TRANSITION_DISTANCE : -TRANSITION_DISTANCE,
            opacity: 0,
        }
    ),
};

const screenVariants = {
    enter: (isNativeMode) => (
        {
            x: isNativeMode ? TRANSITION_DISTANCE : -TRANSITION_DISTANCE,
            opacity: 0,
        }
    ),
    center: {
        x: 0,
        opacity: 1,
    },
    exit: (isNativeMode) => (
        {
            x: isNativeMode ? -TRANSITION_DISTANCE : TRANSITION_DISTANCE,
            opacity: 0,
        }
    ),
};

const searchTransition = {
    x: { type: 'spring', stiffness: 300, damping: 20 },
    opacity: { duration: 0.1 },
};


/**
 * Section containing the search input box, search-mode toggle, and search supplement box.
 */
const SearchSection = ({ onReceiveCollectionTitles }) => {
    /** Current input text box value */
    const [searchTerm, setSearchTerm] = useSessionStorage('home-search', '');
    /** True if searching in native (ENCODE) mode; false for SCREEN mode */
    const [isNativeMode, setIsNativeMode] = React.useState(true);
    /** Top matching hits for the user's search term from server */
    const [typeHits, setTypeHits] = React.useState([]);
    /** User-entered term that generated the search results */
    const [searchTermForRequest, setSearchTermForRequest] = React.useState('');
    /** Suggestions for user-entered search term from SCREEN server */
    const [screenSuggestions, setScreenSuggestions] = React.useState([]);
    const homeSearchSectionBoxCss = `home-search-section__box${isNativeMode ? ' home-search-section__box--native' : ' home-search-section__box--screen'}`;

    /**
     * Called when the user clicks on a suggested SCREEN search term from the suggestion menu. It
     * puts the selected term into the search box and clears the suggestion menu.
     * @param {string} suggestion - Suggested search term from SCREEN server
     */
    const onSelectSuggestion = (suggestion) => {
        setSearchTerm(suggestion);
        setScreenSuggestions([]);
    };

    /**
     * Called when the collection titles and counts, and type hits, are received from the server.
     * @param {object} receivedCollectionTitles - Collection titles and corresponding hit counts
     * @param {array} receivedTypeHits - Top type hits for the user's search term
     * @param {string} resultSearchedTerm - User-entered search term that generated these results
     */
    const onReceiveCollectionsAndTypeHits = (receivedCollectionTitles, receivedTypeHits, resultSearchedTerm) => {
        setTypeHits(receivedTypeHits);
        setSearchTermForRequest(resultSearchedTerm);
        onReceiveCollectionTitles(receivedCollectionTitles, resultSearchedTerm);
    };

    /**
     * Called when the user changes the search mode between native and screen.
     * @param {boolean} newNativeMode - New native-mode setting; true for native, false for screen
     */
    const setNewNativeMode = (newNativeMode) => {
        setIsNativeMode(newNativeMode);
        setSearchTerm('');
        setScreenSuggestions([]);
        setTypeHits([]);
        onReceiveCollectionTitles({}, '');
    };

    return (
        <section className="home-search-section">
            <div className="home-search-section__title">
                <AnimatePresence initial={false} custom={isNativeMode}>
                    {isNativeMode
                        ?
                            <motion.label
                                key="native"
                                variants={nativeVariants}
                                initial="enter"
                                animate="center"
                                exit="exit"
                                custom={isNativeMode}
                                transition={searchTransition}
                                htmlFor={SEARCH_INPUT_ID_NATIVE}
                            >
                                Search the ENCODE Portal
                                <Tooltip
                                    trigger={svgIcon('questionCircle')}
                                    tooltipId="search-encode"
                                    css="tooltip-container--home-search"
                                >
                                    Search the entire ENCODE portal by using terms like
                                    &ldquo;skin,&rdquo; &ldquo;ChIP-seq,&rdquo; or
                                    &ldquo;CTCF.&rdquo;
                                </Tooltip>
                            </motion.label>
                        :
                            <motion.label
                                key="screen"
                                variants={screenVariants}
                                initial="exit"
                                animate="center"
                                exit="enter"
                                custom={isNativeMode}
                                transition={searchTransition}
                                htmlFor={SEARCH_INPUT_ID_SCREEN}
                            >
                                Search SCREEN
                                <Tooltip
                                    trigger={svgIcon('questionCircle')}
                                    tooltipId="search-encode"
                                    css="tooltip-container--home-search"
                                >
                                    Search for candidate Cis-Regulatory Elements by entering a gene name or
                                    alias, SNP rsID, ccRE accession, or genomic region in the form
                                    chr:start-end; or enter a cell type to filter results e.g.
                                    &ldquo;chr11:5226493-5403124&rdquo; or &ldquo;rs4846913.&rdquo;
                                </Tooltip>
                            </motion.label>
                    }
                </AnimatePresence>
            </div>
            <div className={homeSearchSectionBoxCss}>
                <SearchInput
                    searchTerm={searchTerm}
                    isNativeMode={isNativeMode}
                    onSearchTermChange={setSearchTerm}
                    onReceiveCollectionsAndTypeHits={onReceiveCollectionsAndTypeHits}
                    onReceiveScreenSuggestions={(suggestions) => setScreenSuggestions(suggestions)}
                />
                <SearchModeSelector isNativeMode={isNativeMode} onNativeModeSet={setNewNativeMode} />
                <SearchModeIcon isNativeMode={isNativeMode} />
            </div>
            {screenSuggestions.length > 0 &&
                <ScreenSuggestionsMenu
                    suggestions={screenSuggestions}
                    onSelectSuggestion={onSelectSuggestion}
                    onClearSuggestions={() => setScreenSuggestions([])}
                />
            }
            {isNativeMode
                ? <NativeSupplement typeHits={typeHits} searchedTerm={searchTermForRequest} />
                : <ScreenSupplement searchTerm={searchTerm} />
            }
        </section>
    );
};

SearchSection.propTypes = {
    /** Called when the searched term receives relevant collection titles */
    onReceiveCollectionTitles: PropTypes.func.isRequired,
};

export default SearchSection;
