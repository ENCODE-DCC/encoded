import _ from 'underscore';
import PropTypes from 'prop-types';
import Group from './group';
import {
    Input,
    InputWithIcon,
} from '../input';
import {
    queries
} from './constants';


const shouldRenderResults = (name, results) => {
    return results[name] && results[name].length > 0;
};


const makeGroupsForResults = (props) => (
    queries.map(
        ([name, , Component, title]) => (
            shouldRenderResults(name, props.results) &&
            <Group
                title={title}
                key={name}
                input={props.input}
                results={props.results[name]}
                component={Component}
                handleClickAway={props.handleClickAway}
            />
        )
    ).filter(
        (group) => Boolean(group)
    )
);


const Form = (props) => {
    const groups = makeGroupsForResults(props);
    return (
        <form className="multisearch__multiform" action="/search/">
            {props.children}
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
