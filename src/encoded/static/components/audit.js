'use strict';
var React = require('react');
var _ = require('underscore');
var {Panel} = require('../libs/bootstrap/panel');
var { collapseIcon } = require('../libs/svg-icons');

var editTargetMap = {
    'experiments': 'Experiment',
    'antibodies': 'Antibody',
    'antibody-characterizations': 'Antibody Characterization',
    'biosamples': 'Biosample',
    'documents': 'Document',
    'libraries': 'Library',
    'files': 'File',
    'labs': 'Lab',
    'platform': 'Platform',
    'targets': 'Target',
    'datasets': 'Dataset',
    'publications': 'Publication',
    'software': 'Software',
    'pages': 'Page',
    'awards': 'Award',
    'replicates': 'Replicate'
};

var AuditMixin = module.exports.AuditMixin = {
    childContextTypes: {
        auditDetailOpen: React.PropTypes.bool, // Audit details open
        auditStateToggle: React.PropTypes.func // Function to set current audit detail type
    },

    // Retrieve current React context
    getChildContext: function() {
        return {
            auditDetailOpen: this.state.auditDetailOpen,
            auditStateToggle: this.auditStateToggle
        };
    },

    getInitialState: function() {
        return {auditDetailOpen: false};
    },

    // React to click in audit indicator. Set state to clicked indicator's error level
    auditStateToggle: function(e) {
        e.preventDefault();
        this.setState({auditDetailOpen: !this.state.auditDetailOpen});
    },

    auditStateClosed: function() {
        this.setState({auditDetailOpen: false});
    },
};


var AuditIcon = module.exports.AuditIcon = React.createClass({
    propTypes: {
        level: React.PropTypes.string, // Level name from an audit object
        addClasses: React.PropTypes.string // CSS classes to add to default
    },

    render: function() {
        var {level, addClasses} = this.props;
        var levelName = this.props.level.toLowerCase();
        var iconClass = 'icon audit-activeicon-' + levelName + (addClasses ? ' ' + addClasses : '');

        return <i className={iconClass}><span className="sr-only">{'Audit'} {levelName}</span></i>;
    }
});


var AuditIndicators = module.exports.AuditIndicators = React.createClass({
    contextTypes: {
        auditDetailOpen: React.PropTypes.bool,
        auditStateToggle: React.PropTypes.func,
        session: React.PropTypes.object,
        hidePublicAudits: React.PropTypes.bool
    },

    render: function() {
        var auditCounts = {};
        var audits = this.props.audits;
        var loggedIn = this.context.session && this.context.session['auth.userid'];

        if ((!this.context.hidePublicAudits || loggedIn) && audits && Object.keys(audits).length) {
            // Sort the audit levels by their level number, using the first element of each warning category
            var sortedAuditLevels = _(Object.keys(audits)).sortBy(level => -audits[level][0].level);

            var indicatorClass = "audit-indicators btn btn-info" + (this.context.auditDetailOpen ? ' active' : '') + (this.props.search ? ' audit-search' : '');
            if (loggedIn || !(sortedAuditLevels.length === 1 && sortedAuditLevels[0] === 'INTERNAL_ACTION')) {
                return (
                    <button className={indicatorClass} aria-label="Audit indicators" aria-expanded={this.context.auditDetailOpen} aria-controls={this.props.id} onClick={this.context.auditStateToggle}>
                        {sortedAuditLevels.map(level => {
                            if (loggedIn || level !== 'INTERNAL_ACTION') {
                                // Calculate the CSS class for the icon
                                var levelName = level.toLowerCase();
                                var btnClass = 'btn-audit btn-audit-' + levelName + ' audit-level-' + levelName;
                                var iconClass = 'icon audit-activeicon-' + levelName;
                                var groupedAudits = _(audits[level]).groupBy('category');

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
        } else {
            return null;
        }
    }
});


var AuditDetail = module.exports.AuditDetail = React.createClass({
    propTypes: {
        audits: React.PropTypes.object, // Audit object
        except: React.PropTypes.string, // @id of object whose audits are being displayed, to prevent them from being linked to in detail messages
    },

    contextTypes: {
        auditDetailOpen: React.PropTypes.bool,
        session: React.PropTypes.object
    },

    render: function() {
        const { audits, except } = this.props;

        if (audits && this.context.auditDetailOpen) {
            // Sort the audit levels by their level number, using the first element of each warning category
            const sortedAuditLevelNames = _(Object.keys(audits)).sortBy(level => -audits[level][0].level);
            var loggedIn = this.context.session && this.context.session['auth.userid'];

            // First loop by audit level, then by audit group
            return (
                <Panel addClasses="audit-details" id={this.props.id.replace(/\W/g, '')} aria-hidden={!this.context.auditDetailOpen}>
                    {sortedAuditLevelNames.map(auditLevelName => {
                        if (loggedIn || auditLevelName !== 'INTERNAL_ACTION') {
                            var audit = audits[auditLevelName];
                            var level = auditLevelName.toLowerCase();
                            var iconClass = 'icon audit-icon-' + level;
                            var alertClass = 'audit-detail-' + level;
                            var levelClass = 'audit-level-' + level;

                            // Group audits within a level by their category ('name' corresponds to
                            // 'category' in a more machine-like form)
                            var groupedAudits = _(audit).groupBy('category');

                            return Object.keys(groupedAudits).map(groupName =>
                                <AuditGroup
                                    group={groupedAudits[groupName]}
                                    groupName={groupName}
                                    auditLevelName={auditLevelName}
                                    except={except}
                                    forcedEditLink={this.props.forcedEditLink}
                                    key={groupName}
                                />
                            );
                        }
                        return null;
                    })}
                </Panel>
            );
        }
        return null;
    }
});


var AuditGroup = module.exports.AuditGroup = React.createClass({
    propTypes: {
        group: React.PropTypes.array.isRequired, // Array of audits in one name/category
        groupName: React.PropTypes.string.isRequired, // Name of the group
        auditLevelName: React.PropTypes.string.isRequired, // Audit level
        except: React.PropTypes.string, // @id of object whose audits are being displayed.
    },

    contextTypes: {
        session: React.PropTypes.object
    },

    getInitialState: function() {
        return {detailOpen: false};
    },

    detailSwitch: function() {
        // Click on the detail disclosure triangle
        this.setState({detailOpen: !this.state.detailOpen});
    },

    render: function() {
        var { group, groupName, except } = this.props;
        var auditLevelName = this.props.auditLevelName.toLowerCase();
        var detailOpen = this.state.detailOpen;
        var alertClass = 'audit-detail-' + auditLevelName.toLowerCase();
        var alertItemClass = 'panel-collapse collapse audit-item-' + auditLevelName + (detailOpen ? ' in' : '');
        var iconClass = 'icon audit-icon-' + auditLevelName;
        var levelClass = 'audit-level-' + auditLevelName;
        var level = auditLevelName.toLowerCase();
        var categoryName = group[0].category.uppercaseFirstChar();
        var loggedIn = this.context.session && this.context.session['auth.userid'];

        return (
            <div className={alertClass}>
                <div className={'icon audit-detail-trigger-' + auditLevelName}>
                    <a href="#" data-trigger onClick={this.detailSwitch} className="collapsing-title">
                        {collapseIcon(!detailOpen)}
                    </a>
                </div>
                <div className="audit-detail-info">
                    <i className={iconClass}></i>
                    <strong>&nbsp;{categoryName}</strong>
                    <div className="btn-info-audit">
                        <a href={'/data-standards/audits/#' + categoryName.toLowerCase().split(' ').join('_')} title={'View description of ' + categoryName + ' in a new tab'} target="_blank"><i className="icon icon-question-circle"></i></a>
                    </div>
                </div>
                <div className="audit-details-section">
                    <div className="audit-details-decoration"></div>
                    {group.map((audit, i) =>
                        <div className={alertItemClass} key={i} role="alert">
                            <DetailEmbeddedLink detail={audit.detail} except={except} forcedEditLink={this.props.forcedEditLink} />
                        </div>
                    )}
                </div>
            </div>
        );
    }
});


// Display details with embedded links.
// props.detail: String possibly containing paths.
// props.except: Path of object being reported on.
// props.forcedEditLink: T if display path of reported object anyway.

var DetailEmbeddedLink = React.createClass({
    render: function() {
        var detail = this.props.detail;

        // Get an array of all paths in the detail string, if any.
        var matches = detail.match(/(\/.*?\/.*?\/)(?=[\t \n,.]|$)/gmi);
        if (matches) {
            // Build React object of text followed by path for all paths in detail string
            var lastStart = 0;
            var result = matches.map((match, i) => {
                var linkStart = detail.indexOf(match, lastStart);
                var preText = detail.slice(lastStart, linkStart);
                lastStart = linkStart + match.length;
                var linkText = detail.slice(linkStart, lastStart);
                if (match !== this.props.except || this.props.forcedEditLink) {
                    return <span key={i}>{preText}<a href={linkText}>{linkText}</a></span>;
                } else {
                    return <span key={i}>{preText}{linkText}</span>;
                }
            });

            // Pick up any trailing text after the last path, if any
            var postText = detail.slice(lastStart);
            
            // Render all text and paths, plus the trailing text
            return <span>{result}{postText}</span>;
        } else {
            // No links in the detail string; just display it with no links
            return <span>{detail}</span>;
        }
    }
});
