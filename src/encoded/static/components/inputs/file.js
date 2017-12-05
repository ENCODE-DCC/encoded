import React from 'react';
import PropTypes from 'prop-types';


export default class FileInput extends React.Component {
    static onDragOver(e) {
        e.dataTransfer.dropEffect = 'copy';
        e.preventDefault();  // indicate we are going to handle the drop
    }

    constructor() {
        super();

        // Bind this to non-React methods
        this.onDrop = this.onDrop.bind(this);
        this.onChange = this.onChange.bind(this);
    }

    onDrop(e) {
        const file = e.dataTransfer.files[0];
        this.onChange(null, file);
        e.preventDefault();
    }

    onChange(e, file) {
        let rFile = file;
        if (rFile === undefined) {
            const input = this.refs.input;
            rFile = input.files[0];
        }
        const reader = new FileReader();
        reader.onloadend = () => {
            const value = {
                download: rFile.name,
                type: rFile.type || undefined,
                href: reader.result,
            };
            this.props.onChange(value);
        };
        if (rFile) {
            reader.readAsDataURL(rFile);
        }
    }

    render() {
        const value = this.props.value || {};
        const mimetype = value.type;
        const preview = (mimetype && mimetype.indexOf('image/') === 0) ? <img src={value.href} alt="File" width="128" /> : '';
        const filename = value.download;
        return (
            <div className={`dropzone${this.props.disabled ? ' disabled' : ''}`} onDragOver={FileInput.onDragOver} onDrop={this.onDrop}>
                <div className="drop">
                    {filename ? <div>
                        <a href={value.href} target="_blank" rel="noopener noreferrer">{filename}</a>
                    </div> : ''}
                    <div>{preview}</div>
                    <br />Drop a {filename ? 'replacement' : ''} file here.
                    Or <input ref="input" type="file" onChange={this.onChange} disabled={this.props.disabled} />
                    <br /><br />
                </div>
            </div>
        );
    }
}

FileInput.propTypes = {
    value: PropTypes.object.isRequired,
    disabled: PropTypes.bool,
    onChange: PropTypes.func.isRequired,
};

FileInput.defaultProps = {
    disabled: false,
};
