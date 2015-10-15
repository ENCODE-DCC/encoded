'use strict';
var ReactForms = require('react-forms');

export default ReactForms.schema.Mapping({}, {
    userid: ReactForms.schema.Scalar({
        label: 'User',
        hint: 'Enter the email of the user you want to impersonate.',
    }),
});
