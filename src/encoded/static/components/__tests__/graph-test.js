/** @jsx React.DOM */
'use strict';

jest.autoMockOff();

// Fixes https://github.com/facebook/jest/issues/78
jest.dontMock('react');
jest.dontMock('underscore');


describe('Experiment Graph', function() {
    var React, TestUtils, assembleGraph, context, _;

    // Utility to check whether the node ids in the "ids" array are all in the graph given in "graph"
    function containsNodes(graph, ids) {
        return _(ids).all(function(id) {
            return _(graph.nodes).any(function(graphNode) {
                return id === graphNode.id;
            });
        });
    }

    // Utility returns true if child ID has all parents in "parent" IDs
    function hasParents(graph, child, parents) {
        var matchingTargets = _(graph.edges).where({target: child});
        if (matchingTargets.length) {
            return _(parents).all(function(parent) {
                return _(matchingTargets).any(function(target) {
                    return parent === target.source;
                });
            });
        }
    }

    beforeEach(function() {
        React = require('react');
        TestUtils = require('react/lib/ReactTestUtils');
        _ = require('underscore');

        assembleGraph = require('../experiment').assembleGraph;
        context = require('../testdata/experiment');
    });

    // One file derived from two files, through one step.
    describe('Basic graph display', function() {
        var experimentGraph, graph, files;

        beforeEach(function() {
            var context_graph = _.clone(context);
            context_graph.files = files = [require('../testdata/file/bam-vuq'), require('../testdata/file/bam-vus'), require('../testdata/file/bam-2cos')];
            graph = assembleGraph(context_graph, '', files);
        });

        it('Has the correct number of nodes and edges', function() {
            expect(graph.nodes.length).toEqual(4);
            expect(graph.edges.length).toEqual(3);
        });

        it('has the right nodes', function() {
            expect(containsNodes(graph, ["file:ENCFF000VUQ", "file:ENCFF000VUS", "file:ENCFF002COS", "step:ENCFF000VUQ,ENCFF000VUS/analysis-steps/1b7bec83-dd21-4086-8673-2e08cf8f1c0f/"])).toBeTruthy();
        });

        it('has the right relationships between edges and nodes', function() {
            expect(hasParents(graph, "step:ENCFF000VUQ,ENCFF000VUS/analysis-steps/1b7bec83-dd21-4086-8673-2e08cf8f1c0f/", ["file:ENCFF000VUS", "file:ENCFF000VUQ"])).toBeTruthy();
            expect(hasParents(graph, "file:ENCFF002COS", ["step:ENCFF000VUQ,ENCFF000VUS/analysis-steps/1b7bec83-dd21-4086-8673-2e08cf8f1c0f/"])).toBeTruthy();
        });
    });

    // Two files each deriving from one file each; share a step.
    // There should be two copies of the step with different file
    // accessions in their IDs.
    describe('Basic graph step duplication display', function() {
        var experimentGraph, graph, files;

        beforeEach(function() {
            var context_graph = _.clone(context);
            context_graph.files = files = [require('../testdata/file/bam-vuq'), require('../testdata/file/bam-vus'), require('../testdata/file/bam-3cos'), require('../testdata/file/bam-4cos')];
            graph = assembleGraph(context_graph, '', files);
        });

        it('Has the correct number of nodes and edges', function() {
            expect(graph.nodes.length).toEqual(6);
            expect(graph.edges.length).toEqual(4);
        });

        it('has the right nodes', function() {
            expect(containsNodes(graph, ["file:ENCFF000VUQ", "file:ENCFF000VUS", "file:ENCFF003COS", "file:ENCFF004COS", "step:ENCFF000VUQ/analysis-steps/1b7bec83-dd21-4086-8673-2e08cf8f1c0f/", "step:ENCFF000VUS/analysis-steps/1b7bec83-dd21-4086-8673-2e08cf8f1c0f/"])).toBeTruthy();
        });

        it('has the right relationships between edges and nodes', function() {
            expect(hasParents(graph, "step:ENCFF000VUQ/analysis-steps/1b7bec83-dd21-4086-8673-2e08cf8f1c0f/", ["file:ENCFF000VUQ"])).toBeTruthy();
            expect(hasParents(graph, "step:ENCFF000VUS/analysis-steps/1b7bec83-dd21-4086-8673-2e08cf8f1c0f/", ["file:ENCFF000VUS"])).toBeTruthy();
            expect(hasParents(graph, "file:ENCFF003COS", ["step:ENCFF000VUQ/analysis-steps/1b7bec83-dd21-4086-8673-2e08cf8f1c0f/"])).toBeTruthy();
            expect(hasParents(graph, "file:ENCFF004COS", ["step:ENCFF000VUS/analysis-steps/1b7bec83-dd21-4086-8673-2e08cf8f1c0f/"])).toBeTruthy();
        });
    });
});
