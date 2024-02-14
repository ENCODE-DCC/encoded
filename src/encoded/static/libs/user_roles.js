/**
 * Indicate the roles the current user has.
 * @param {object} sessionProperties - From <App> context
 */
export default class UserRoles {
    constructor(sessionProperties) {
        this._roles = [];

        if (sessionProperties && Object.keys(sessionProperties).length > 0) {
            // Non-empty auth.userid-object shows user is logged in at least, so has at least
            // unprivileged rights
            if (sessionProperties['auth.userid']) {
                this._roles.push('unprivileged');
            }

            const userProperties = sessionProperties.user;
            if (userProperties?.lab?.status === 'current'
                && userProperties?.submits_for?.length > 0) {
                this._roles.push('submitter');
            }

            if (sessionProperties.admin) {
                this._roles.push('admin');
            }
        }
    }

    /**
     * Returns all the roles the current user has. It includes the relevant following roles in this
     * order:
     * - unprivileged - User-created account
     * - submitter - Account for lab submitter
     * - admin - Account largely for DCC members
     */
    get userRoles() {
        return this._roles;
    }

    /**
     * Returns true if the current user has logged in having any role.
     */
    get isLoggedIn() {
        return this._roles.length > 0;
    }

    /**
     * Returns true if the current user created their own account.
     */
    get isUnprivileged() {
        return this._roles.length === 1 && this._roles[0] === 'unprivileged';
    }

    /**
     * Returns true if the current user is a submitter or admin.
     */
    get isPrivileged() {
        return this._roles.includes('submitter');
    }

    /**
     * Returns true if the current user is a lab submitter.
     */
    get isSubmitter() {
        return this._roles.includes('submitter') && !this._roles.includes('admin');
    }

    /**
     * Returns true if the current user is a DCC admin.
     */
    get isAdmin() {
        return this._roles.includes('admin');
    }
}
