/**
 * Functions to handle the current logged-in user's cart settings. The cart settings object:
 * {
 *     current: '<@id of user's current cart>',
 *     quickSelects: [<@ids of quick-select carts (not currently used)]
 * }
 */


/**
 * Generate a cart localstorage key from a user object.
 * @param {object} user User object from DB
 * @return {string} User's localstorage key
 */
const cartLocalstorageKey = (user) => `encode-cart-${user['@id']}`;


/**
 * Get the current user's cart settings from browser localstorage.
 * @param {object} user Currently logged-in user's object from DB
 * @return {object} User's cart settings, or basic one if none
 */
export const cartGetSettings = (user) => {
    const userKey = cartLocalstorageKey(user);
    const cartSettingsJson = localStorage.getItem(userKey);
    return cartSettingsJson ? JSON.parse(cartSettingsJson) : { current: '', quickSelects: [] };
};


/**
 * Set the current cart in the user's localstorage object.
 * @param {object} user User object from DB
 * @param {string} current Current cart @id
 * @return {object} Updated cart settings object
 */
export const cartSetSettingsCurrent = (user, current) => {
    const existingSettings = cartGetSettings(user);
    existingSettings.current = current;
    const userKey = cartLocalstorageKey(user);
    localStorage.setItem(userKey, JSON.stringify(existingSettings));
    return existingSettings;
};
