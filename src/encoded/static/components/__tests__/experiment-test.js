/** @jsx React.DOM */
'use strict';

// Fixes https://github.com/facebook/jest/issues/78
jest.dontMock('react');
jest.dontMock('underscore');
jest.dontMock('url');

jest.dontMock('../experiment.js');
jest.dontMock('../globals.js');
jest.dontMock('../dbxref.js');
jest.dontMock('../dataset.js');
jest.dontMock('../antibody.js');
jest.dontMock('../biosample.js');
jest.dontMock('../image.js');
jest.dontMock('../../libs/registry.js');

jest.dontMock('../jestdata/experiment.js');
jest.dontMock('../jestdata/file.js');
jest.dontMock('../jestdata/document.js');


describe('experiment', function() {
    var React = require('react');
    var Experiment = require('../experiment.js').Experiment;
    var TestUtils = require('react/lib/ReactTestUtils');
    var context = require('../jestdata/experiment.js').experiment_basic;
    context.files = require('../jestdata/file.js').file_basic;
    context.documents = require('../jestdata/document.js').document_basic;

    it('displays proper variants of experiments', function() {
        // Render a basic experiment
        var experiment = <Experiment context={context} />;
        TestUtils.renderIntoDocument(experiment);

        // Seven <dt> and <dd> elements
        var defTerms = TestUtils.scryRenderedDOMComponentsWithTag(experiment, 'dt');
        expect(defTerms.length).toEqual(7);
        var defDescs = TestUtils.scryRenderedDOMComponentsWithTag(experiment, 'dd');
        expect(defDescs.length).toEqual(7);

        // Two experiment status elements
        var statusList = TestUtils.scryRenderedDOMComponentsWithClass(experiment, 'status-list')[0].getDOMNode();
        expect(statusList.hasChildNodes()).toEqual(true);
        expect(statusList.childNodes.length).toEqual(2);

        // Two rows in the file list
        var fileList = TestUtils.findRenderedDOMComponentWithTag(experiment, 'tbody').getDOMNode();
        expect(fileList.hasChildNodes()).toEqual(true);
        expect(fileList.childNodes.length).toEqual(2);

        // One document panel
        //var document = TestUtils.findRenderedDOMComponentWithClass(experiment, 'type-document').getDOMNode();
        //var figure = document.getElementsByTagName('figure');
        //expect (figure.length).toEqual(1);

    });
});