/** @jsx React.DOM */
'use strict';
var React = require('react');
var FetchedData = require('../fetched').FetchedData;
var globals = require('../globals');
var item = require('./item');
var richtext = require('./richtext');
var _ = require('underscore');

var ReactForms = require('react-forms');
var Schema = ReactForms.schema.Schema;
var Property = ReactForms.schema.Property;

var ItemBlockView = item.ItemBlockView;
var ObjectPicker = item.ObjectPicker;
var RichTextBlockView = richtext.RichTextBlockView;


var TeaserBlockView = React.createClass({

    getDefaultProps: function() {
        return {value: {
            href: '#',
            image: '',
            caption: '',
        }};
    },

    shouldComponentUpdate: function(nextProps) {
        return (!_.isEqual(nextProps.value, this.props.value));
    },

    render: function() {
        var url = this.props.value.image;
        if (url && url.indexOf('/') !== 0) {
            url = '/' + url;
        }
        return (
            <a className="img-link" href={this.props.value.href}>
              <div className="teaser thumbnail">
                <FetchedData url={url} Component={ItemBlockView} loadingComplete={true} />
                <div className="caption" dangerouslySetInnerHTML={{__html: this.props.value.body}}></div>
              </div>
            </a>
        );
    }
});


var RichEditor = React.createClass({

    childContextTypes: {
        editable: React.PropTypes.bool
    },

    getChildContext: function() {
        return {editable: true}
    },

    getInitialState: function() {
        return {value: {body: this.props.value}};
    },

    render: function() {
        return (
            <div className="form-control" style={{height: 'auto'}}>
                {this.transferPropsTo(<RichTextBlockView value={this.state.value} onChange={this.onChange} />)}
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
    icon: 'icon-link',
    schema: (
        <Schema>
          <Property name="display" label="Display Layout" input={displayModeSelect} defaultValue="search" />
          <Property name="image" label="Image" input={imagePicker} />
          <Property name="body" label="Caption" input={<RichEditor />} />
          <Property name="href" label="Link URL" />
        </Schema>
    ),
    view: TeaserBlockView
}, 'teaserblock');
