import React from 'react';
import PropTypes from 'prop-types';
import * as globals from './globals';


// `objectStatuses` holds all possible statuses for each kind of object at the different logged-in
// levels. These must be kept in sync with statuses defined in each object's schema. Each top-level
// property has a name matching the @type of each kind of object. Within that property are objects of
// arrays; each array defining the statuses available at each logged-in level represented by that
// object.

// Many objects defined in the schemas use statuses from mixins.json. The following objects match
// those mixed-in statuses to reduce repetition and memory.

const accessionedStatuses = {
    external: [
        'released',
        'revoked',
    ],
    consortium: [
        'in progress',
    ],
    administrator: [
        'deleted',
        'replaced',
    ],
};

const datasetStatuses = {
    external: [
        'released',
        'archived',
        'revoked',
    ],
    consortium: [
        'in progress',
        'submitted',
    ],
    administrator: [
        'deleted',
        'replaced',
    ],
};

const sharedStatuses = {
    external: [
        'current',
    ],
    administrator: [
        'deleteed',
        'disabled',
    ],
};

const standardStatuses = {
    external: [
        'released',
    ],
    consortium: [
        'in progress',
    ],
    administrator: [
        'deleted',
    ],
};

// If a base object and its derivatives share the same statuses, only the base object needs an
// entry here, e.g. Experiments share the same statuses as the Datasets they derive from, so only
// `Dataset` is needed here.
const objectStatuses = {
    AccessKey: {
        external: [
            'current',
        ],
        administrator: [
            'deleted',
        ],
    },
    AnalysisStepRun: standardStatuses,
    AnalysisStepVersion: standardStatuses,
    AnalysisStep: standardStatuses,
    AntibodyCharacterization: {
        external: [
            'compliant',
            'exempt from standards',
            'not compliant',
            'not reviewed',
            'not submitted for review by lab',
        ],
        consortium: [
            'in progress',
            'pending dcc review',
        ],
        administrator: [
            'deleted',
        ],
    },
    AntibodyLot: accessionedStatuses,
    Award: sharedStatuses,
    BiosampleCharacterization: standardStatuses,
    Biosample: accessionedStatuses,
    Characterization: standardStatuses,
    Dataset: datasetStatuses,
    Document: standardStatuses,
    Donor: accessionedStatuses,
    File: {
        external: [
            'released',
            'archived',
            'revoked',
        ],
        consortium: [
            'in progress',
            'uploading',
            'upload failed',
            'content error',
        ],
        administrator: [
            'deleted',
            'replaced',
        ],
    },
    FileSet: accessionedStatuses,
    Image: standardStatuses,
    Lab: sharedStatuses,
    Library: accessionedStatuses,
    Organism: standardStatuses,
    Page: standardStatuses,
    Pipeline: {
        external: [
            'released',
            'archived',
            'revoked',
        ],
        consortium: [
            'in progress',
        ],
        administrator: [
            'deleted',
            'replaced',
        ],
    },
    Platform: standardStatuses,
    Publication: standardStatuses,
    QualityMetric: standardStatuses,
    Replicate: {
        external: [
            'released',
            'archived',
            'revoked',
        ],
        consortium: [
            'in progress',
        ],
        administrator: [
            'deleted',
        ],
    },
    Software: standardStatuses,
    SoftwareVersion: standardStatuses,
    Source: standardStatuses,
    Target: {
        external: [
            'current',
        ],
        administrator: [
            'deleted',
            'replaced',
        ],
    },
    Treatment: standardStatuses,
    User: sharedStatuses,
};


// SVG components for each status icon. These can be imported into something like Ink or Adobe
// Illustrator for modification, and saved with minificiation. You can remove some elements from
// the resulting SVG (e.g. <title>, <def>), and viewBox and transform might need adjustment.
const iconDefinitions = {
    archived: <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16"><path d="M8,4a8,8,0,0,0-8,8H16A8,8,0,0,0,8,4Z" /></svg>,
    completed: <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16"><path d="M8,0a8,8,0,1,0,8,8A8,8,0,0,0,8,0ZM8,14.17A6.17,6.17,0,1,1,14.17,8,6.17,6.17,0,0,1,8,14.17ZM8,3.75A4.25,4.25,0,1,0,12.25,8,4.25,4.25,0,0,0,8,3.75Z" /></svg>,
    deleted: <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16"><polygon points="8 0 16 13 0 13 8 0" transform="translate(0 1.5)" /></svg>,
    disabled: <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16"><path d="M14.62,3.5l-1.1,1.1a6.44,6.44,0,0,1,0,6.8l1.1,1.1a8,8,0,0,0,0-9ZM1.38,3.5a8,8,0,0,0,0,9l1.1-1.1a6.44,6.44,0,0,1,0-6.8ZM3.5,1.38l1.1,1.1a6.44,6.44,0,0,1,6.8,0l1.1-1.1a8,8,0,0,0-9,0ZM8,14.49a6.45,6.45,0,0,1-3.4-1l-1.1,1.1a8,8,0,0,0,9,0l-1.1-1.1A6.45,6.45,0,0,1,8,14.49Z" /></svg>,
    empty: <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16"><path d="M8,0a8,8,0,1,0,8,8A8,8,0,0,0,8,0ZM8,14.17A6.17,6.17,0,1,1,14.17,8,6.17,6.17,0,0,1,8,14.17Z" /></svg>,
    error: <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16"><path d="M8,0a8,8,0,1,0,8,8A8,8,0,0,0,8,0ZM8,14.17A6.17,6.17,0,1,1,14.17,8,6.17,6.17,0,0,1,8,14.17Zm2.24-9.86L8,6.55,5.76,4.31,4.31,5.76,6.55,8,4.31,10.24l1.45,1.45L8,9.45l2.24,2.24,1.45-1.45L9.45,8l2.24-2.24Z" /></svg>,
    exempt: <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16"><rect x="0.45" y="4.23" width="15.09" height="7.54" transform="translate(19.32 8) rotate(135)" /></svg>,
    inProgress: <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16"><path d="M8,16A8,8,0,1,0,0,8,8,8,0,0,0,8,16ZM8,1.83A6.17,6.17,0,0,1,8,14.17Z" /></svg>,
    notCompliant: <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16"><rect width="16" height="8" transform="translate(0 4)" /></svg>,
    notReviewed: <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16"><rect width="16" height="16" rx="3.92" ry="3.92" /></svg>,
    notSubmitted: <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16"><rect width="8" height="16" transform="translate(4 0)" /></svg>,
    released: <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16"><circle cx="8" cy="8" r="8" /></svg>,
    replaced: <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16"><path d="M8,5.88A2.13,2.13,0,1,0,10.12,8,2.12,2.12,0,0,0,8,5.88ZM8,0a8,8,0,1,0,8,8A8,8,0,0,0,8,0ZM8,12.53A4.53,4.53,0,1,1,12.53,8,4.53,4.53,0,0,1,8,12.53Z" /></svg>,
    review: <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16"><path d="M16,8a8,8,0,1,0-8,8A8,8,0,0,0,16,8ZM1.83,8A6.17,6.17,0,0,1,14.17,8Z" /></svg>,
    submitted: <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16"><path d="M8,0a8,8,0,1,0,8,8A8,8,0,0,0,8,0ZM8,12.53A4.53,4.53,0,1,1,12.53,8,4.53,4.53,0,0,1,8,12.53Z" /></svg>,
    waiting: <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16"><path d="M8,0a8,8,0,1,0,8,8A8,8,0,0,0,8,0ZM8,14.17A6.17,6.17,0,1,1,14.17,8,6.17,6.17,0,0,1,8,14.17ZM9.5,6.5v-3h-3v3h-3v3h3v3h3v-3h3v-3Z" /></svg>,
    unusuable: <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16"><path d="M8,0a8,8,0,1,0,8,8A8,8,0,0,0,8,0ZM8,14.17A6.17,6.17,0,1,1,14.17,8,6.17,6.17,0,0,1,8,14.17ZM3.5,6.5v3h9v-3Z" /></svg>,
    uploading: <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16"><path d="M0,0V16H16V0ZM14.17,14.17H8V1.83h6.17Z" /></svg>,
};

// Maps each status to the SVG icon displayed for that status.
const statusIcons = {
    // External
    released: iconDefinitions.released,
    current: iconDefinitions.released,
    compliant: iconDefinitions.released,
    'not-compliant': iconDefinitions.notCompliant,
    'not-reviewed': iconDefinitions.notReviewed,
    'not-submitted-for-review-by-lab': iconDefinitions.notSubmitted,
    'exempt-from-standards': iconDefinitions.exempt,
    archived: iconDefinitions.archived,
    revoked: iconDefinitions.error,

    // Consortium
    'in-progress': iconDefinitions.inProgress,
    'pending-dcc-review': iconDefinitions.review,
    submitted: iconDefinitions.submitted,
    uploading: iconDefinitions.uploading,
    'upload-failed': iconDefinitions.error,
    'content-error': iconDefinitions.error,

    // Administrative
    deleted: iconDefinitions.deleted,
    replaced: iconDefinitions.replaced,
    disabled: iconDefinitions.disabled,

    // internal_status
    unreviewed: iconDefinitions.notReviewed,
    'pipeline-ready': iconDefinitions.waiting,
    processing: iconDefinitions.inProgress,
    'pipeline-completed': iconDefinitions.completed,
    'release-ready': iconDefinitions.released,
    'requires-lab-review': iconDefinitions.review,
    'no-available-pipeline': iconDefinitions.empty,
    'pipeline-error': iconDefinitions.error,
    unrunnable: iconDefinitions.unusuable,

    // lot_review.status
    'awaiting-characterization': iconDefinitions.waiting,
    'characterized-to-standards': iconDefinitions.released,
    'partially-characterized': iconDefinitions.inProgress,
    'characterized-to-standards-with-exemption': iconDefinitions.completed,
    'not-characterized-to-standards': iconDefinitions.notCompliant,
    'not-pursued': iconDefinitions.notReviewed,
};


// Defines the order of the viewing access of the different logged-in states.
const objectStatusLevels = ['external', 'consortium', 'administrator'];


/**
 * Maps the current session information from the <App> React context to an access level from the
 * objectStatusLevels array.
 *
 * @param {object} session - From encoded session context
 * @param {object} sessionProperties - From encoded session_properties context
 * @return {string} - access level matching an entry in `objectStatusLevels`
 */
export const sessionToAccessLevel = (session, sessionProperties) => {
    const loggedIn = !!(session && session['auth.userid']);
    const administrativeUser = loggedIn && !!(sessionProperties && sessionProperties.admin);
    return loggedIn ? (administrativeUser ? 'administrator' : 'consortium') : 'external';
};


/**
 * Given an object or an @type and login level, get an array of all possible statuses for that
 * object at that login level. For objects, the `@type` array is searched until a type matching
 * a defined one is found. If you pass an `@type` string, then that string must have a matching
 * element in `objectStatuses`.
 *
 * @param {object,string} item - Object whose statuses we're getting, or base object type.
 * @param {string} accessLevel - Level of statuses to get (external, consortium, administrator).
 * @return {array} - Returns array of possible statuses for given object/@type and access level.
 */
export const getObjectStatuses = (item, accessLevel = 'external') => {
    // Go down the @type list for the object until a matching block is found in `objectStatuses`.
    const objectType = typeof item === 'string' ? item : item['@type'].find(type => objectStatuses[type]);

    if (objectType && objectStatuses[objectType]) {
        // To collect all possible statuses for the given `accessLevel` and item @type, concatenate
        // all `objectStatusGroups` arrays that are at the `accessLevel` and below.
        const allowedAccessLevels = objectStatusLevels.slice(0, objectStatusLevels.indexOf(accessLevel) + 1);
        if (allowedAccessLevels.length > 0) {
            return (
                Object.keys(objectStatuses[objectType]).reduce((combinedStatuses, level) => (
                    (allowedAccessLevels.indexOf(level) > -1 ? combinedStatuses.concat(objectStatuses[objectType][level]) : combinedStatuses)
                ), [])
            );
        }
    }

    // No matching block of statuses for the given item, or the given `accessLevel` isn't known.
    return [];
};


// Display an object status or a status from a string. The "released" icon gets displayed if the
// given status isn't defined.
const Status = ({ item, badgeSize, title, css, noLabel, noIcon, inline }) => {
    const status = typeof item === 'string' ? item : item.status;
    const classElement = globals.statusToClassElement(status);

    return (
        <div className={`${inline ? 'status--inline' : ''}${css ? ` ${css}` : ''}`}>
            <div className={`status status--${badgeSize} status--${classElement}`} {...(title ? { title } : {})}>
                {!noIcon ? <div className={`status__icon${!noLabel ? ' status__icon--spacer' : ''}`}>{statusIcons[classElement] || statusIcons.released}</div> : null}
                {!noLabel ? <div className="status__label">{status}</div> : null}
            </div>
        </div>
    );
};

Status.propTypes = {
    item: PropTypes.oneOfType([
        PropTypes.string,
        PropTypes.object,
    ]).isRequired, // Object with status property to display, or the status itself
    badgeSize: PropTypes.oneOf([
        'small',
        'standard',
        'large',
    ]), // Size of status label
    title: PropTypes.string, // Tooltip text
    css: PropTypes.string, // CSS classes to add to surrounding div
    noLabel: PropTypes.bool, // True to supress display of status label
    noIcon: PropTypes.bool, // True to supress display of status icon
    inline: PropTypes.bool, // True to display as CSS inline-block
};

Status.defaultProps = {
    badgeSize: 'standard',
    title: '',
    css: '',
    noLabel: false,
    noIcon: false,
    inline: false,
};

export default Status;
