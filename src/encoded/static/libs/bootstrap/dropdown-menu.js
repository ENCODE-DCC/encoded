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
    render: function() {
        return (
            <ul className="dropdown-menu" role="menu">
                {this.props.children.map((child, i) => <li key={i}>{child}</li>)}
            </ul>
        );
    }
});
