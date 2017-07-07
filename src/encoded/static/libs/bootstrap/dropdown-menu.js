import React from 'react';
import PropTypes from 'prop-types';


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

export const DropdownMenu = props => (
    <ul className="dropdown-menu" aria-labelledby={props.label}>
        {props.children.map((child, i) => <li key={i}>{child}</li>)}
    </ul>
);

// One might think `label` should be isRequired. But we can't because of:
// https://github.com/facebook/react/issues/4494#issuecomment-125068868
DropdownMenu.propTypes = {
    label: PropTypes.string, // id attribute value for the button that controls this menu
    children: PropTypes.array.isRequired, // Items within the drop-down menu
};

DropdownMenu.defaultProps = {
    label: '',
};


export const DropdownMenuSep = () => (
    <div className="dropdown-sep" />
);
