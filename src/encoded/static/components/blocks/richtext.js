'use strict';
var React = require('react');
var globals = require('../globals');
var noarg_memoize = require('../../libs/noarg-memoize');
var $script = require('scriptjs');


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
        if (this.context.editable) {
            $script('ckeditor/ckeditor', this.setupEditor);
        }
    },

    setupEditor: function() {
        var ck = require('ckeditor');
        ck.disableAutoInline = true;
        this.editor = ck.inline(this.getDOMNode(), {
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
            <div contentEditable={this.context.editable} dangerouslySetInnerHTML={{__html: this.state.value.body}} />
        );
    }
});


globals.blocks.register({
    label: 'rich text block',
    icon: 'icon icon-file-text',
    schema: noarg_memoize(function() {
        var ReactForms = require('react-forms');
        return ReactForms.schema.Mapping({}, {
            body: ReactForms.schema.Scalar({label: 'HTML Source', input: <textarea rows="15" cols="80" />}),
            className: ReactForms.schema.Scalar({label: 'CSS Class'}),
        });
    }),
    view: RichTextBlockView,
    initial: {
        'body': '<p>This is a new block.</p>'
    }
}, 'richtextblock');
