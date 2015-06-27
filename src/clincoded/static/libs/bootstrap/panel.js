"use strict";
var React = require('react');


// Controls a group of Panel components. Useful for accordions.
var PanelGroup = module.exports.PanelGroup = React.createClass({
    propTypes: {
        accordion: React.PropTypes.bool // T if child panels should accordion
    },

    render: function() {
        // If accordion panel group, add accordion property to child Panels
        var children = React.Children.map(this.props.children, function(child) {
            if (child.type === Panel) {
                // Adding properties to children means cloning them, so...
                var clone = React.cloneElement(child, {accordion: true});
                return clone;
            }
            return child;
        }.bind(this));

        return (
            <div className="panel-group">
                {children}
            </div>
        );
    }
});


// Displays one panel. It can be a child of a PanelGroup if you're doing accordions.
var Panel = module.exports.Panel = React.createClass({
    propTypes: {
        title: React.PropTypes.string, // Title in panel's header
        accordion: React.PropTypes.bool // T if part of an accordion panel group; copied from PanelGroup props
    },

    getInitialState: function() {
        return {
            open: !!this.props.open
        };
    },

    handleClick: function() {
        this.setState({open: !this.state.open});
    },

    render: function() {
        return (
            <div className="panel panel-default">
                {this.props.title ?
                    <div className="panel-heading" role="tab">
                        {this.props.accordion ?
                            <h4><a href="#" onClick={this.handleClick}>{this.props.title}</a></h4>
                        :
                            <h4>{this.props.title}</h4>
                        }
                    </div>
                : null}
                {this.state.open || !this.props.accordion ?
                    <div className="panel-body">
                        {this.props.children}
                    </div>
                : null}
            </div>
        );
    }
});
