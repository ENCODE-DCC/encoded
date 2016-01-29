'use strict';

jest.autoMockOff();

// Fixes https://github.com/facebook/jest/issues/78
jest.dontMock('react');
jest.dontMock('underscore');


var React = require('react');
var TestUtils = require('react/lib/ReactTestUtils');
var annotationBiosampleSummary = require('../dataset').annotationBiosampleSummary;

describe('Annotation biosample summary', function() {
    it('it works for just scientific name, life stage', function() {
        var context = {
            organism: {
                scientific_name: 'Mus musculus'
            },
            relevant_life_stage: 'adult'
        };
        var summary = TestUtils.renderIntoDocument(
            annotationBiosampleSummary(context)
        );

        var summaryOutput = TestUtils.findRenderedDOMComponentWithClass(summary, 'biosample-summary').getDOMNode();
        expect(summaryOutput.textContent).toEqual('Mus musculus, adult');
    });

    it('it works for just scientific name, unknown life stage', function() {
        var context = {
            organism: {
                scientific_name: 'Mus musculus'
            },
            relevant_life_stage: 'unknown'
        };
        var summary = TestUtils.renderIntoDocument(
            annotationBiosampleSummary(context)
        );

        var summaryOutput = TestUtils.findRenderedDOMComponentWithClass(summary, 'biosample-summary').getDOMNode();
        expect(summaryOutput.textContent).toEqual('Mus musculus');
    });

    it('it works for just scientific name, life stage, timepoint', function() {
        var context = {
            organism: {
                scientific_name: 'Mus musculus'
            },
            relevant_life_stage: 'adult',
            relevant_timepoint: '11.5'
        };
        var summary = TestUtils.renderIntoDocument(
            annotationBiosampleSummary(context)
        );

        var summaryOutput = TestUtils.findRenderedDOMComponentWithClass(summary, 'biosample-summary').getDOMNode();
        expect(summaryOutput.textContent).toEqual('Mus musculus, adult, 11.5');
    });

    it('it works for just scientific name, life stage, timepoint, timepoint units', function() {
        var context = {
            organism: {
                scientific_name: 'Mus musculus'
            },
            relevant_life_stage: 'adult',
            relevant_timepoint: '11.5',
            relevant_timepoint_units: 'year'
        };
        var summary = TestUtils.renderIntoDocument(
            annotationBiosampleSummary(context)
        );

        var summaryOutput = TestUtils.findRenderedDOMComponentWithClass(summary, 'biosample-summary').getDOMNode();
        expect(summaryOutput.textContent).toEqual('Mus musculus, adult, 11.5 year');
    });
});
