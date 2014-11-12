/** @jsx React.DOM */
'use strict';
var React = require('react');
var _ = require('underscore');
var cx = require('react/lib/cx');

var AuditMixin = module.exports.AuditMixin = {
    childContextTypes: {
        auditDetailOpen: React.PropTypes.bool,
        auditStateToggle: React.PropTypes.func
    },

    // Retrieve current React context
    getChildContext: function() {
        return {
            auditDetailOpen: this.state.auditDetailOpen, // True if audit details visible
            auditStateToggle: this.auditStateToggle // Function to process clicks in audit indicators
        };
    },

    getInitialState: function() {
        return {auditDetailOpen: false};
    },

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
        var auditCounts = {}  ;
        var audits = this.props.audits;

        // Count the errors at each level, then sort the keys by level
        audits.forEach(function(audit) {
            if (auditCounts[audit.level]) {
                auditCounts[audit.level].count++;
            } else {
                auditCounts[audit.level] = {count: 1, level_name: audit.level_name.toLowerCase()};
            }
        });
        var sortedAuditKeys = _(Object.keys(auditCounts)).sortBy(function(key) {
            return -key;
        });

        return (
            <div className="btn-group audit-indicators">
                {sortedAuditKeys.map(function(level) {
                    // Calculate the CSS class for the icon
                    var btnClass = 'btn btn-audit-' + auditCounts[level].level_name;
                    var iconClass = 'icon audit-activeicon-' + auditCounts[level].level_name;

                    return (
                        <button type="button" className={btnClass}>
                            <i className={iconClass}><span className="sr-only">{'Audit'} {auditCounts[level].level_name}</span></i>
                            {auditCounts[level].count}
                        </button>
                    );
                })}
            </div>
        );
    }
});


var AuditDetail = module.exports.AuditDetail = React.createClass({
    contextTypes: {
        auditDetailOpen: React.PropTypes.bool,
        auditStateToggle: React.PropTypes.func
    },

    render: function() {
        var audits = this.props.audits;

        // Sort audit records
        var audits_sorted = _.sortBy(audits, function(audit) {
            return -audit.level;
        });

        if (audits && this.context.auditDetailOpen) {
            return (
                <div className="audit-details" id="audit-details" aria-hidden={!this.context.auditDetailOpen}>
                    {audits_sorted.map(function(audit, i) {
                        var level = audit.level_name.toLowerCase();
                        var iconClass = 'icon audit-icon-' + level;
                        var alertClass = 'audit-detail-' + level;
                        var levelClass = 'audit-level-' + level;
                        return (
                            <div className={alertClass} key={i} role="alert">
                                <i className={iconClass}></i>
                                <strong className={levelClass}>{audit.level_name.split('_').join(' ')}</strong>
                                &nbsp;&mdash;&nbsp;
                                <strong>{audit.category}</strong>: {audit.detail}
                            </div>
                        );
                    }.bind(this))}
            </div>
            );
        } else {
            return null;
        }
    }
});
