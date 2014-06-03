/** @jsx React.DOM */
'use strict';
var React = require('react');
var globals = require('../globals');


var RichTextBlockView = module.exports.RichTextBlockView = React.createClass({

    getInitialState: function() {
        return {
            'value': this.props.value
        }
    },

    componentWillReceiveProps: function(nextProps) {
        this.setState({value: nextProps.value});
    },

    componentDidMount: function() {
        if (this.props.editable) {
            $script('ckeditor/ckeditor', this.setupEditor);
        }
    },

    setupEditor: function() {
        var ck = window.CKEDITOR;
        ck.disableAutoInline = true;
        this.editor = ck.inline(this.getDOMNode(), {
            toolbar: [
                { name: 'basicstyles', groups: [ 'basicstyles', 'cleanup' ], items: [ 'Bold', 'Italic', 'Underline', 'Strike', '-', 'RemoveFormat' ] },
                { name: 'styles', items: [ 'Format' ] },
                { name: 'paragraph', groups: [ 'list', 'indent', 'align'], items: [ 'NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock' ] },
                { name: 'links', items: [ 'Link', 'Unlink', 'Anchor' ] },
                { name: 'undo', groups: [ 'undo' ], items: [ 'Undo', 'Redo' ] },
                { name: 'document', groups: [ 'mode' ], items: [ 'Source' ] },
            ],
        });
        this.editor.on('change', function() {
            this.state.value.body = this.editor.getData();
            this.setState(this.state);
            this.props.onChange(this.state.value);
        }.bind(this));
    },

    shouldComponentUpdate: function(nextProps, nextState) {
        return (!this.editor || nextState.value.body != this.editor.getData());
    },

    render: function() {
        return (
            <div contentEditable={this.props.editable} dangerouslySetInnerHTML={{__html: this.state.value.body}} />
        );
    }
});


globals.block_views.register(RichTextBlockView, 'richtextblock');
