import React from 'react';
import PropTypes from 'prop-types';


/**
 * Displays a pager component that lets users navigate a list of items. It displays a left and
 * right arrow, and the current displayed item number and the total number of items. When the
 * user clicks a page, it calls the `updateCurrentPage` callback so that the component that uses
 * <Pager> can react to the click.
 */
const Pager = ({ total, current, updateCurrentPage }) => {
    const handlePrev = () => {
        updateCurrentPage(current - 1);
    };

    const handleNext = () => {
        updateCurrentPage(current + 1);
    };

    const prevDisabled = current === 0;
    const nextDisabled = current === (total - 1);

    return (
        <nav className="pager" aria-label="Pagination">
            <ul>
                <li><button className="pager__dir" disabled={prevDisabled} aria-label={prevDisabled ? '' : `Previous page ${current} of ${total}`} onClick={handlePrev}><i className="icon icon-chevron-left" /></button></li>
                <li><div className="pager__index"><div>{current + 1} OF {total}</div></div></li>
                <li><button className="pager__dir" disabled={nextDisabled} aria-label={nextDisabled ? '' : `Next page ${current + 2} of ${total}`} onClick={handleNext}><i className="icon icon-chevron-right" /></button></li>
            </ul>
        </nav>
    );
};

Pager.propTypes = {
    /** Total number of pages */
    total: PropTypes.number.isRequired,
    /** Current page number; 0 based */
    current: PropTypes.number.isRequired,
    /** Callback with new page number user selects */
    updateCurrentPage: PropTypes.func.isRequired,
};

export default Pager;
