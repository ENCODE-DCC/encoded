import React from 'react';
import PropTypes from 'prop-types';


// This module lets you have a tooltip pop up when any component is hovered over or focused. The
// general usage is:
//
// <Tooltip trigger={<Trigger />} tooltipId="html-id-unique-on-page" css="custom-css-classes">
//     <TooltipContent />
// </Tooltip>
//
// The component that the user can hover over to trigger the tooltip is given in the `trigger`
// property and appears in the DOM whereever you place the <Tooltip> component. Put the contents
// of the tooltip between the opening and closing <Tooltip> tags. This can simply be a string if
// that's all you need, or a full-fledged component.

export default class Tooltip extends React.Component {
    constructor() {
        super();
        this.state = {
            tooltipDisplayed: false,
        };
        this.timer = null;
        this.hoveringOverTooltip = false;
        this.handleTriggerMouseEnter = this.handleTriggerMouseEnter.bind(this);
        this.handleTriggerMouseLeave = this.handleTriggerMouseLeave.bind(this);
        this.handleTooltipMouseEnter = this.handleTooltipMouseEnter.bind(this);
        this.handleTooltipMouseLeave = this.handleTooltipMouseLeave.bind(this);
        this.handleTriggerFocus = this.handleTriggerFocus.bind(this);
        this.handleTriggerBlur = this.handleTriggerBlur.bind(this);
    }

    handleTriggerMouseEnter() {
        // Mouse entered the tooltip trigger element.
        this.setState({ tooltipDisplayed: true });

        // If we happen to have a running timer, clear it so we don't hide the tooltip while
        // hovering over the trigger.
        if (this.timer) {
            clearTimeout(this.timer);
            this.timer = null;
        }
    }

    handleTriggerMouseLeave() {
        // Start a timer that might hide the tooltip after a second passes. It won't hide the
        // tooltip if they're now hovering over the tooltip itself.
        this.timer = setTimeout(() => {
            this.timer = null;
            if (!this.hoveringOverTooltip) {
                this.setState({ tooltipDisplayed: false });
            }
        }, 1000);
    }

    handleTriggerFocus() {
        // Show tooltip when keyboard focus lands on tooltip trigger.
        this.setState({ tooltipDisplayed: true });
    }

    handleTriggerBlur() {
        // Hide tooltip when keyboard focus leaves tooltip trigger.
        this.setState({ tooltipDisplayed: false });
    }

    handleTooltipMouseEnter() {
        // Mouse started hovering over the tooltip itself. Prevent the tooltip from hiding even if
        // the one-second trigger time expires.
        this.hoveringOverTooltip = true;
    }

    handleTooltipMouseLeave() {
        // Mouse stopped hovering over the tooltip itself. If the timer's not running, hide the
        // tooltip, otherwise let the existing timer hide the tooltip when it expires.
        this.hoveringOverTooltip = false;
        if (!this.timer) {
            this.setState({ tooltipDisplayed: false });
        }
    }

    render() {
        const { trigger, direction, tooltipId, css } = this.props;
        const tooltipCss = `tooltip ${direction}`;
        const wrapperCss = `tooltip-container${css ? ` ${css}` : ''}`;
        return (
            <div className={wrapperCss}>
                {this.state.tooltipDisplayed ?
                    <div className={tooltipCss} role="tooltip" id={tooltipId} onMouseEnter={this.handleTooltipMouseEnter} onMouseLeave={this.handleTooltipMouseLeave}>
                        <div className="tooltip-arrow" />
                        <div className="tooltip-inner">{this.props.children}</div>
                    </div>
                : null}
                <button
                    aria-describedby={this.state.tooltipDisplayed ? tooltipId : ''}
                    onMouseEnter={this.handleTriggerMouseEnter}
                    onMouseLeave={this.handleTriggerMouseLeave}
                    onFocus={this.handleTriggerFocus}
                    onBlur={this.handleTriggerBlur}
                    className="tooltip-container__trigger"
                >
                    {trigger}
                </button>
            </div>
        );
    }
}

Tooltip.propTypes = {
    trigger: PropTypes.element.isRequired, // Visible tooltip triggering component
    tooltipId: PropTypes.string.isRequired, // HTML ID of tooltip <div>; unique within page
    direction: PropTypes.oneOf(['left', 'top', 'bottom', 'right']), // Direction of bootstrap tooltip location
    css: PropTypes.string, // CSS classes to add to tooltip-container wrapper class
    children: PropTypes.node,
};

Tooltip.defaultProps = {
    direction: 'bottom',
    css: '',
    children: null,
};
