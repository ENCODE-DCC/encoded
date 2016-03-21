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

var DropdownMenu = module.exports.DropdownMenu = React.createClass({
    // After the dropdown menu gets drawn, get its height and call parent function to report it
    componentDidUpdate: function() {
        if (this.props.updateElement) {
            var el = this.refs.dropdownbutton.getDOMNode(); // Change for React 0.14
            this.props.updateElement(el);
        }
    },

    render: function() {
        return (
            <ul ref="dropdownbutton" className="dropdown-menu" data-status={this.props.status} role="menu">
                {this.props.children.map((child, i) => <li key={i}>{child}</li>)}
            </ul>
        );
    }
});
