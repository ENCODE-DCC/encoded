import React from 'react';
import PropTypes from 'prop-types';
import _ from 'underscore';
import { collapseIcon } from '../libs/svg-icons';
import { Panel } from '../libs/bootstrap/panel';

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
//   * options.except (string): @id to *not* make into a link in the detail text
//   * options.forcedEditLink (boolean): `true` to make the `except` string a link anyway


// Display an audit icon. This normally gets displayed within the audit indicator button, but it
// doesn't rely on much so you could use it anywhere you want to display the icon associated with
// the audit with the level passed in the `level` property.
export class AuditIcon extends React.Component {
    render() {
        const { level, addClasses } = this.props;
        const levelName = level.toLowerCase();
        const iconClass = `icon audit-activeicon-${levelName}${addClasses ? ` ${addClasses}` : ''}`;

        return <i className={iconClass}><span className="sr-only">Audit {levelName}</span></i>;
    }
}

AuditIcon.propTypes = {
    level: PropTypes.string.isRequired, // Level name from an audit object
    addClasses: PropTypes.string, // CSS classes to add to default
};

AuditIcon.defaultProps = {
    addClasses: '',
};


// Display details text with embedded links. This gets displayed in each row of the audit details.
class DetailEmbeddedLink extends React.Component {
    render() {
        const { detail } = this.props;

        // Get an array of all paths in the detail string, if any.
        const matches = detail.match(/([^a-z0-9]|^)(\/.*?\/.*?\/)(?=[\t \n,.]|$)/gmi);
        if (matches) {
            // Build React object of text followed by path for all paths in detail string
            let lastStart = 0;
            const result = matches.map((match) => {
                let preMatchedChar = '';
                const linkStart = detail.indexOf(match, lastStart);
                const preText = detail.slice(lastStart, linkStart);
                lastStart = linkStart + match.length;
                const linkText = detail.slice(linkStart, lastStart);
                if (linkText[0] !== '/') {
                    preMatchedChar = linkText[0];
                }
                if (match !== this.props.except || this.props.forcedEditLink) {
                    return <span key={linkStart}>{preText}{preMatchedChar}<a href={linkText}>{linkText}</a></span>;
                }
                return <span key={linkStart}>{preText}{preMatchedChar}{linkText}</span>;
            });

            // Pick up any trailing text after the last path, if any
            const postText = detail.slice(lastStart);

            // Render all text and paths, plus the trailing text
            return <span>{result}{postText}</span>;
        }

        // No links in the detail string; just display it with no links
        return <span>{detail}</span>;
    }
}

DetailEmbeddedLink.propTypes = {
    detail: PropTypes.string.isRequired, // Test to display in each audit's detail, possibly containing @ids that this component turns into links automatically
    except: PropTypes.string, // @id of object being reported on. Specifying it here prevents it from being converted to a link in the `detail` text
    forcedEditLink: PropTypes.bool, // `true` to display the `except` path as a link anyway
};

DetailEmbeddedLink.defaultProps = {
    except: '',
    forcedEditLink: false,
};


class AuditGroup extends React.Component {
    constructor() {
        super();
        this.state = { detailOpen: false };
        this.detailSwitch = this.detailSwitch.bind(this);
    }

    detailSwitch() {
        // Click on the detail disclosure triangle
        this.setState({ detailOpen: !this.state.detailOpen });
    }

    render() {
        const { group, except, auditLevelName, forcedEditLink } = this.props;
        const level = auditLevelName.toLowerCase();
        const { detailOpen } = this.state;
        const alertClass = `audit-detail-${level}`;
        const alertItemClass = `panel-collapse collapse audit-item-${level}${detailOpen ? ' in' : ''}`;
        const iconClass = `icon audit-icon-${level}`;
        const categoryName = group[0].category.uppercaseFirstChar();

        return (
            <div className={alertClass}>
                <div className={`icon audit-detail-trigger-${level}`}>
                    <button onClick={this.detailSwitch} className="collapsing-title">
                        {collapseIcon(!detailOpen)}
                    </button>
                </div>
                <div className="audit-detail-info">
                    <i className={iconClass} />
                    <strong>&nbsp;{categoryName}</strong>
                    <div className="btn-info-audit">
                        <a href={`/data-standards/audits/#${categoryName.toLowerCase().split(' ').join('_')}`} title={`View description of ${categoryName} in a new tab`} rel="noopener noreferrer" target="_blank"><i className="icon icon-question-circle" /></a>
                    </div>
                </div>
                <div className="audit-details-section">
                    <div className="audit-details-decoration" />
                    {group.map((audit, i) =>
                        <div className={alertItemClass} key={i} role="alert">
                            <DetailEmbeddedLink detail={audit.detail} except={except} forcedEditLink={forcedEditLink} />
                        </div>,
                    )}
                </div>
            </div>
        );
    }
}

AuditGroup.propTypes = {
    group: PropTypes.array.isRequired, // Array of audits in one name/category
    auditLevelName: PropTypes.string.isRequired, // Audit level name
    except: PropTypes.string, // @id of object whose audits are being displayed.
    forcedEditLink: PropTypes.bool, // `true` to display the `except` path as a link anyway
};

AuditGroup.defaultProps = {
    except: '',
    forcedEditLink: false,
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

    return (audits && Object.keys(audits).length) && (loggedIn || !(Object.keys(audits).length === 1 && audits.INTERNAL_ACTION));
}


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
        const { session, search } = options || {};
        const loggedIn = !!(session && session['auth.userid']);

        if (auditsDisplayed(audits, session)) {
            // Sort the audit levels by their level number, using the first element of each warning
            // category.
            const sortedAuditLevels = _(Object.keys(audits)).sortBy(level => -audits[level][0].level);

            // Calculate the class of the indicator button based on whether the audit detail panel
            // is open or not.
            const indicatorClass = `audit-indicators btn btn-info${this.state.auditDetailOpen ? ' active' : ''}${search ? ' audit-search' : ''}`;

            return (
                <button className={indicatorClass} aria-label="Audit indicators" aria-expanded={this.state.auditDetailOpen} aria-controls={id} onClick={this.toggleAuditDetail}>
                    {sortedAuditLevels.map((level) => {
                        if (loggedIn || level !== 'INTERNAL_ACTION') {
                            // Calculate the CSS class for the icon
                            const levelName = level.toLowerCase();
                            const btnClass = `btn-audit btn-audit-${levelName} audit-level-${levelName}`;
                            const groupedAudits = _(audits[level]).groupBy('category');

                            return (
                                <span className={btnClass} key={level}>
                                    <AuditIcon level={level} />
                                    {Object.keys(groupedAudits).length}
                                </span>
                            );
                        }
                        return null;
                    })}
                </button>
            );
        }

        // No audits provided.
        return null;
    }

    auditDetail(audits, id, options) {
        const { except, forcedEditLink, session } = options || {};
        if (audits && this.state.auditDetailOpen) {
            // Sort the audit levels by their level number, using the first element of each warning
            // category.
            const sortedAuditLevelNames = _(Object.keys(audits)).sortBy(level => -audits[level][0].level);
            const loggedIn = session && session['auth.userid'];

            // First loop by audit level, then by audit group
            return (
                <Panel addClasses="audit-details" id={id.replace(/\W/g, '')} aria-hidden={!this.state.auditDetailOpen}>
                    {sortedAuditLevelNames.map((auditLevelName) => {
                        if (loggedIn || auditLevelName !== 'INTERNAL_ACTION') {
                            const audit = audits[auditLevelName];

                            // Group audits within a level by their category ('name' corresponds to
                            // 'category' in a more machine-like form)
                            const groupedAudits = _(audit).groupBy('category');

                            return Object.keys(groupedAudits).map(groupName =>
                                <AuditGroup
                                    group={groupedAudits[groupName]}
                                    groupName={groupName}
                                    auditLevelName={auditLevelName}
                                    except={except}
                                    forcedEditLink={forcedEditLink}
                                    key={groupName}
                                />,
                            );
                        }
                        return null;
                    })}
                </Panel>
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
