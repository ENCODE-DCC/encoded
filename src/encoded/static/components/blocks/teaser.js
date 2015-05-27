'use strict';
var React = require('react');
var fetched = require('../fetched');
var globals = require('../globals');
var item = require('./item');
var noarg_memoize = require('../../libs/noarg-memoize');
var richtext = require('./richtext');
var _ = require('underscore');

var ItemBlockView = item.ItemBlockView;
var ObjectPicker = require('../inputs').ObjectPicker;
var RichTextBlockView = richtext.RichTextBlockView;


var TeaserCore = React.createClass({
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


var TeaserBlockView = React.createClass({

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


var RichEditor = React.createClass({

    childContextTypes: {
        editable: React.PropTypes.bool
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
    schema: noarg_memoize(function() {
        var ReactForms = require('react-forms');
        var Scalar = ReactForms.schema.Scalar;
        return ReactForms.schema.Mapping({}, {
            display: Scalar({label: "Display Layout", input: displayModeSelect, defaultValue: "search"}),
            image: Scalar({label: "Image", input: imagePicker}),
            body: Scalar({label: "Caption", input: <RichEditor />}),
            href: Scalar({label: "Link URL"}),
            className: Scalar({label: 'CSS Class'}),
        });
    }),
    view: TeaserBlockView
}, 'teaserblock');
