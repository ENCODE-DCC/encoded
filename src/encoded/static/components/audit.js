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
        var auditCounts = {};
        var audits = this.props.audits;

        if (audits && Object.keys(audits).length) {
            // Sort the audit levels by their level number, using the first element of each warning category
            var sortedAuditLevels = _(Object.keys(audits)).sortBy(function(level) {
                return -audits[level][0].level;
            });

            var indicatorClass = "audit-indicators btn btn-default" + (this.context.auditDetailOpen ? ' active' : '') + (this.props.search ? ' audit-search' : '');

            return (
                <button className={indicatorClass} aria-label="Audit indicators" aria-expanded={this.context.auditDetailOpen} aria-controls={this.props.key.replace(/\W/g, '')} onClick={this.context.auditStateToggle}>
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
        var audits = this.props.audits;

        if (this.context.auditDetailOpen) {
            // Sort the audit levels by their level number, using the first element of each warning category
            var sortedAuditLevels = _(Object.keys(audits)).sortBy(function(level) {
                return -audits[level][0].level;
            });

            return (
                <div className="audit-details" id={this.props.key.replace(/\W/g, '')} key={this.props.key} aria-hidden={!this.context.auditDetailOpen}>
                    {sortedAuditLevels.map(function(level, i) {
                        var levelText = level.toLowerCase();
                        var iconClass = 'icon audit-icon-' + levelText;
                        var alertClass = 'audit-detail-' + levelText;
                        var levelClass = 'audit-level-' + levelText;
                        var sortedAudits = _(audits[level]).sortBy(function(audit) {
                            return audit.category;
                        });

                        return (
                            <div key={i}>
                                {sortedAudits.map(function(audit, j) {
                                    return (
                                        <div className={alertClass} key={j} role="alert">
                                            <i className={iconClass}></i>
                                            <strong className={levelClass}>{level.split('_').join(' ')}</strong>
                                            &nbsp;&mdash;&nbsp;
                                            <strong>{audit.category}</strong>: {audit.detail}
                                        </div>
                                    );
                                })}
                            </div>
                        );
                    })}
                </div>
            );
        }
        return null;
    }
});
