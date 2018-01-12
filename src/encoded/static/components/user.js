/** @preventMunge */
/* ^ see http://stackoverflow.com/questions/30110437/leading-underscore-transpiled-wrong-with-es6-classes */

import React from 'react';
import PropTypes from 'prop-types';
import ItemStore from './lib/store';
import { Modal, ModalHeader, ModalBody } from '../libs/bootstrap/modal';
import { Form } from './form';
import * as globals from './globals';
import { Breadcrumbs } from './navigation';


class AccessKeyStore extends ItemStore {
    resetSecret(id) {
        this.fetch(`${id}reset-secret`, {
            method: 'POST',
        }, response => this.dispatch('onResetSecret', response));
    }
}


class AccessKeyTable extends React.Component {
    constructor(props, context) {
        super(props, context);
        const accessKeys = this.props.access_keys;
        this.store = new AccessKeyStore(accessKeys, this, 'access_keys');

        // Set initial React state.
        this.state = { access_keys: accessKeys };

        // Bind this to non-React methods.
        this.create = this.create.bind(this);
        this.doAction = this.doAction.bind(this);
        this.onCreate = this.onCreate.bind(this);
        this.onResetSecret = this.onResetSecret.bind(this);
        this.showNewSecret = this.showNewSecret.bind(this);
        this.onDelete = this.onDelete.bind(this);
        this.onError = this.onError.bind(this);
        this.hideModal = this.hideModal.bind(this);
    }

    onDelete(item) {
        this.setState({
            modal: (
                <Modal closeModal={this.hideModal}>
                    <ModalHeader title={'Access key deleted.'} closeModal={this.hideModal} />
                    <ModalBody>
                        <p>{`Access key ${item.access_key_id} has been deleted.`}</p>
                    </ModalBody>
                </Modal>
            ),
        });
    }

    onError(error) {
        const View = globals.contentViews.lookup(error);
        this.setState({
            modal: (
                <Modal closeModal={this.hideModal}>
                    <ModalHeader title="Error" closeModal={this.hideModal} />
                    <ModalBody>
                        <View context={error} loadingComplete />
                    </ModalBody>
                </Modal>
            ),
        });
    }

    onResetSecret(response) {
        this.showNewSecret('Your secret key has been reset.', response);
    }

    onCreate(response) {
        this.showNewSecret('Your secret key has been created.', response);
    }

    create(e) {
        e.preventDefault();
        const item = {};
        if (this.props.user['@id'] !== this.context.session_properties.user['@id']) {
            item.user = this.props.user['@id'];
        }
        this.store.create('/access-keys/', item);
    }

    doAction(action, arg) {
        this.store[action](arg);
    }

    showNewSecret(title, response) {
        this.setState({
            modal: (
                <Modal closeModal={this.hideModal}>
                    <ModalHeader title={title} closeModal={this.hideModal} />
                    <ModalBody>
                        Please make a note of the new secret access key.
                        This is the last time you will be able to view it.
                        <dl className="key-value">
                            <div data-test="accesskeyid">
                                <dt>Access Key ID</dt>
                                <dd>{response.access_key_id}</dd>
                            </div>
                            <div data-test="secretaccesskey">
                                <dt>Secret Access Key</dt>
                                <dd>{response.secret_access_key}</dd>
                            </div>
                        </dl>
                    </ModalBody>
                </Modal>
            ),
        });
    }

    hideModal() {
        this.setState({ modal: null });
    }

    render() {
        return (
            <div>
                <button className="btn btn-success" onClick={this.create}>Add Access Key</button>
                {this.state.access_keys.length ?
                    <table className="table">
                        <thead>
                            <tr>
                                <th>Access Key ID</th>
                                <th>Description</th>
                                <th />
                            </tr>
                        </thead>
                        <tbody>
                            {this.state.access_keys.map(k =>
                                <tr key={k.access_key_id}>
                                    <td>{k.access_key_id}</td>
                                    <td>{k.description}</td>
                                    <AccessKeyActions doAction={this.doAction} accessKeyId={k['@id']} />
                                </tr>
                            )}
                        </tbody>
                    </table>
                : ''}
                {this.state.modal}
            </div>
        );
    }
}

AccessKeyTable.propTypes = {
    user: PropTypes.object.isRequired,
    access_keys: PropTypes.array,
};

AccessKeyTable.defaultProps = {
    access_keys: null,
};

AccessKeyTable.contextTypes = {
    fetch: PropTypes.func,
    session_properties: PropTypes.object,
};


class AccessKeyActions extends React.Component {
    constructor() {
        super();

        // Bind this to non-React methods.
        this.doActionReset = this.doActionReset.bind(this);
        this.doActionDelete = this.doActionDelete.bind(this);
    }

    doActionReset(e) {
        e.preventDefault();
        this.props.doAction('resetSecret', this.props.accessKeyId);
    }

    doActionDelete(e) {
        e.preventDefault();
        this.props.doAction('delete', this.props.accessKeyId);
    }

    render() {
        return (
            <td>
                <a href="" onClick={this.doActionReset}>reset</a>
                {' '}<a href="" onClick={this.doActionDelete}>delete</a>
            </td>
        );
    }
}

AccessKeyActions.propTypes = {
    doAction: PropTypes.func.isRequired,
    accessKeyId: PropTypes.string.isRequired,
};


const User = (props) => {
    const context = props.context;
    const crumbs = [
        { id: 'Users' },
    ];
    return (
        <div>
            <header className="row">
                <Breadcrumbs root="/search/?type=user" crumbs={crumbs} />
                <div className="col-sm-12">
                    <h1 className="page-title">{context.title}</h1>
                </div>
            </header>
            <div className="panel data-display">
                <dl className="key-value">
                    <div>
                        <dt>Title</dt>
                        <dd>{context.job_title}</dd>
                    </div>
                    <div>
                        <dt>Lab</dt>
                        <dd>{context.lab ? context.lab.title : ''}</dd>
                    </div>
                </dl>
            </div>
            {context.email ?
                <div>
                    <h3>Contact Info</h3>
                    <div className="panel data-display">
                        <dl className="key-value">
                            <dt>Email</dt>
                            <dd><a href={`mailto:${context.email}`}>{context.email}</a></dd>
                        </dl>
                    </div>
                </div>
            : ''}
            {context.access_keys ?
                <div className="access-keys">
                    <h3>Access Keys</h3>
                    <div className="panel data-display">
                        <AccessKeyTable user={context} access_keys={context.access_keys} />
                    </div>
                </div>
            : ''}
        </div>
    );
};

User.propTypes = {
    context: PropTypes.object.isRequired, // User object from DB
};

globals.contentViews.register(User, 'User');


const ImpersonateUserSchema = {
    type: 'object',
    properties: {
        user: {
            title: 'User',
            linkTo: ['User'],
        },
    },
};


class ImpersonateUserForm extends React.Component {
    constructor(props, context) {
        super(props, context);

        // Bind this to non-React methods.
        this.finished = this.finished.bind(this);
    }

    finished() {
        this.context.navigate('/');
    }

    render() {
        return (
            <div>
                <h2>Impersonate User</h2>
                <Form
                    schema={ImpersonateUserSchema}
                    submitLabel="Submit"
                    method="POST"
                    action="/impersonate-user"
                    onFinish={this.finished}
                />
            </div>
        );
    }
}

ImpersonateUserForm.contextTypes = {
    navigate: PropTypes.func.isRequired,
};

globals.contentViews.register(ImpersonateUserForm, 'Portal', 'impersonate-user');
