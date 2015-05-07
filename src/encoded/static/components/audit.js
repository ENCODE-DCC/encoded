'use strict';
var React = require('react');
var _ = require('underscore');
var cx = require('react/lib/cx');

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
    }
};


var AuditIndicators = module.exports.AuditIndicators = React.createClass({
    contextTypes: {
        auditDetailOpen: React.PropTypes.bool,
        auditStateToggle: React.PropTypes.func
    },

    render: function() {
        var auditCounts = {};
        var audits = this.props.audits;

        if (audits && Object.keys(audits).length) {
            // Sort the audit levels by their level number, using the first element of each warning category
            var sortedAuditLevels = _(Object.keys(audits)).sortBy(function(level) {
                return -audits[level][0].level;
            });

            var indicatorClass = "audit-indicators btn btn-default" + (this.context.auditDetailOpen ? ' active' : '') + (this.props.search ? ' audit-search' : '');

            return (
                <button className={indicatorClass} aria-label="Audit indicators" aria-expanded={this.context.auditDetailOpen} aria-controls={this.props.id} onClick={this.context.auditStateToggle}>
                    {sortedAuditLevels.map(function(level, i) {
                        // Calculate the CSS class for the icon
                        var levelName = level.toLowerCase();
                        var btnClass = 'btn-audit btn-audit-' + levelName + ' audit-level-' + levelName;
                        var iconClass = 'icon audit-activeicon-' + levelName;

                        return (
                            <span className={btnClass} key={i}>
                                <i className={iconClass}><span className="sr-only">{'Audit'} {levelName}</span></i>
                                {audits[level].length}
                            </span>
                        );
                    })}
                </button>
            );
        } else {
            return null;
        }
    }
});


var AuditDetail = module.exports.AuditDetail = React.createClass({
    contextTypes: {
        auditDetailOpen: React.PropTypes.bool
    },

    render: function() {
        var context = this.props.context;
        var auditLevels = context.audit;

        if (this.context.auditDetailOpen) {
            // Sort the audit levels by their level number, using the first element of each warning category
            var sortedAuditLevelNames = _(Object.keys(auditLevels)).sortBy(function(level) {
                return -auditLevels[level][0].level;
            });

            return (
                <div className="audit-details" id={this.props.id.replace(/\W/g, '')} aria-hidden={!this.context.auditDetailOpen}>
                    {sortedAuditLevelNames.map(function(auditLevelName) {
                        var audits = auditLevels[auditLevelName];
                        var level = auditLevelName.toLowerCase();
                        var iconClass = 'icon audit-icon-' + level;
                        var alertClass = 'audit-detail-' + level;
                        var levelClass = 'audit-level-' + level;

                        return audits.map(function(audit, i) {
                            var editLink = (this.props.forcedEditLink || (audit.path !== context['@id'])) ? audit.path : null;
                            var editTarget;

                            // Get the target string from the path
                            if (editLink) {
                                var start = audit.path.indexOf('/') + 1;
                                var end = audit.path.indexOf('/', start);
                                var editTargetType = audit.path.substring(start, end);
                                editTarget = editTargetMap[editTargetType];
                            }
                            return (
                                <div className={alertClass} key={i} role="alert">
                                    <i className={iconClass}></i>
                                    <strong className={levelClass}>{auditLevelName.split('_').join(' ')}</strong>
                                    &nbsp;&mdash;&nbsp;
                                    <strong>{audit.category}</strong>: {audit.detail}
                                    {editLink ?
                                        <a className="audit-link" href={editLink}>Go to {editTarget}</a>
                                    : null}
                                </div>
                            );
                        }, this);
                    }, this)}
                </div>
            );
        }
        return null;
    }
});
