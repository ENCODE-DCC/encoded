import PropTypes from 'prop-types';
import {
    Input,
    InputWithIcon,
} from './input';
import Results from './results';


/** Renders the input and dropdown (if there are any results). */
const Form = (props) => (
    <form className="top-hits-search__form" action="/search/">
        {props.children}
        {
            !!props.results.length > 0 &&
            <Results
               input={props.input}
               results={props.results}
               handleClickAway={props.handleClickAway}
            />
        }
    </form>
);


Form.propTypes = {
    children: PropTypes.element.isRequired,
    input: PropTypes.string.isRequired,
    results: PropTypes.array.isRequired,
    handleClickAway: PropTypes.func.isRequired,
};


/** Uses input form with icon */
export const NavBarForm = (props) => (
    <Form {...props}>
        <InputWithIcon
            input={props.input}
            onChange={props.handleInputChange}
        />
    </Form>
);


/** Required but set in cloneElement */
NavBarForm.propTypes = {
    input: PropTypes.string,
    handleInputChange: PropTypes.func,
};


NavBarForm.defaultProps = {
    input: null,
    handleInputChange: null,
};


/** Uses plain input form */
export const PageForm = (props) => (
    <Form {...props}>
        <Input
            input={props.input}
            onChange={props.handleInputChange}
        />
    </Form>
);


/** Required but set in cloneElement */
PageForm.propTypes = {
    input: PropTypes.string,
    handleInputChange: PropTypes.func,
};


PageForm.defaultProps = {
    input: null,
    handleInputChange: null,
};
