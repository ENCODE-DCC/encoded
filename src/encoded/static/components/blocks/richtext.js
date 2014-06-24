/** @jsx React.DOM */
'use strict';
var React = require('react');
var globals = require('../globals');

var ReactForms = require('react-forms');
var Schema = ReactForms.schema.Schema;
var Property = ReactForms.schema.Property;


var RichTextBlockView = React.createClass({

    getInitialState: function() {
        return {
            'value': this.props.value
        };
    },

    componentWillReceiveProps: function(nextProps) {
        this.setState({value: nextProps.value});
    },

    componentDidMount: function() {
        if (this.props.editable) {
            $script('scribe', this.setupEditor);
        }
    },

    setupEditor: function() {
        var Scribe = require('scribe-editor');
        this.editor = new Scribe(this.getDOMNode());
        this.editor.on('content-changed', function() {
            this.state.value.body = this.editor.getHTML();
            this.setState(this.state);
            this.props.onChange(this.state.value);
        }.bind(this));
    },

    shouldComponentUpdate: function(nextProps, nextState) {
        return (!this.editor || nextState.value.body != this.editor.getHTML());
    },

    render: function() {
        return (
            <div contentEditable={this.props.editable} dangerouslySetInnerHTML={{__html: this.state.value.body}} />
        );
    }
});


globals.blocks.register({
    label: 'rich text block',
    icon: 'icon-file-alt',
    schema: (
        <Schema>
          <Property name="body" label="HTML Source" input={<textarea rows="15" cols="80" />} />
        </Schema>
    ),
    view: RichTextBlockView,
    initial: {
        'body': '<p>This is a new block.</p>'
    }
}, 'richtextblock');
