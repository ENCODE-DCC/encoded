import React from 'react';
import PropTypes from 'prop-types';
import * as globals from './globals';


// objectStatuses holds all possible statuses for each kind of object at the different logged-in
// levels. These must be kept in sync with statuses defined in each object's schema. Each top-level
// property has a name matching the @type of each kind of object. Within that property are objects of
// arrays; each array defining the statuses available at each logged-in level represented by that
// object.

const datasetObjectStatuses = {
    external: [
        'released',
        'archived',
        'revoked',
    ],
    consortium: [
        'proposed',
        'started',
        'submitted',
    ],
    administrator: [
        'deleted',
        'replaced',
    ],
};

const objectStatuses = {
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
    Experiment: datasetObjectStatuses,
};


// Defines the order of the viewing access of the different logged-in states.
const objectStatusLevels = ['external', 'consortium', 'administrator'];


/**
 * Maps the current session information from the <App> React context to an access level from the
 * objectStatusLevels array.
 *
 * @param {object} session - From encoded session context
 * @param {object} sessionProperties - From encoded session_properties context
 */
export const sessionToAccessLevel = (session, sessionProperties) => {
    const loggedIn = !!(session && session['auth.userid']);
    const administrativeUser = loggedIn && !!(sessionProperties && sessionProperties.admin);
    return loggedIn ? (administrativeUser ? 'administrator' : 'consortium') : 'external';
};


/**
 * Given an object @type and login level, get an array of all possible statuses for that object at
 * that login level.
 *
 * @param {string} objectType - Retrieve possible statuses for this @type.
 * @param {string} accessLevel - Level of statuses to get (external, consortium, administrator).
 *         If nothing is passed in this parameter, then 'administrator' is assumed.
 * @return (array) - Returns array of possible statuses for the given object and access level.
 */
export function getObjectStatuses(objectType, accessLevel = 'administrator') {
    const maximumLevelIndex = objectStatusLevels.indexOf(accessLevel);
    const objectStatusGroups = objectStatuses[objectType];
    if (maximumLevelIndex !== -1 && objectStatusGroups) {
        let statuses = [];
        for (let levelIndex = 0; levelIndex <= maximumLevelIndex; levelIndex += 1) {
            statuses = statuses.concat(objectStatusGroups[objectStatusLevels[levelIndex]]);
        }
        return statuses;
    }
    return [];
}


export const StatusLabel = (props) => {
    const { status, title, buttonLabel, fileStatus } = props;

    // Handle file statuses speficially.
    if (fileStatus) {
        return (
            <ul className="status-list">
                <li className={`label file-status-${status.replace(/ /g, '-')}`}>
                    {title ? <span className="status-list-title">{`${title}: `}</span> : null}
                    {buttonLabel || status}
                </li>
            </ul>
        );
    }

    // Handle any other kind of status.
    if (typeof status === 'string') {
        // Display simple string and optional title in badge
        return (
            <ul className="status-list">
                <li className={globals.statusClass(status, 'label')}>
                    {title ? <span className="status-list-title">{`${title}: `}</span> : null}
                    {buttonLabel || status}
                </li>
            </ul>
        );
    } else if (typeof status === 'object') {
        // Display a list of badges from array of objects with status and optional title
        return (
            <ul className="status-list">
                {status.map(singleStatus => (
                    <li key={singleStatus.title} className={globals.statusClass(singleStatus.status, 'label')}>
                        {singleStatus.title ? <span className="status-list-title">{`${singleStatus.title}: `}</span> : null}
                        {singleStatus.status}
                    </li>
                ))}
            </ul>
        );
    }
    return null;
};

StatusLabel.propTypes = {
    status: PropTypes.oneOfType([
        PropTypes.string,
        PropTypes.array,
    ]).isRequired, // Array of status objects with status and badge title
    title: PropTypes.string,
    buttonLabel: PropTypes.string,
    fileStatus: PropTypes.bool,
};

StatusLabel.defaultProps = {
    title: '',
    buttonLabel: '',
    fileStatus: false,
};
