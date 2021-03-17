import _ from 'underscore';
import {
    MAX_WORDS_SHORT,
    SCIENTIFIC_NAME,
    TERM_NAME,
    WHITESPACE,
} from '../constants';
import { fieldToComponent } from './parts';


/**
* Shortens a sentence to maxWords.
* @param {string} value - Sentence to trim.
* @param {number} maxWords - Max number of words to return.
* @return {string} Trimmed sentence.
*/
export const maybeTrimByWord = (value, maxWords) => {
    const splitValue = value.split(WHITESPACE);
    if (splitValue.length > maxWords) {
        return `${splitValue.slice(0, maxWords).join(WHITESPACE)}...`;
    }
    return value;
};


/**
* Some fields are lists and should be converted to strings.
* @param {string|array} value - String or array to convert to string.
* @param {string} sep - Token to join array on.
* @return {string} Original string or joined array.
*/
export const maybeConvertArrayToString = (value, sep = ', ') => {
    if (Array.isArray(value)) {
        return value.join(sep);
    }
    return value;
};


/**
* Helper function to filter arrays of undefined values and only keep
* unique values.
* @param {array} values - Array to filter and make unique.
* @return {array} Unique array with only truthy values.
*/
export const uniqueAndDefinedValues = (values) => (
    _.uniq(
        _.compact(
            values
        )
    )
);


/**
* Helper function to pull desired field from an object
* or a list of objects.
* @param {object|array} valueOrValues - Object or array of objects that might have field.
* @return {string|array} Value or unique list of values found (if they exist).
*/
export const maybeGetUniqueFieldsFromArray = (valueOrValues, fieldName) => {
    if (Array.isArray(valueOrValues)) {
        const values = valueOrValues.map(
            (value) => value[fieldName]
        );
        return uniqueAndDefinedValues(values);
    }
    return valueOrValues[fieldName];
};


/**
* Encapsulates all the formatting for a raw top hit result. This
* tries to generalize across most objects and return the first
* value for that category that exists. It's important to remember
* that these fields have to be specifically requested in the params
* of the query URL (i.e. ?field=param) defined in ./constants.
*/
class Hit {
    constructor(item) {
        this.item = item;
    }

    /**
    * @return {string|array|undefined} Term name value pulled from biosample ontology field.
    */
    maybeGetBiosampleOntologyFromArray() {
        return maybeGetUniqueFieldsFromArray(
            this.item.biosample_ontology || this.item.dataset_details.biosample_ontology,
            TERM_NAME
        );
    }

    /**
    * @return {string|array|undefined} Scientific name pulled from organism field.
    */
    maybeGetOrganismFromArray() {
        return maybeGetUniqueFieldsFromArray(
            this.item.organism,
            SCIENTIFIC_NAME
        );
    }

    /**
    * @return {array} Unique organisms pulled from replicates.
    */
    getOrganismFromReplicates() {
        const organisms = (
            this.item.replicates || []
        ).map(
            (replicate) => (
                replicate.library &&
                replicate.library.biosample &&
                replicate.library.biosample.organism &&
                replicate.library.biosample.organism.scientific_name
            )
        );
        return uniqueAndDefinedValues(organisms);
    }

    /**
    * @return {array} Unique labels pulled from targets.
    */
    getLabelsFromTargets() {
        const labels = (
            this.item.targets || []
        ).map(
            (target) => target.label
        );
        return uniqueAndDefinedValues(labels);
    }

    /**
    * @return {string|undefined} Title value pulled from item.
    */
    formatTitle() {
        return (
            this.item.assay_title ||
            (this.item.dataset_details && this.item.dataset_details.assay_title) ||
            this.item.assay_term_name ||
            (this.item.dataset_details && this.item.dataset_details.assay_term_name) ||
            this.item.term_name ||
            this.item.category ||
            this.item.assay_term_names
        );
    }

    /**
    * @return {string|undefined} Annotation type pulled from annotation.
    */
    formatAnnotationType() {
        return (
            this.item.annotation_type ||
            (this.item.dataset_details && this.item.dataset_details.annotation_type)
        );
    }

    /**
    * @return {string|undefined} Biosample value pulled from item.
    */
    formatBiosample() {
        return (
            (
                this.item.biosample_ontology ||
                (this.item.dataset_details && this.item.dataset_details.biosample_ontology)
            ) &&
            this.maybeGetBiosampleOntologyFromArray()
        );
    }

    /**
    * @return {string|undefined} Target value pulled from item.
    */
    formatTarget() {
        return (
            (this.item.target && this.item.target.label) ||
            (
                this.item.dataset_details &&
                this.item.dataset_details.target &&
                this.item.dataset_details.target.label
            ) ||
            (this.item.targets && this.getLabelsFromTargets())
        );
    }

    /**
    * @return {string|array|undefined} Organism value pulled from item.
    */
    formatOrganism() {
        return (
            (this.item.organism && this.maybeGetOrganismFromArray()) ||
            (this.item.replicates && this.getOrganismFromReplicates())
        );
    }

    /**
    * @return {string|undefined} Name value pulled from item.
    */
    formatName() {
        return (
            this.item.symbol ||
            this.item.label ||
            this.item.title ||
            this.item.accession ||
            this.item.external_accession ||
            (this.item.attachment && this.item.attachment.download) ||
            this.item['@id']
        );
    }

    /**
    * @return {string|undefined} Description value pulled from item.
    */
    formatDescription() {
        return (
            this.item.biosample_summary ||
            this.item.summary ||
            this.item.description ||
            this.item.classification ||
            this.item.antigen_description ||
            this.item.news_excerpt ||
            this.item.abstract ||
            this.item.institute_name ||
            this.item.name ||
            this.item.purpose
        );
    }

    /**
    * Prepends organism to description if it exists. Organism could
    * be a list so it's collapsed to a string first (separated by commas),
    * then organism and description are joined by whitespace.
    * @return {string} Description value prepended with organism.
    */
    formatDescriptionWithOrganism() {
        return maybeConvertArrayToString(
            uniqueAndDefinedValues(
                [
                    maybeConvertArrayToString(
                        this.formatOrganism()
                    ),
                    this.formatDescription(),
                ]
            ),
            WHITESPACE
        );
    }

    /**
    * @return {string|undefined} Lot ID pulled from antibody lot.
    */
    formatLotId() {
        return this.item.lot_id;
    }

    /**
    * @return {string|undefined} Authors pulled from publication.
    */
    formatAuthors() {
        return this.item.authors;
    }

    /**
    * @return {string|undefined} Detail value pulled from item.
    */
    formatDetails() {
        return (
            this.item.document_type ||
            this.item.product_id ||
            this.item.method
        );
    }

    /**
    * This controls the order of values that are displayed in a
    * result, and can be overriden in subtypes to control the values
    * rendered for a specific type. The field string is used to
    * recover the appropriate formatting component and also as a
    * unique rendering key.
    * @return {array} [[field, value], ...] array from item.
    */
    getValues() {
        return [
            ['name', this.formatName()],
            ['annotationType', this.formatAnnotationType()],
            ['title', this.formatTitle()],
            ['biosample', this.formatBiosample()],
            ['target', this.formatTarget()],
            ['details', this.formatDetails()],
            ['lotId', this.formatLotId()],
            ['authors', this.formatAuthors()],
            ['description', this.formatDescriptionWithOrganism()],
        ];
    }

    /**
    * The display values are converted to a string (in case they are
    * a list), and then empty values are filtered out (e.g. not
    * every object has a target etc.).
    * @return {array} Filtered [[field, value], ...] array from item.
    */
    getConvertedAndFilteredValues() {
        return this.getValues().map(
            ([field, value]) => (
                [
                    field,
                    maybeConvertArrayToString(value),
                ]
            )
        ).filter(
            ([, value]) => Boolean(value)
        );
    }

    /**
    * This is the main method called by the Item component that renders a
    * given hit. Long values are trimmed before being wrapped in a formatting
    * component.
    * @return {array} React components to render as a string.
    */
    asString() {
        return this.getConvertedAndFilteredValues().map(
            ([field, value]) => {
                const trimmedValue = maybeTrimByWord(value, MAX_WORDS_SHORT);
                const Component = fieldToComponent[field];
                return <Component key={field} value={trimmedValue} />;
            }
        );
    }

    asDetail() {
        return this.asString(); // useless for now, but allows more detailed view on hover
    }
}


export default Hit;
