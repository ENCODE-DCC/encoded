
const SUBS = { '&': '\\u0026', '<': '\\u003C', '>': '\\u003E' };
// eslint-disable-next-line no-useless-escape
const unsafeRe = /[\<\>\&]/g;

const sub = (match) => SUBS[match];
const jsonScriptEscape = (jsonString) => jsonString.replace(unsafeRe, sub);

module.exports = jsonScriptEscape;
