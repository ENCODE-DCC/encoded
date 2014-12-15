/** @jsx React.DOM */
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
    auditStateToggle: function() {
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
        var context = this.props.context;
        var audits = context.audit;

        if (audits && audits.length) {
            // Count the errors at each level
            audits.forEach(function(audit) {
                if (auditCounts[audit.level]) {
                    auditCounts[audit.level].count++;
                } else {
                    auditCounts[audit.level] = {count: 1, level_name: audit.level_name.toLowerCase()};
                }
            });

            // Sort the audit levels by their level number
            var sortedAuditLevels = _(Object.keys(auditCounts)).sortBy(function(level) {
                return -parseInt(level, 10);
            });

            var indicatorClass = "audit-indicators btn btn-default" + (this.context.auditDetailOpen ? ' active' : '') + (this.props.search ? ' audit-search' : '');

            return (
                <button className={indicatorClass} aria-label="Audit indicators" aria-expanded={this.context.auditDetailOpen} aria-controls={this.props.key.replace(/\W/g, '')} onClick={this.context.auditStateToggle}>
                    {sortedAuditLevels.map(function(level) {
                        // Calculate the CSS class for the icon
                        var level_name = auditCounts[level].level_name;
                        var btnClass = 'btn-audit btn-audit-' + level_name + ' audit-level-' + level_name;
                        var iconClass = 'icon audit-activeicon-' + level_name;

                        return (
                            <span className={btnClass}>
                                <i className={iconClass}><span className="sr-only">{'Audit'} {level_name}</span></i>
                                {auditCounts[level].count}
                            </span>
                        );
                    }.bind(this))}
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
        var audits = context.audit;

        // Sort audit records
        var audits_sorted = _.sortBy(audits, function(audit) {
            return -audit.level;
        });

        if (audits_sorted && this.context.auditDetailOpen) {
            return (
                <div className="audit-details" id={this.props.key.replace(/\W/g, '')} aria-hidden={!this.context.auditDetailOpen}>
                    {audits_sorted.map(function(audit, i) {
                        var level = audit.level_name.toLowerCase();
                        var iconClass = 'icon audit-icon-' + level;
                        var alertClass = 'audit-detail-' + level;
                        var levelClass = 'audit-level-' + level;
                        var editLink = this.props.forceEditLink || (audit.path !== context['@id']) ? audit.path : null;
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
                                <strong className={levelClass}>{audit.level_name.split('_').join(' ')}</strong>
                                &nbsp;&mdash;&nbsp;
                                <strong>{audit.category}</strong>: {audit.detail}
                                {editLink ?
                                    <a className="audit-link" href={editLink}>Go to {editTarget}</a>
                                : null}
                            </div>
                        );
                    }, this)}
            </div>
            );
        } else {
            return null;
        }
    }
});
