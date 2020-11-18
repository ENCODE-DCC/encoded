/** @preventMunge */
/* ^ see http://stackoverflow.com/questions/30110437/leading-underscore-transpiled-wrong-with-es6-classes */

import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { Panel, PanelHeading, PanelBody } from '../libs/ui/panel';
import ItemStore from './lib/store';
import { Modal, ModalHeader, ModalBody, ModalFooter } from '../libs/ui/modal';
import { cartRemoveElements } from './cart';
import { Form } from './form';
import * as globals from './globals';
import { ItemAccessories, TopAccessories } from './objectutils';
import { SortTablePanel, SortTable } from './sorttable';


/**
 * Item store that adds a `resetSecret` method to reset the access key secret.
 */
class AccessKeyStore extends ItemStore {
    resetSecret(id) {
        this.fetch(`${id}reset-secret`, {
            method: 'POST',
        }, response => this.dispatch('onResetSecret', response));
    }
}


/**
 * Displays and reacts to the Reset and Delete controls in the access key table.
 */
class AccessKeyActions extends React.Component {
    constructor() {
        super();
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
            <div className="access-keys__actions">
                <button onClick={this.doActionReset} className="btn btn-info btn-sm">Reset</button>
                <button onClick={this.doActionDelete} className="btn btn-danger btn-sm">Delete</button>
            </div>
        );
    }
}

AccessKeyActions.propTypes = {
    /** Callback to perform access key store action */
    doAction: PropTypes.func.isRequired,
    /** Access key  */
    accessKeyId: PropTypes.string.isRequired,
};


/**
 * Defines the columns of the access key table.
 */
const accessKeyColumns = {
    access_key_id: {
        title: 'Access key ID',
        sorter: false,
    },
    description: {
        title: 'Description',
        sorter: false,
    },
    actions: {
        title: 'Actions',
        display: (item, meta) => <AccessKeyActions doAction={meta.action} accessKeyId={item['@id']} />,
        sorter: false,
    },
};


class AccessKeyTable extends React.Component {
    constructor(props, context) {
        super(props, context);
        this.store = new AccessKeyStore(props.user.access_keys, this, 'access_keys');

        this.state = {
            accessKeys: [...props.user.access_keys],
            /** Access key message modal component */
            modal: null,
        };

        this.create = this.create.bind(this);
        this.doAction = this.doAction.bind(this);
        this.onCreate = this.onCreate.bind(this);
        this.onResetSecret = this.onResetSecret.bind(this);
        this.showNewSecret = this.showNewSecret.bind(this);
        this.onDelete = this.onDelete.bind(this);
        this.onError = this.onError.bind(this);
        this.hideModal = this.hideModal.bind(this);
    }

    /**
     * Called after an access key was deleted from the item store.
     * @param {object} item Access key that was deleted
     */
    onDelete(item) {
        this.setState((prevState) => {
            // Remove the deleted item from the existing access key entry, and display the modal
            // that shows what happened.
            const deletedIndex = prevState.accessKeys.findIndex(accessKey => accessKey.access_key_id === item.access_key_id);
            if (deletedIndex !== -1) {
                return ({
                    accessKeys: [...prevState.accessKeys.slice(0, deletedIndex), ...prevState.accessKeys.slice(deletedIndex + 1)],
                    modal: (
                        <Modal closeModal={this.hideModal}>
                            <ModalHeader title={'Access key deleted.'} closeModal={this.hideModal} />
                            <ModalBody>
                                <p>{`Access key ${item.access_key_id} has been deleted.`}</p>
                            </ModalBody>
                            <ModalFooter closeModal={this.hideModal} cancelTitle="OK" />
                        </Modal>
                    ),
                });
            }

            // Else matching access key is oddly not in local state. Fail silently.
            return null;
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

    /**
     * Called after an access key for the user gets created on the server.
     * @param {object} response Search result containing new access key object
     */
    onCreate(response) {
        this.setState((prevState) => {
            // Add new secret from item store to the beginning of the `accessKeys` state array.
            const newSecret = Object.assign({}, response['@graph'][0]);
            return { accessKeys: [newSecret, ...prevState.accessKeys] };
        });
        this.showNewSecret('Your secret key has been created.', response);
    }

    /**
     * Called when the user requests a new access key.
     * @param {object} e React synthetic event
     */
    create(e) {
        e.preventDefault();
        const item = {};
        if (this.props.user['@id'] !== this.context.session_properties.user['@id']) {
            item.user = this.props.user['@id'];
        }
        this.store.create('/access-keys/', item);
    }

    /**
     * Called to perform an access key store action, e.g. reset, delete.
     * @param {string} action Code for action to perform
     * @param {string} accessKeyId
     */
    doAction(action, accessKeyId) {
        this.store[action](accessKeyId);
    }

    /**
     * Called when a new secret gets created on the server.
     * @param {string} title Title bar message
     * @param {object} response Access key creation response from server
     */
    showNewSecret(title, response) {
        this.setState({
            modal: (
                <Modal closeModal={this.hideModal}>
                    <ModalHeader title={title} closeModal={this.hideModal} />
                    <ModalBody>
                        <p>
                            Please make a note of the new secret access key.
                            This is the last time you will be able to view it.
                        </p>
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
                    <ModalFooter closeModal={this.hideModal} cancelTitle="OK" />
                </Modal>
            ),
        });
    }

    hideModal() {
        this.setState({ modal: null });
    }

    render() {
        const accessKeyHeader = (
            <div className="access-keys__header">
                <h4 className="access-keys__header-title">Access keys</h4>
                <button onClick={this.create} className="btn btn-info btn-sm access-keys__header-control">Add access key</button>,
            </div>
        );

        return (
            <React.Fragment>
                {this.state.accessKeys.length > 0 ?
                    <SortTablePanel header={accessKeyHeader} css="access-keys__table">
                        <SortTable list={this.state.accessKeys} columns={accessKeyColumns} meta={{ action: this.doAction }} />
                    </SortTablePanel>
                :
                    <Panel addClasses="access-keys__table">
                        <PanelHeading>
                            {accessKeyHeader}
                        </PanelHeading>
                        <PanelBody>
                            <div className="access-keys__empty-message">No access keys</div>
                        </PanelBody>
                    </Panel>
                }
                {this.state.modal}
            </React.Fragment>
        );
    }
}

AccessKeyTable.propTypes = {
    user: PropTypes.object.isRequired,
};

AccessKeyTable.contextTypes = {
    fetch: PropTypes.func,
    session_properties: PropTypes.object,
};


const User = ({ context }) => {
    const itemClass = globals.itemClass(context, 'view-item');
    const isVerifiedMember = context.groups && context.groups.includes('verified');
    const isAdmin = context.groups && context.groups.includes('admin');
    const hasAccessKeyRights = isVerifiedMember || isAdmin;

    return (
        <div className={itemClass}>
            <header>
                <h1>{context.title}</h1>
                <ItemAccessories item={context} />
            </header>
            <Panel>
                <PanelBody>
                    <dl className="key-value">
                        {context.job_title ?
                            <div data-test="title">
                                <dt>Title</dt>
                                <dd>{context.job_title}</dd>
                            </div>
                        : null}
                        {context.lab ?
                            <div data-test="lab">
                                <dt>Lab</dt>
                                <dd>{context.lab.title}</dd>
                            </div>
                        : null}
                        {context.email ?
                            <div data-test="email">
                                <dt>Email</dt>
                                <dd><a href={`mailto:${context.email}`}>{context.email}</a></dd>
                            </div>
                        : null}
                    </dl>
                </PanelBody>
            </Panel>

            {hasAccessKeyRights ? <AccessKeyTable user={context} accessKeys={context.access_keys} /> : null}
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


class ImpersonateUserFormComponent extends React.Component {
    constructor(props) {
        super(props);
        this.finished = this.finished.bind(this);
    }

    finished() {
        this.props.clearCart(this.props.elements);
        this.props.navigate('/');
    }

    render() {
        return (
            <div>
                <h1>Impersonate User</h1>
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

ImpersonateUserFormComponent.propTypes = {
    /** Current contents of cart; array of @ids */
    elements: PropTypes.array.isRequired,
    /** Function to call to clear the cart from the Redux store */
    clearCart: PropTypes.func.isRequired,
    /** navigate callback from <App> context */
    navigate: PropTypes.func.isRequired,
};


const mapStateToProps = state => ({ elements: state.elements });
const mapDispatchToProps = dispatch => ({
    clearCart: elementAtIds => cartRemoveElements(elementAtIds, dispatch),
});

const ImpersonateUserFormInternal = connect(mapStateToProps, mapDispatchToProps)(ImpersonateUserFormComponent);


const ImpersonateUserForm = (props, reactContext) => (
    <ImpersonateUserFormInternal {...props} navigate={reactContext.navigate} />
);

ImpersonateUserForm.contextTypes = {
    navigate: PropTypes.func.isRequired,
};

globals.contentViews.register(ImpersonateUserForm, 'Portal', 'impersonate-user');
