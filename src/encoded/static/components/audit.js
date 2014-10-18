/** @jsx React.DOM */
'use strict';
var React = require('react');
var cx = require('react/lib/cx');


var AuditSet = module.exports.AuditSet = React.createClass({
    getInitialState: function() {
        return {detailOpen: []};
    },

    handleClick: function(i) {
        // Clone state array, then set toggled element
        var detailOpen = this.state.detailOpen.slice(0);
        detailOpen[i] = detailOpen[i] ? false : true;
        this.setState({detailOpen: detailOpen});
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
