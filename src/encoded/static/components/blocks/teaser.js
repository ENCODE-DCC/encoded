'use strict';
var React = require('react');
import PropTypes from 'prop-types';
import createReactClass from 'create-react-class';
var fetched = require('../fetched');
var globals = require('../globals');
var item = require('./item');
var richtext = require('./richtext');
var _ = require('underscore');

var ItemBlockView = item.ItemBlockView;
var ObjectPicker = require('../inputs').ObjectPicker;
var RichTextBlockView = richtext.RichTextBlockView;


var TeaserCore = createReactClass({
    renderImage: function() {
        var context = this.props.value.image;
        if (typeof context === 'object') {
            return <ItemBlockView context={context} />;
        }
        if (typeof context === 'string') {
            return (
                <fetched.FetchedData>
                    <fetched.Param name="context" url={context} />
                    <ItemBlockView />
                </fetched.FetchedData>
            );
        }
        return null;
    },

    render: function() {
        var image = this.props.value.image;
        // Must work with both paths (edit form) and embedded objects (display)
        return (
            <div className="teaser thumbnail clearfix">
                {this.renderImage()}
                <div className="caption" dangerouslySetInnerHTML={{__html: this.props.value.body}}></div>
            </div>
        );
    }
});


var TeaserBlockView = createReactClass({

    getDefaultProps: function() {
        return {value: {
            href: '#',
            image: '',
            body: ' ',
        }};
    },

    shouldComponentUpdate: function(nextProps) {
        return (!_.isEqual(nextProps.value, this.props.value));
    },

    render: function() {
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
});


var RichEditor = createReactClass({

    childContextTypes: {
        editable: PropTypes.bool
    },

    getChildContext: function() {
        return {editable: true};
    },

    getInitialState: function() {
        return {value: {body: this.props.value || '<p></p>'}};
    },

    render: function() {
        return (
            <div className="form-control" style={{height: 'auto'}}>
                <RichTextBlockView {...this.props} value={this.state.value} onChange={this.onChange} />
            </div>
        );
    },

    onChange: function(value) {
        this.props.onChange(value.body);
    }
});



var displayModeSelect = (
    <div><select>
        <option value="">default</option>
    </select></div>
);
var imagePicker = <ObjectPicker searchBase={"?mode=picker&type=image"} />;

globals.blocks.register({
    label: 'teaser block',
    icon: 'icon icon-image',
    schema: {
        type: 'object',
        properties: {
            display: {
                title: 'Display Layout',
                type: 'string',
                formInput: displayModeSelect
            },
            image: {
                title: 'Image',
                type: 'string',
                formInput: imagePicker
            },
            body: {
                title: 'Caption',
                type: 'string',
                formInput: <RichEditor />
            },
            href: {
                title: 'Link URL',
                type: 'string'
            },
            className: {
                title: 'CSS Class',
                type: 'string'
            }
        }
    },
    view: TeaserBlockView
}, 'teaserblock');
