import React, {useState} from 'react';

const Button = ({children, ...rest}) => {
    return (
        <button {...rest}>
          {children}
        </button>
    );
};


export const LinkWithHover = (props) => {
    const [isHovered, setIsHovered] = useState(false);
    return (
        <button
          className={isHovered ? props.hoverClass: props.defaultClass}
          onMouseEnter={() => setIsHovered(true)}
          onMouseLeave={() => setIsHovered(false)}
        >
          <a href={props.href}>
            {isHovered ? props.defaultValue : props.hoverValue || props.defaultValue}
          </a>
        </button>
    );
};


export const Title = (props) => {
    return (
        <LinkWithHover
          defaultValue={props.value}
          defaultClass={'top-hits-search__suggested-results-title'}
          hoverClass={'top-hits-search__suggested-results-title--selected'}
          href={props.href}
        />
    );
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
