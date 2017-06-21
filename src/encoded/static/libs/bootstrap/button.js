import React from 'react';
import PropTypes from 'prop-types';
import { DropdownMenu } from './dropdown-menu';


// Render a dropdown menu. All components within the dropdown get wrapped in <li> tags, so the 'a' elements in:
//
// <DropdownMenu>
//   <a href="#">First</a>
//   <a href="#">Second</a>
// </DropdownMenu>
//
// ...get rendered as
// <li><a href="#">First</a></li>
// <li><a href="#">Second</a></li>
//
// Click handling method taken from:
// https://github.com/facebook/react/issues/579#issuecomment-60841923

class DropdownButton extends React.Component {
    constructor() {
        super();

        // Set initial React state.
        this.state = {
            open: false, // True if dropdown is open
        };

        // Bind this to non-React components.
        this.documentClickHandler = this.documentClickHandler.bind(this);
        this.triggerClickHandler = this.triggerClickHandler.bind(this);
    }

    componentDidMount() {
        // Add a click handler to the DOM document -- the entire page
        document.addEventListener('click', this.documentClickHandler);
    }

    componentWillUnmount() {
        // Remove the DOM document click handler now that the DropdownButton is going away.
        document.removeEventListener('click', this.documentClickHandler);
    }

    documentClickHandler() {
        // A click outside the DropdownButton closes the dropdown
        this.setState({ open: false });
    }

    triggerClickHandler(e) {
        // After clicking the dropdown trigger button, don't allow the event to bubble to the rest of the DOM.
        e.nativeEvent.stopImmediatePropagation();
        this.setState(prevState => ({ open: !prevState.open }));
    }

    render() {
        const { title, label, disabled, wrapperClasses } = this.props;

        // Add the `label` property to any <DropdownMenu> child components
        const children = React.Children.map(this.props.children, (child) => {
            if (child.type === DropdownMenu) {
                return React.cloneElement(child, { label: this.props.label });
            }
            return child;
        });

        return (
            <div className={`dropdown${this.state.open ? ' open' : ''}${wrapperClasses ? ` ${wrapperClasses}` : ''}`}>
                <button
                    disabled={disabled}
                    className="btn btn-info btn-sm dropdown-toggle"
                    type="button"
                    id={label}
                    data-toggle="dropdown"
                    aria-haspopup="true"
                    aria-expanded={this.state.open}
                    onClick={this.triggerClickHandler}
                >
                    {title}&nbsp;<span className="caret" />
                </button>
                {children}
            </div>
        );
    }
}

DropdownButton.propTypes = {
    title: PropTypes.string, // Title of the trigger button
    label: PropTypes.string, // id (unique in doc) for this button
    disabled: PropTypes.bool, // True to disable button
    wrapperClasses: PropTypes.string, // Classes to add to wrapper div
    children: PropTypes.node, // Components rendered inside DropdownButton, usually drop-down items
};

DropdownButton.defaultProps = {
    title: '',
    label: '',
    disabled: false,
    wrapperClasses: '',
    children: null,
};
