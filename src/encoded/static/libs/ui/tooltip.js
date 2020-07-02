import React from 'react';
import PropTypes from 'prop-types';
import { BrowserFeat } from '../../components/browserfeat';

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

const Tooltip = (props) => {
    const [showDefinition, setDefinition] = React.useState(false);
    const [isMobile, setIsMobile] = React.useState(false);
    const { trigger, position, tooltipId, css, innerCss, children, timerFlag, relativeTooltipFlag } = props;
    const wrapperCss = `tooltip-container${css ? ` ${css}` : ''}`;
    const tooltipCss = `${innerCss || `tooltip ${position}`}`;

    // Display or hide tooltip pop-up
    const setDefinitionVisibility = (param, e) => {
        // Set delay on hiding the pop-up on "mouseleave" unless timerFlag is set to false
        if (timerFlag && e.type === 'mouseleave') {
            setTimeout(() => {
                setDefinition(param);
            }, 1000);
        } else {
            setDefinition(param);
        }
    };

    // Check to see if device is mobile (small width with touch screen)
    React.useEffect(() => {
        const updateWidth = () => {
            const screenWidth = Math.min(screen.width, window.innerWidth);
            setIsMobile(BrowserFeat.feat.touchEnabled && screenWidth <= 800);
        };
        updateWidth();
        window.addEventListener('resize', updateWidth);
        return () => window.removeEventListener('resize', updateWidth);
    }, [isMobile, setIsMobile]);

    // Special case for menu tooltips on mobile to allow the pop-up to be displayed as position relative on devices smaller than 800px wide with touch screens
    if (isMobile && relativeTooltipFlag) {
        return (
            <React.Fragment>
                <button
                    aria-describedby={showDefinition ? tooltipId : ''}
                    onMouseEnter={e => setDefinitionVisibility(true, e)}
                    onMouseLeave={e => setDefinitionVisibility(false, e)}
                    onFocus={e => setDefinitionVisibility(true, e)}
                    onBlur={e => setDefinitionVisibility(false, e)}
                    className={`tooltip-container__trigger ${showDefinition ? 'show' : ''}`}
                >
                    {trigger}
                </button>
                {showDefinition ?
                    <div
                        className={tooltipCss}
                        role="tooltip"
                        id={tooltipId}
                    >
                        <div className="tooltip-inner">{children}</div>
                    </div>
                : null}
            </React.Fragment>
        );
    }
    return (
        <div className={wrapperCss}>
            <button
                aria-describedby={showDefinition ? tooltipId : ''}
                onMouseEnter={e => setDefinitionVisibility(true, e)}
                onMouseLeave={e => setDefinitionVisibility(false, e)}
                onFocus={e => setDefinitionVisibility(true, e)}
                onBlur={e => setDefinitionVisibility(false, e)}
                className={`tooltip-container__trigger ${showDefinition ? 'show' : ''}`}
            >
                {trigger}
            </button>
            {showDefinition ?
                <div
                    className={tooltipCss}
                    role="tooltip"
                    id={tooltipId}
                >
                    <div className="tooltip-arrow" />
                    <div className="tooltip-inner">{children}</div>
                </div>
            : null}
        </div>
    );
};

Tooltip.propTypes = {
    trigger: PropTypes.element.isRequired, // Visible tooltip triggering component
    tooltipId: PropTypes.string.isRequired, // HTML ID of tooltip <div>; unique within page
    position: PropTypes.oneOf(['left', 'top', 'bottom', 'right']), // Position of bootstrap tooltip location
    css: PropTypes.string, // CSS classes to add to tooltip-container wrapper class
    innerCss: PropTypes.string, // CSS classes to add to tooltip class
    children: PropTypes.node, // Tooltip pop-up component
    timerFlag: PropTypes.bool, // Optional flag for when timer should be implemented on mouseLeave
    relativeTooltipFlag: PropTypes.bool, // Optional flag for tooltips that have relative position (touch device only)
};

Tooltip.defaultProps = {
    position: 'bottom',
    css: '',
    innerCss: '',
    children: null,
    timerFlag: true,
    relativeTooltipFlag: false,
};

export default Tooltip;
