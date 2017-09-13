import React from 'react';
import PropTypes from 'prop-types';
import { FetchedData, Param } from './fetched';
import * as globals from './globals';


function sortedJson(obj) {
    if (obj instanceof Array) {
        return obj.map(value => sortedJson(value));
    } else if (obj instanceof Object) {
        const sorted = {};
        Object.keys(obj).sort().forEach((key) => {
            sorted[key] = obj[key];
        });
        return sorted;
    }
    return obj;
}


class EditForm extends React.Component {
    constructor() {
        super();

        // Intialize component state.
        this.state = {
            communicating: false,
            data: undefined,
            putRequest: undefined,
            erred: false,
        };

        // Bind `this` to non-React methods.
        this.setupEditor = this.setupEditor.bind(this);
        this.hasErrors = this.hasErrors.bind(this);
        this.save = this.save.bind(this);
        this.receive = this.receive.bind(this);
    }

    componentDidMount() {
        this.setupEditor();
    }

    setupEditor() {
        require.ensure([
            'brace',
            'brace/mode/json',
            'brace/theme/solarized_light',
        ], (require) => {
            const ace = require('brace');
            require('brace/mode/json');
            require('brace/theme/solarized_light');
            const value = JSON.stringify(sortedJson(this.props.data), null, 4);
            const editor = ace.edit(this.editor);
            const session = editor.getSession();
            session.setMode('ace/mode/json');
            editor.setValue(value);
            editor.setOptions({
                maxLines: 1000,
                minLines: 24,
            });
            editor.clearSelection();
            this.setState({ editor });
            session.on('changeAnnotation', this.hasErrors);
        }, 'brace');
    }

    hasErrors() {
        const annotations = this.state.editor.getSession().getAnnotations();
        const hasError = annotations.reduce((value, anno) => value || (anno.type === 'error'), false);
        this.setState({ editor_error: hasError });
    }

    save(e) {
        e.preventDefault();
        const value = this.state.editor.getValue();
        const url = this.props.context['@id'];
        const request = this.context.fetch(url, {
            method: 'PUT',
            headers: {
                'If-Match': this.props.etag,
                Accept: 'application/json',
                'Content-Type': 'application/json',
            },
            body: value,
        });
        request.then((response) => {
            if (!response.ok) throw response;
            return response.json();
        })
        .catch(globals.parseAndLogError.bind(undefined, 'putRequest'))
        .then(this.receive);
        this.setState({
            communicating: true,
            putRequest: request,
        });
    }

    receive(data) {
        const erred = (data['@type'] || []).indexOf('Error') > -1;
        this.setState({
            data,
            communicating: false,
            erred,
            error: erred ? data : undefined,
        });
        if (!erred) this.context.navigate('');
    }

    render() {
        const error = this.state.error;
        return (
            <div>
                <div
                    ref={(div) => { this.editor = div; }}
                    style={{
                        position: 'relative !important',
                        border: '1px solid lightgray',
                        margin: 'auto',
                        width: '100%',
                    }}
                />
                <div style={{ float: 'right', margin: '10px' }}>
                    <a href="" className="btn btn-default">Cancel</a>
                    {' '}
                    <button onClick={this.save} className="btn btn-success" disabled={this.communicating || this.state.editor_error}>Save</button>
                </div>
                <ul style={{ clear: 'both' }}>
                    {error && error.code === 422 ? error.errors.map((err, i) => (
                        <li key={i} className="alert alert-error"><b>{`/${(err.name || []).join('/')}: `}</b><span>{err.description}</span></li>
                    )) : error ? <li className="alert alert-error">{JSON.stringify(error)}</li> : null}
                </ul>
            </div>
        );
    }
}

EditForm.propTypes = {
    context: PropTypes.object.isRequired,
    data: PropTypes.object,
    etag: PropTypes.string,
};

EditForm.defaultProps = {
    data: {},
    etag: '',
};

EditForm.contextTypes = {
    fetch: PropTypes.func,
    navigate: PropTypes.func,
};


const ItemEdit = (props) => {
    const context = props.context;
    const itemClass = globals.itemClass(context, 'view-item');
    const title = globals.listingTitles.lookup(context)({ context });
    const url = `${context['@id']}?frame=edit`;
    return (
        <div className={itemClass}>
            <header className="row">
                <div className="col-sm-12">
                    <h2>Edit {title}</h2>
                </div>
            </header>
            <FetchedData>
                <Param name="data" url={url} etagName="etag" />
                <EditForm {...props} />
            </FetchedData>
        </div>
    );
};

ItemEdit.propTypes = {
    context: PropTypes.object.isRequired,
};

globals.contentViews.register(ItemEdit, 'Item', 'edit-json');
