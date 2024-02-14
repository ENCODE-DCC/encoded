import { partitionStringByMatchingOrNot } from './match';
import { WHITESPACE } from '../top_hits/constants';
import {
    maybeConvertArrayToString,
    uniqueAndDefinedValues,
} from '../top_hits/hits/base';


/**
* Used to add square brackets around a string value that might not exist.
* @param {string} value - String value to put in brackets.
* @return {string} Either the empty string or a string with square brackets.
*/
export const maybeFormatStringInSquareBrackets = (value) => {
    if (value.length > 0) {
        return `[${value}]`;
    }
    return value;
};


/**
* Used to normalize a value for improved highlighting of matching term.
* Removes single and double quotes (helps highlight terms even if query
* is in quotes), makes lowercase (helps for case insenstive matching),
* and trims whitespace.
* @param {string} value - String value to normalize.
* @return {string} Normalized string.
*/
export const normalizeStringForMatching = (value) => (
    value.replace(/['"]+/g, '').toLowerCase().trim()
);


/**
* Encapsulates all of the parsing and highlighting for a gene search result
* as well the calculation for getting the gene location by assembly for
* visualization on a browser.
*/
class Gene {
    constructor(item, searchTerm) {
        this.item = item;
        this.searchTerm = searchTerm;
        this.normalizedSearchTerm = normalizeStringForMatching(
            searchTerm
        );
    }

    /**
    * We only want to show synonyms or dbxrefs if they match
    * the user's searchTerm.
    */
    getFilteredGeneSynonymsAndRefs() {
        const filteredSynonymsAndRefs = (
            this.item.synonyms || []
        ).concat(
            this.item.dbxrefs || []
        ).filter(
            (alias) => alias.toLowerCase().includes(
                this.normalizedSearchTerm
            )
        );
        return maybeFormatStringInSquareBrackets(
            maybeConvertArrayToString(
                filteredSynonymsAndRefs
            )
        );
    }

    /**
    * We check to see if the search result has the user's
    * searchTerm in the title of the gene.
    */
    searchTermMatchesGeneTitle() {
        return this.item.title.toLowerCase().includes(
            this.normalizedSearchTerm
        );
    }

    /**
    * We show the title if the user's searchTerm has a match
    * in the title. Otherwise we show the title and matching
    * synonyms or dbxrefs, if any.
    */
    formatGeneTitleAndMaybeSynonyms() {
        if (this.searchTermMatchesGeneTitle()) {
            return this.item.title;
        }
        return maybeConvertArrayToString(
            uniqueAndDefinedValues(
                [
                    this.item.title,
                    this.getFilteredGeneSynonymsAndRefs(),
                ],
            ),
            WHITESPACE
        );
    }

    /**
    * Used for display in input box.
    */
    asString() {
        return this.formatGeneTitleAndMaybeSynonyms();
    }

    /**
    * Used for mapping the matching and mismatching parts
    * to formatting components.
    */
    asMatchingOrNot() {
        return partitionStringByMatchingOrNot(
            this.normalizedSearchTerm,
            this.asString(),
        );
    }

    /**
    * Sometimes nice to have the plain title for display.
    */
    title() {
        return this.item.title;
    }

    /**
    * This returns the appropriate gene location (which
    * should exist) given the assembly.
    */
    location(assembly) {
        return this.item.locations.find(
            (location) => location.assembly === assembly
        );
    }

    /**
    * This is for passing to the genome browser for viewing
    * the gene at a slightly zoomed out resolution.
    */
    locationForVisualization(assembly) {
        const location = this.location(assembly);
        const halfGeneLength = Math.round(
            (location.end - location.start) / 2
        );
        return {
            contig: location.chromosome,
            x0: location.start - halfGeneLength,
            x1: location.end + halfGeneLength,
        };
    }
}


export const geneFactory = (item, searchTerm) => (
    new Gene(item, searchTerm)
);


export default Gene;
