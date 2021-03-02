module.exports = {
    env: {
        browser: true,
        es2021: true,
    },
    extends: [
        'plugin:react/recommended',
        'airbnb',
    ],
    parserOptions: {
        ecmaFeatures: {
            jsx: true,
        },
        ecmaVersion: 12,
        sourceType: 'module',
    },
    plugins: [
        'react',
    ],
    rules: {
        'comma-dangle': ['error', {
            arrays: 'always-multiline',
            functions: 'ignore',
            objects: 'always-multiline',
            imports: 'always-multiline',
            exports: 'always-multiline',
        }],
        'global-require': 'off', // Requiring this gets tricky
        'import/no-cycle': 'off', // Legal Javascript we've used
        indent: ['error', 4, { ignoredNodes: ['ConditionalExpression'] }],
        'jsx-a11y/label-has-associated-control': ['error', { assert: 'either' }], // Even a11y demos code fail default
        'max-len': 0, // No maximum line length, but try to keep to 100 except with URLs
        'max-classes-per-file': 'off', // Causes too many code changes
        'import/extensions': 'off',
        'no-await-in-loop': 'off', // Sometimes needed when promise relies on previous promise
        'no-bitwise': 'off', // We use bitwise operators
        'no-cond-assign': ['error', 'except-parens'], // Valid use case for assigning variable in a conditional statement as long as it's within parentheses.
        'no-console': 'off', // We allow console messages
        'no-param-reassign': 'off',
        'no-multiple-empty-lines': [2, { max: 2 }], // Allow up to 2 empty lines
        'no-nested-ternary': 'off', // Probably a good rule, but too many code changes
        'no-underscore-dangle': 'off',
        'object-curly-newline': ['error', { // Default seems needlessly strict
            ObjectPattern: { multiline: true },
            ExportDeclaration: { multiline: true, minProperties: 3 },
        }],
        'operator-linebreak': 'off', // Causes too many code changes
        'prefer-destructuring': ['error', {
            array: false,
            object: true,
        }],
        'react/destructuring-assignment': 'off', // Causes too many code changes
        'react/forbid-prop-types': 'off', // Causes too many code changes
        'react/jsx-curly-newline': 'off', // Causes too many code changes
        'react/jsx-filename-extension': 'off', // Avoid changing every file to .jsx
        'react/jsx-indent': 'off', // To indent by 4 always
        'react/jsx-indent-props': 'off', // To indent by 4 always
        'react/jsx-one-expression-per-line': 'off', // Causes too many code changes
        'react/jsx-props-no-spreading': 'off', // Probably a good rule, but too many code changes
        'react/jsx-uses-react': 'off', // Not needed with new transform
        'react/jsx-wrap-multilines': 'off', // Causes too many code changes
        'react/no-array-index-key': 'off', // Sometimes we have no choice
        'react/no-danger': 'off', // We need to do this
        'react/react-in-jsx-scope': 'off', // Not needed with new transform
    },
};
