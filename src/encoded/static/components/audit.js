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
        var audits = this.props.audits;
        var indicatorClasses = "audit-indicators" + (this.context.auditDetailOpen ? ' active' : '');
        if (audits && audits.length) {
            // Sort audit records
            var audits_sorted = _.sortBy(audits, function(audit) {
                return -audit.level;
            });

            return (
                <button className={indicatorClasses} aria-expanded={this.context.auditDetailOpen} aria-controls="#audit-details" onClick={this.context.auditStateToggle}>
                    {audits_sorted.map(function(audit, i) {
                        return <AuditIndicator audit={audit} />;
                    }.bind(this))}
                </button>
            );
        } else {
            return null;
        }
    }
});


var AuditIndicator = React.createClass({
    contextTypes: {
        auditDetailOpen: React.PropTypes.bool,
        auditStateToggle: React.PropTypes.func // Function for clicks in audit indicators
    },

    render: function() {
        var audit = this.props.audit;
        var iconClass = 'icon audit-activeicon-' + audit.level_name.toLowerCase();
        return (
            <i className={iconClass}><span className="sr-only">{'Audit'} {audit.level_name}</span></i>
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
