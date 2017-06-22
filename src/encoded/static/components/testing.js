import React from 'react';
import * as globals from './globals';


export default class TestingRenderErrorPanel extends React.Component {
    render() {
        console.log('log');
        console.warn('warn');
        return this.method_does_not_exist();
    }
}

globals.panelViews.register(TestingRenderErrorPanel, 'TestingRenderError');
