import React from 'react';
import PropTypes from 'prop-types';
import queryString from 'query-string';
import url from 'url';
import { svgIcon } from '../libs/svg-icons';
import QueryString from '../libs/query_string';
import HumanBodyDiagram from '../img/bodyMap/Deselected_Body';
import MouseBodyDiagram from '../img/bodyMap/Deselected-mouse';
import getSeriesData from './series_search';

// Query for systems slim
export const systemsField = 'biosample_ontology.system_slims';
// Query for organ slim
export const organField = 'biosample_ontology.organ_slims';

// Mapping from organ slims to paths and shapes on the body map SVG
// Note: there is some complexity here because some organ slims are overlapping, or subsets of each other, or synonymous
// For example, "intestine" highlights both "large intestine" and "small intestine"
//     The mapping lists the organs which are a subset of "intestine" which the code uses as references to look up the paths
// As another type of example, note that "skeleton" highlights "bone element" but not the other way around
// A third case is "esophagus" and "trachea": they each highlight the same paths but are not the same organ
//     Because of the way the code works, we need to include both the paths and the synonymous term for each
export const HumanList = {
    'adrenal gland': ['cls-34'],
    'arterial blood vessel': ['cls-11'],
    'bone element': ['cls-65', 'cls-77', 'cls-78', 'cls-80', 'cls-81'],
    brain: ['cls-6', 'cls-68', 'cls-69', 'cls-70'],
    breast: ['cls-breast', 'cls-97', 'cls-98', 'cls-99', 'cls-100', 'cls-101', 'mammary gland'],
    bronchus: ['cls-25'],
    colon: ['large intestine'],
    // Currently there are no organ slims for epiglottis, nor are any planned
    // However, the artist did include a shape for it, so we may want to add it back at some time
    // epiglottis: ['cls-epiglottis'],
    esophagus: ['trachea', 'cls-37', 'cls-38'],
    eye: ['cls-4', 'cls-71', 'cls-73', 'cls-74', 'cls-75'],
    gallbladder: ['cls-gallbladder'],
    gonad: ['testis', 'ovary'],
    heart: ['cls-33', 'cls-44', 'cls-45'],
    intestine: ['large intestine', 'small intestine', 'colon'],
    kidney: ['cls-kidney'],
    'large intestine': ['cls-29', 'cls-30', 'cls-lg-intestine', 'colon'],
    limb: ['cls-limb'],
    liver: ['cls-31', 'cls-32'],
    lung: ['bronchus', 'cls-24'],
    'mammary gland': ['cls-98'],
    mouth: ['cls-8'],
    'musculature of body': ['cls-83', 'cls-84', 'cls-85', 'cls-88', 'cls-89', 'cls-90', 'cls-91'],
    nerve: ['cls-21', 'cls-nervebackground'],
    nose: ['cls-nose'],
    ovary: ['cls-ovary'],
    pancreas: ['cls-23'],
    penis: ['cls-62'],
    pericardium: ['cls-46', 'cls-48'],
    'prostate gland': ['cls-54'],
    skeleton: ['cls-65', 'cls-77', 'cls-78', 'cls-80', 'cls-81', 'bone element'],
    'skin of body': ['cls-5', 'cls-limb-skin'],
    'small intestine': ['cls-27', 'cls-28'],
    'spinal cord': ['cls-66'],
    spleen: ['cls-7'],
    stomach: ['cls-stomach'],
    testis: ['cls-testis'],
    thymus: ['cls-thymus', 'cls-40'],
    'thyroid gland': ['cls-39', 'cls-41'],
    trachea: ['esophagus', 'cls-37', 'cls-38'],
    tongue: ['cls-95'],
    ureter: ['cls-57'],
    uterus: ['cls-uterus'],
    'urinary bladder': ['cls-35', 'cls-36'],
    vagina: ['cls-vagina', 'cls-vagina2'],
    vein: ['cls-vein'],
};

export const MouseList = {
    'adrenal gland': ['cls-27'],
    'arterial blood vessel': ['cls-26'],
    'bone element': ['cls-bone', 'cls-5', 'cls-bone1', 'cls-bone6'],
    brain: ['cls-21', 'cls-22', 'cls-23', 'cls-24'],
    breast: ['cls-41', 'cls-42'],
    colon: ['cls-colon', 'cls-9'],
    esophagus: ['cls-esophagus', 'cls-esophagus2', 'cls-29'],
    'extraembryonic component': ['placenta'],
    eye: ['cls-39', 'cls-40', 'cls-eye'],
    gonad: ['testis', 'ovary'],
    heart: ['cls-33', 'cls-34', 'cls-18'],
    intestine: ['large intestine', 'small intestine', 'colon'],
    kidney: ['cls-kidney'],
    'large intestine': ['cls-largeintestine', 'cls-19'],
    limb: ['cls-limb1', 'cls-limb2'],
    liver: ['cls-17', 'cls-liver'],
    lung: ['cls-lung'],
    'lymph node': ['cls-28'],
    'mammary gland': ['breast'],
    'musculature of body': ['cls-14', 'cls-15', 'cls-16'],
    nose: ['cls-11'],
    ovary: ['cls-6', 'cls-7', 'cls-35'],
    pancreas: ['cls-12'],
    'skin of body': ['cls-1', 'cls-2', 'cls-32', 'cls-3', 'cls-limb1', 'cls-limb2', 'cls-10'],
    'small intestine': ['cls-8', 'cls-smallintestine', 'cls-smallintestine19'],
    'spinal cord': ['cls-20'],
    spleen: ['cls-13'],
    stomach: ['cls-stomach'],
    testis: ['cls-37', 'cls-36'],
    thymus: ['cls-30', 'cls-31'],
    'urinary bladder': ['cls-38'],
    vein: ['cls-25'],
};

// Mapping from cells and tissue types to inset images
// All mappings are empty because there are no paths or shapes that correspond to the inset images
//     (each has one associated image with a name corresponding to the cell or tissue term)
export const HumanCellsList = {
    'adipose tissue': [],
    blood: [],
    'blood vessel': [],
    'bone marrow': [],
    'connective tissue': [],
    embryo: [],
    epithelium: [],
    'lymphoid tissue': [],
    'lymph node': [],
    'lymphatic vessel': [],
    placenta: [],
};

export const MouseCellsList = {
    'adipose tissue': [],
    blood: [],
    'bone marrow': [],
    'connective tissue': [],
    embryo: [],
    epithelium: [],
    placenta: [],
};

// Mapping for systems slims
// Systems slims are mapped to organs in the "BodyList"
export const HumanSystemsList = {
    'central nervous system': ['brain', 'spinal cord'],
    'circulatory system': ['blood', 'blood vessel', 'arterial blood vessel', 'heart', 'pericardium', 'vein', 'lymphatic vessel'],
    'digestive system': ['esophagus', 'intestine', 'small intestine', 'large intestine', 'liver', 'gallbladder', 'mouth', 'spleen', 'stomach', 'tongue', 'colon'],
    'endocrine system': ['adrenal gland', 'liver', 'gallbladder', 'pancreas', 'thymus', 'thyroid gland'],
    'excretory system': ['urinary bladder', 'kidney', 'ureter'],
    'exocrine system': ['mammary gland', 'liver'],
    'immune system': ['lymphoid tissue', 'spleen', 'thymus', 'bone marrow', 'lymph node', 'lymphatic vessel'],
    musculature: ['musculature of body', 'limb'],
    'peripheral nervous system': ['nerve'],
    'reproductive system': ['gonad', 'ovary', 'penis', 'placenta', 'prostate gland', 'testis', 'uterus', 'vagina'],
    'respiratory system': ['trachea', 'bronchus', 'lung'],
    'sensory system': ['eye', 'nose', 'tongue'],
    'skeletal system': ['bone element', 'skeleton', 'bone marrow', 'limb'],
    'integumental system': ['mammary gland', 'skin of body'],
};

export const MouseSystemsList = {
    'central nervous system': ['brain', 'spinal cord'],
    'circulatory system': ['blood', 'heart', 'arterial blood vessel', 'vein'],
    'digestive system': ['large intestine', 'small intestine', 'stomach', 'pancreas', 'colon', 'spleen', 'esophagus'],
    'endocrine system': ['liver', 'pancreas', 'thymus', 'adrenal gland'],
    'excretory system': ['kidney', 'urinary bladder'],
    'exocrine system': ['mammary gland', 'liver'],
    'immune system': ['lymph node', 'spleen', 'thymus', 'bone marrow'],
    'integumental system': ['mammary gland'],
    musculature: ['musculature of body', 'limb'],
    'reproductive system': ['ovary', 'testis'],
    'respiratory system': ['lung'],
    'sensory system': ['eye'],
    'skeletal system': ['bone element', 'bone marrow', 'limb'],
};

const SelectedFilters = (props) => {
    const selectedFilters = props.filters;
    const organTerms = selectedFilters.filter((f) => f.field === organField);
    const systemsTerms = selectedFilters.filter((f) => f.field === systemsField);
    const freeSearchTerms = selectedFilters.filter((f) => f.field === 'searchTerm');
    const selectedTerms = [...organTerms, ...systemsTerms, ...freeSearchTerms];
    return (
        <>
            {(selectedTerms.length > 0) ?
                <div className="filter-container">
                    <div className="filter-hed">Selected filters:</div>
                    {selectedTerms.map((filter) => {
                        const isNegativeTerm = filter.field.indexOf('!') > -1;
                        return (
                            <a
                                href={filter.remove}
                                key={filter.term}
                                className={`filter-link${isNegativeTerm ? ' filter-link--negative' : ''}`}
                            >
                                <div className="filter-link__title">
                                    {filter.term}
                                </div>
                                <div className="filter-link__icon">{svgIcon('multiplication')}</div>
                            </a>
                        );
                    })}
                </div>
            : null}
        </>
    );
};

SelectedFilters.propTypes = {
    filters: PropTypes.array.isRequired,
};

// Unhighlight all highlighted organ / inset image / systems terms and all highlighted svg paths / shapes and all highlighted inset images
const unHighlightOrgan = () => {
    const matchingElems = document.querySelectorAll('.highlight');
    matchingElems.forEach((el) => {
        el.classList.remove('highlight');
    });
};

// Add class "changedClass" to all elements that match input parameter string "matchingString"
// removeFlag = true will remove the class rather than add it
const addingClass = (changedClass, matchingString, removeFlag = false) => {
    const matchingElems = document.querySelectorAll(`.${matchingString}`);
    if (removeFlag) {
        matchingElems.forEach((el) => {
            el.classList.remove(changedClass);
        });
    } else {
        matchingElems.forEach((el) => {
            el.classList.add(changedClass);
        });
    }
};

// Set body map diagram colors based on url, when component mounts
export const initializeBodyMap = (searchQuery, BodyList, SystemsList) => {
    const query = new QueryString(searchQuery);
    const terms = query.getKeyValues(organField);
    if (terms.length > 0) {
        terms.forEach((term) => {
            if (BodyList[term]) {
                BodyList[term].forEach((bodyClass) => {
                    addingClass('active', bodyClass);
                });
            }
            if (SystemsList[term]) {
                document.getElementById(term).classList.add('active');
            }
        });
    }
};

// Clearing organ and systems key value selections from a url
export const clearBodyMapSelectionsFromUrl = (originalUrl) => {
    const parsedUrl = url.parse(originalUrl);
    const query = new QueryString(parsedUrl.query);
    query.deleteKeyValue(organField);
    query.deleteKeyValue(systemsField);
    const href = `?${query.format()}`;
    return href;
};

// Highlight all of the svg paths / shapes corresponding to a hovered-over svg path / shape and highlight corresponding term(s)
// Most organs are comprised of multiple svg paths and we want all of the corresponding svg components to highlight together
// For example, when the user hovers over one kidney, we want both kidneys to highlight because both will be selected upon click
// As another example, "musculature of body" is comprised of 7 paths right next to each other and it would be confusing for just one line or section to highlight on hover
const svgHighlight = (e, BodyList) => {
    // Remove existing highlights
    unHighlightOrgan();
    const svgClass = e.target.className.baseVal;
    if (svgClass) {
        e.target.className.baseVal = `${svgClass} highlight`;
        Object.keys(BodyList).forEach((b) => {
            if (BodyList[b] === svgClass || BodyList[b].includes(svgClass)) {
                // Highlight corresponding organ term
                document.getElementById(b).classList.add('highlight');
                BodyList[b].forEach((bodyClass) => {
                    addingClass('highlight', bodyClass);
                    if (bodyClass.indexOf('cls') === -1) {
                        // Highlight corresponding organ term
                        document.getElementById(bodyClass).classList.add('highlight');
                    }
                });
            }
        });
    }
};

// Highlight all of the paths corresponding to a particular organ / system / inset image term
// Additionally, highlight any other associated terms
// For example, if hovering over "large intestine", we want all "large intestine" svg components to highlight as well as the term "colon"
// Hovering over a system term name should highlight all associated organ terms and inset image terms and their corresponding svg elements or inset images
const highlightOrgan = (e, BodyList, CellsList, SystemsList) => {
    const currentOrgan = e.target.id || e.target.parentNode.id;
    // Check inset images mapping to see if term exists in that object
    if (Object.keys(CellsList).includes(currentOrgan)) {
        addingClass('highlight', currentOrgan.replace(' ', '-'));
        document.getElementById(currentOrgan).classList.add('highlight');
    // If not, check organs mapping searching for the term
    } else {
        Object.keys(BodyList).forEach((b) => {
            if (b === currentOrgan) {
                BodyList[b].forEach((bodyClass) => {
                    if (bodyClass.indexOf('cls') === -1) {
                        document.getElementById(bodyClass).classList.add('highlight');
                        const newBodyClass = BodyList[bodyClass];
                        if (!newBodyClass) {
                            addingClass('highlight', bodyClass);
                        } else {
                            newBodyClass.forEach((b2) => {
                                addingClass('highlight', b2);
                            });
                        }
                    } else {
                        addingClass('highlight', bodyClass);
                    }
                });
            }
        });
        // In either case, check systems list for term
        Object.keys(SystemsList).forEach((b) => {
            if (b === e.target.id) {
                SystemsList[b].forEach((bodyClass) => {
                    if (bodyClass.indexOf('cls') === -1) {
                        document.getElementById(bodyClass).classList.add('highlight');
                        const newBodyClass = BodyList[bodyClass];
                        if (!newBodyClass) {
                            const matchingElems = document.querySelectorAll(`.${bodyClass}, .${bodyClass.replace(' ', '-')}`);
                            matchingElems.forEach((el) => {
                                el.classList.add('highlight');
                            });
                        } else {
                            newBodyClass.forEach((b2) => {
                                addingClass('highlight', b2);
                            });
                        }
                    } else {
                        addingClass('highlight', bodyClass);
                    }
                });
            }
        });
    }
};

// Checks to see if "organ" is included in "selectedOrgan"
// checkClass is used to set an active class on buttons or images based on whether or not they are selected
const checkClass = (selectedOrgan, organ) => selectedOrgan.includes(organ);

// The BodyMap component is comprised of several different elements:
// (1) List of system slims ("central nervous system", "skeletal system", "digestive system")
// (2) Diagram of body in svg format with selectable organs
// (3) List of organ slims selectable on body diagram ("adrenal gland", "bone element")
// (4) Inset images representing organ slims difficult to represent on a body diagram ("adipose tissue")
// (5) List of organ slims represented by inset images
// (6) A button (could be optional) to clear organ and system slims selected on BodyMap
// All of these components are responsive (they stack and change position relative to each other based on screen width)
class BodyMap extends React.Component {
    constructor(props) {
        super(props);

        const searchQuery = url.parse(this.props.context['@id']).search;

        // Determine which organ and system slims are already selected (based on the url)
        const terms = queryString.parse(searchQuery);
        let organTerms = terms[organField];
        const systemsTerms = terms[systemsField];

        let BodyList = {};
        let CellsList = {};
        let SystemsList = {};
        if (props.organism === 'Homo sapiens') {
            BodyList = HumanList;
            CellsList = HumanCellsList;
            SystemsList = HumanSystemsList;
        } else if (props.organism === 'Mus musculus') {
            BodyList = MouseList;
            CellsList = MouseCellsList;
            SystemsList = MouseSystemsList;
        }

        // In the case that there are only organ slims, we initialize "organTerms" to consist of organ slims
        // In the case that there are both organ and system slims, append system terms to organ terms
        // Currently this code has a lot of cases to prevent spread syntax from spreading single terms (strings) into individual letters
        if (systemsTerms && organTerms) {
            if (typeof organTerms === 'string') {
                // There is one organ term, one systems term
                if (typeof systemsTerms === 'string') {
                    organTerms = [organTerms, systemsTerms];
                // There is one organ term, multiple systems terms (no examples but maybe leave for completeness?)
                } else {
                    organTerms = [organTerms, ...systemsTerms];
                }
            // There are multiple organ terms and one systems term
            } else if (typeof systemsTerms === 'string') {
                organTerms = [...organTerms, systemsTerms];
            // There are multiple organ terms and multiple systems terms
            } else {
                organTerms = [...organTerms, ...systemsTerms];
            }
        // In the case that there are only systems terms, set organ terms to be systems terms
        } else if (systemsTerms) {
            organTerms = systemsTerms;
        }
        // Initialize state, "selectedOrgan", to be combined organ and system terms
        this.state = {
            selectedOrgan: organTerms || [],
            organFacets: [],
            systemFacets: [],
        };
        this.CellsList = CellsList;
        this.BodyList = BodyList;
        this.SystemsList = SystemsList;
        this.svgClick = this.svgClick.bind(this);
        this.chooseOrgan = this.chooseOrgan.bind(this);
        this.clearOrgans = this.clearOrgans.bind(this);
    }

    // Once the page has loaded, we want to check to see if any terms are selected
    // and highlight the body map elements which correspond to those terms
    componentDidMount() {
        const searchQuery = url.parse(this.props.context['@id']).search;
        initializeBodyMap(searchQuery, this.BodyList, this.SystemsList);

        // Find url for page without any organs or systems selected
        const query = new QueryString(searchQuery);
        const linkOrgans = query.getKeyValues(organField);
        linkOrgans.forEach((term) => {
            query.deleteKeyValue(organField, term);
        });
        const linkSystems = query.getKeyValues(systemsField);
        linkSystems.forEach((term) => {
            query.deleteKeyValue(systemsField, term);
        });
        const unfilteredHref = query.format();
        getSeriesData(unfilteredHref, this.context.fetch).then((response) => {
            const { facets } = response;
            const organFacets = facets.filter((f) => f.field === organField)[0].terms.map((f) => f.key);
            let systemFacets = [];
            if (facets.filter((f) => f.field === systemsField)[0]) {
                systemFacets = facets.filter((f) => f.field === systemsField)[0].terms.map((f) => f.key);
            }
            this.setState({
                organFacets,
                systemFacets,
            }, () => {
                // Add a class to disable pointer events on paths associated with unavailable organ terms
                Object.keys(this.BodyList).forEach((b) => {
                    if (this.state.organFacets.indexOf(b) === -1) {
                        this.BodyList[b].forEach((path) => {
                            addingClass('disabled', path);
                        });
                    }
                });
            });
        });
    }

    // Clear all organ and system slims selections (clear state and navigate to new url)
    clearOrgans() {
        if (this.state.selectedOrgan.length !== 0) {
            // Clear terms from state and clear "active" class from organs
            this.setState({ selectedOrgan: [] });
            // Removing class "active" from all elements with an "active" class (removeFlag = true)
            addingClass('active', 'active', true);
            // Renavigate to fresh url
            const href = clearBodyMapSelectionsFromUrl(this.props.context['@id']);
            this.context.navigate(href, { noscroll: true });
        }
    }

    // Executes on click of organ, inset image, or system term
    chooseOrgan(e) {
        // Clicked-on organ or system term name is the "currentOrgan"
        const currentOrgan = e.target.id;

        // Selection of an organ or system term is a toggle
        // active = true corresponds to a term that should be selected now that the user has clicked
        // active = false corresponds to a term that should be de-selected now
        let active = true;
        if ((typeof this.state.selectedOrgan === 'string' && this.state.selectedOrgan === currentOrgan) || (typeof this.state.selectedOrgan !== 'string' && this.state.selectedOrgan.includes(currentOrgan))) {
            active = false;
        }

        // We need to keep track of (de)selected terms that may also necessitate other terms' (de)selection
        // For instance, selecting "central nervous system" will also select "brain" and "spinal cord"
        // Similarly, selecting "lung" will also select "brochus"
        const multipleAssociations = [];

        // "systemsClick" represents whether the user clicked on an systems term
        // If the click was on a systems term, we need to append an extra query at the end of the new url
        let systemsClick = false;

        // User has selected a term, so all corresponding body map elements need to be selected
        // Any associated terms and their body map elements must also be selected
        if (active) {
            Object.keys(this.BodyList).forEach((b) => {
                if (b === e.target.id) {
                    this.BodyList[b].forEach((bodyClass) => {
                        if (bodyClass.indexOf('cls') === -1) {
                            multipleAssociations.push(bodyClass);
                            document.getElementById(bodyClass).classList.add('active');
                            const newBodyClass = this.BodyList[bodyClass];
                            if (!newBodyClass) {
                                addingClass('active', bodyClass);
                            } else {
                                newBodyClass.forEach((b2) => {
                                    addingClass('active', b2);
                                });
                            }
                        } else {
                            addingClass('active', bodyClass);
                        }
                    });
                }
            });
            // If the term is a systems term, all systems elements (terms and body map elements) must be selected
            Object.keys(this.SystemsList).forEach((b) => {
                if (b === e.target.id) {
                    systemsClick = true;
                    this.SystemsList[b].forEach((bodyClass) => {
                        if (bodyClass.indexOf('cls') === -1) {
                            multipleAssociations.push(bodyClass);
                            document.getElementById(bodyClass).classList.add('active');
                            const newBodyClass = this.BodyList[bodyClass];
                            if (!newBodyClass) {
                                addingClass('active', bodyClass);
                            } else {
                                newBodyClass.forEach((b2) => {
                                    addingClass('active', b2);
                                });
                            }
                        } else {
                            addingClass('active', bodyClass);
                        }
                    });
                }
            });
        // User has de-selected a term, so all corresponding body map elements need to be de-selected
        // Any associated terms and their body map elements must also be de-selected
        } else {
            Object.keys(this.BodyList).forEach((b) => {
                if (b === e.target.id) {
                    this.BodyList[b].forEach((bodyClass) => {
                        if (bodyClass.indexOf('cls') === -1) {
                            multipleAssociations.push(bodyClass);
                            document.getElementById(bodyClass).classList.remove('active');
                            const newBodyClass = this.BodyList[bodyClass];
                            if (!newBodyClass) {
                                // Removing "active" class (removeFlag = true)
                                addingClass('active', bodyClass, true);
                            } else {
                                newBodyClass.forEach((b2) => {
                                    // Removing "active" class (removeFlag = true)
                                    addingClass('active', b2, true);
                                });
                            }
                        } else {
                            // Removing "active" class (removeFlag = true)
                            addingClass('active', bodyClass, true);
                        }
                    });
                }
            });
            // If the term is a systems term, all systems elements (terms and body map elements) must be de-selected
            Object.keys(this.SystemsList).forEach((b) => {
                if (b === e.target.id) {
                    systemsClick = true;
                    this.SystemsList[b].forEach((bodyClass) => {
                        if (bodyClass.indexOf('cls') === -1) {
                            multipleAssociations.push(bodyClass);
                            document.getElementById(bodyClass).classList.remove('active');
                            const newBodyClass = this.BodyList[bodyClass];
                            if (!newBodyClass) {
                                // Removing "active" class (removeFlag = true)
                                addingClass('active', bodyClass, true);
                            } else {
                                newBodyClass.forEach((b2) => {
                                    // Removing "active" class (removeFlag = true)
                                    addingClass('active', b2, true);
                                });
                            }
                        } else {
                            // Removing "active" class (removeFlag = true)
                            addingClass('active', bodyClass, true);
                        }
                    });
                }
            });
        }

        // Update state based on whether or not the term (and its associated terms) are selected or de-selected
        // Here also we have extra cases to prevent spread syntax from spreading single terms
        // If there is no "currentOrgan" in state, we add the new organ and associated terms
        const previousState = this.state.selectedOrgan;
        if (this.state.currentOrgan === []) {
            this.setState({
                selectedOrgan: [currentOrgan, ...multipleAssociations],
            });
        // If the state already includes the term, we remove it and its associated terms from state
        } else if (this.state.selectedOrgan.includes(currentOrgan)) {
            if (typeof this.state.selectedOrgan !== 'string') {
                this.setState((prevState) => ({
                    selectedOrgan: prevState.selectedOrgan.filter((organ) => organ !== currentOrgan && !(multipleAssociations.includes(organ))) || [],
                }));
            } else {
                this.setState({ selectedOrgan: [] });
            }
        // If there is already a "currentOrgan" in state but it does not include the clicked-on slim,
        // we add the organ and its associations to the state
        } else {
            let newState;
            if (typeof this.state.selectedOrgan !== 'string') {
                newState = [...this.state.selectedOrgan, ...multipleAssociations, currentOrgan];
            } else {
                newState = [this.state.selectedOrgan, ...multipleAssociations, currentOrgan];
            }
            // Just to keep state clean, we remove any possible duplicates here
            this.setState({
                selectedOrgan: [...new Set(newState)],
            });
        }

        // Construct and navigate to a new url with added or deleted key values for the organ and system fields
        const parsedUrl = url.parse(this.props.context['@id']);
        const query = new QueryString(parsedUrl.query);
        if (active) {
            if (systemsClick) {
                query.addKeyValue(systemsField, e.target.id);
            } else {
                query.addKeyValue(organField, e.target.id);
            }
            if (multipleAssociations) {
                multipleAssociations.forEach((assoc) => {
                    // If you select "bronchus" and then "lung", "bronchus" is associated with "lung", so we need to take care not to append "bronchus" to the url twice here (can cause JS errors)
                    if (!previousState.includes(assoc)) {
                        query.addKeyValue(organField, assoc);
                    }
                });
            }
        } else {
            if (systemsClick) {
                query.deleteKeyValue(systemsField, e.target.id);
            } else {
                query.deleteKeyValue(organField, e.target.id);
            }
            if (multipleAssociations) {
                multipleAssociations.forEach((assoc) => {
                    query.deleteKeyValue(organField, assoc);
                });
            }
        }
        const href = `?${query.format()}#openModal`;
        this.context.navigate(href, { noscroll: true });
    }

    // Executes on click on SVG body map diagram
    svgClick(e) {
        // Clicked-on body map element class name is the "svgClass"
        // Strip out "highlight" class to get primary identifier of svg element
        let svgClass = e.target.className.baseVal.replace(' highlight', '');

        // We have to check to make sure a class exists because the SVG background has no class and we don't want any update to execute in that case
        if (svgClass) {
            // Selection of an organ is a toggle
            let active = true;
            // If the svg class contains "active", then we are de-selecting the organ
            if (svgClass.indexOf('active') > -1) {
                svgClass = svgClass.replace(' active', '');
                active = false;
            // If not, we are selecting the organ, an append an active class to it
            } else {
                e.target.className.baseVal = `${svgClass} active`;
            }

            // To determine the organ(s) to which the svg element corresponds, we loop through BodyList
            let newOrgan;
            // An organ may have multiple associations and we want to be sure to highlight all the associated terms on click
            // For example, clicking on the "intestine" organ should also highlight the "colon" organ
            const multipleAssociations = [];
            Object.keys(this.BodyList).forEach((b) => {
                if (this.BodyList[b] === svgClass || this.BodyList[b].includes(svgClass)) {
                    // This is the new organ that we want to append to state
                    newOrgan = b;
                    // Make sure all svg elements associated with that organ are selected, not just the clicked-on element
                    if (active) {
                        this.BodyList[b].forEach((bodyClass) => {
                            addingClass('active', bodyClass);
                            if (bodyClass.indexOf('cls') === -1) {
                                multipleAssociations.push(bodyClass);
                                if (active) {
                                    document.getElementById(bodyClass).classList.add('active');
                                } else {
                                    document.getElementById(bodyClass).classList.remove('active');
                                }
                            }
                        });
                    // De-select all svg elements associated with clicked-on organ
                    } else {
                        this.BodyList[b].forEach((bodyClass) => {
                            // Removing "active" class (removeFlag = true)
                            addingClass('active', bodyClass, true);
                            if (bodyClass.indexOf('cls') === -1) {
                                multipleAssociations.push(bodyClass);
                                if (active) {
                                    document.getElementById(bodyClass).classList.add('active');
                                } else {
                                    document.getElementById(bodyClass).classList.remove('active');
                                }
                            }
                        });
                    }
                }
            });

            // Set state to be new organ and any other matches
            // We need to check if there is a new organ found because there are a very very few shapes that do not have corresponding organ_slims and in that case we do not want to add an undefined value to the state / try to navigate to undefined url
            // For example, the uterine walls and vas deferens shapes do not correspond to any organ slim
            if (newOrgan) {
                const previousState = this.state.selectedOrgan;
                // If there is no "currentOrgan" in state, we add the new organ and its associated terms
                if (this.state.currentOrgan === []) {
                    this.setState({
                        selectedOrgan: [newOrgan, ...multipleAssociations],
                    });
                // If the state already includes the newly selected organ, we remove it and its associated terms
                } else if (this.state.selectedOrgan.includes(newOrgan)) {
                    if (typeof this.state.selectedOrgan !== 'string') {
                        this.setState((prevState) => ({
                            selectedOrgan: prevState.selectedOrgan.filter((organ) => organ !== newOrgan && !(multipleAssociations.includes(organ))) || [],
                        }));
                    } else {
                        this.setState({ selectedOrgan: [] });
                    }
                // If there already is a "currentOrgan" but it does not include the clicked-on organ, add the new organ and its associations
                } else {
                    let newState;
                    if (typeof this.state.selectedOrgan !== 'string') {
                        newState = [...this.state.selectedOrgan, ...multipleAssociations, newOrgan];
                    } else {
                        newState = [this.state.selectedOrgan, ...multipleAssociations, newOrgan];
                    }
                    this.setState({
                        selectedOrgan: [...new Set(newState)],
                    });
                }

                // Append or remove organ(s) to / from the search query
                const parsedUrl = url.parse(this.props.context['@id']);
                const query = new QueryString(parsedUrl.query);
                if (active) {
                    query.addKeyValue(organField, newOrgan);
                    if (multipleAssociations) {
                        multipleAssociations.forEach((assoc) => {
                            if (!previousState.includes(assoc)) {
                                query.addKeyValue(organField, assoc);
                            }
                        });
                    }
                } else {
                    query.deleteKeyValue(organField, newOrgan);
                    if (multipleAssociations) {
                        multipleAssociations.forEach((assoc) => {
                            query.deleteKeyValue(organField, assoc);
                        });
                    }
                }
                const href = `?${query.format()}#openModal`;
                this.context.navigate(href, { noscroll: true });
            }
        }
    }

    render() {
        return (
            <div className={`body-facet-container ${this.props.organism.toLowerCase().replace(/\s/g, '-')}`}>
                <div className="body-list body-list-top">
                    <ul className="body-list-inner">
                        {Object.keys(this.SystemsList).map((b) => (
                            <li key={b}>
                                <span
                                    id={b}
                                    className={`body-list-element ${checkClass(this.state.selectedOrgan, b) ? 'active' : ''}`}
                                    role="button"
                                    tabIndex="0"
                                    onClick={(e) => this.chooseOrgan(e)}
                                    onKeyPress={(e) => this.chooseOrgan(e)}
                                    onMouseEnter={(e) => highlightOrgan(e, this.BodyList, this.CellsList, this.SystemsList)}
                                    onMouseLeave={unHighlightOrgan}
                                    disabled={this.state.systemFacets.indexOf(b) === -1}
                                >
                                    {b}
                                </span>
                            </li>
                        ))}
                        <button type="button" className="clear-organs" onClick={this.clearOrgans}>
                            <i className="icon icon-times-circle" />
                            Clear body map selections
                        </button>
                    </ul>
                </div>
                <div className="body-facet">
                    <div className="body-image-container">
                        {this.props.organism === 'Homo sapiens' ?
                            <HumanBodyDiagram
                                handleClick={this.svgClick}
                                handleHighlight={svgHighlight}
                                BodyList={this.BodyList}
                            />
                        : null}
                        {this.props.organism === 'Mus musculus' ?
                            <MouseBodyDiagram
                                handleClick={this.svgClick}
                                handleHighlight={svgHighlight}
                                BodyList={this.BodyList}
                            />
                        : null}
                    </div>
                    <div className="body-list">
                        <ul className="body-list-inner">
                            {Object.keys(this.BodyList).map((b) => (
                                <li key={b}>
                                    <span
                                        id={b}
                                        className={`body-list-element ${checkClass(this.state.selectedOrgan, b) ? 'active' : ''}`}
                                        role="button"
                                        tabIndex="0"
                                        onClick={(e) => this.chooseOrgan(e)}
                                        onKeyPress={(e) => this.chooseOrgan(e)}
                                        onMouseEnter={(e) => highlightOrgan(e, this.BodyList, this.CellsList, this.SystemsList)}
                                        onMouseLeave={unHighlightOrgan}
                                        disabled={this.state.organFacets.indexOf(b) === -1}
                                    >
                                        {b}
                                    </span>
                                </li>
                            ))}
                        </ul>
                    </div>
                    <div className="body-inset-container">
                        {Object.keys(this.CellsList).map((image) => (
                            <button
                                type="button"
                                id={image}
                                className={`body-inset ${image.replace(' ', '-')} ${checkClass(this.state.selectedOrgan, image) ? 'active' : ''}`}
                                onClick={(e) => this.chooseOrgan(e)}
                                onMouseEnter={(e) => highlightOrgan(e, this.BodyList, this.CellsList, this.SystemsList)}
                                onMouseLeave={unHighlightOrgan}
                                key={image}
                                disabled={this.state.organFacets.indexOf(image) === -1}
                            >
                                {((typeof this.state.selectedOrgan === 'string' && this.state.selectedOrgan === image) || (typeof this.state.selectedOrgan !== 'string' && this.state.selectedOrgan.includes(image))) ?
                                    <img src={`/static/img/bodyMap/insetSVGs/${this.props.organism === 'Mus musculus' ? 'mouse_' : ''}${image.replace(' ', '_')}.svg`} alt={image} />
                                :
                                    <img src={`/static/img/bodyMap/insetSVGs/${this.props.organism === 'Mus musculus' ? 'mouse_' : ''}${image.replace(' ', '_')}_deselected.svg`} alt={image} />
                                }
                                <div className="overlay" />
                            </button>
                        ))}
                    </div>
                    <div className="body-list body-list-narrow">
                        <ul className="body-list-inner">
                            {Object.keys(this.CellsList).map((b) => (
                                <li key={b}>
                                    <span
                                        id={b}
                                        className={`body-list-element ${b.replace(' ', '-')} ${checkClass(this.state.selectedOrgan, b) ? 'active' : ''}`}
                                        role="button"
                                        tabIndex="0"
                                        onClick={(e) => this.chooseOrgan(e)}
                                        onKeyPress={(e) => this.chooseOrgan(e)}
                                        onMouseEnter={(e) => highlightOrgan(e, this.BodyList, this.CellsList, this.SystemsList)}
                                        onMouseLeave={unHighlightOrgan}
                                        disabled={this.state.organFacets.indexOf(b) === -1}
                                    >
                                        {b}
                                    </span>
                                </li>
                            ))}
                        </ul>
                    </div>
                </div>
            </div>
        );
    }
}

BodyMap.propTypes = {
    context: PropTypes.object.isRequired,
    organism: PropTypes.string.isRequired,
};

BodyMap.contextTypes = {
    navigate: PropTypes.func,
    location_href: PropTypes.string,
    fetch: PropTypes.func,
};

// Clickable thumbnail
// Comprised of body map svg and inset images, with expand icon and instructions
// Button to display the actual body map facet <BodyMapModal>
export const ClickableThumbnail = (props) => {
    // "toggleThumbnail" toggles whether or not the pop-up is displayed
    const { toggleThumbnail, organism, context } = props;
    let CellsList = {};
    if (props.organism === 'Homo sapiens') {
        CellsList = HumanCellsList;
    } else if (props.organism === 'Mus musculus') {
        CellsList = MouseCellsList;
    }

    return (
        <>
            <button
                type="button"
                className="body-image-thumbnail"
                onClick={() => toggleThumbnail()}
            >
                <div className="body-map-expander">Filter results by body diagram</div>
                {svgIcon('expandArrows')}
                {organism === 'Homo sapiens' ?
                    <HumanBodyDiagram
                        BodyList={HumanList}
                    />
                : null}
                {organism === 'Mus musculus' ?
                    <MouseBodyDiagram
                        BodyList={MouseList}
                    />
                : null}
                <div className="body-list body-list-narrow">
                    <ul className="body-list-inner">
                        {Object.keys(CellsList).map((image) => (
                            <div
                                className={`body-inset ${image}`}
                                id={image}
                                key={image}
                            >
                                <img className="active-image" src={`/static/img/bodyMap/insetSVGs/${organism === 'Mus musculus' ? 'mouse_' : ''}${image.replace(' ', '_')}.svg`} alt={image} />
                                <img className="inactive-image" src={`/static/img/bodyMap/insetSVGs/${organism === 'Mus musculus' ? 'mouse_' : ''}${image.replace(' ', '_')}_deselected.svg`} alt={image} />
                                <div className="overlay" />
                            </div>
                        ))}
                    </ul>
                </div>
            </button>
            <SelectedFilters filters={context.filters} />
        </>
    );
};

ClickableThumbnail.propTypes = {
    toggleThumbnail: PropTypes.func.isRequired,
    organism: PropTypes.string.isRequired,
    context: PropTypes.object.isRequired,
};

// Pop-up body map facet
// Displayed when you click on <ClickableThumbnail>
// Allows you to select organ / system filters
export const BodyMapModal = (props) => {
    const { context, isThumbnailExpanded, toggleThumbnail, organism } = props;
    return (
        <div className="modal" style={{ display: 'block' }}>
            <div className={`body-map-container-pop-up ${isThumbnailExpanded ? 'expanded' : 'collapsed'}`}>
                <button type="button" className="collapse-body-map" onClick={() => toggleThumbnail()}>
                    {svgIcon('collapseArrows')}
                    <div className="body-map-collapser">Hide body diagram</div>
                </button>
                <div className="clickable-diagram-container">
                    <BodyMap
                        context={context}
                        organism={organism}
                    />
                </div>
            </div>
            <div className="modal-backdrop in" />
        </div>
    );
};

BodyMapModal.propTypes = {
    isThumbnailExpanded: PropTypes.bool.isRequired,
    toggleThumbnail: PropTypes.func.isRequired,
    context: PropTypes.object.isRequired,
    organism: PropTypes.string.isRequired,
};

// Combining the body map thumbnail and the body map modal into one component
export const BodyMapThumbnailAndModal = (props) => {
    const [isThumbnailExpanded, setIsThumbnailExpanded] = React.useState(false);

    let BodyList = {};
    let CellsList = {};
    let SystemsList = {};
    if (props.organism === 'Homo sapiens') {
        BodyList = HumanList;
        CellsList = HumanCellsList;
        SystemsList = HumanSystemsList;
    } else if (props.organism === 'Mus musculus') {
        BodyList = MouseList;
        CellsList = MouseCellsList;
        SystemsList = MouseSystemsList;
    }

    React.useEffect(() => {
        // Display modal if page has just refreshed because of user selection from body map
        setIsThumbnailExpanded(props.location.includes('#openModal'));

        // Highlight body map selections based on url
        const searchQuery = url.parse(props.context['@id']).search;
        initializeBodyMap(searchQuery, BodyList, SystemsList);
        const query = new QueryString(searchQuery);
        const terms = query.getKeyValues(organField);
        terms.forEach((term) => {
            if (CellsList[term] && document.getElementById(term)) {
                document.getElementById(term).classList.add('active');
            }
        });
    }, [setIsThumbnailExpanded, props.context, props.location]);

    const toggleThumbnail = () => {
        setIsThumbnailExpanded(!isThumbnailExpanded);
    };

    return (
        <div className="body-map-thumbnail-and-modal">
            <ClickableThumbnail
                toggleThumbnail={toggleThumbnail}
                organism={props.organism}
                CellsList={CellsList}
                context={props.context}
            />
            {isThumbnailExpanded ?
                <BodyMapModal
                    isThumbnailExpanded
                    toggleThumbnail={toggleThumbnail}
                    context={props.context}
                    organism={props.organism}
                />
            : null}
        </div>
    );
};

BodyMapThumbnailAndModal.propTypes = {
    context: PropTypes.object.isRequired,
    location: PropTypes.string.isRequired, // Should be context.location_href from parent
    organism: PropTypes.string.isRequired,
};

export default BodyMap;
