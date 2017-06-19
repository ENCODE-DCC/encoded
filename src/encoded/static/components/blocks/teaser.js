import React from 'react';
import PropTypes from 'prop-types';
import _ from 'underscore';
import { FetchedData, Param } from '../fetched';
import globals from '../globals';
import { ObjectPicker } from '../inputs';
import { ItemBlockView } from './item';
import { RichTextBlockView } from './richtext';


class TeaserCore extends React.Component {
    constructor() {
        super();

        // Bind this to non-React methods.
        this.renderImage = this.renderImage.bind(this);
    }

    renderImage() {
        const context = this.props.value.image;
        if (typeof context === 'object') {
            return <ItemBlockView context={context} />;
        }
        if (typeof context === 'string') {
            return (
                <FetchedData>
                    <Param name="context" url={context} />
                    <ItemBlockView />
                </FetchedData>
            );
        }
        return null;
    }

    render() {
        // Must work with both paths (edit form) and embedded objects (display)
        return (
            <div className="teaser thumbnail clearfix">
                {this.renderImage()}
                <div className="caption" dangerouslySetInnerHTML={{ __html: this.props.value.body }} />
            </div>
        );
    }
}

TeaserCore.propTypes = {
    value: PropTypes.object.isRequired,
};


class TeaserBlockView extends React.Component {
    shouldComponentUpdate(nextProps) {
        return (!_.isEqual(nextProps.value, this.props.value));
    }

    render() {
        return (
            <div>
                {this.props.value.href ?
                    <a className="img-link" href={this.props.value.href}>
                        <TeaserCore {...this.props} />
                    </a>
                :
                    <div>
                        <TeaserCore {...this.props} />
                    </div>
                }
            </div>
        );
    }
}

TeaserBlockView.propTypes = {
    value: PropTypes.object,
};

TeaserBlockView.defaultProps = {
    value: {
        href: '#',
        image: '',
        body: ' ',
    },
};


class RichEditor extends React.Component {
    constructor(props) {
        super(props);

        // Set initial React component state.
        this.state = { value: { body: this.props.value || '<p></p>' } };

        // Bind this to non-React components.
        this.onChange = this.onChange.bind(this);
    }

    getChildContext() {
        return { editable: true };
    }

    onChange(value) {
        this.props.onChange(value.body);
    }

    render() {
        return (
            <div className="form-control" style={{ height: 'auto' }}>
                <RichTextBlockView {...this.props} value={this.state.value} onChange={this.onChange} />
            </div>
        );
    }
}

RichEditor.propTypes = {
    value: PropTypes.object,
    onChange: PropTypes.func,
};

RichEditor.defaultProps = {
    value: undefined,
    onChange: null,
};

RichEditor.childContextTypes = {
    editable: PropTypes.bool,
};


const displayModeSelect = (
    <div><select>
        <option value="">default</option>
    </select></div>
);
const imagePicker = <ObjectPicker searchBase={'?mode=picker&type=image'} />;

globals.blocks.register({
    label: 'teaser block',
    icon: 'icon icon-image',
    schema: {
        type: 'object',
        properties: {
            display: {
                title: 'Display Layout',
                type: 'string',
                formInput: displayModeSelect,
            },
            image: {
                title: 'Image',
                type: 'string',
                formInput: imagePicker,
            },
            body: {
                title: 'Caption',
                type: 'string',
                formInput: <RichEditor />,
            },
            href: {
                title: 'Link URL',
                type: 'string',
            },
            className: {
                title: 'CSS Class',
                type: 'string',
            },
        },
    },
    view: TeaserBlockView,
}, 'teaserblock');
