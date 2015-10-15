'use strict';
var ReactForms = require('react-forms');

export var ImpersonateUserSchema = ReactForms.schema.Mapping({}, {
    userid: ReactForms.schema.Scalar({
        label: 'User',
        hint: 'Enter the email of the user you want to impersonate.',
    }),
});
