import React from 'react';
import PropTypes from 'prop-types';
import * as globals from './globals';


// objectStatuses holds all possible statuses for each kind of object at the different logged-in
// levels. These must be kept in sync with statuses defined in each object's schema. Each top-level
// property has a name matching the @type of each kind of object. Within that property are objects of
// arrays; each array defining the statuses available at each logged-in level represented by that
// object.
const objectStatuses = {
    Experiment: {
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
        admin: [
            'deleted',
            'replaced',
        ],
    },
};


// Defines the order of the viewing access of the different logged-in states, and has to match the
// order of arrays in each @type property in `objectStatuses`.
const objectStatusLevelOrder = ['external', 'consortium', 'admin'];


/**
 * Given an object @id and login level, get an array of all possible statuses for that object at
 * that login level.
 *
 * @param {string} objectType - Retrieve possible statuses for this @type.
 * @param {string} level - Level of statuses to get (external, consortium, admin). If nothing is
 *         passed in this parameter, then 'admin' is assumed.
 * @return (array) - Returns array of possible statuses for the given object and access level.
 */
export function getObjectStatuses(objectType, level = 'admin') {
    const maxLevelIndex = objectStatusLevelOrder.indexOf(level);
    const objectStatusGroups = objectStatuses[objectType];
    if (maxLevelIndex !== -1 && objectStatusGroups) {
        let statuses = [];
        for (let levelIndex = 0; levelIndex <= maxLevelIndex; levelIndex += 1) {
            statuses = statuses.concat(objectStatusGroups[objectStatusLevelOrder[levelIndex]]);
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
