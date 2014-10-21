/** @jsx React.DOM */
'use strict';
var React = require('react');
var cx = require('react/lib/cx');
var bsLevelMap = {warning: 'warning', error: 'danger'};


var AuditMixin = module.exports.AuditMixin = {
    childContextTypes: {
        auditDetailOpen: React.PropTypes.array,
        auditStateToggle: React.PropTypes.func
    },

    // Retrieve current React context
    getChildContext: function() {
        return {
            auditDetailOpen: this.state.auditDetailOpen, // Array of flags for which audits are visible
            auditStateToggle: this.auditStateToggle // Function to process clicks in audit indicators
        };
    },

    getInitialState: function() {
        return {auditDetailOpen: []};
    },

    auditStateToggle: function(i) {
        // Clone state array, then set toggled element
        var auditDetailOpen = this.state.auditDetailOpen.slice(0);
        auditDetailOpen[i] = auditDetailOpen[i] ? false : true;
        this.setState({auditDetailOpen: auditDetailOpen});
    },

    clearAudits: function() {
        this.setState({auditDetailOpen: []});
    }
};


var AuditIndicators = module.exports.AuditIndicators = React.createClass({
    render: function() {
        var audits = this.props.audits;
        if (audits) {
            return (
                <div className="audit-indicators">
                    {audits.map(function(audit, i) {
                        return <AuditIndicator audit={audit} key={i} />;
                    }.bind(this))}
                </div>
            );
        } else {
            return null;
        }
    }
});


var AuditIndicator = React.createClass({
    contextTypes: {
        auditDetailOpen: React.PropTypes.array,
        auditStateToggle: React.PropTypes.func // Function for clicks in audit indicators
    },

    render: function() {
        var audit = this.props.audit;
        var iconClass = 'icon audit-activeicon-' + audit.level_name.toLowerCase() + (this.context.auditDetailOpen[this.props.key] ? ' active' : '');
        return (
            <button className={iconClass} onClick={this.context.auditStateToggle.bind(null, this.props.key)} />
        );
    }
});


var AuditDetail = module.exports.AuditDetail = React.createClass({
    contextTypes: {
        auditDetailOpen: React.PropTypes.array,
        auditStateToggle: React.PropTypes.func
    },

    render: function() {
        var audits = this.props.audits;
        if (audits) {
            return (
                <div className="audit-detail">
                    {audits.map(function(audit, i) {
                        if (this.context.auditDetailOpen[i]) {
                            var level = audit.level_name.toLowerCase();
                            var bsLevel = bsLevelMap[level];
                            var iconClass = 'icon audit-icon-' + level;
                            var alertClass = 'alert alert-' + bsLevel;
                            return (
                                <div className={alertClass} key={i} role="alert">
                                    <button type="button" className="close" onClick={this.context.auditStateToggle.bind(null, i)}>
                                        <span area-hidden="true">×</span>
                                        <span className="sr-only">Close</span>
                                    </button>
                                    <i className={iconClass}></i>
                                    <strong>{audit.level_name}</strong>: {audit.detail}
                                </div>
                            );
                        } else {
                            return null;
                        }
                    }.bind(this))}
                </div>
            );
        } else {
            return null;
        }
    }
});
