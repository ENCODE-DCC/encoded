// node_modules
import React from 'react';
import { PropTypes } from 'prop-types';
// libs
import { encodedURIComponent } from '../../libs/query_encoding';
// libs/ui
import { DropdownMenu } from '../../libs/ui/dropdown-menu';
import { svgIcon } from '../../libs/svg-icons';


/**
 * Displays the dropdown menu for the given SCREEN suggestions.
 */
export const ScreenSuggestionsMenu = ({ suggestions, onSelectSuggestion, onClearSuggestions }) => {
    React.useEffect(() => {
        // Clicks in the document outside the suggestion menu should close the menu.
        const onClickOutsideSuggestionsMenu = () => {
            onClearSuggestions();
        };

        // Add the click handler to dismiss the dropdown menu.
        document.addEventListener('click', onClickOutsideSuggestionsMenu, false);
        return () => {
            document.removeEventListener('click', onClickOutsideSuggestionsMenu);
        };
    }, []);

    return (
        <div className="home-screen-suggestions">
            <DropdownMenu>
                {suggestions.map((suggestion) => (
                    <button
                        type="button"
                        key={suggestion}
                        onClick={() => { onSelectSuggestion(suggestion); }}
                    >
                        {suggestion}
                    </button>
                ))}
            </DropdownMenu>
        </div>
    );
};

ScreenSuggestionsMenu.propTypes = {
    /** User search-term suggestions from SCREEN server */
    suggestions: PropTypes.array.isRequired,
    /** Called when the user selects a suggestion */
    onSelectSuggestion: PropTypes.func.isRequired,
    /** Called when the user wants to hide the suggestions menu */
    onClearSuggestions: PropTypes.func.isRequired,
};


/**
 * Compose a URL for the SCREEN server to search for a given search term.
 * @param {string} searchTerm - The user's SCREEN search term
 * @param {string} assembly - The assembly to search; GRCh38 or mm10
 * @returns {string} The URL to the SCREEN server for the given search term
 */
const screenSearchUrl = (searchTerm, assembly) => (
    `https://screen.wenglab.org/search/?q=${encodedURIComponent(searchTerm)}&uuid=0&assembly=${assembly}`
);


/**
 * Displays the supplemental search section showing links to the SCREEN search page for human and
 * mouse assemblies for the given search term.
 */
export const ScreenSupplement = ({ searchTerm }) => (
    <div className="home-search-section__supplement home-search-section__supplement--screen">
        <a
            className="btn btn-info btn-sm"
            href={screenSearchUrl(searchTerm, 'GRCh38')}
            disabled={!searchTerm}
            target="_blank"
            rel="noopener noreferrer"
        >
            Human GRCh38
            {svgIcon('magnifyingGlass')}
        </a>
        <a
            className="btn btn-info btn-sm"
            href={screenSearchUrl(searchTerm, 'mm10')}
            target="_blank"
            disabled={!searchTerm}
            rel="noopener noreferrer"
        >
            Mouse mm10
            {svgIcon('magnifyingGlass')}
        </a>
    </div>
);

ScreenSupplement.propTypes = {
    /** User-entered SCREEN search-term */
    searchTerm: PropTypes.string.isRequired,
};
