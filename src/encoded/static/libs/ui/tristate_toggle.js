import React from 'react';
import PropTypes from 'prop-types';

const TriStateToggle = ({ href, neutralHref, negHref, identifier }) => (
    <div className="switch-toggle switch-3 switch-candy">
        <input id="on" name={identifier} disabled={!href} type="radio" onChange={() => { window.location = href; }} />
        <label htmlFor="on">
            <i className="icon icon-check on-switch" />
        </label>

        <input id="na" name={identifier} type="radio" disabled={!neutralHref} checked="checked" onChange={() => { window.location = neutralHref; }} />
        <label htmlFor="na" className="disabled">
            <i className="icon icon-minus-circle neutral-switch" />
        </label>

        <input id="off" name={identifier} type="radio" disabled={!negHref} onChange={() => { window.location = negHref; }} />
        <label htmlFor="off">
            <i className="icon icon-times off-switch" />
        </label>
    </div>
);

TriStateToggle.propTypes = {
    href: PropTypes.string.isRequired,
    neutralHref: PropTypes.string.isRequired,
    negHref: PropTypes.string.isRequired,
    identifier: PropTypes.string.isRequired,
};

export default TriStateToggle;
