import { useState } from 'react';
import PropTypes from 'prop-types';
import hitFactory from './hits';


/**
* The LinkWithHover keeps track of whether the user is hovering
* and displays default or hover values and classes. The user
* is redirected to href when clicked.
*/
export const LinkWithHover = (props) => {
    const [isHovered, setIsHovered] = useState(false);
    return (
        <a
            href={props.href}
            className={isHovered ? props.hoverClass : props.defaultClass}
            onMouseEnter={() => setIsHovered(true)}
            onMouseLeave={() => setIsHovered(false)}
        >
            {isHovered ? props.hoverValue || props.defaultValue : props.defaultValue}
        </a>
    );
};


LinkWithHover.propTypes = {
    href: PropTypes.string.isRequired,
    defaultClass: PropTypes.string,
    hoverClass: PropTypes.string,
    defaultValue: PropTypes.oneOfType(
        [
            PropTypes.string,
            PropTypes.arrayOf(
                PropTypes.element
            ),
        ]
    ).isRequired,
    hoverValue: PropTypes.oneOfType(
        [
            PropTypes.string,
            PropTypes.arrayOf(
                PropTypes.element
            ),
        ]
    ),
};


LinkWithHover.defaultProps = {
    defaultClass: null,
    hoverClass: null,
    hoverValue: null,
};


/**
* A LinkWithHover that renders section title and count and
* redirects to search results of that type.
*/
export const Title = (props) => (
    <LinkWithHover
        defaultValue={props.value}
        defaultClass="section-title"
        hoverClass="section-title--selected"
        href={props.href}
    />
);


Title.propTypes = {
    value: PropTypes.string.isRequired,
    href: PropTypes.string.isRequired,
};


/**
* A LinkWithHover that renders a top hit in list form and
* redirects to that specific document when clicked.
*/
export const Item = (props) => {
    // This class knows how to format a raw hit for display.
    const hit = hitFactory(props.item);
    return (
        <li>
            <LinkWithHover
                defaultValue={hit.asString()}
                hoverValue={hit.asDetail()}
                defaultClass="section-item"
                hoverClass="section-item--selected"
                href={props.href}
            />
        </li>
    );
};


Item.propTypes = {
    item: PropTypes.object.isRequired,
    href: PropTypes.string.isRequired,
};
