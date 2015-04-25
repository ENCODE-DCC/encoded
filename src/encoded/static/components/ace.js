'use strict';
var React = require('react');
var Ace = module.exports = React.createClass({
  propTypes: {
    mode: React.PropTypes.string,
    theme: React.PropTypes.string,
    value: React.PropTypes.string,
    options: React.PropTypes.object,
    onChange: React.PropTypes.func,
    onChangeAnnotation: React.PropTypes.func,
    style: React.PropTypes.object,
  },
  getDefaultProps: function() {
    return {
      mode: 'ace/theme/text',
      theme: 'ace/theme/textmate',
      value: '',
      options: {},
      style: {}
    };
  },
  onChange: function() {
    if (this.props.onChange) {
      this.props.onChange(this.editor.getValue());
    }
  },
  onChangeAnnotation: function() {
    if (this.props.onChangeAnnotation) {
      this.props.onChangeAnnotation(this.editor);
    }
  },
  componentDidMount: function() {
    var ace = require('brace');
    var editor = this.editor = ace.edit(this.refs.editor.getDOMNode());
    editor.setOptions(this.props.options);
    editor.setTheme(this.props.theme);
    var session = this.session = editor.getSession();
    session.setMode(this.props.mode);
    session.setValue(this.props.value);
    session.on('change', this.onChange);
    session.on('changeAnnotation', this.onChangeAnnotation);
  },
  componentWillReceiveProps: function(nextProps) {
    var editor = this.editor;
    editor.setOptions(this.props.options);
    editor.setTheme(this.props.theme);
    var session = editor.getSession();
    session.setMode(this.props.mode);
    if (session.getValue() !== nextProps.value) {
      session.setValue(nextProps.value);
    }
  },
  render: function() {
    return (<div ref="editor" style={this.props.style}></div>);
  }
});
