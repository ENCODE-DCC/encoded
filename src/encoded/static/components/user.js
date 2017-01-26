/** @preventMunge */
/* ^ see http://stackoverflow.com/questions/30110437/leading-underscore-transpiled-wrong-with-es6-classes */

'use strict';
var React = require('react');
var globals = require('./globals');
var _ = require('underscore');
var parseAndLogError = require('./mixins').parseAndLogError;
var navigation = require('./navigation');
var {Modal, ModalHeader, ModalBody, ModalFooter, ModalMixin} = require('../libs/bootstrap/modal');
var ItemStore = require('./lib/store').ItemStore;
var Form = require('./form').Form;
var ObjectPicker = require('./inputs').ObjectPicker;

var Breadcrumbs = navigation.Breadcrumbs;


class AccessKeyStore extends ItemStore {
    resetSecret(id) {
        this.fetch(id + 'reset-secret', {
            method: 'POST',
        }, response => this.dispatch('onResetSecret', response));
    }
}


var AccessKeyTable = React.createClass({
    mixins: [ModalMixin],

    contextTypes: {
        fetch: React.PropTypes.func,
        session_properties: React.PropTypes.object
    },

    getInitialState: function() {
        var access_keys = this.props.access_keys;
        this.store = new AccessKeyStore(access_keys, this, 'access_keys');
        return {access_keys: access_keys};
    },

    render: function() {
        return (
            <div>
                <a className="btn btn-success" onClick={this.create}>Add Access Key</a>
                {this.state.access_keys.length ?
                    <table className="table">
                        <thead>
                            <tr>
                                <th>Access Key ID</th>
                                <th>Description</th>
                                <th></th>
                            </tr>
                        </thead>
                        <tbody>
                            {this.state.access_keys.map(k =>
                                <tr key={k.access_key_id}>
                                    <td>{k.access_key_id}</td>
                                    <td>{k.description}</td>
                                    <td>
                                        <a href="" onClick={this.doAction.bind(this, 'resetSecret', k['@id'])}>reset</a>
                                        {' '}<a href="" onClick={this.doAction.bind(this, 'delete', k['@id'])}>delete</a>
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                : ''}
                {this.state.modal}
            </div>
        );
    },

    create: function(e) {
        e.preventDefault();
        var item = {};
        if (this.props.user['@id'] != this.context.session_properties.user['@id']) {
            item['user'] = this.props.user['@id'];
        }
        this.store.create('/access-keys/', item);
    },

    doAction: function(action, arg, e) {
        e.preventDefault();
        this.store[action](arg);
    },

    onCreate: function(response) {
        this.showNewSecret('Your secret key has been created.', response);
    },
    onResetSecret: function(response) {
        this.showNewSecret('Your secret key has been reset.', response);
    },
    showNewSecret: function(title, response) {
        this.setState({modal:
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
        });
    },

    onDelete: function(item) {
        this.setState({modal:
            <Modal closeModal={this.hideModal}>
                <ModalHeader title={'Access key deleted.'} closeModal={this.hideModal} />
                <ModalBody>
                    <p>{'Access key ' + item['access_key_id'] + ' has been deleted.'}</p>
                </ModalBody>
            </Modal>
        });
    },

    onError: function(error) {
        var View = globals.content_views.lookup(error);
        this.setState({modal:
            <Modal closeModal={this.hideModal}>
                <ModalHeader title="Error" closeModal={this.hideModal} />
                <ModalBody>
                    <View context={error} loadingComplete={true} />
                </ModalBody>
            </Modal>
        });
    },

    hideModal: function() {
        this.setState({modal: null});
    },
});


var User = module.exports.User = React.createClass({
    render: function() {
        var context = this.props.context;
        var crumbs = [
            {id: 'Users'}
        ];
        return (
            <div>
                <header className="row">
                    <Breadcrumbs root='/search/?type=user' crumbs={crumbs} />
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
                                <dd><a href={'mailto:' + context.email}>{context.email}</a></dd>
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
    }
});


globals.content_views.register(User, 'User');


var ImpersonateUserSchema = {
    type: 'object',
    properties: {
        userid: {
            title: 'User',
            description: 'Enter the email of the user you want to impersonate.'
        }
    }
};


var ImpersonateUserForm = React.createClass({
    contextTypes: {
        navigate: React.PropTypes.func
    },

    render: function() {
        return (
            <div>
                <h2>Impersonate User</h2>
                <Form schema={ImpersonateUserSchema} submitLabel="Submit"
                      method="POST" action="/impersonate-user"
                      onFinish={this.finished} />
            </div>
        );
    },

    finished: function(data) {
        this.context.navigate('/');
    }
});
globals.content_views.register(ImpersonateUserForm, 'Portal', 'impersonate-user');
