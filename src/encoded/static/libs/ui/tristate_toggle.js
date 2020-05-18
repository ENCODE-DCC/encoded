import React from 'react';
import PropTypes from 'prop-types';

const TriStateToggle = ({ undoHref, removeHref, href, identifier }) => (
    <div className="switch-toggle switch-3 switch-candy">
        <input id="na" name={identifier} type="radio" disabled={!removeHref} checked="checked" onChange={() => { window.location = removeHref; }} />
        <label htmlFor="on">
            <i className="icon icon-check on-switch" />
        </label>

        <input id="on" name={identifier} disabled={!undoHref} type="radio" onChange={() => { window.location = undoHref; }} />
        <label htmlFor="na" className="disabled">
            <i className="icon icon-minus-circle neutral-switch" />
        </label>

        <input id="off" name={identifier} type="radio" disabled={!href} onChange={() => { window.location = href; }} />
        <label htmlFor="off">
            <i className="icon icon-times off-switch" />
        </label>
    </div>
);

TriStateToggle.propTypes = {
    undoHref: PropTypes.string.isRequired,
    removeHref: PropTypes.string.isRequired,
    href: PropTypes.string.isRequired,
    identifier: PropTypes.string.isRequired,
};

export default TriStateToggle;
