import React from 'react';


const Pager = React.createClass({
    propTypes: {
        total: React.PropTypes.number.isRequired, // Total number of pages
        current: React.PropTypes.number.isRequired, // Current page number; 0 based
        updateCurrentPage: React.PropTypes.func.isRequired, // Callback with new page number of user selects
    },

    handlePrev: function () {
        const { current, updateCurrentPage } = this.props;
        updateCurrentPage(current - 1);
    },

    handleNext: function () {
        const { current, updateCurrentPage } = this.props;
        updateCurrentPage(current + 1);
    },

    render: function () {
        const { total, current } = this.props;
        const prevDisabled = current === 0;
        const nextDisabled = current === (total - 1);

        return (
            <div className="pager" role="navigation" aria-label="Pagination">
                <button className="pager__dir" disabled={prevDisabled} aria-label={prevDisabled ? '' : 'Previous page'} onClick={this.handlePrev}><i className="icon icon-chevron-left" /></button>
                <div className="pager__index">{current + 1} OF {total}</div>
                <button className="pager__dir" disabled={nextDisabled} aria-label={nextDisabled ? '' : 'Next page'} onClick={this.handleNext}><i className="icon icon-chevron-right" /></button>
            </div>
        );
    },
});

export default Pager;
