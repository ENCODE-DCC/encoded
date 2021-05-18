import _ from 'underscore';
import PropTypes from 'prop-types';
import {
    Input,
    InputWithIcon,
} from './input';
import {
    queries
} from './constants';


const shouldRenderResults = (name, results) => {
    return results[name] && results[name].length > 0;
};


const GroupTitle = ({title}) => (
    <div className="top-hits-search__results">
        <span className="group-title">
            {title}
        </span>
    </div>
);


const Group = (props) => {
    const Component = props.component;
    return (
        <>
            <GroupTitle
                title={props.title}
            />
            <Component
                input={props.input}
                results={props.results}
                handleClickAway={props.handleClickAway}
            />
        </>
    );
};


/** Renders the input and dropdown (if there are any results). */
const MultiResultsForm = (props) => {
    const results = queries.map(
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
        (value) => Boolean(value)
    );
    return (
        <form className="multisearch__multiform" action="/search/">
            {props.children}
            {
                results.length > 0 &&
                <div className="multisearch__results-container">
                    {results}
                </div>
            }
        </form>
    );
};


MultiResultsForm.propTypes = {
    children: PropTypes.element.isRequired,
    input: PropTypes.string.isRequired,
    results: PropTypes.object.isRequired,
    handleClickAway: PropTypes.func.isRequired,
};


/** Uses input form with icon */
export const MultiResultsNavBarForm = (props) => (
    <MultiResultsForm {...props}>
        <InputWithIcon
            input={props.input}
            onChange={props.handleInputChange}
        />
    </MultiResultsForm>
);


/** Required but set in cloneElement */
MultiResultsNavBarForm.propTypes = {
    input: PropTypes.string,
    handleInputChange: PropTypes.func,
};


MultiResultsNavBarForm.defaultProps = {
    input: null,
    handleInputChange: null,
};
