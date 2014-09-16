/** @jsx React.DOM */
'use strict';
var React = require('react');
var globals = require('./globals');

var StatusLabel = module.exports.StatusLabel = React.createClass({
    render: function() {
        var status = this.props.status;
        var title = this.props.title;
        if (typeof status === 'string') {
            // Display simple string and optional title in badge
            return (
                <div className="status-list">
                    <span className={globals.statusClass(status, 'label')}>
                        {title ? <span className="status-list-title">{title + ': '}</span> : null}
                        {status}
                    </span>
                </div>
            );
        } else if (typeof status === 'object') {
            // Display a list of badges from array of objects with status and optional title
            return (
                <ul className="status-list">
                    {status.map(function (status) {
                        return(
                            <li key={status.title} className={globals.statusClass(status.status, 'label')}>
                                {status.title ? <span className="status-list-title">{status.title + ': '}</span> : null}
                                {status.status}
                            </li>
                        );
                    })}
                </ul>
            );
        } else {
            return null;
        }
    }
});
