/**
 * Functions to handle the current logged-in user's cart settings. The cart settings object:
 * {
 *     current: '<@id of user's current cart>',
 *     quickSelects: [<@ids of quick-select carts (not currently used)]
 * }
 */


/**
 * Generate a cart localstorage key from a user object.
 * @param {string} userURI user @id
 * @return {string} User's localstorage key
 */
const cartLocalstorageKey = userURI => `encode-cart-${userURI}`;


/**
 * Get the current user's cart settings from browser localstorage.
 * @param {string} userURI user @id
 * @return {object} User's cart settings, or basic one if none
 */
export const cartGetSettings = (userURI) => {
    const userKey = cartLocalstorageKey(userURI);
    const cartSettingsJson = localStorage.getItem(userKey);
    return cartSettingsJson ? JSON.parse(cartSettingsJson) : { current: '', quickSelects: [] };
};


/**
 * Set the current cart in the user's localstorage object.
 * @param {string} userURI user @id
 * @param {string} current Current cart @id
 * @return {object} Updated cart settings object
 */
export const cartSetSettingsCurrent = (userURI, current) => {
    const existingSettings = cartGetSettings(userURI);
    existingSettings.current = current;
    const userKey = cartLocalstorageKey(userURI);
    localStorage.setItem(userKey, JSON.stringify(existingSettings));
    return existingSettings;
};
