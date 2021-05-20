import PropTypes from 'prop-types';
import Group from './group';
import {
    InputWithIcon,
} from '../input';
import QUERIES from './constants';


const shouldRenderResults = (name, results) => (
    results[name] && results[name].length > 0
);


const makeGroupsForResults = (input, results, handleClickAway) => (
    QUERIES.map(
        ([name, , Component, title]) => (
            shouldRenderResults(name, results) &&
            <Group
                title={title}
                key={name}
                input={input}
                results={results[name]}
                component={Component}
                handleClickAway={handleClickAway}
            />
        )
    ).filter(
        (group) => Boolean(group)
    )
);


const Form = ({ children, input, results, handleClickAway }) => {
    const groups = makeGroupsForResults(input, results, handleClickAway);
    return (
        <form className="multisearch__multiform" action="/search/">
            {children}
            {
                groups.length > 0 &&
                <div className="multisearch__results-container">
                    {groups}
                </div>
            }
        </form>
    );
};


Form.propTypes = {
    children: PropTypes.element.isRequired,
    input: PropTypes.string.isRequired,
    results: PropTypes.object.isRequired,
    handleClickAway: PropTypes.func.isRequired,
};


const NavBarForm = (props) => (
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


export default NavBarForm;
