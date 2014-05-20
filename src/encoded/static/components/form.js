/** @jsx React.DOM */
'use strict';
var React = require('react');
var ReactForms = require('react-forms');
var parseError = require('./mixins').parseError;
var globals = require('./globals');

// Override pieces of react-forms to use bootstrap classes :-[

var invariant         = require('react/lib/invariant');
var FormElementMixin  = require('react-forms/lib/FormElementMixin');
var schema            = require('react-forms/lib/schema');
var FieldsetMixin     = require('react-forms/lib/FieldsetMixin');
var RepeatingFieldset = require('react-forms/lib/RepeatingFieldset');
var cx                = require('react/lib/cx');
var mergeInto         = require('react/lib/mergeInto');
var FieldMixin        = require('react-forms/lib/FieldMixin');
var Message           = require('react-forms/lib/Message');


var Field = React.createClass({
  mixins: [FieldMixin],

  propTypes: {
    label: React.PropTypes.string
  },

  renderLabel: function(props) {
    var schema = this.schema();
    var label = this.props.label ? this.props.label : schema.props.label;
    var hint = this.props.hint ? this.props.hint : schema.props.hint;
    var labelProps = {};
    if (props) {
      mergeInto(labelProps, props);
    }
    return (label || hint) && React.DOM.label(labelProps,
      label,
      hint && <p className="help-block">{hint}</p>);
  },

  render: function() {
    var validation = this.validationLens().val();

    var className = cx({
      'form-group': true,
      'has-error': validation.isFailure
    });

    var id = this._rootNodeID;

    return (
      <div className={className}>
        {this.renderLabel({htmlFor: id})}
        {this.transferPropsTo(this.renderInputComponent({id, className: 'form-control'}))}
        {validation.isFailure &&
          <Message>{validation.validation.failure}</Message>}
      </div>
    );
  }
});


var Fieldset = React.createClass({
    mixins: [FieldsetMixin],

    render: function() {
      var schema = this.schema();
      return this.transferPropsTo(
        <fieldset>
          {schema.props.label && <legend>{schema.props.label}</legend>}
          {schema.map(createComponentFromSchema)}
        </fieldset>
      );
    }

});


/**
 * Create a component which represents provided schema node
 *
 * @private
 * @param {SchemaNode} node
 * @returns {ReactComponent}
 */
function createComponentFromSchema(node) {
  if (node.props.component) {
    return node.props.component({key: node.name, name: node.name});
  }

  if (schema.isList(node)) {
    return <RepeatingFieldset key={node.name} name={node.name} />;
  } else if (schema.isSchema(node)) {
    return <Fieldset key={node.name} name={node.name} />;
  } else if (schema.isProperty(node)) {
    return <Field key={node.name} name={node.name} />;
  } else {
    invariant(false, 'invalid schema node: %s', node);
  }
}


/**
 * A "proxy" component which renders into field, fieldset or repeating fieldset
 * based on a current schema node.
 */
var FormFor = module.exports.FormFor = React.createClass({
  mixins: [FormElementMixin],

  propTypes: {
    name: React.PropTypes.string
  },

  render: function() {
    return this.transferPropsTo(createComponentFromSchema(this.schema()));
  }
});


var Form = module.exports.Form = React.createClass({
    mixins: [ReactForms.FormMixin],

    // make sure the Form finds the data from FetchedData
    getDefaultProps: function() {
        return {
            value: this.props.data
        }
    },

    render: function() {
        var error = this.state.error;
        return (
          <form>
            <FormFor />
            <div className="pull-right">
                <a href="" className="btn btn-default">Cancel</a>
                {' '}
                <button onClick={this.save} className="btn btn-success" disabled={this.communicating || this.state.editor_error}>Save</button>
            </div>
            <ul style={{clear: 'both'}}>
                {error && error.code === 422 ? error.errors.map(function (error) {
                    return <li className="alert alert-error"><b>{'/' + error.name.join('/') + ': '}</b><span>{error.description}</span></li>;
                }) : error ? <li className="alert alert-error">{JSON.stringify(error)}</li> : null}
            </ul>
          </form>
        )
    },

    save: function() {
        var $ = require('jquery');
        var value = this.state.value;
        var method = this.props.method;
        var url = this.props.action;
        var xhr = $.ajax({
            url: url,
            type: method,
            contentType: "application/json",
            data: JSON.stringify(value),
            dataType: 'json',
            headers: {'If-Match': this.props.etag}
        }).fail(this.fail)
        .done(this.receive);
        xhr.href = url;
        this.setState({
            communicating: true,
            putRequest: xhr
        });
        xhr.done(this.finish);
        return false;
    },

    finish: function (data) {
        this.props.navigate(data['@graph'][0]['@id']);
    },

    fail: function (xhr, status, error) {
        if (status == 'abort') return;
        var ga = window.ga;
        var data = parseError(xhr, status);
        ga('send', 'exception', {
            'exDescription': 'putRequest:' + status + ':' + xhr.statusText,
            'location': window.location.href
        });
        this.receive(data, status, xhr, true);
    },

    receive: function (data, status, xhr, erred) {
        this.setState({
            data: data,
            communicating: false,
            erred: erred,
            error: erred ? data : undefined
        });
    }
});
