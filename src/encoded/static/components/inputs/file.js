'use strict';
var React = require('react');


var FileInput = module.exports.FileInput = React.createClass({

    getInitialState: function() {
        return {
            value: this.props.value || {},
        };
    },

    componentWillReceiveProps: function(nextProps) {
        this.setState({value: nextProps.value});
    },

    render: function() {
        var mimetype = this.state.value.type;
        var preview = (mimetype && mimetype.indexOf('image/') === 0) ? <img src={this.state.value.href} width="128" /> : '';
        var filename = this.state.value.download;
        return (
            <div className="dropzone" onDragOver={this.onDragOver} onDrop={this.onDrop}>
                <div className="drop">
                    {filename ? <div>
                        <a href={this.state.value.href} target="_blank">{filename}</a>
                    </div> : ''}
                    <div>{preview}</div>
                    <br />Drop a {filename ? 'replacement' : ''} file here.
                    Or <input ref="input" type="file" onChange={this.onChange} />
                    <br /><br />
                </div>      
            </div>
        );
    },

    onDragOver: function(e) {
        e.dataTransfer.dropEffect = 'copy';
        e.preventDefault();  // indicate we are going to handle the drop
    },

    onDrop: function(e) {
        var file = e.dataTransfer.files[0];
        this.onChange(null, file);
        e.preventDefault();
    },

    onChange: function(e, file) {
        if (file === undefined) {
            var input = this.refs.input.getDOMNode();
            file = input.files[0];
        }
        var reader = new FileReader();
        reader.onloadend = function() {
            var value = {
                download: file.name,
                type: file.type,
                href: reader.result
            };
            this.props.onChange(value);
        }.bind(this);
        if (file) {
            reader.readAsDataURL(file);
        }
    }
});

module.exports = FileInput;
