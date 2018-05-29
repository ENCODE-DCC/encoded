module.exports = {
    extends: 'airbnb',
    env: {
        browser: true,
    },
    parserOptions: {
        ecmaVersion: 6,
        ecmaFeatures: {
            jsx: true,
        },
    },
    // Rules with the "FF" comment means "follow this rule in the future." The rule is currently
    // disabled, but any new or modified code should follow this rule. Those without the "FF"
    // have been disabled in encoded for a reason, and you don't need to follow them.
    rules: {
        'comma-dangle': ['error', {
            arrays: 'always-multiline',
            functions: 'ignore',
            objects: 'always-multiline',
            imports: 'always-multiline',
            exports: 'always-multiline',
        }],
        flatTernaryExpressions: false,
        'function-paren-newline': 0,
        'global-require': 0,
        indent: ['error', 4, { ignoredNodes: ['ConditionalExpression'] }],
        'jsx-a11y/label-has-for': [2, {
            required: {
                every: ['id'],
            },
        }],
        'max-len': 0,
        'no-bitwise': 0,
        'no-console': 0, // FF
        'no-nested-ternary': 0,
        'no-param-reassign': [2, { props: false }],
        'no-underscore-dangle': 0,
        'no-restricted-properties': 0,
        'object-curly-newline': ['error', {
            ObjectExpression: { consistent: true },
            ObjectPattern: { multiline: true },
        }],
        'prefer-destructuring': 0, // FF
        'react/forbid-prop-types': 0,
        'react/jsx-filename-extension': 0,
        'react/jsx-indent': 0,
        'react/jsx-indent-props': [2, 4],
        'react/jsx-curly-brace-presence': 0,
        'react/jsx-wrap-multilines': 0,
        'react/no-array-index-key': 0,
        'react/no-danger': 0,
        'react/no-did-mount-set-state': 0,
        'react/no-did-update-set-state': 0,
        'react/no-multi-comp': 0,
    },
};
