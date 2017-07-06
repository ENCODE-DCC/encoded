import React from 'react';
import PropTypes from 'prop-types';
import offset from '../libs/offset';


// Render the collection table header that sticks to the top of the browser window, or below the
// navigation bar of that’s position fixed (as it is if the browser window is wide enough). Note
// that this method makes the sticky header shudder up and down while scrolling. Better ways exist
// to do this without shudderingm, but they don't work on tables.
export default class StickyHeader extends React.Component {
    constructor() {
        super();

        // Bind this to non-React components.
        this.stickyHeader = this.stickyHeader.bind(this);
    }

    componentDidMount() {
        // Avoid shimming as ie8 does not support css transform
        if (window.getComputedStyle === undefined) return;
        this.stickyHeader();
        window.addEventListener('scroll', this.stickyHeader);
        window.addEventListener('resize', this.stickyHeader);
    }

    componentWillUnmount() {
        if (window.getComputedStyle === undefined) return;
        window.removeEventListener('scroll', this.stickyHeader);
        window.removeEventListener('resize', this.stickyHeader);
    }

    stickyHeader() {
        // http://stackoverflow.com/a/6625189/199100
        // http://css-tricks.com/persistent-headers/
        const header = this.stickyHeaderComp;
        if (header) {
            const table = header.parentElement;
            const offsetTop = offset(table).top;
            const nb = document.querySelector('.navbar-fixed-top');
            let nbHeight = 0;

            if (window.getComputedStyle(nb).getPropertyValue('position') === 'fixed') {
                nbHeight = nb.clientHeight;
            }
            const scrollTop = document.body.scrollTop + nbHeight;
            let y = 0;

            if ((scrollTop > offsetTop) && (scrollTop < (offsetTop + table.clientHeight))) {
                y = scrollTop - offsetTop - 3; // correction for borders
            }
            const transform = `translate(0px,${y}px)`;
            header.style.transform = transform;
        }
    }

    render() {
        const child = React.cloneElement(this.props.children, { ref: (comp) => { this.stickyHeaderComp = comp; } });
        return React.Children.only(child);
    }
}

StickyHeader.propTypes = {
    children: PropTypes.object.isRequired,
};
