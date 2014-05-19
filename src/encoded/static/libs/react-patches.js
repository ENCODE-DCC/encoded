'use strict';
// These patches must be executed before any call to require('react').

// https://github.com/facebook/react/pull/1183
var DefaultDOMPropertyConfig = require('react/lib/DefaultDOMPropertyConfig');
DefaultDOMPropertyConfig.DOMAttributeNames.httpEquiv = 'http-equiv';
