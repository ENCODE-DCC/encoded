import React from 'react';
import PropTypes from 'prop-types';
import _ from 'underscore';
import { collapseIcon } from '../libs/svg-icons';
import * as globals from './globals';

// This module supports the display of an object's audits in the form of an indicator button that
// shows a summary of the categories of audits in the current object. Currently, we have four
// categories: ERROR, NOT_COMPLIANT, WARNING, and INTERNAL_ACTION. This module needs no
// modification if we change the number or meanings of audit categories though. Clicking the button
// causes a panel of audit details to appear. It contains one row per audit type -- basically
// groupings of audits of the same kind. The left of each audit detail row has a disclosure icon.
// Clicking that reveals details of individual audits.
//
// This module hides all that functionality into two rendering functions that the modules using
// this audit module place into their rendering code wherever they want them to appear: one
// function to render the audit indicator button, and one to render the audit details panel.
//
// To add this functionality to existing ENCODE object rendering modules, they have to import this
// module's audit component function, auditDecor:
//
// import { auditDecor } from './audit';
//
// As its name might imply, this function acts as a decorator on your existing object rendering
// modules. Wrapping your modules in this component gives your module the ability to display its
// audits. As an example, if you have a component that can have audits called `Blaine`, we change
// the name of that component to something non-conflicting. In ENCODE, we use the standard of
// adding `Component` to the module name, then make the real module name the result of the audit
// decorator, like:
//
//     class BlaineComponent extends React.Component {
//         ...
//     }
//
//     class Blaine = auditDecor(BlaineComponent);
//
//     <Blaine />
//
// The two audit rendering components get added to the wrapped component's properties, so they also
// have to add them to their propTypes. The two functions are called auditIndicators and
// auditDetail:
//
//     BlaineComponent.propTypes = {
//         ...
//         blaineData: PropTypes.object,
//         auditIndicators: PropTypes.func,
//         auditDetail: PropTypes.func,
//         ...
//     };
//
// Finally, to insert the indicator and detail rendering components into the wrapped component's
// render function, just call these functions, e.g.:
//
//     render() {
//         const { auditIndicators, auditDetail } = this.props;
//         return (
//             ...
//             <h1>Blaine Fitzgerald</h1>
//             {auditIndicators(...)}
//             <div />
//             {auditDetail(...)}
//             <span />
//             ...
//         );
//     }
//
// These are the parameters needed/allowed by these two functions:
//
// auditIndicators
// ---------------
// * audits (Required object): the `audit` object from the wrapped component's object data.
//
// * id (Required string): Arbitrary text used for to identify the button/panel accessibility
// arias. ENCODE has the standard of the lowercase wrapped component name and `-audit`. In the
// above example, that would be `blaine-audit`.
//
// * options (Optional object):
//   * options.session (object): session object from app context
//   * options.search (boolean): `true` if audit displayed on a search result page, so styling's
//                               different
//
// auditDetail
// -----------
// * audits (Required object): the `audit` object from the wrapped component's object data.
//
// * id (Required string): Arbitrary text used for to identify the button/panel accessibility
//                         arias. ENCODE has the standard of the lowercase wrapped component name
//                         and `-audit`. In the above example, that would be `blaine-audit`.
//
// * options (Optional object):
//   * options.session (object): session object from app context


// Display an audit icon. This normally gets displayed within the audit indicator button, but it
// doesn't rely on much so you could use it anywhere you want to display the icon associated with
// the audit with the level passed in the `level` property.
/* eslint-disable react/prefer-stateless-function */
export class AuditIcon extends React.Component {
    render() {
        const { level, addClasses } = this.props;
        const levelName = level.toLowerCase();
        const iconClass = `icon audit-activeicon-${levelName}${addClasses ? ` ${addClasses}` : ''}`;

        return <i className={iconClass}><span className="sr-only">Audit {levelName}</span></i>;
    }
}
/* eslint-enable react/prefer-stateless-function */

AuditIcon.propTypes = {
    level: PropTypes.string.isRequired, // Level name from an audit object
    addClasses: PropTypes.string, // CSS classes to add to default
};

AuditIcon.defaultProps = {
    addClasses: '',
};


/**
 * Display the audit icon for the highest audit level for the given object.
 */
export const ObjectAuditIcon = ({ object, audit, isAuthorized }) => {
    if (audit !== null) {
        let highestAuditLevel;
        const objectAudit = audit || object.audit;

        if (objectAudit) {
            const sortedAuditLevels = _(Object.keys(objectAudit)).sortBy(level => -objectAudit[level][0].level);

            // Only authorized users should see ambulance icon (INTERNAL_ACTION)
            highestAuditLevel = !isAuthorized && sortedAuditLevels[0] === 'INTERNAL_ACTION' ? 'OK' : sortedAuditLevels[0];
        } else {
            highestAuditLevel = 'OK';
        }
        return <AuditIcon level={highestAuditLevel} addClasses="audit-status" />;
    }
    return null;
};

ObjectAuditIcon.propTypes = {
    /** Object whose audit we display */
    object: PropTypes.object.isRequired,
    /** Audit object when `object` has none; null to suppress display */
    audit: PropTypes.object,
    /** True if user is authorized in */
    isAuthorized: PropTypes.bool,
};

ObjectAuditIcon.defaultProps = {
    audit: undefined,
    isAuthorized: false,
};


// Regex to find a simplified markdown in the form "{link text|path}"
const markdownRegex = /{(.+?)\|(.+?)}/g;


/**
 * Display details text with embedded links. This gets displayed in each row of the audit details.
 * Links, if they exist in the `detail` text, must be formatted in this form:
 * {link text|URI}
 */
const DetailEmbeddedLink = ({ detail }) => {
    let linkMatches = markdownRegex.exec(detail);
    if (linkMatches) {
        // `detail` has at least one "markdown" sequence, so treat the whole thing as marked-down
        // text. Each loop iteration finds each markdown sequence. That gets broken into the
        // non-link text before the link and then the link itself.
        const renderedDetail = [];
        let segmentIndex = 0;
        while (linkMatches) {
            const linkText = linkMatches[1];
            const linkPath = linkMatches[2];
            const preText = detail.substring(segmentIndex, linkMatches.index);
            renderedDetail.push(preText ? <span key={segmentIndex}>{preText}</span> : null, <a href={linkPath} key={linkMatches.index}>{linkText}</a>);
            segmentIndex = linkMatches.index + linkMatches[0].length;
            linkMatches = markdownRegex.exec(detail);
        }

        // Lastly, render any non-link text after the last link.
        const postText = detail.substring(segmentIndex, detail.length);
        return renderedDetail.concat(postText ? <span key={segmentIndex}>{postText}</span> : null);
    }
    return detail;
};

DetailEmbeddedLink.propTypes = {
    /** Audit detail text containing formatted links */
    detail: PropTypes.string.isRequired,
};


class AuditGroup extends React.Component {
    constructor() {
        super();
        this.state = { detailOpen: false };
        this.detailSwitch = this.detailSwitch.bind(this);
    }

    detailSwitch() {
        // Click on the detail disclosure triangle
        this.setState(prevState => (
            ({ detailOpen: !prevState.detailOpen })
        ));
    }

    render() {
        const { group, auditLevelName } = this.props;
        const level = auditLevelName.toLowerCase();
        const { detailOpen } = this.state;
        const alertClass = `audit-detail__${level}`;
        const alertItemClass = `audit-item-${level}`;
        const iconClass = `icon audit-icon-${level}`;
        const categoryName = group[0].category.uppercaseFirstChar();

        return (
            <div className={alertClass}>
                <div className="audit-detail__summary">
                    <div className={`icon audit-detail__trigger--${level}`}>
                        <button onClick={this.detailSwitch} className="collapsing-title">
                            {collapseIcon(!detailOpen)}
                        </button>
                    </div>
                    <div className="audit-detail__info">
                        <i className={iconClass} />
                        <strong>&nbsp;{categoryName}</strong>
                        <div className="btn-info-audit">
                            <a href={`/data-standards/audits/#${categoryName.toLowerCase().split(' ').join('_')}`} title={`View description of ${categoryName} in a new tab`} rel="noopener noreferrer" target="_blank"><i className="icon icon-info-circle" /></a>
                        </div>
                    </div>
                </div>
                {this.state.detailOpen ?
                    <div className="audit-details-section">
                        <div className="audit-details-decoration" />
                        {group.map((audit, i) =>
                            <div className={alertItemClass} key={i} role="alert">
                                <DetailEmbeddedLink detail={audit.detail} />
                            </div>
                        )}
                    </div>
                : null}
            </div>
        );
    }
}

AuditGroup.propTypes = {
    group: PropTypes.array.isRequired, // Array of audits in one name/category
    auditLevelName: PropTypes.string.isRequired, // Audit level name
};


// Determine whether audits should be displayed or not, given the audits object from a data object,
// and an optional session to determine logged-in state. It follows this logic:
//
// if audits exist
//     if logged out
//         if only one audit level and it's INTERNAL_ACTION
//             return do display audits
//         return don't display audits
//     return do display audits
// return don't display audits
export function auditsDisplayed(audits, session) {
    const loggedIn = !!(session && session['auth.userid']);

    return (audits && Object.keys(audits).length > 0) && (loggedIn || !(Object.keys(audits).length === 1 && audits.INTERNAL_ACTION));
}


/**
 * Display a summary of audit levels and their counts. Useful in audit buttons.
 */
export const AuditCounts = ({ audits, useWrapper, isAuthorized }) => {
    // Sort the audit levels by their level number, using the first element of each warning
    // category.
    if (audits && Object.keys(audits).length > 0) {
        const sortedAuditLevels = _(Object.keys(audits)).sortBy(level => -audits[level][0].level);
        const auditCountsContent = (
            sortedAuditLevels.map((level) => {
                if (isAuthorized || level !== 'INTERNAL_ACTION') {
                    // Calculate the CSS class for the icon.
                    const levelName = level.toLowerCase();
                    const btnClass = `audit-counts__level audit-counts__level--${levelName}`;
                    const groupedAudits = _(audits[level]).groupBy('category');
                    return (
                        <span className={btnClass} key={level}>
                            <AuditIcon level={level} />
                            {Object.keys(groupedAudits).length}
                        </span>
                    );
                }
                return null;
            })
        );

        // Render components surrounded by a default wrapper div.
        if (useWrapper) {
            return (
                <div className="audit-counts">
                    {auditCountsContent}
                </div>
            );
        }

        // Render components so that the parent component can provide the wrapper.
        return auditCountsContent;
    }
    return null;
};

AuditCounts.propTypes = {
    /** Audit object from any encode object that has audits */
    audits: PropTypes.object,
    /** True to wrap counts in a div with appropriate CSS class; false if taken care of outside */
    useWrapper: PropTypes.bool,
    /** True if user is authorized to view */
    isAuthorized: PropTypes.bool,
};

AuditCounts.defaultProps = {
    audits: null,
    useWrapper: true,
    isAuthorized: false,
};


// Audit decorator function. For any component that displays audits, pass this component as the
// parameter to this function. This decorator returns a component that's the original component
// plus the audit rendering functions. These functions get added to the original component's
// properties. See the documentation at the top of this file for details.
export const auditDecor = AuditComponent => class extends React.Component {
    constructor() {
        super();
        this.state = { auditDetailOpen: false };
        this.toggleAuditDetail = this.toggleAuditDetail.bind(this);
        this.auditIndicators = this.auditIndicators.bind(this);
        this.auditDetail = this.auditDetail.bind(this);
    }

    toggleAuditDetail() {
        this.setState(prevState => ({ auditDetailOpen: !prevState.auditDetailOpen }));
    }

    auditIndicators(audits, id, options) {
        const { session, search, sessionProperties } = options || {};
        const roles = globals.getRoles(sessionProperties);
        const isAuthorized = ['admin', 'submitter'].some(role => roles.includes(role));

        if (auditsDisplayed(audits, session)) {
            // Calculate the class of the indicator button based on whether the audit detail panel
            // is open or not.
            const indicatorClass = `audit-indicators btn btn-sm${this.state.auditDetailOpen ? ' active' : ''}${search ? ' audit-search' : ''}`;
            const auditItems = Object.keys(audits);

            // special case for unauthorized users
            if (!isAuthorized && auditItems.length === 1 && auditItems[0] === 'INTERNAL_ACTION') {
                return null;
            }

            return (
                <button className={indicatorClass} aria-label="Audit indicators" aria-expanded={this.state.auditDetailOpen} aria-controls={id} onClick={this.toggleAuditDetail}>
                    <AuditCounts audits={audits} useWrapper={false} isAuthorized={isAuthorized} />
                </button>
            );
        }

        // No audits provided.
        return null;
    }

    auditDetail(audits, id, options) {
        const { sessionProperties } = options || {};
        if (audits && this.state.auditDetailOpen) {
            // Sort the audit levels by their level number, using the first element of each warning
            // category.
            const sortedAuditLevelNames = _(Object.keys(audits)).sortBy(level => -audits[level][0].level);
            const roles = globals.getRoles(sessionProperties);
            const isAuthorized = ['admin', 'submitter'].some(role => roles.includes(role));

            // First loop by audit level, then by audit group
            return (
                <div className="audit-detail" id={id.replace(/\W/g, '')} aria-hidden={!this.state.auditDetailOpen}>
                    {sortedAuditLevelNames.map((auditLevelName) => {
                        if (isAuthorized || auditLevelName !== 'INTERNAL_ACTION') {
                            const audit = audits[auditLevelName];

                            // Group audits within a level by their category ('name' corresponds to
                            // 'category' in a more machine-like form)
                            const groupedAudits = _(audit).groupBy('category');

                            return Object.keys(groupedAudits).map(groupName =>
                                <AuditGroup
                                    group={groupedAudits[groupName]}
                                    groupName={groupName}
                                    auditLevelName={auditLevelName}
                                    key={groupName}
                                />
                            );
                        }
                        return null;
                    })}
                </div>
            );
        }
        return null;
    }

    render() {
        return (
            <AuditComponent
                {...this.props}
                auditIndicators={this.auditIndicators}
                auditDetail={this.auditDetail}
            />
        );
    }
};
