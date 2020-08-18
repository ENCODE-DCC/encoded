import React from 'react';
import PropTypes from 'prop-types';


/**
 * Depending on the filename extension, adjust the type and base64-encoded contents from the
 * defaults that FileReader assigns. Return unchanged results for any file types that don't need
 * special treatment.
 * @param {object} rFile Object from <input type="file" />
 * @param {string} readerResult FileReader `result` property.
 *
 * @return {object} -
 *   type - mime type for file
 *   href - base64-encoded contents of file
 */
const adjustFileValues = (rFile, readerResult) => {
    let type = rFile.type;
    let href = readerResult;

    // https://stackoverflow.com/questions/190852/how-can-i-get-file-extensions-with-javascript/1203361#answer-12900504
    const extension = rFile.name.slice((Math.max(0, rFile.name.lastIndexOf('.')) || Infinity) + 1);

    // Add to this `if` as more attachment file types need special treatment. Change to a `switch`
    // if convenient.
    if (extension === 'as') {
        // .as AutoSQL files.
        type = 'text/autosql';
        href = readerResult.replace(/^(data:).+?(;.*)$/, '$1text/autosql$2');
    }

    return {
        type,
        href,
    };
};


export default class FileInput extends React.Component {
    static onDragOver(e) {
        e.dataTransfer.dropEffect = 'copy';
        e.preventDefault(); // indicate we are going to handle the drop
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
            const input = this.input;
            rFile = input.files[0];
        }
        const reader = new FileReader();
        reader.onloadend = () => {
            // Fill in the attachment values for edited object PUT requests. Some file types need
            // special adjustments.
            const { type, href } = adjustFileValues(rFile, reader.result);
            const value = {
                download: rFile.name,
                type: type || undefined,
                href,
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
                    {filename ?
                        <div>
                            <a href={value.href} target="_blank" rel="noopener noreferrer">{filename}</a>
                        </div>
                    : ''}
                    <div>{preview}</div>
                    <br />Drop a {filename ? 'replacement' : ''} file here.
                    Or <input ref={(input) => { this.input = input; }} type="file" onChange={this.onChange} disabled={this.props.disabled} />
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
