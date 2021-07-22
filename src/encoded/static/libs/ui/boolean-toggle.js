import React from 'react';
import PropTypes from 'prop-types';


/**
 * Renders a boolean switch in the style of iOS. This keeps no internal state -- the parent
 * component keeps this state and passes it down. The "frame" of the switch represents the space in
 * which the actuator slides. The actuator represents the "physical" switch you would slide in real
 * life.
 */
const DEFAULT_SWITCH_HEIGHT = 22;
const DEFAULT_SWITCH_WIDTH = DEFAULT_SWITCH_HEIGHT * 1.6;
const BooleanToggle = ({
    id,
    state,
    title,
    voice,
    triggerHandler,
    disabled,
    options: {
        width,
        height,
        cssSwitch,
        cssTitle,
        cssFrame,
        cssActuator,
    },
}) => {
    // True if checkbox input has focus.
    const [focused, setFocused] = React.useState(false);

    /**
     * Called when the user focuses on this control.
     */
    const handleFocus = () => {
        setFocused(true);
    };

    /**
     * Called when the user moves focus away from this control.
     */
    const handleBlur = () => {
        setFocused(false);
    };

    // Calculate the inline styles for the switch and actuator.
    const switchWidth = width || DEFAULT_SWITCH_WIDTH;
    const switchHeight = height || DEFAULT_SWITCH_HEIGHT;
    const triggerSize = switchHeight - 4;
    const switchStyles = {
        width: switchWidth,
        height: switchHeight,
        borderRadius: switchHeight / 2,
        backgroundColor: state ? '#4183c4' : '#e9e9eb',
    };
    const actuatorStyles = {
        width: triggerSize,
        height: triggerSize,
        borderRadius: (switchHeight / 2) - 2,
        top: 2,
        left: state ? (switchWidth - switchHeight) + 2 : 2,
    };

    return (
        <label htmlFor={id} aria-label={voice} className={`boolean-toggle${focused ? ' boolean-toggle--focused' : ''}${disabled ? ' boolean-toggle--disabled' : ''}${cssSwitch ? ` ${cssSwitch}` : ''}`}>
            <div className={`boolean-toggle__title${cssTitle ? ` ${cssTitle}` : ''}`}>{title}</div>
            <div style={switchStyles} className={`boolean-toggle__frame${cssFrame ? ` ${cssFrame}` : ''}`}>
                <div style={actuatorStyles} className={`boolean-toggle__actuator${cssActuator ? ` ${cssActuator}` : ''}`} />
            </div>
            <input id={id} type="checkbox" checked={state} disabled={disabled} onChange={triggerHandler} onFocus={handleFocus} onBlur={handleBlur} />
        </label>
    );
};

BooleanToggle.propTypes = {
    /** Unique HTML ID for <input> */
    id: PropTypes.string.isRequired,
    /** Current state to display in the switch */
    state: PropTypes.bool.isRequired,
    /** Title of the button */
    title: PropTypes.oneOfType([
        /** Text title */
        PropTypes.string,
        /** React component to render as the title; include a11y elements */
        PropTypes.element,
    ]).isRequired,
    /** Text for screen readers to speak */
    voice: PropTypes.string,
    /** Called when the user clicks anywhere in the switch */
    triggerHandler: PropTypes.func.isRequired,
    /** True to disable toggle */
    disabled: PropTypes.bool,
    /** Other styling options */
    options: PropTypes.exact({
        /** Width of switch in pixels; 36px by default */
        width: PropTypes.number,
        /** Height of switch in pixels; 22px by default */
        height: PropTypes.number,
        /** Css class to add to the outer switch element */
        cssSwitch: PropTypes.string,
        /** CSS class to add to the switch title */
        cssTitle: PropTypes.string,
        /** CSS class to add to the switch frame */
        cssFrame: PropTypes.string,
        /** CSS class to add to the switch actuator */
        cssActuator: PropTypes.string,
    }),
};

BooleanToggle.defaultProps = {
    voice: '',
    disabled: false,
    options: {},
};

export default BooleanToggle;
