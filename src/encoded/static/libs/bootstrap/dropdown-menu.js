'use strict';
var React = require('react');


// Render a dropdown menu. All components within the dropdown get wrapped in <li> tags, so the 'a'
// elements in:
//
// <DropdownMenu>
//   <a href="#">First</a>
//   <a href="#">Second</a>
//   <DropdownMenuSep>
//  <a href="#">Third</a>
// </DropdownMenu>
//
// ...get rendered as
// <li><a href="#">First</a></li>
// <li><a href="#">Second</a></li>
// <li> --separator-- </li> (well, actually a line, not the word "separator")
// <li><a href="#">Third</a></li>

module.exports.DropdownMenu = React.createClass({
    // One might think `label` should be isRequired. But we can't because of:
    // https://github.com/facebook/react/issues/4494#issuecomment-125068868
    propTypes: {
        label: React.PropTypes.string, // id attribute value for the button that controls this menu
    },

    render: function() {
        return (
            <ul className="dropdown-menu" aria-labelledby={this.props.label}>
                {this.props.children.map((child, i) => {
                    return <li key={i}>{child}</li>;
                })}
            </ul>
        );
    }
});


module.exports.DropdownMenuSep = React.createClass({
    render: function() {
        return <div className="dropdown-sep"></div>;
    }
});
