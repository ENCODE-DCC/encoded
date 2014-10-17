/** @jsx React.DOM */
'use strict';
var React = require('react');
var cx = require('react/lib/cx');


var AuditSet = module.exports.AuditSet = React.createClass({
    render: function() {
        var audits = this.props.audits;
        return (
            <div className="audit-set">
                {audits.map(function(audit) {
                    return <AuditItem audit={audit} />;
                })}
            </div>
        );
    }
});


var AuditItem = React.createClass({
    render: function() {
        var audit = this.props.audit;
        var iconClass = 'icon audit-icon-' + audit.level_name.toLowerCase();
        return (
            <i className={iconClass}></i>
        );
    }
});
