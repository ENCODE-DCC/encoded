'use strict';
var React = require('react');


// Render a dropdown menu. All components within the dropdown get wrapped in <li> tags, so the 'a' elements in:
//
// <DropdownMenu>
//   <a href="#">First</a>
//   <a href="#">Second</a>
// </DropdownMenu>
//
// ...get rendered as
// <li><a href="#">First</a></li>
// <li><a href="#">Second</a></li>
//
// Click handling method taken from:
// https://github.com/facebook/react/issues/579#issuecomment-60841923

var DropdownButton = module.exports.DropdownButton = React.createClass({
    propTypes: {
        title: React.PropTypes.string.isRequired, // Title of the trigger button
        disabled: React.PropTypes.bool // True to disable button
    },

    getInitialState: function() {
        return {
            open: false // True if dropdown is open
        }
    },

    componentDidMount: function() {
        // Add a click handler to the DOM document -- the entire page
        document.addEventListener('click', this.documentClickHandler);
    },

    componentWillUnmount: function() {
        // Remove the DOM document click handler now that the DropdownButton is going away.
        document.removeEventListener('click', this.documentClickHandler);
    },

    documentClickHandler: function() {
        // A click outside the DropdownButton closes the dropdown
        this.setState({open: false});
    },

    triggerClickHandler: function(e) {
        // After clicking the dropdown trigger button, don't allow the event to bubble to the rest of the DOM.
        e.nativeEvent.stopImmediatePropagation();
        this.setState({open: !this.state.open});
    },

    render: function() {
        return (
            <div className={'btn-group' + (this.state.open ? ' open' : '')}>
                <a disabled={this.props.disabled} className="btn btn-info btn-sm dropdown-toggle" href="#" onClick={this.triggerClickHandler}>
                    {this.props.title}&nbsp;<span className="caret"></span>
                </a>
                {this.props.children}
            </div>
        );
    }
});
