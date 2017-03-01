'use strict';
var React = require('react');
var globals = require('../globals');


var RichTextBlockView = module.exports.RichTextBlockView = React.createClass({

    contextTypes: {
        editable: React.PropTypes.bool
    },

    getInitialState: function() {
        return {
            'value': this.props.value
        };
    },

    componentWillReceiveProps: function(nextProps) {
        this.setState({value: nextProps.value});
    },

    componentDidMount: function() {
        var $script = require('scriptjs');
        if (this.context.editable) {
            $script('ckeditor/ckeditor', this.setupEditor);
        }
    },

    setupEditor: function() {
        var ck = require('ckeditor');
        ck.disableAutoInline = true;
        this.editor = ck.inline(this.domNode, {
            language: 'en',
            toolbar: [
                { name: 'basicstyles', groups: [ 'basicstyles', 'cleanup' ], items: [ 'Bold', 'Italic', 'Underline', 'Strike', '-', 'RemoveFormat' ] },
                { name: 'styles', items: [ 'Format' ] },
                { name: 'paragraph', groups: [ 'list', 'indent', 'align'], items: [ 'NumberedList', 'BulletedList' ] },
                { name: 'links', items: [ 'Link', 'Unlink', 'Anchor' ] },
                { name: 'undo', groups: [ 'undo' ], items: [ 'Undo', 'Redo' ] },
                { name: 'document', groups: [ 'mode' ], items: [ 'Source' ] },
            ],
            format_tags: 'p;h1;h2;h3;h4;h5;h6;pre;code;cite',
            format_code: { name: 'Inline Code', element: 'code'},
            format_cite: { name: 'Citation', element: 'cite'},
            allowedContent: true
        });
        this.editor.on('change', () => {
            this.state.value.body = this.editor.getData();
            this.setState(this.state);
            this.props.onChange(this.state.value);
        });
    },

    shouldComponentUpdate: function(nextProps, nextState) {
        return (!this.editor || nextState.value.body != this.editor.getData());
    },

    render: function() {
        return (
            <div contentEditable={this.context.editable} dangerouslySetInnerHTML={{__html: this.state.value.body}} ref={(comp) => { this.domNode = comp; }} />
        );
    }
});


globals.blocks.register({
    label: 'rich text block',
    icon: 'icon icon-file-text',
    schema: {
        type: 'object',
        properties: {
            body: {
                title: 'HTML Source',
                type: 'string',
                formInput: <textarea rows="10" />
            },
            className: {
                title: 'CSS Class',
                type: 'string'
            }
        }
    },
    view: RichTextBlockView,
    initial: {
        'body': '<p>This is a new block.</p>'
    }
}, 'richtextblock');
