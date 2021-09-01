import PropTypes from 'prop-types';
import { motion, AnimatePresence } from 'framer-motion';
import { svgIcon } from '../../libs/svg-icons';


/**
 * Generate a group's identifier for the given group so that we can identify which group title
 * button the user clicked.
 * @param {object} group The group to generate an identifier for.
 * @returns {string} The generated identifier.
 */
export const generateFacetGroupIdentifier = (group) => `facet-group-${group.title}-${group.name}`;


/**
 * Filters the given facets so that only the ones not included in the given facet groups get
 * returned.
 * @param {array} facets The facets to filter
 * @param {array} facetGroups The facet groups to filter against
 * @returns {array} The filtered facets
 */
export const filterTopLevelFacets = (facets, facetGroups) => {
    const groupedFacetFields = facetGroups.reduce((accFacetFields, group) => accFacetFields.concat(group.facet_fields), []);
    return facets.filter((facet) => !groupedFacetFields.includes(facet.field));
};


/**
 * Generate an array with the identifiers for all the given facet groups.
 * @param {array} facetGroups The facet groups to generate the identifiers for
 * @returns {array} The identifiers for the given facet groups
 */
export const generateFacetGroupIdentifierList = (facetGroups) => {
    if (facetGroups?.length > 1) {
        return facetGroups.map((group) => generateFacetGroupIdentifier(group));
    }
    return [];
};


/**
 * Returns an array of all facet schema names in the given facet groups.
 * @param {array} facetGroups The facet groups to get the facet schema names from
 * @returns {array} The facet schema names, deduped
 */
export const generateFacetGroupNameList = (facetGroups) => {
    if (facetGroups?.length > 1) {
        const facetGroupNameList = facetGroups.reduce((accFacetGroupNames, group) => (
            accFacetGroupNames.add(group.name)
        ), new Set());
        return [...facetGroupNameList];
    }
    return [];
};


/**
 * Display the facet section title button.
 */
const FacetGroupTitle = ({ group, isExpanded, isNameDisplayed, expanderHandler }, { profilesTitles }) => {
    const groupIdentifier = generateFacetGroupIdentifier(group);
    const profileName = profilesTitles?.[group.name];

    /**
     * Called when the user clicks the expander.
     */
    const handleClick = (e) => {
        expanderHandler(groupIdentifier, e.altKey);
    };

    return (
        <button
            type="button"
            className={`facet-group-title${isExpanded ? ' facet-group-title--open' : ''}`}
            aria-expanded={isExpanded}
            aria-controls={generateFacetGroupIdentifier(group)}
            onClick={handleClick}
        >
            <div className="facet-group-title__title-name">
                <div className="facet-group-title__title">
                    {group.title}
                </div>
                {isNameDisplayed && (
                    <div className="facet-group-title__name">
                        {profileName || group.name}
                    </div>
                )}
            </div>
            <div className="facet-group-title__expand-indicator">
                {svgIcon(isExpanded ? 'chevronUp' : 'chevronDown')}
            </div>
        </button>
    );
};

FacetGroupTitle.propTypes = {
    /** Section definition from schema */
    group: PropTypes.object.isRequired,
    /** True if section appears expanded */
    isExpanded: PropTypes.bool.isRequired,
    /** True to display the schema name below the title */
    isNameDisplayed: PropTypes.bool.isRequired,
    /** Called to handle clicks in the section title */
    expanderHandler: PropTypes.func.isRequired,
};

FacetGroupTitle.contextTypes = {
    profilesTitles: PropTypes.object,
};

/**
 * Renders one facet group when searched objects have a schema with a `facet_groups` property.
 */
export const FacetGroup = ({
    group,
    isExpanded,
    isNameDisplayed,
    expanderHandler,
    children,
}) => (
    <div className="facet-group">
        <FacetGroupTitle group={group} isExpanded={isExpanded} isNameDisplayed={isNameDisplayed} expanderHandler={expanderHandler} />
        <AnimatePresence>
            {children &&
                <motion.div
                    id={generateFacetGroupIdentifier(group)}
                    className="facet-group__content"
                    initial="collapsed"
                    animate="open"
                    exit="collapsed"
                    transition={{ duration: 0.2, ease: 'easeInOut' }}
                    variants={{
                        open: { height: 'auto' },
                        collapsed: { height: 0 },
                    }}
                >
                    {children}
                </motion.div>
            }
        </AnimatePresence>
    </div>
);

FacetGroup.propTypes = {
    /** facet_group definition from schema */
    group: PropTypes.object.isRequired,
    /** True if group appears expanded */
    isExpanded: PropTypes.bool.isRequired,
    /** True to display the schema name below the title */
    isNameDisplayed: PropTypes.bool.isRequired,
    /** Called to handle clicks in the group title */
    expanderHandler: PropTypes.func.isRequired,
    /** Children to render inside the group */
    children: PropTypes.node,
};

FacetGroup.defaultProps = {
    children: null,
};