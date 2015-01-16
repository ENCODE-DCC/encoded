/** @jsx React.DOM */
'use strict';
var React = require('react');
var _ = require('underscore');
var cx = require('react/lib/cx');

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
        var auditCounts = {}  ;
        var audits = this.props.audits;

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
        var audits = this.props.audits;

        // Sort audit records
        var audits_sorted = _.chain(audits).sortBy(function(audit) {
            return audit.category.toLowerCase();
        }).sortBy(function(audit) {
            return -audit.level;
        }).value();

        if (audits_sorted && this.context.auditDetailOpen) {
            return (
                <div className="audit-details" id={this.props.key.replace(/\W/g, '')} aria-hidden={!this.context.auditDetailOpen}>
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
                    })}
            </div>
            );
        } else {
            return null;
        }
    }
});
