import PropTypes from 'prop-types';


/**
* Components for rendering groups of results in search-as-you-type dropdown.
* A Group has a title and renders a specific Results component.
*/


const Title = ({ title }) => (
    <span className="group-title">
        {title}
    </span>
);


Title.propTypes = {
    title: PropTypes.string.isRequired,
};


const Group = (props) => {
    const Component = props.component;
    return (
        <>
            <Title
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


Group.propTypes = {
    title: PropTypes.string.isRequired,
    input: PropTypes.string.isRequired,
    results: PropTypes.array.isRequired,
    handleClickAway: PropTypes.func.isRequired,
    component: PropTypes.func.isRequired,
};


export default Group;
