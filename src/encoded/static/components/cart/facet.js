import React from 'react';
import PropTypes from 'prop-types';
import _ from 'underscore';
import { Modal, ModalHeader, ModalBody } from '../../libs/ui/modal';
import { encodedURIComponent } from '../../libs/query_encoding';
import { svgIcon } from '../../libs/svg-icons';
import { tintColor, isLight } from '../datacolors';
import { keyCode } from '../globals';
import {
    isFileVisualizable,
    computeAssemblyAnnotationValue,
    filterForDefaultFiles,
    Checkbox,
} from '../objectutils';
import { getAnalysesFileIds, getObjectFieldValue } from './util';


/**
 * Sorter function to sort an array of assemblies/annotations for display in the facet according to
 * system-wide criteria.
 * @param {array} facetTerms Assembly facet terms to sort
 *
 * @return {array} Same as `facetTerms` but sorted
 */
const assemblySorter = (facetTerms) => (
    // Negate the sorting value to sort from highest to lowest.
    _(facetTerms).sortBy((facetTerm) => -computeAssemblyAnnotationValue(facetTerm.term))
);


/**
 * Sorter function for analyses facet terms matches the order from the given analyses which have
 * already been sorted.
 * @param {array} facetTerms Analysis facet terms to sort
 *
 * @return {array} Same as `facetTerms`
 */
const analysisSorter = (facetTerms, analyses) => (
    _(facetTerms).sortBy((facetTerm) => (
        analyses.findIndex((analysis) => analysis.title === facetTerm.term)
    ))
);


/**
 * Field mapping transform for analyses. Generate a query string corresponding to all the selected
 * analyses with the given titles. More than one title can be selected, and more than one analysis
 * can correspond to a title, so all these get combined into one query string.
 * @param {array} analysisTitles Selected analysis titles from the facet.
 *
 * @return {string} Combined query string selecting file.analyses titles.
 */
const analysisFieldMap = (analysisTitles) => (
    analysisTitles.map((title) => `files.analyses.title=${encodedURIComponent(title)}`).join('&')
);


/**
 * Field `getValue` function to extract the top @type from the given dataset.
 * @param {object} dataset ...from which to extract its @type
 * @return {string} Top-level @type of given dataset
 */
const datasetTypeValue = (dataset) => dataset['@type'][0];


/**
 * Display a term of the Dataset Term facets mapped to the English-language equivalent from the
 * profile titles from <App> page load, e.g. "Functional Characterization Experiment" instead of
 * "FunctionalCharacterizationExperiment."
 */
const DatasetTypeTermDisplay = ({ term }, { profilesTitles }) => {
    if (profilesTitles && profilesTitles[term]) {
        return <div className="cart-facet-term__text">{profilesTitles[term]}</div>;
    }
    return <div className="cart-facet-term__text">{term}</div>;
};

DatasetTypeTermDisplay.propTypes = {
    /** Displayed facet term */
    term: PropTypes.string.isRequired,
};

DatasetTypeTermDisplay.contextTypes = {
    profilesTitles: PropTypes.object,
};


/**
 * File facet fields to display in order of display.
 * - field: `facet` field property
 * - title: Displayed facet title
 * - radio: True if radio-button facet; otherwise checkbox facet
 * - dataset: True to retrieve value from dataset instead of files
 * - sorter: Function to sort terms within the facet
 * - fieldMapper: Function to generate a batch download query string
 * - preferred: Facet appears when preferred_default selected
 * - calculated: True for facets displaying calculated (not requested) file/dataset props
 * - parent: Copy expanded state of this field; suppress this facet's expander title
 * - expanded: True to appear expanded by default
 * - nonCollapsable: True for the facet to always appear expanded; no expander trigger
 * - persistent: True if the facet should appear on the main page, not only in the modal
 */
export const displayedFileFacetFields = [
    {
        field: 'assembly',
        title: 'Analysis/Assembly',
        radio: true,
        sorter: assemblySorter,
        preferred: true,
        expanded: true,
        persistent: true,
    },
    {
        field: 'analysis',
        title: 'Analysis',
        dataset: true,
        sorter: analysisSorter,
        fieldMapper: analysisFieldMap,
        persistent: true,
        calculated: true,
        parent: 'assembly',
        css: 'cart-facet--analysis',
    },
    {
        field: 'output_type',
        title: 'Output type',
    },
    {
        field: 'file_type',
        title: 'File type',
    },
    {
        field: 'file_format',
        title: 'File format',
    },
    {
        field: 'lab.title',
        title: 'Lab',
        preferred: true,
    },
    {
        field: 'status',
        title: 'Status',
    },
];

export const displayedDatasetFacetFields = [
    {
        field: 'type',
        title: 'Dataset type',
        getValue: datasetTypeValue,
        termDisplay: DatasetTypeTermDisplay,
        nonCollapsable: true,
        persistent: true,
    },
    {
        field: 'assay_title',
        title: 'Assay title',
    },
    {
        field: 'biosample_ontology.term_name',
        title: 'Biosample',
    },
    {
        field: 'target.label',
        title: 'Target',
    },
    {
        field: 'annotation_type',
        title: 'Annotation type',
    },
    {
        field: 'replicates.library.biosample.organism.scientific_name',
        title: 'Organism',
    },
    {
        field: 'lab.title',
        title: 'Lab',
    },
    {
        field: 'status',
        title: 'Status',
    },
];


/** Get all the facet fields with the `persistent` flag set */
const displayedPersistentFacetFields = displayedDatasetFacetFields.filter((fieldConfig) => fieldConfig.persistent)
    .concat(displayedFileFacetFields.filter((fieldConfig) => fieldConfig.persistent));

/** Facet `field` values for properties from dataset instead of files */
export const datasetFieldFileFacets = ['biosample_ontology.term_name', 'target.label'];


/**
 * Display a count of the total number of elements selected in the facet, given the current facet term
 * selections. Shows the facet-loading progress bar if needed.
 */
const FacetCount = ({ count, element, facetLoadProgress }) => {
    const [triggerEnabled, setTriggerEnabled] = React.useState(false);

    /**
     * Called when CSS animation ends. Removes the <div> that shows the yellow highlight when the
     * count changes.
     */
    const handleAnimationEnd = () => {
        setTriggerEnabled(false);
    };

    React.useEffect(() => {
        // Inserts the <div> to show the yellow highlight when the file count changes.
        setTriggerEnabled(true);
    }, [count]);

    if (facetLoadProgress === -1) {
        const fileCountFormatted = count.toLocaleString ? count.toLocaleString() : count.toString();
        return (
            <div className="cart__facet-count">
                {triggerEnabled ? <div className="cart__facet-count-changer" onAnimationEnd={handleAnimationEnd} /> : null}
                {count > 0 ?
                    <>{svgIcon(element)} {fileCountFormatted} {element}{count !== 1 ? 's' : ''} selected</>
                :
                    <>No files selected for download</>
                }
            </div>
        );
    }

    return <progress value={facetLoadProgress} max="100" />;
};

FacetCount.propTypes = {
    /** Number of files selected for download */
    count: PropTypes.number,
    /** What sort of element to document in the display, e.g. "dataset" */
    element: PropTypes.string.isRequired,
    /** Value for the progress bar; -1 to not show it */
    facetLoadProgress: PropTypes.number,
};

FacetCount.defaultProps = {
    count: 0,
    facetLoadProgress: -1,
};


/**
 * Renders one button showing a current facet selection, and allowing the user to clear the
 * selection.
 */
const SelectionItem = ({ selection, term, selectionType, clickHandler }) => (
    <button
        type="button"
        key={selection}
        onClick={() => clickHandler(term, selection)}
        className="btn btn-xs facet-selections-button"
        aria-label={`Remove ${selection} from filters`}
    >
        <div className="facet-selections-button__icon">{svgIcon(selectionType)}</div>
        <div className="facet-selections-button__label">
            {selection}
        </div>
    </button>
);

SelectionItem.propTypes = {
    selection: PropTypes.string.isRequired,
    term: PropTypes.string.isRequired,
    selectionType: PropTypes.oneOf(['dataset', 'file']).isRequired,
    clickHandler: PropTypes.func.isRequired,
};


/**
 * Renders the buttons that show all the currently selected facet terms.
 */
const Selections = ({ datasetTerms, datasetTermClickHandler, fileTerms, fileTermClickHandler }) => (
    <div className="facet-selections">
        {Object.keys(datasetTerms).map((term) => {
            // Render the selected dataset facet terms first.
            if (datasetTerms[term].length > 0) {
                return (
                    datasetTerms[term].map((selection) => (
                        <SelectionItem key={selection} selection={selection} term={term} selectionType="dataset" clickHandler={datasetTermClickHandler} />
                    ))
                );
            }
            return null;
        })}
        {Object.keys(fileTerms).map((term) => {
            // Render the selected file facet terms second.
            const matchingDisplayField = displayedFileFacetFields.find((fieldDef) => (
                fieldDef.field === term
            ));
            if (!matchingDisplayField.radio && fileTerms[term].length > 0) {
                return (
                    fileTerms[term].map((selection) => (
                        <SelectionItem key={selection} selection={selection} term={term} selectionType="file" clickHandler={fileTermClickHandler} />
                    ))
                );
            }
            return null;
        })}
    </div>
);

Selections.propTypes = {
    datasetTerms: PropTypes.object.isRequired,
    datasetTermClickHandler: PropTypes.func.isRequired,
    fileTerms: PropTypes.object.isRequired,
    fileTermClickHandler: PropTypes.func.isRequired,
};


/**
 * Display the selection checkbox for a single cart file facet term.
 */
const FacetTermCheck = ({ checked }) => (
    <div className={`cart-facet-term__check${checked ? ' cart-facet-term__check--checked' : ''}`}>
        {checked ?
            <i className="icon icon-check" />
        : null}
    </div>
);

FacetTermCheck.propTypes = {
    /** True if facet term checkbox checked */
    checked: PropTypes.bool,
};

FacetTermCheck.defaultProps = {
    checked: false,
};


/**
 * Display the selection radio button for a single cart file facet term.
 */
const FacetTermRadio = ({ checked }) => (
    <div className={`cart-facet-term__radio${checked ? ' cart-facet-term__radio--checked' : ''}`}>
        {checked ?
            <i className="icon icon-circle" />
        : null}
    </div>
);

FacetTermRadio.propTypes = {
    /** True if facet term radio button checked */
    checked: PropTypes.bool,
};

FacetTermRadio.defaultProps = {
    checked: false,
};


/**
 * Render the text contents of a facet term, using custom displays from the `termDisplay` property
 * of a facet definition if provided.
 */
const FacetTermContent = ({ term, displayedFacetField }) => {
    if (displayedFacetField.termDisplay) {
        return <displayedFacetField.termDisplay term={term} displayedFacetField={displayedFacetField} />;
    }
    return <div className="cart-facet-term__text">{term}</div>;
};

FacetTermContent.propTypes = {
    /** Displayed facet term */
    term: PropTypes.string.isRequired,
    /** Field definition representing the facet being displayed */
    displayedFacetField: PropTypes.object.isRequired,
};


/**
 * Display the cart file facet term count that shows the magnitude of a facet term through its
 * color tint. The maximum value for the facet gets the full base color, and lesser values get
 * lighter tints.
 */
const FacetTermMagnitude = ({ termCount, maxTermCount }) => {
    const MAGNITUDE_BASE_COLOR = '#656BFF';
    const magnitudeColor = tintColor(MAGNITUDE_BASE_COLOR, 1 - (termCount / maxTermCount));
    const textColor = isLight(magnitudeColor) ? '#000' : '#fff';
    return (
        <div className="cart-facet-term__magnitude" style={{ backgroundColor: magnitudeColor }}>
            <span style={{ color: textColor }}>{termCount}</span>
        </div>
    );
};

FacetTermMagnitude.propTypes = {
    /** Number of items this facet term indicates */
    termCount: PropTypes.number.isRequired,
    /** Maximum count value among all terms in this facet */
    maxTermCount: PropTypes.number.isRequired,
};


/**
 * Display one term of a facet.
 */
const FacetTerm = ({
    term,
    displayedFacetField,
    termCount,
    maxTermCount,
    selected,
    visualizable,
    termClickHandler,
    FacetTermSelectRenderer,
}) => {
    /**
     * Called when user clicks a term within a facet.
     */
    const handleTermClick = () => {
        termClickHandler(term);
    };

    return (
        <li className="cart-facet-term">
            <button
                className="cart-facet-term__item"
                type="button"
                id={`cart-facet-term-${term}`}
                onClick={handleTermClick}
                aria-pressed={selected}
                aria-label={`${termCount} ${term} file${termCount === 1 ? '' : 's'}${visualizable ? ' visualizable' : ''}`}
            >
                <FacetTermSelectRenderer checked={selected} />
                <FacetTermContent term={term} displayedFacetField={displayedFacetField} />
                <FacetTermMagnitude termCount={termCount} maxTermCount={maxTermCount} />
                <div className="cart-facet-term__visualizable">
                    {visualizable ?
                        <div title="Selects visualizable files">{svgIcon('genomeBrowser')}</div>
                    : null}
                </div>
            </button>
        </li>
    );
};

FacetTerm.propTypes = {
    /** Displayed facet term */
    term: PropTypes.string.isRequired,
    /** Field definition representing the facet being displayed */
    displayedFacetField: PropTypes.object.isRequired,
    /** Displayed number of files for this term */
    termCount: PropTypes.number.isRequired,
    /** Maximum number of files for all terms in the facet */
    maxTermCount: PropTypes.number.isRequired,
    /** True if this term should appear selected */
    selected: PropTypes.bool,
    /** True if term selection results in visualizable files */
    visualizable: PropTypes.bool,
    /** Callback for handling clicks in the term */
    termClickHandler: PropTypes.func.isRequired,
    /** Facet term checkbox/radio renderer */
    FacetTermSelectRenderer: PropTypes.elementType.isRequired,
};

FacetTerm.defaultProps = {
    selected: false,
    visualizable: false,
};


/**
 * Display the title inside the facet expander.
 */
const FacetTitle = ({ title }) => (
    <div className="cart-facet__expander-title">
        {title}
    </div>
);

FacetTitle.propTypes = {
    /** Text title to display */
    title: PropTypes.string.isRequired,
};


/**
 * Display a button that shows an indicator when the user has selected at least one term in the
 * facet, and allows the user to click the indicator to clear all selections within that facet.
 */
const FacetSelectionControl = ({ selectionCount, name, clearSelectionHandler }) => {
    /**
     * Called when the user types a key while the control holds the current selection.
     */
    const handleKeyPress = (e) => {
        if (e.keyCode === keyCode.RETURN || e.keyCode === keyCode.SPACE) {
            e.preventDefault();
            clearSelectionHandler(e);
        }
    };

    if (selectionCount > 0) {
        return (
            <div role="button" tabIndex="0" id={`cart-facet-clear-${name}`} className="cart-facet-clear" onKeyDown={handleKeyPress} onClick={clearSelectionHandler}>
                <div className="cart-facet-clear__control cart-facet-clear__control--has-selections">{svgIcon('circle')}</div>
                <div className="cart-facet-clear__control cart-facet-clear__control--clear-selections">{svgIcon('multiplication')}</div>
                <span className="sr-only">
                    Clear {selectionCount} {selectionCount === 1 ? 'selection' : 'selections'}
                </span>
            </div>
        );
    }
    return null;
};

FacetSelectionControl.propTypes = {
    /** Number of selected terms in the facet */
    selectionCount: PropTypes.number.isRequired,
    /** Used as part of the ID to uniquely identify the button on the page */
    name: PropTypes.string.isRequired,
    /** Function to call when someone clicks the control */
    clearSelectionHandler: PropTypes.func.isRequired,
};


/**
 * Display the facet title and expansion icon, and react to clicks in the button to tell the parent
 * component that a facet needs to be expanded or collapsed.
 */
const FacetExpander = ({ title, field, labelId, expanded, selectionCount, expanderEventHandler, clearFacetSelections }) => {
    /**
     * Called when the user clicks the control to clear all selected terms in the facet.
     */
    const controlClickHandler = (e) => {
        e.stopPropagation();
        clearFacetSelections(field);
    };

    // Use an expander button if the caller provides an event handler to expand or collapse
    // the facet.
    if (expanderEventHandler) {
        return (
            <button
                type="button"
                id={labelId}
                className="cart-facet__expander"
                aria-controls={field}
                aria-expanded={expanded}
                onClick={expanderEventHandler}
            >
                <FacetTitle title={title} />
                {clearFacetSelections ? <FacetSelectionControl name={field} selectionCount={selectionCount} clearSelectionHandler={controlClickHandler} /> : null}
                <i className={`icon icon-chevron-${expanded ? 'up' : 'down'}`} />
            </button>
        );
    }

    // Just display the title without an expander button if no event handler given.
    return (
        <div className="cart-facet__expander cart-facet__expander--non-collapsable">
            <FacetTitle title={title} />
            {clearFacetSelections ? <FacetSelectionControl name={field} selectionCount={selectionCount} clearSelectionHandler={controlClickHandler} /> : null}
        </div>
    );
};

FacetExpander.propTypes = {
    /** Displayed title of the facet */
    title: PropTypes.string.isRequired,
    /** File facet field representing this facet */
    field: PropTypes.string.isRequired,
    /** Used as an id for this button corresponding to expanded component label */
    labelId: PropTypes.string.isRequired,
    /** True if facet is currently expanded */
    expanded: PropTypes.bool.isRequired,
    /** Number of selected terms */
    selectionCount: PropTypes.number.isRequired,
    /** Called when the user clicks the expander button; null for always-open */
    expanderEventHandler: PropTypes.func,
    /** Called when the user clears all selections in a facet */
    clearFacetSelections: PropTypes.func,
};

FacetExpander.defaultProps = {
    expanderEventHandler: null,
    clearFacetSelections: null,
};


/**
 * Display a single file facet.
 */
class Facet extends React.Component {
    constructor() {
        super();
        this.handleFacetTermClick = this.handleFacetTermClick.bind(this);
        this.handleExpanderEvent = this.handleExpanderEvent.bind(this);
    }

    /**
     * Handle a click in a facet term by calling a parent handler.
     * @param {string} term Clicked facet term
     */
    handleFacetTermClick(term) {
        this.props.facetTermClickHandler(this.props.displayedFacetField.field, term);
    }

    /**
     * Handle a click in the facet expander by calling a parent handler.
     * @param {object} e React synthetic event
     */
    handleExpanderEvent(e) {
        this.props.expanderClickHandler(this.props.displayedFacetField.field, e.altKey);
    }

    render() {
        const {
            facet,
            displayedFacetField,
            expanded,
            expanderClickHandler,
            selectedFacetTerms,
            clearFacetSelections,
            options,
        } = this.props;
        const maxTermCount = Math.max(...facet.terms.map((term) => term.count));
        const labelId = `${displayedFacetField.field}-label`;
        const FacetTermSelectRenderer = displayedFacetField.radio ? FacetTermRadio : FacetTermCheck;
        return (
            <div className="facet">
                {!options.supressTitle
                    ? (
                        <FacetExpander
                            title={facet.title}
                            field={displayedFacetField.field}
                            labelId={labelId}
                            expanded={expanded}
                            expanderEventHandler={displayedFacetField.nonCollapsable || !expanderClickHandler ? null : this.handleExpanderEvent}
                            selectionCount={selectedFacetTerms.length}
                            clearFacetSelections={displayedFacetField.radio ? null : clearFacetSelections}
                        />
                    )
                : null}
                {expanded || displayedFacetField.nonCollapsable ?
                    <ul className={`cart-facet${displayedFacetField.css ? ` ${displayedFacetField.css}` : ''}`} role="region" id={displayedFacetField.field} aria-labelledby={labelId}>
                        {facet.terms.map((facetTerm) => (
                            <FacetTerm
                                key={facetTerm.term}
                                displayedFacetField={displayedFacetField}
                                term={facetTerm.term}
                                termCount={facetTerm.count}
                                visualizable={options.suppressVisualizable ? false : facetTerm.visualizable}
                                maxTermCount={maxTermCount}
                                selected={selectedFacetTerms.indexOf(facetTerm.term) > -1}
                                termClickHandler={this.handleFacetTermClick}
                                FacetTermSelectRenderer={FacetTermSelectRenderer}
                            />
                        ))}
                    </ul>
                : null}
            </div>
        );
    }
}

Facet.propTypes = {
    /** Facet object to display */
    facet: PropTypes.object.isRequired,
    /** Field definition representing the facet being displayed */
    displayedFacetField: PropTypes.object.isRequired,
    /** True if facet should appear expanded */
    expanded: PropTypes.bool.isRequired,
    /** Called when the expander button is clicked */
    expanderClickHandler: PropTypes.func,
    /** Selected term keys */
    selectedFacetTerms: PropTypes.array,
    /** Called when a facet term is clicked */
    facetTermClickHandler: PropTypes.func.isRequired,
    /** Called when the user clears all selections in a facet */
    clearFacetSelections: PropTypes.func,
    /** Facet-specific options */
    options: PropTypes.shape({
        /** Suppress display of facet title */
        supressTitle: PropTypes.bool,
        /** Suppress display of visualizable icons */
        suppressVisualizable: PropTypes.bool,
    }),
};

Facet.defaultProps = {
    expanderClickHandler: null,
    clearFacetSelections: null,
    selectedFacetTerms: [],
    options: {},
};


/**
 * Manage the expanded states of collapsable facets in a facet list.
 * @param {object} facetFields Definitions for facet list
 * @return {array} expanded states of each facet; callback when user clicks an expander
 */
const useExpanders = (facetFields) => {
    /** Expanded facet fields; `displayedFileFacetFields` array creates an entry for each field */
    const [expandedStates, setExpandedStates] = React.useState(() => (
        facetFields.reduce((accExpanded, facetField) => (
            ({ ...accExpanded, [facetField.field]: !!facetField.expanded })
        ), {})
    ));

    /**
     * Called when the user clicks a facet expander button. Updates the expander states so the
     * facets re-render to the new expanded states.
     * @param {string} field Field name for clicked facet expander
     * @param {boolean} altKey True if alt/option key down at time of click
     */
    const handleExpanderClick = (field, altKey) => {
        setExpandedStates((prevExpandedStates) => {
            if (altKey) {
                // Alt key held down, so expand or collapse *all* facets.
                const allExpandedState = !prevExpandedStates[field];
                const nextExpandedStates = {};
                Object.keys(prevExpandedStates).forEach((facetField) => {
                    nextExpandedStates[facetField] = allExpandedState;
                });
                return nextExpandedStates;
            }

            // Alt key not held down, so just expand or collapse the clicked facet.
            const nextExpandedStates = { ...prevExpandedStates };
            nextExpandedStates[field] = !prevExpandedStates[field];
            return nextExpandedStates;
        });
    };

    return [expandedStates, handleExpanderClick];
};


/**
 * Display the file facets. These display the number of files involved -- not the number of
 * experiments with files matching a criteria. As the primary input to this component is currently
 * an array of experiment IDs while these facets displays all the files involved with those
 * experiments, this component begins by retrieving information about all relevant files from the
 * DB. Each time an experiment is removed from the cart while viewing the cart page, this component
 * again retrieves all relevant files for the remaining experiments.
 */
export const FileFacets = ({
    facets,
    usedFacetFields,
    selectedTerms,
    selectedFileCount,
    termClickHandler,
    visualizableOnly,
    visualizableOnlyChangeHandler,
    preferredOnly,
    preferredOnlyChangeHandler,
    facetLoadProgress,
    clearFacetSelections,
}) => {
    const [expandedStates, handleExpanderClick] = useExpanders(displayedFileFacetFields);

    return (
        <div className="cart-facet-modal-column">
            <FacetCount count={selectedFileCount} element="file" />
            <div className="cart-facet-list">
                <Checkbox label="Show default data only" id="default-data-toggle" checked={preferredOnly} css="cart-checkbox" clickHandler={preferredOnlyChangeHandler} />
                {!preferredOnly ? <Checkbox label="Show visualizable data only" id="visualizable-data-toggle" checked={visualizableOnly} css="cart-checkbox" clickHandler={visualizableOnlyChangeHandler} /> : null}
                {facets && facets.length > 0 ?
                    <>
                        {usedFacetFields.map((facetField) => {
                            const facetContent = facets.find((facet) => facet.field === facetField.field);
                            if (facetContent) {
                                const expanded = facetField.parent ? expandedStates[facetField.parent] : expandedStates[facetField.field];
                                return (
                                    <Facet
                                        key={facetField.field}
                                        facet={facetContent}
                                        displayedFacetField={facetField}
                                        selectedFacetTerms={selectedTerms[facetField.field]}
                                        facetTermClickHandler={termClickHandler}
                                        expanded={expanded}
                                        expanderClickHandler={handleExpanderClick}
                                        options={{ supressTitle: !!facetField.parent, suppressVisualizable: preferredOnly }}
                                        clearFacetSelections={clearFacetSelections}
                                    />
                                );
                            }
                            return null;
                        })}
                    </>
                :
                    <>
                        {facetLoadProgress === -1 ?
                            <div className="cart__empty-message">No files available</div>
                        : null}
                    </>
                }
            </div>
        </div>
    );
};

FileFacets.propTypes = {
    /** Array of objects for each displayed facet */
    facets: PropTypes.array,
    /** Currently displayed facet fields */
    usedFacetFields: PropTypes.array,
    /** Selected facet fields */
    selectedTerms: PropTypes.object,
    /** Number of files currently selected */
    selectedFileCount: PropTypes.number,
    /** Callback when the user clicks on a file format facet item */
    termClickHandler: PropTypes.func.isRequired,
    /** True to check the Show Visualizable Data Only checkbox */
    visualizableOnly: PropTypes.bool,
    /** Call to handle clicks in the Visualize Only checkbox */
    visualizableOnlyChangeHandler: PropTypes.func.isRequired,
    /** True to check the Show Preferred Data Only checkbox */
    preferredOnly: PropTypes.bool,
    /** Call to handle clicks in the Preferred Only checkbox */
    preferredOnlyChangeHandler: PropTypes.func.isRequired,
    /** Facet-loading progress for progress bar, or null if not displayed */
    facetLoadProgress: PropTypes.number,
    /** Called when the user clears all selections in a facet */
    clearFacetSelections: PropTypes.func.isRequired,
};

FileFacets.defaultProps = {
    facets: [],
    usedFacetFields: [],
    selectedTerms: null,
    selectedFileCount: 0,
    visualizableOnly: false,
    preferredOnly: false,
    facetLoadProgress: null,
};


/**
 * Display the dataset facets relevant to the currently selected facet terms and datasets in the
 * cart.
 */
export const DatasetFacets = ({
    facets,
    selectedTerms,
    selectedDatasetCount,
    termClickHandler,
    clearFacetSelections,
}) => {
    const [expandedStates, handleExpanderClick] = useExpanders(displayedDatasetFacetFields);

    return (
        <div className="cart-facet-modal-column">
            <FacetCount count={selectedDatasetCount} element="dataset" />
            <div className="cart-facet-list">
                {displayedDatasetFacetFields.map((facetField) => {
                    const facetContent = facets.find((facet) => facet.field === facetField.field);
                    if (facetContent) {
                        const expanded = facetField.parent ? expandedStates[facetField.parent] : expandedStates[facetField.field];
                        return (
                            <Facet
                                key={facetField.field}
                                facet={facetContent}
                                displayedFacetField={facetField}
                                selectedFacetTerms={selectedTerms[facetField.field]}
                                facetTermClickHandler={termClickHandler}
                                expanded={expanded}
                                expanderClickHandler={handleExpanderClick}
                                clearFacetSelections={clearFacetSelections}
                            />
                        );
                    }
                    return null;
                })}
            </div>
        </div>
    );
};

DatasetFacets.propTypes = {
    /** Array of objects for each displayed facet */
    facets: PropTypes.array,
    /** Selected facet fields */
    selectedTerms: PropTypes.object,
    /** Number of datasets currently selected */
    selectedDatasetCount: PropTypes.number,
    /** Callback when the user clicks on a file format facet item */
    termClickHandler: PropTypes.func.isRequired,
    /** Callback for clearing a single facet's selections */
    clearFacetSelections: PropTypes.func.isRequired,
};

DatasetFacets.defaultProps = {
    facets: [],
    selectedTerms: null,
    selectedDatasetCount: 0,
};


/**
 * Main entry point to render the facet column contents. It displays the checkbox options, the
 * persistent facets, the button to display the modal with all facets, and the current facet
 * selections.
 */
export const CartFacets = ({
    datasetProps,
    fileProps,
    options,
    datasets,
    files,
    facetProgress,
}) => {
    const [isModalOpen, setIsModalOpen] = React.useState(false);
    const closeRef = React.useRef(null);

    const handleClick = () => {
        setIsModalOpen(true);
    };

    const handleClose = () => {
        setIsModalOpen(false);
    };

    React.useEffect(() => {
        // Make sure the user can type into this field as soon as the modal appears without having
        // to click in the field.
        if (closeRef.current) {
            closeRef.current.focus();
            closeRef.current.select();
        }
    }, []);

    return (
        <div className="cart__display-facets">
            <FacetCount count={files.length} element="file" facetLoadProgress={facetProgress} />
            <Checkbox label="Show default data only" id="default-data-toggle" checked={options.preferredOnly} css="cart-checkbox" clickHandler={options.preferredOnlyChangeHandler} />
            {!options.preferredOnly ? <Checkbox label="Show visualizable data only" id="visualizable-data-toggle" checked={options.visualizableOnly} css="cart-checkbox" clickHandler={options.visualizableOnlyChangeHandler} /> : null}
            <div className="cart-facet-list">
                {displayedPersistentFacetFields.map((facetField) => {
                    const datasetFacetContent = datasetProps.facets.find((facet) => facet.field === facetField.field);
                    if (datasetFacetContent) {
                        return (
                            <Facet
                                key={facetField.field}
                                facet={datasetFacetContent}
                                displayedFacetField={facetField}
                                selectedFacetTerms={datasetProps.selectedTerms[facetField.field]}
                                facetTermClickHandler={datasetProps.termClickHandler}
                                expanded
                            />
                        );
                    }
                    const fileFacetContent = fileProps.facets.find((facet) => facet.field === facetField.field);
                    if (fileFacetContent) {
                        return (
                            <Facet
                                key={facetField.field}
                                facet={fileFacetContent}
                                displayedFacetField={facetField}
                                selectedFacetTerms={fileProps.selectedTerms[facetField.field]}
                                facetTermClickHandler={fileProps.termClickHandler}
                                options={{ supressTitle: !!facetField.parent, suppressVisualizable: options.preferredOnly }}
                                expanded
                            />
                        );
                    }
                    return null;
                })}
            </div>
            <div className="facet-selections-section">
                <button type="button" className="btn btn-info btn-sm facet-selections-actuator" onClick={handleClick} disabled={facetProgress !== -1}>More filters</button>
                <Selections
                    datasetTerms={datasetProps.selectedTerms}
                    datasetTermClickHandler={datasetProps.termClickHandler}
                    fileTerms={fileProps.selectedTerms}
                    fileTermClickHandler={fileProps.termClickHandler}
                />
            </div>
            {isModalOpen ?
                <Modal closeModal={handleClose}>
                    <ModalHeader title="Dataset and file filters" labelId="selection-modal" closeModal={handleClose} focusClose />
                    <ModalBody>
                        <div className="cart-facet-modal">
                            <DatasetFacets
                                facets={datasetProps.facets}
                                selectedTerms={datasetProps.selectedTerms}
                                selectedDatasetCount={datasets.length}
                                termClickHandler={datasetProps.termClickHandler}
                                clearFacetSelections={datasetProps.clearFacetSelections}
                            />
                            <FileFacets
                                facets={fileProps.facets}
                                selectedTerms={fileProps.selectedTerms}
                                selectedFileCount={files.length}
                                usedFacetFields={fileProps.usedFacetFields}
                                elements={datasets}
                                termClickHandler={fileProps.termClickHandler}
                                visualizableOnly={options.visualizableOnly}
                                visualizableOnlyChangeHandler={options.visualizableOnlyChangeHandler}
                                preferredOnly={options.preferredOnly}
                                preferredOnlyChangeHandler={options.preferredOnlyChangeHandler}
                                clearFacetSelections={fileProps.clearFacetSelections}
                            />
                        </div>
                    </ModalBody>
                </Modal>
            : null}
        </div>
    );
};

CartFacets.propTypes = {
    /** Properties specific to the dataset facets */
    datasetProps: PropTypes.exact({
        /** Currently displayed dataset facets */
        facets: PropTypes.array,
        /** Currently selected facet terms */
        selectedTerms: PropTypes.object,
        /** Called when the user clicks a facet term on or off */
        termClickHandler: PropTypes.func,
        /** Called when the user clears all selections within a single facet */
        clearFacetSelections: PropTypes.func,
    }).isRequired,
    /** Properties specific to the file facets */
    fileProps: PropTypes.exact({
        /** Currently displayed file facets */
        facets: PropTypes.array,
        /** Currently selected facet terms */
        selectedTerms: PropTypes.object,
        /** Function to call when the user clicks a facet term on or off */
        termClickHandler: PropTypes.func,
        /** Called when the user clears all selections within a single facet */
        clearFacetSelections: PropTypes.func,
        /** Facets currently enabled based on options */
        usedFacetFields: PropTypes.array,
    }).isRequired,
    /** Other options controlled by the main cart-page code */
    options: PropTypes.exact({
        /** True if user has chosen to view visualizable facet terms only */
        visualizableOnly: PropTypes.bool,
        /** Called when the user changes the Visualizable Only checkbox */
        visualizableOnlyChangeHandler: PropTypes.func,
        /** True if user has chosen to view default files only */
        preferredOnly: PropTypes.bool,
        /** Called when the user changes the checkbox for viewing default files only */
        preferredOnlyChangeHandler: PropTypes.func,
    }).isRequired,
    /** Currently selected datasets */
    datasets: PropTypes.array.isRequired,
    /** Currently selected files */
    files: PropTypes.array.isRequired,
    /** Current progress of loading the datasets/files for the facets */
    facetProgress: PropTypes.number,
};

CartFacets.defaultProps = {
    facetProgress: null,
};


/**
 * Update the `facets` array by incrementing the count of the term within it selected by the
 * `field` within the given `dataset`.
 * @param {array} facets Facet array to update - mutated!
 * @param {string} field Field key within the facet to update
 * @param {object} dataset Contains the term to add to the facet
 */
const addDatasetTermToFacet = (facets, field, dataset) => {
    const facetTerm = getObjectFieldValue(dataset, field);
    if (facetTerm !== undefined) {
        const matchingFacet = facets.find((facet) => facet.field === field);
        if (matchingFacet) {
            // The facet has been seen in this loop before, so add to or initialize
            // the relevant term within this facet.
            const matchingTerm = matchingFacet.terms.find((matchingFacetTerm) => matchingFacetTerm.term === facetTerm);
            if (matchingTerm) {
                // Facet term has been counted before, so add to its count. Mark the term as
                // visualizable if any file contributing to this term is visualizable.
                matchingTerm.count += 1;
            } else {
                // Facet term has not been counted before, so initialize a new facet term entry.
                matchingFacet.terms.push({ term: facetTerm, count: 1 });
            }
        } else {
            // The facet has not been seen in this loop before, so initialize it as
            // well as the value of the relevant term within the facet.
            facets.push({ field, terms: [{ term: facetTerm, count: 1 }] });
        }
    }
};


/**
 * Update the `facets` array by incrementing the count of the term within it selected by the
 * `field` within the given `file`.
 * @param {array} facets Facet array to update - mutated!
 * @param {string} field Field key within the facet to update
 * @param {object} file File containing the term to add to the facet
 */
const addFileTermToFacet = (facets, field, file) => {
    const facetTerm = getObjectFieldValue(file, field);
    const visualizable = isFileVisualizable(file);
    if (facetTerm !== undefined) {
        const matchingFacet = facets.find((facet) => facet.field === field);
        if (matchingFacet) {
            // The facet has been seen in this loop before, so add to or initialize
            // the relevant term within this facet.
            const matchingTerm = matchingFacet.terms.find((matchingFacetTerm) => matchingFacetTerm.term === facetTerm);
            if (matchingTerm) {
                // Facet term has been counted before, so add to its count. Mark the term as
                // visualizable if any file contributing to this term is visualizable.
                matchingTerm.count += 1;
                if (visualizable) {
                    matchingTerm.visualizable = visualizable;
                }
            } else {
                // Facet term has not been counted before, so initialize a new facet term entry.
                matchingFacet.terms.push({ term: facetTerm, count: 1, visualizable });
            }
        } else {
            // The facet has not been seen in this loop before, so initialize it as
            // well as the value of the relevant term within the facet.
            facets.push({ field, terms: [{ term: facetTerm, count: 1, visualizable }] });
        }
    }
};


/**
 * Based on the currently selected facet terms and the current set of datasets in the cart,
 * generate the simplified facets and the subset of datasets these facets select.
 * @param {object} selectedTerms Currently selected terms within each facet
 * @param {array} datasets Datasets to consider when building these facets.
 * @param {array} usedFacetFields Facet fields to consider when assembling.
 *
 * @return {object}
 *     {array} facets - Array of simplified facet objects including fields and terms;
 *                               empty array if none
 *     {array} selectedFiles - Array of datasets selected by currently selected facets
 */
export const assembleDatasetFacets = (selectedTerms, datasets, usedFacetFields) => {
    const assembledFacets = [];
    const selectedDatasets = [];

    if (datasets.length > 0) {
        const selectedFacetKeys = Object.keys(selectedTerms).filter((term) => selectedTerms[term].length > 0);
        datasets.forEach((dataset) => {
            // Determine whether the dataset passes the currently selected facet terms. Properties
            // within the dataset have to match any of the terms within a facet, and across all
            // facets that include selected terms. This is the "first test" I refer to later.
            let match = selectedFacetKeys.every((selectedFacetKey) => {
                // `selectedFacetKey` is one facet field, e.g. "assay_title".
                // `propValue` is the dataset's value for that field.
                const propValue = getObjectFieldValue(dataset, selectedFacetKey);

                // Determine if the dataset's `selectedFacetKey` prop has been selected by at
                // least one facet term.
                return selectedTerms[selectedFacetKey].indexOf(propValue) !== -1;
            });

            // Datasets that pass the first test add their properties to the relevant facet term
            // counts. Datasets that don't pass go through a second test to see if their properties
            // should appear unselected within a facet. Datasets that fail both tests get ignored
            // for facets.
            if (match) {
                // The dataset passed the first test, so its terms appear selected in their facets.
                // Add all its properties to the relevant facet terms.
                Object.keys(selectedTerms).forEach((facetField) => {
                    addDatasetTermToFacet(assembledFacets, facetField, dataset);
                });
                selectedDatasets.push(dataset);
            } else {
                // The dataset didn't pass the first test, so run the same test repeatedly but
                // with one facet removed from the test each time. For each easier test the
                // dataset passes, add to the corresponding term count for the removed facet,
                // allowing the user to select it to extend the set of selected datasets.
                selectedFacetKeys.forEach((selectedFacetField) => {
                    // Remove one facet containing a selection from the test.
                    const filteredSelectedFacetKeys = selectedFacetKeys.filter((key) => key !== selectedFacetField);
                    match = filteredSelectedFacetKeys.every((filteredSelectedFacetKey) => {
                        const datasetPropValue = getObjectFieldValue(dataset, filteredSelectedFacetKey);
                        return selectedTerms[filteredSelectedFacetKey].indexOf(datasetPropValue) !== -1;
                    });

                    // A match means to add to the count of the current facet field dataset term
                    // only.
                    if (match) {
                        addDatasetTermToFacet(assembledFacets, selectedFacetField, dataset);
                    }
                });
            }
        });

        // We need to include selected terms that happen to have a zero count, so add all
        // selected facet terms not yet included in `facets`.
        Object.keys(selectedTerms).forEach((field) => {
            const matchingFacet = assembledFacets.find((facet) => facet.field === field);
            if (matchingFacet) {
                // Find selected terms NOT in facets and add them with a zero count.
                const matchingFacetTerms = matchingFacet.terms.map((facetTerm) => facetTerm.term);
                const missingTerms = selectedTerms[field].filter((term) => matchingFacetTerms.indexOf(term) === -1);
                if (missingTerms.length > 0) {
                    missingTerms.forEach((term) => {
                        matchingFacet.terms.push({ term, count: 0, visualizable: false });
                    });
                }
            }
        });

        // Sort each facet's terms either alphabetically or by some criteria specific to a
        // facet. `facets` and `usedFacetFields` have the same order, but `facets` might
        // not have all possible facets -- just currently relevant ones.
        assembledFacets.forEach((facet) => {
            // We know a corresponding `usedFacetFields` entry exists because `facets` gets
            // built from it, so no not-found condition needs checking.
            const facetDisplay = usedFacetFields.find((facetField) => facetField.field === facet.field);
            facet.title = facetDisplay.title;
            facet.terms = _(facet.terms).sortBy((facetTerm) => facetTerm.term.toLowerCase());
        });
    }

    return { datasetFacets: assembledFacets.length > 0 ? assembledFacets : [], selectedDatasets };
};


/**
 * Based on the currently selected facet terms and the files collected from the datasets in the
 * cart, generate the simplified facets and the subset of files these facets select. `analyses` not
 * needed when `assembleFileFacets` called simply to reset the facets.
 * @param {object} selectedTerms Currently selected terms within each facet
 * @param {array} files Partial files to consider when building these facets.
 * @param {array} analyses Compiled analysis objects from experiments in cart.
 * @param {array} usedFacetFields Facet fields to consider when assembling.
 *
 * @return {object}
 *     {array} facets - Array of simplified facet objects including fields and terms;
 *                               empty array if none
 *     {array} selectedFiles - Array of partial files selected by currently selected facets
 */
export const assembleFileFacets = (selectedTerms, files, analyses, usedFacetFields) => {
    const assembledFacets = [];
    const selectedFiles = [];
    const usedSelectedTerms = {};
    const usedFieldValues = usedFacetFields.map((facetField) => facetField.field);
    Object.keys(selectedTerms).forEach((term) => {
        if (usedFieldValues.includes(term)) {
            usedSelectedTerms[term] = selectedTerms[term];
        }
    });

    // Get complete list of files to consider -- processed files, and those associated with all
    // available analyses if any selected.
    let consideredFiles;
    consideredFiles = files.filter((file) => file.assembly);
    if (usedSelectedTerms.analysis && usedSelectedTerms.analysis.length > 0) {
        // Consider all files the selected analyses corresponds to.
        const fileIds = getAnalysesFileIds(analyses);
        consideredFiles = _.compact(fileIds.map((id) => files.find((file) => id === file['@id'])));
    }
    if (consideredFiles.length > 0) {
        const selectedFacetKeys = Object.keys(usedSelectedTerms).filter((term) => usedSelectedTerms[term].length > 0);
        consideredFiles.forEach((file) => {
            // Determine whether the file passes the currently selected facet terms. Properties
            // within the file have to match any of the terms within a facet, and across all
            // facets that include selected terms. This is the "first test" I refer to later.
            let match = selectedFacetKeys.every((selectedFacetKey) => {
                // `selectedFacetKey` is one facet field, e.g. "output_type".
                // `filePropValue` is the file's value for that field.
                const filePropValue = getObjectFieldValue(file, selectedFacetKey);

                // Determine if the file's `selectedFacetKey` prop has been selected by at
                // least one facet term.
                return usedSelectedTerms[selectedFacetKey].indexOf(filePropValue) !== -1;
            });

            // Files that pass the first test add their properties to the relevant facet term
            // counts. Files that don't pass go through a second test to see if their properties
            // should appear unselected within a facet. Files that fail both tests get ignored for
            // facets.
            if (match) {
                // The file passed the first test, so its terms appear selected in their facets.
                // Add all its properties to the relevant facet terms.
                Object.keys(usedSelectedTerms).forEach((facetField) => {
                    addFileTermToFacet(assembledFacets, facetField, file);
                });
                selectedFiles.push(file);
            } else {
                // The file didn't pass the first test, so run the same test repeatedly but
                // with one facet removed from the test each time. For each easier test the
                // file passes, add to the corresponding term count for the removed facet,
                // allowing the user to select it to extend the set of selected files.
                selectedFacetKeys.forEach((selectedFacetField) => {
                    // Remove one facet containing a selection from the test.
                    const filteredSelectedFacetKeys = selectedFacetKeys.filter((key) => key !== selectedFacetField);
                    match = filteredSelectedFacetKeys.every((filteredSelectedFacetKey) => {
                        const filePropValue = getObjectFieldValue(file, filteredSelectedFacetKey);
                        return selectedTerms[filteredSelectedFacetKey].indexOf(filePropValue) !== -1;
                    });

                    // A match means to add to the count of the current facet field file term
                    // only.
                    if (match) {
                        addFileTermToFacet(assembledFacets, selectedFacetField, file);
                    }
                });
            }
        });

        // We need to include selected terms that happen to have a zero count, so add all
        // selected facet terms not yet included in `facets`.
        Object.keys(usedSelectedTerms).forEach((field) => {
            const matchingFacet = assembledFacets.find((facet) => facet.field === field);
            if (matchingFacet) {
                // Find selected terms NOT in facets and add them with a zero count.
                const matchingFacetTerms = matchingFacet.terms.map((facetTerm) => facetTerm.term);
                const missingTerms = selectedTerms[field].filter((term) => matchingFacetTerms.indexOf(term) === -1);
                if (missingTerms.length > 0) {
                    missingTerms.forEach((term) => {
                        matchingFacet.terms.push({ term, count: 0, visualizable: false });
                    });
                }
            }
        });

        // Sort each facet's terms either alphabetically or by some criteria specific to a
        // facet. `facets` and `usedFacetFields` have the same order, but `facets` might
        // not have all possible facets -- just currently relevant ones.
        assembledFacets.forEach((facet) => {
            // We know a corresponding `usedFacetFields` entry exists because `facets` gets
            // built from it, so no not-found condition needs checking.
            const facetDisplay = usedFacetFields.find((facetField) => facetField.field === facet.field);
            facet.title = facetDisplay.title;
            facet.terms = facetDisplay.sorter ? facetDisplay.sorter(facet.terms, analyses) : _(facet.terms).sortBy((facetTerm) => facetTerm.term.toLowerCase());
        });
    }

    return { fileFacets: assembledFacets.length > 0 ? assembledFacets : [], selectedFiles, defaultFiles: filterForDefaultFiles(selectedFiles) };
};


/**
 * For any radio-button facets, select the first term if no items within them have been selected.
 * @param {array} facets Simplified facet object
 * @param {object} selectedTerms Selected terms within the facets
 *
 * @return {object} Same as `selectedTerms` but with radio-button facet terms selected
 */
const initRadioFacets = (facets, selectedTerms, usedFacetFields) => {
    const newSelectedTerms = {};
    usedFacetFields.forEach((facetField) => {
        if (facetField.radio && selectedTerms[facetField.field].length === 0) {
            // Assign the first term of the radio-button facet as the sole selection. In the
            // unusual case that no facet terms for this radio-button facet have been collected,
            // just copy the existing selection for the facet.
            const matchingFacet = facets.find((facet) => facet.field === facetField.field);
            newSelectedTerms[facetField.field] = (
                matchingFacet ? [matchingFacet.terms[0].term] : selectedTerms[facetField.field].slice(0)
            );
        } else {
            // Not a radio-button facet, or radio-button facet has selected terms; copy existing
            // selected terms.
            newSelectedTerms[facetField.field] = selectedTerms[facetField.field].slice(0);
        }
    });
    return newSelectedTerms;
};


/**
 * Make a selected-terms object showing no selections based on the given facet properties.
 * @param {array} usedFacetFields Currently used subset of `displayedFileFacetFields`.
 *
 * @return {object} Selected facet showing no selections; used with `assembleFileFacets`
 */
const initSelectedTerms = (usedFacetFields) => {
    const emptySelectedTerms = {};
    usedFacetFields.forEach((facetField) => {
        emptySelectedTerms[facetField.field] = [];
    });
    return emptySelectedTerms;
};


/**
 * Reset the facets to no selections as if the page has just been loaded.
 * @param {array} files Files to consider when building facets.
 * @param {array} usedFacetFields Facet fields to consider
 *
 * @return {object} Initial facet-term selections
 */
export const resetDatasetFacets = (datasets, usedFacetFields) => {
    // Make an empty selected-terms object so `assembleDatasetFacets` can generate fresh simplified
    // facets.
    const emptySelectedTerms = initSelectedTerms(usedFacetFields);

    // Build the facets based on no selections, then select the first term of any radio-button
    // facets.
    const { datasetFacets } = assembleDatasetFacets(emptySelectedTerms, datasets, usedFacetFields);
    return initRadioFacets(datasetFacets, emptySelectedTerms, usedFacetFields);
};


/**
 * Reset the facets to no selections, and select the first term of radio-button facets, all as if
 * the page has just been loaded.
 * @param {array} files Files to consider when building facets.
 * @param {array} usedFacetFields Facet fields to consider
 *
 * @return {object} Initial facet-term selections
 */
export const resetFileFacets = (files, analyses, usedFacetFields) => {
    // Make an empty selected-terms object so `assembleFileFacets` can generate fresh simplified
    // facets.
    const emptySelectedTerms = initSelectedTerms(usedFacetFields);

    // Build the facets based on no selections, then select the first term of any radio-button
    // facets.
    const { fileFacets } = assembleFileFacets(emptySelectedTerms, files, analyses, usedFacetFields);
    return initRadioFacets(fileFacets, emptySelectedTerms, usedFacetFields);
};
