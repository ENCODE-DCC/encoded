import React from 'react';
import ReactDOM from 'react-dom';
import ReactDOMServer from 'react-dom/server';
import { getRenderedProps } from '../app';
import App from '..';


describe('Server rendering', () => {
    let document;
    const homeUrl = 'http://localhost/';
    const home = {
        '@id': '/',
        '@type': ['Portal'],
        portal_title: 'ENCODE',
        title: 'Home',
    };

    beforeEach(() => {
        const serverApp = <App context={home} href={homeUrl} styles="/static/build/style.css" />;
        const markup = `<!DOCTYPE html>\n${ReactDOMServer.renderToString(serverApp)}`;
        const parser = new DOMParser();
        document = parser.parseFromString(markup, 'text/html');
        window.location.href = homeUrl;
    });

    test('renders the application to html', () => {
        expect(document.title).toEqual(home.portal_title);
    });

    test('react render http-equiv correctly', () => {
        const metaHttpEquiv = document.querySelectorAll('meta[http-equiv]');
        expect(metaHttpEquiv).not.toHaveLength(0);
    });

    test('mounts the application over the rendered html', () => {
        let domNode;
        const props = getRenderedProps(document);
        ReactDOM.render(<App {...props} domReader={(node) => { domNode = node; }} />, document);
        expect(domNode).toBe(document.documentElement);
    });
});
