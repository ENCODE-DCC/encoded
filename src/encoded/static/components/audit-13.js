import React from 'react';
import shortid from 'shortid';
import _ from 'underscore';
import { collapseIcon } from '../libs/svg-icons';
import { Panel } from '../libs/bootstrap/panel';

// This 

// Display an audit icon within the audit indicator button. The type of icon depends on the given
// audit level.
class AuditIcon extends React.Component {
    render() {
        const { level, addClasses } = this.props;
        const levelName = level.toLowerCase();
        const iconClass = `icon audit-activeicon-${levelName}${addClasses ? ` ${addClasses}` : ''}`;

        return <i className={iconClass}><span className="sr-only">Audit {levelName}</span></i>;
    }
}

AuditIcon.propTypes = {
    level: React.PropTypes.string.isRequired, // Level name from an audit object
    addClasses: React.PropTypes.string, // CSS classes to add to default
};

AuditIcon.defaultProps = {
    addClasses: '',
};


// Display details text with embedded links. This gets displayed in each row of the audit details.
class DetailEmbeddedLink extends React.Component {
    render() {
        const { detail } = this.props;

        // Get an array of all paths in the detail string, if any.
        const matches = detail.match(/(\/.*?\/.*?\/)(?=[\t \n,.]|$)/gmi);
        if (matches) {
            // Build an array of React objects containing text followed by a path. In effect, the
            // detail text is broken up into pieces, with each piece ending in a @id, combined
            // with the text leading up to it. Any text following the last @id in the detail text
            // gets picked up after this loop.
            let lastStart = 0;
            const result = matches.map((match) => {
                const linkStart = detail.indexOf(match, lastStart);
                const preText = detail.slice(lastStart, linkStart);
                lastStart = linkStart + match.length;
                const linkText = detail.slice(linkStart, lastStart);

                // Render the text leading up to the path, and then the path as a link.
                if (match !== this.props.except || this.props.forcedEditLink) {
                    return <span key={linkStart}>{preText}<a href={linkText}>{linkText}</a></span>;
                }

                // For the case where we have an @id not to be rendered as a link.
                return <span key={linkStart}>{preText}{linkText}</span>;
            });

            // Pick up any trailing text after the last path, if any
            const postText = detail.slice(lastStart);

            // Render all text and paths, plus the trailing text
            return <span>{result}{postText}</span>;
        }

        // No links in the detail string; just display it with no links.
        return <span>{detail}</span>;
    }
}

DetailEmbeddedLink.propTypes = {
    detail: React.PropTypes.string.isRequired, // Test to display in each audit's detail, possibly containing @ids that this component turns into links automatically
    except: React.PropTypes.string, // @id of object being reported on. Specifying it here prevents it from being converted to a link in the `detail` text
    forcedEditLink: React.PropTypes.bool, // `true` to display the `except` path as a link anyway
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
                    {group.map(audit =>
                        <div className={alertItemClass} key={audit.id} role="alert">
                            <DetailEmbeddedLink detail={audit.detail} except={except} forcedEditLink={forcedEditLink} />
                        </div>,
                    )}
                </div>
            </div>
        );
    }
}

AuditGroup.propTypes = {
    group: React.PropTypes.array.isRequired, // Array of audits in one name/category
    auditLevelName: React.PropTypes.string.isRequired, // Audit level name
    except: React.PropTypes.string, // @id of object whose audits are being displayed.
    forcedEditLink: React.PropTypes.bool, // `true` to display the `except` path as a link anyway
};

AuditGroup.defaultProps = {
    except: '',
    forcedEditLink: false,
};


function idAudits(audits) {
    Object.keys(audits).forEach((auditType) => {
        const typeAudits = audits[auditType];
        typeAudits.forEach((audit) => {
            audit.id = shortid.generate();
        });
    });
}


const auditDecor = AuditComponent => class extends React.Component {
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
        const { session, search } = options ? options : {};
        const loggedIn = session && session['auth.userid'];

        if (audits && Object.keys(audits).length) {
            // Attach unique IDs to each audit to use as React keys.
            idAudits(audits);

            // Sort the audit levels by their level number, using the first element of each warning category
            const sortedAuditLevels = _(Object.keys(audits)).sortBy(level => -audits[level][0].level);

            const indicatorClass = `audit-indicators btn btn-info${this.context.auditDetailOpen ? ' active' : ''}${search ? ' audit-search' : ''}`;
            if (loggedIn || !(sortedAuditLevels.length === 1 && sortedAuditLevels[0] === 'INTERNAL_ACTION')) {
                return (
                    <button className={indicatorClass} aria-label="Audit indicators" aria-expanded={this.context.auditDetailOpen} aria-controls={id} onClick={this.toggleAuditDetail}>
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

            // Logged out and the only audit level is DCC action, so don't show a button
            return null;
        }

        // No audits provided.
        return null;
    }

    auditDetail(audits, except, id, forcedEditLink, session) {
        if (audits && this.state.auditDetailOpen) {
            // Sort the audit levels by their level number, using the first element of each warning category
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

export default auditDecor;
