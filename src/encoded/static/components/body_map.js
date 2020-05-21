import React from 'react';
import PropTypes from 'prop-types';
import queryString from 'query-string';
import url from 'url';
import QueryString from '../libs/query_string';
import BodyDiagram from '../img/bodyMap/Deselected_Body';

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
const BodyList = {
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
    'spinal chord': ['cls-66'],
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

// Mapping from cells and tissue types to inset images
// All mappings are empty because there are no paths or shapes that correspond to the inset images
//     (each has one associated image with a name corresponding to the cell or tissue term)
const CellsList = {
    'adipose tissue': [],
    blood: [],
    'blood vessel': [],
    'bone marrow': [],
    'connective tissue': [],
    embryo: [],
    epithelium: [],
    placenta: [],
    'lymphoid tissue': [],
    'lymph node': [],
    'lymphatic vessel': [],
};

// Mapping for systems slims
// Systems slims are mapped to organs in the "BodyList"
const SystemsList = {
    'central nervous system': ['brain', 'spinal chord'],
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

// Highlight all of the svg paths / shapes corresponding to a hovered-over svg path / shape and highlight corresponding term(s)
// Most organs are comprised of multiple svg paths and we want all of the corresponding svg components to highlight together
// For example, when the user hovers over one kidney, we want both kidneys to highlight because both will be selected upon click
// As another example, "musculature of body" is comprised of 7 paths right next to each other and it would be confusing for just one line or section to highlight on hover
const svgHighlight = (e) => {
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
const highlightOrgan = (e) => {
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

        // Determine which organ and system slims are already selected (based on the url)
        const searchQuery = url.parse(this.props.context['@id']).search;
        const terms = queryString.parse(searchQuery);
        let organTerms = terms[organField];
        const systemsTerms = terms[systemsField];

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
            selectedOrgan: [organTerms] || [],
        };
        console.log(this.state.selectedOrgan);
        this.svgClick = this.svgClick.bind(this);
        this.chooseOrgan = this.chooseOrgan.bind(this);
        this.clearOrgans = this.clearOrgans.bind(this);
    }

    // Once the page has loaded, we want to check to see if any terms are selected
    // and highlight the body map elements which correspond to those terms
    componentDidMount() {
        const searchQuery = url.parse(this.props.context['@id']).search;
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
    }

    // Clear all organ and system slims selections (clear state and navigate to new url)
    clearOrgans() {
        if (this.state.selectedOrgan.length !== 0) {
            // Clear terms from state and clear "active" class from organs
            this.setState({ selectedOrgan: [] });
            // Removing class "active" from all elements with an "active" class (removeFlag = true)
            addingClass('active', 'active', true);
            // Renavigate to fresh url
            const parsedUrl = url.parse(this.props.context['@id']);
            const query = new QueryString(parsedUrl.query);
            query.deleteKeyValue(organField);
            query.deleteKeyValue(systemsField);
            const href = `?${query.format()}`;
            this.context.navigate(href);
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
            Object.keys(BodyList).forEach((b) => {
                if (b === e.target.id) {
                    BodyList[b].forEach((bodyClass) => {
                        if (bodyClass.indexOf('cls') === -1) {
                            multipleAssociations.push(bodyClass);
                            document.getElementById(bodyClass).classList.add('active');
                            const newBodyClass = BodyList[bodyClass];
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
            Object.keys(SystemsList).forEach((b) => {
                if (b === e.target.id) {
                    systemsClick = true;
                    SystemsList[b].forEach((bodyClass) => {
                        if (bodyClass.indexOf('cls') === -1) {
                            multipleAssociations.push(bodyClass);
                            document.getElementById(bodyClass).classList.add('active');
                            const newBodyClass = BodyList[bodyClass];
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
            Object.keys(BodyList).forEach((b) => {
                if (b === e.target.id) {
                    BodyList[b].forEach((bodyClass) => {
                        if (bodyClass.indexOf('cls') === -1) {
                            multipleAssociations.push(bodyClass);
                            document.getElementById(bodyClass).classList.remove('active');
                            const newBodyClass = BodyList[bodyClass];
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
            Object.keys(SystemsList).forEach((b) => {
                if (b === e.target.id) {
                    systemsClick = true;
                    SystemsList[b].forEach((bodyClass) => {
                        if (bodyClass.indexOf('cls') === -1) {
                            multipleAssociations.push(bodyClass);
                            document.getElementById(bodyClass).classList.remove('active');
                            const newBodyClass = BodyList[bodyClass];
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
                this.setState(prevState => ({
                    selectedOrgan: prevState.selectedOrgan.filter(organ => organ !== currentOrgan && !(multipleAssociations.includes(organ))) || [],
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
        const href = `?${query.format()}`;
        this.context.navigate(href);
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
            Object.keys(BodyList).forEach((b) => {
                if (BodyList[b] === svgClass || BodyList[b].includes(svgClass)) {
                    // This is the new organ that we want to append to state
                    newOrgan = b;
                    // Make sure all svg elements associated with that organ are selected, not just the clicked-on element
                    if (active) {
                        BodyList[b].forEach((bodyClass) => {
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
                        BodyList[b].forEach((bodyClass) => {
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
                        this.setState(prevState => ({
                            selectedOrgan: prevState.selectedOrgan.filter(organ => organ !== newOrgan && !(multipleAssociations.includes(organ))) || [],
                        }));
                    } else {
                        this.setState({ selectedOrgan: [] });
                    }
                // If there already is a "currentOrgan" but it does not include the clicked-on organ, add the new organ and its assocations
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
                const href = `?${query.format()}`;
                this.context.navigate(href);
            }
        }
    }

    render() {
        return (
            <div className="body-facet-container">
                <div className="body-list body-list-top">
                    <div className="body-list-inner">
                        {Object.keys(SystemsList).map(b =>
                            <button
                                className={`body-list-element ${this.state.selectedOrgan.includes(b) ? 'active' : ''}`}
                                id={b}
                                onClick={e => this.chooseOrgan(e)}
                                onMouseEnter={e => highlightOrgan(e)}
                                onMouseLeave={unHighlightOrgan}
                                key={b}
                            >
                                {b}
                            </button>
                        )}
                        <button className="clear-organs" onClick={this.clearOrgans}>
                            <i className="icon icon-times-circle" />
                            Clear body map selections
                        </button>
                    </div>
                </div>
                <div className="body-facet">
                    <div className="body-image-container">
                        <BodyDiagram
                            handleClick={this.svgClick}
                            handleHighlight={svgHighlight}
                        />
                    </div>
                    <div className="body-list">
                        <div className="body-list-inner">
                            {Object.keys(BodyList).map(b =>
                                <button
                                    className={`body-list-element ${this.state.selectedOrgan.includes(b) ? 'active' : ''}`}
                                    id={b}
                                    onClick={e => this.chooseOrgan(e)}
                                    onMouseEnter={e => highlightOrgan(e)}
                                    onMouseLeave={unHighlightOrgan}
                                    key={b}
                                >
                                    {b}
                                </button>
                            )}
                        </div>
                    </div>
                    <div className="body-inset-container">
                        {Object.keys(CellsList).map(image =>
                            <button
                                className={`body-inset ${image.replace(' ', '-')} ${((typeof this.state.selectedOrgan === 'string' && this.state.selectedOrgan === image) || (typeof this.state.selectedOrgan !== 'string' && this.state.selectedOrgan.includes(image))) ? 'active' : ''}`}
                                id={image}
                                onClick={e => this.chooseOrgan(e)}
                                onMouseEnter={e => highlightOrgan(e)}
                                onMouseLeave={unHighlightOrgan}
                                key={image}
                            >
                                {((typeof this.state.selectedOrgan === 'string' && this.state.selectedOrgan === image) || (typeof this.state.selectedOrgan !== 'string' && this.state.selectedOrgan.includes(image))) ?
                                    <img src={`/static/img/bodyMap/insetSVGs/${image.replace(' ', '_')}.svg`} alt={image} />
                                :
                                    <img src={`/static/img/bodyMap/insetSVGs/${image.replace(' ', '_')}_deselected.svg`} alt={image} />
                                }
                                <div className="overlay" />
                            </button>
                        )}
                    </div>
                    <div className="body-list body-list-narrow">
                        <div className="body-list-inner">
                            {Object.keys(CellsList).map(b =>
                                <button
                                    className={`body-list-element ${b.replace(' ', '-')} ${((typeof this.state.selectedOrgan === 'string' && this.state.selectedOrgan === b) || (typeof this.state.selectedOrgan !== 'string' && this.state.selectedOrgan.includes(b))) ? 'active' : ''}`}
                                    id={b}
                                    onClick={e => this.chooseOrgan(e)}
                                    onMouseEnter={e => highlightOrgan(e)}
                                    onMouseLeave={unHighlightOrgan}
                                    key={b}
                                >
                                    {b}
                                </button>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        );
    }
}

BodyMap.propTypes = {
    context: PropTypes.object.isRequired,
};

BodyMap.contextTypes = {
    navigate: PropTypes.func,
    location_href: PropTypes.string,
};

export default BodyMap;
