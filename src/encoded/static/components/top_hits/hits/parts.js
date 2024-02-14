import PropTypes from 'prop-types';


/**
* Wrapper for applying different formatting to string values.
*/
export const Text = (props) => (
    <span className={props.className}>
        {props.value}
    </span>
);


Text.propTypes = {
    value: PropTypes.string.isRequired,
    className: PropTypes.string.isRequired,
};


/**
* Different types of Text components that correspond to parts of a hit
* and allow formatting via classNames.
*/
export const Description = (props) => <Text className="item-description" value={props.value} />;

export const Authors = (props) => <Text className="item-authors" value={props.value} />;

export const Accession = (props) => <Text className="item-accession" value={props.value} />;

export const Title = (props) => <Text className="item-title" value={props.value} />;

export const Target = (props) => <Text className="item-target" value={props.value} />;

export const Organism = (props) => <Text className="item-organism" value={props.value} />;

export const Other = (props) => <Text className="item-other" value={props.value} />;


Description.propTypes = { value: PropTypes.string.isRequired };

Authors.propTypes = { value: PropTypes.string.isRequired };

Accession.propTypes = { value: PropTypes.string.isRequired };

Target.propTypes = { value: PropTypes.string.isRequired };

Title.propTypes = { value: PropTypes.string.isRequired };

Organism.propTypes = { value: PropTypes.string.isRequired };

Other.propTypes = { value: PropTypes.string.isRequired };


/**
* Maps a field to the formatting component used to style
* that part of the hit.
*/
export const fieldToComponent = {
    name: Accession,
    title: Title,
    annotationType: Title,
    target: Target,
    biosample: Other,
    organism: Organism,
    details: Other,
    lotId: Other,
    authors: Authors,
    description: Description,
};
