# Managing ENCODE npm packages

Our Javascript front end code requires several third-party packages which get installed during the ENCODE make process, and which you can install manually when rare circumstances call for it. This process has changed since npm version 5, and this document describes how to update and maintain the files npm 5 and beyond uses to retrieve the versions of packages ENCODE needs. When you modify package.json and package-lock.json, make sure to commit them to your branch that requires these changes so that others building the front end also get your branch’s updates.

## Manual install

Because `make install` installs the required npm packages, you rarely need to install them manually. But if you do, use this rather than the older `npm install` command:

    npm ci

This uses the package-lock.json file in the repo to retrieve precisely the versions of packages you need.

## Adding new npm packages

The package.json file in the root encoded directory holds a manifest of the packages we require as well as version information. If you need a new npm package for a feature you have developed, use this for packages used during run time (e.g. React):

    npm install <npm-package-name> --save

Use this for packages used for a Javascript build (e.g. babel)

    npm install <npm-package-name> --save-dev

Verify your package-lock.json file has also been updated automatically. If it has not, use this command to update package-lock.json:

    npm update

These modify your package.json file to include single-line entries for your new npm package in the "dependencies" or "devDependencies" sections. In addition, an entry in package-lock.json specifies the precise version of your new package for npm to install going forward. Commit both of these files’ modifications with your branch.

## Updating the npm packages

If you want to update the version of an npm package we already include, we have a couple recommended ways:

### Update package.json

Modify the npm package’s entry in package.json to specify the version you want, then remove your root-level node_modules directory, then use:

    npm update

This updates package-lock.json and does a complete install of the npm packages ENCODE needs.

### Update npm package as if new

Remove the entry for the package you want to update from package.json. Then add the npm package as you would a new npm package.
