import React, { useState } from 'react';
import PropTypes from 'prop-types';
import Hit from './hit';


export const LinkWithHover = (props) => {
    const [isHovered, setIsHovered] = useState(false);
    return (
        <button
            className={isHovered ? props.hoverClass : props.defaultClass}
            onMouseEnter={() => setIsHovered(true)}
            onMouseLeave={() => setIsHovered(false)}
        >
            <a href={props.href}>
                {isHovered ? props.defaultValue : props.hoverValue || props.defaultValue}
            </a>
        </button>
    );
};


LinkWithHover.propTypes = {
    href: PropTypes.string.isRequired,
    defaultClass: PropTypes.string,
    hoverClass: PropTypes.string,
    defaultValue: PropTypes.string.isRequired,
    hoverValue: PropTypes.oneOfType(
        [
            PropTypes.string,
            PropTypes.element,
        ]
    ),
};


LinkWithHover.defaultProps = {
    defaultClass: null,
    hoverClass: null,
    hoverValue: null,
};


export const Title = props => (
    <LinkWithHover
        defaultValue={props.value}
        defaultClass={'top-hits-search__suggested-results-title'}
        hoverClass={'top-hits-search__suggested-results-title--selected'}
        href={props.href}
    />
);


Title.propTypes = {
    value: PropTypes.string.isRequired,
    href: PropTypes.string.isRequired,
};


export const Item = (props) => {
    const hit = new Hit(props.item);
    return (
        <li>
            <LinkWithHover
                defaultValue={hit.asString()}
                hoverClass={'top-hits-search__suggested-results--selected'}
                href={props.href}
            />
        </li>
    );
};


Item.propTypes = {
    item: PropTypes.object.isRequired,
    href: PropTypes.string.isRequired,
};
