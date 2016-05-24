'use strict';
var ReactForms = require('react-forms');

module.exports = ReactForms.schema.Mapping({}, {
    userid: ReactForms.schema.Scalar({
        label: 'User',
        hint: 'Enter the email of the user you want to impersonate.',
    }),
});
