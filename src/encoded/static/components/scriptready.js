'use strict';
/* Wrapper component to require async script loading.

Example::

    <ScriptReady scripts={['brace']}>
        <Ace />
    </ScriptReady>

*/
var React = require('react');
var $script = require('scriptjs');
var ScriptReady = module.exports = React.createClass({
    propTypes: {
        scripts: React.PropTypes.array,
        spinner: React.PropTypes.element
    },
    getDefaultProps: function() {
        return {
            scripts: [],
            spinner: null,
        }
    },
    getInitialState: function() {
        return {loaded: {}};
    },
    componentDidMount: function() {
        var scripts = this.props.scripts;
        $script(scripts, this.onScriptLoad.bind(null, scripts));
    },
    componentWillReceiveProps: function(nextProps) {
        var loaded = this.state.loaded;
        var scripts = nextProps.scripts;
        if (scripts.filter(name => !loaded[name]).length > 0) {
            $script(scripts, this.onScriptLoad.bind(null, scripts));
        }
    },
    onScriptLoad: function(scripts) {
        var loaded = this.state.loaded;
        scripts.forEach(name => {
            loaded[name] = true;
        });
        this.setState({loaded: loaded});
    },
    render: function() {
        var loaded = this.state.loaded;
        var scripts = this.props.scripts;
        if (scripts.filter(name => !loaded[name]).length > 0) {
            return this.props.spinner;
        }
        return React.Children.only(this.props.children);
    }
});
