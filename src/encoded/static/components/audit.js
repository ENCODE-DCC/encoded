/** @jsx React.DOM */
'use strict';
var React = require('react');
var cx = require('react/lib/cx');


var AuditSet = module.exports.AuditSet = React.createClass({
    getInitialState: function() {
        return {detailOpen: []};
    },

    handleClick: function(i) {
        console.log('THIS: ' + i);
    },

    render: function() {
        var audits = this.props.audits;
        return (
            <div className="audit-set">
                {audits.map(function(audit, i) {
                    return <AuditItem audit={audit} handleClick={this.handleClick} key={i} />;
                }.bind(this))}
            </div>
        );
    }
});


var AuditItem = React.createClass({
    render: function() {
        var audit = this.props.audit;
        var iconClass = 'icon audit-icon-' + audit.level_name.toLowerCase();
        return (
            <button className={iconClass} onClick={this.props.handleClick.bind(null, this.props.key)} />
        );
    }
});
