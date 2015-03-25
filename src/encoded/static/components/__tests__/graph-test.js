/** @jsx React.DOM */
'use strict';

jest.autoMockOff();

// Fixes https://github.com/facebook/jest/issues/78
jest.dontMock('react');
jest.dontMock('underscore');


describe('Experiment Graph', function() {
    var React, TestUtils, assembleGraph, context, _, collectNodes;

    React = require('react');
    TestUtils = require('react/lib/ReactTestUtils');
    _ = require('underscore');
    assembleGraph = require('../experiment').assembleGraph;
    context = require('../testdata/experiment');
    collectNodes = _.memoize(_collectNodes);

    // Collects all the IDs of all nodes in the given node array and returns it in object keyed by node ID
    function _collectNodes(graphId, nodes) {
        var allNodes = {};

        nodes.forEach(function(node) {
            allNodes[node.id] = node;
            if (node.nodes.length) {
                allNodes = _.extend(allNodes, _collectNodes(graphId, node.nodes));
            }
        });
        return allNodes;
    }

    // Utility to check whether the node ids in the "ids" array are all in the graph given in "graph"
    function containsNodes(graph, ids, debug) {
        var allNodes;

        // Make an object of all nodes in graph
        if (graph.nodes.length) {
            allNodes = collectNodes(graph.id, graph.nodes);
        }

        // See if all the given ids are in the nodes
        return _(ids).all(function(id) {
            return id in allNodes;
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

    // One file derived from two files, through one step.
    describe('Basic graph display', function() {
        var experimentGraph, graph, files;

        beforeEach(function() {
            var context_graph = _.clone(context);
            context_graph.accession = 'ENCTS000BGR';
            context_graph.files = files = [require('../testdata/file/bam-vuq'), require('../testdata/file/bam-vus'), require('../testdata/file/bed-2cos')];
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
            context_graph.accession = 'ENCTS000BDD';
            context_graph.files = files = [require('../testdata/file/bam-vuq'), require('../testdata/file/bam-vus'), require('../testdata/file/bed-3cos'), require('../testdata/file/bed-4cos')];
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

    // Two files each deriving from one file they share; and they share a step.
    // There should be one copy of the step.
    describe('Basic graph step no duplication display', function() {
        var experimentGraph, graph, files;

        beforeEach(function() {
            var context_graph = _.clone(context);
            context_graph.accession = 'ENCTS000NDD';
            context_graph.files = files = [require('../testdata/file/bam-vuq'), require('../testdata/file/bed-5cos'), require('../testdata/file/bed-6cos')];
            graph = assembleGraph(context_graph, '', files);
        });

        it('Has the correct number of nodes and edges', function() {
            expect(graph.nodes.length).toEqual(4);
            expect(graph.edges.length).toEqual(3);
        });

        it('has the right nodes', function() {
            expect(containsNodes(graph, ["file:ENCFF000VUQ", "file:ENCFF005COS", "file:ENCFF006COS", "step:ENCFF000VUQ/analysis-steps/1b7bec83-dd21-4086-8673-2e08cf8f1c0f/"])).toBeTruthy();
        });

        it('has the right relationships between edges and nodes', function() {
            expect(hasParents(graph, "step:ENCFF000VUQ/analysis-steps/1b7bec83-dd21-4086-8673-2e08cf8f1c0f/", ["file:ENCFF000VUQ"])).toBeTruthy();
            expect(hasParents(graph, "file:ENCFF005COS", ["step:ENCFF000VUQ/analysis-steps/1b7bec83-dd21-4086-8673-2e08cf8f1c0f/"])).toBeTruthy();
            expect(hasParents(graph, "file:ENCFF006COS", ["step:ENCFF000VUQ/analysis-steps/1b7bec83-dd21-4086-8673-2e08cf8f1c0f/"])).toBeTruthy();
        });
    });

    // Two files derive from the same two files and share a step.
    // There should be one copy of the step.
    describe('Two files derived from same two files', function() {
        var experimentGraph, graph, files;

        beforeEach(function() {
            var context_graph = _.clone(context);
            context_graph.accession = 'ENCTS000TFS';
            context_graph.files = files = [require('../testdata/file/bam-vuq'), require('../testdata/file/bam-vus'), require('../testdata/file/bed-7cos'), require('../testdata/file/bed-8cos')];
            graph = assembleGraph(context_graph, '', files);
        });

        it('Has the correct number of nodes and edges', function() {
            expect(graph.nodes.length).toEqual(5);
            expect(graph.edges.length).toEqual(4);
        });

        it('has the right nodes', function() {
            expect(containsNodes(graph, ["file:ENCFF000VUQ", "file:ENCFF000VUS", "file:ENCFF008COS", "file:ENCFF008COS", "step:ENCFF000VUQ,ENCFF000VUS/analysis-steps/1b7bec83-dd21-4086-8673-2e08cf8f1c0f/"])).toBeTruthy();
        });

        it('has the right relationships between edges and nodes', function() {
            expect(hasParents(graph, "step:ENCFF000VUQ,ENCFF000VUS/analysis-steps/1b7bec83-dd21-4086-8673-2e08cf8f1c0f/", ["file:ENCFF000VUQ", "file:ENCFF000VUS"])).toBeTruthy();
            expect(hasParents(graph, "file:ENCFF007COS", ["step:ENCFF000VUQ,ENCFF000VUS/analysis-steps/1b7bec83-dd21-4086-8673-2e08cf8f1c0f/"])).toBeTruthy();
            expect(hasParents(graph, "file:ENCFF008COS", ["step:ENCFF000VUQ,ENCFF000VUS/analysis-steps/1b7bec83-dd21-4086-8673-2e08cf8f1c0f/"])).toBeTruthy();
        });
    });

    // Two files derive from two overlapping sets of files. The analysis
    // step should get duplicated, one for each set of derived_from files.
    describe('Two files derived from overlapping set of files', function() {
        var experimentGraph, graph, files;

        beforeEach(function() {
            var context_graph = _.clone(context);
            context_graph.accession = 'ENCTS000TOV';
            context_graph.files = files = [require('../testdata/file/bam-vuq'), require('../testdata/file/bam-vus'), require('../testdata/file/bam-vuz'), require('../testdata/file/bed-10cos'), require('../testdata/file/bed-11cos')];
            graph = assembleGraph(context_graph, '', files);
        });

        it('Has the correct number of nodes and edges', function() {
            expect(graph.nodes.length).toEqual(7);
            expect(graph.edges.length).toEqual(6);
        });

        it('has the right nodes', function() {
            expect(containsNodes(graph, ["file:ENCFF000VUQ", "file:ENCFF000VUS", "file:ENCFF000VUZ", "file:ENCFF010COS", "file:ENCFF011COS", "step:ENCFF000VUQ,ENCFF000VUS/analysis-steps/1b7bec83-dd21-4086-8673-2e08cf8f1c0f/", "step:ENCFF000VUS,ENCFF000VUZ/analysis-steps/1b7bec83-dd21-4086-8673-2e08cf8f1c0f/"])).toBeTruthy();
        });

        it('has the right relationships between edges and nodes', function() {
            expect(hasParents(graph, "step:ENCFF000VUQ,ENCFF000VUS/analysis-steps/1b7bec83-dd21-4086-8673-2e08cf8f1c0f/", ["file:ENCFF000VUQ", "file:ENCFF000VUS"])).toBeTruthy();
            expect(hasParents(graph, "step:ENCFF000VUS,ENCFF000VUZ/analysis-steps/1b7bec83-dd21-4086-8673-2e08cf8f1c0f/", ["file:ENCFF000VUS", "file:ENCFF000VUZ"])).toBeTruthy();
            expect(hasParents(graph, "file:ENCFF010COS", ["step:ENCFF000VUQ,ENCFF000VUS/analysis-steps/1b7bec83-dd21-4086-8673-2e08cf8f1c0f/"])).toBeTruthy();
            expect(hasParents(graph, "file:ENCFF011COS", ["step:ENCFF000VUS,ENCFF000VUZ/analysis-steps/1b7bec83-dd21-4086-8673-2e08cf8f1c0f/"])).toBeTruthy();
        });
    });

    // One file derived from two files, through one step.
    // Another file not derived from, and doesn't derive from others; it should vanish.
    describe('Basic graph with detached node', function() {
        var experimentGraph, graph, files;

        beforeEach(function() {
            var context_graph = _.clone(context);
            context_graph.accession = 'ENCTS000DET';
            context_graph.files = files = [require('../testdata/file/bam-vuq'), require('../testdata/file/bam-vus'), require('../testdata/file/bam-vuz'), require('../testdata/file/bed-2cos')];
            graph = assembleGraph(context_graph, '', files);
        });

        it('Has the correct number of nodes and edges', function() {
            expect(graph.nodes.length).toEqual(4);
            expect(graph.edges.length).toEqual(3);
        });

        /// VUZ should be missing.
        it('has the right nodes', function() {
            expect(containsNodes(graph, ["file:ENCFF000VUQ", "file:ENCFF000VUS", "file:ENCFF002COS", "step:ENCFF000VUQ,ENCFF000VUS/analysis-steps/1b7bec83-dd21-4086-8673-2e08cf8f1c0f/"])).toBeTruthy();
            expect(containsNodes(graph, ["file:ENCFF000VUZ"])).toBeFalsy();
        });

        it('has the right relationships between edges and nodes', function() {
            expect(hasParents(graph, "step:ENCFF000VUQ,ENCFF000VUS/analysis-steps/1b7bec83-dd21-4086-8673-2e08cf8f1c0f/", ["file:ENCFF000VUS", "file:ENCFF000VUQ"])).toBeTruthy();
            expect(hasParents(graph, "file:ENCFF002COS", ["step:ENCFF000VUQ,ENCFF000VUS/analysis-steps/1b7bec83-dd21-4086-8673-2e08cf8f1c0f/"])).toBeTruthy();
        });
    });

    // One file derived from two files, through one step.
    // One derived-from file is missing, and no graph should be generated.
    describe('Basic graph with missing derived from file', function() {
        var experimentGraph, graph, files;

        beforeEach(function() {
            var context_graph = _.clone(context);
            context_graph.accession = 'ENCTS000MDF';
            context_graph.files = files = [require('../testdata/file/bam-vuq'),require('../testdata/file/bed-2cos')];
            graph = assembleGraph(context_graph, '', files);
        });

        it('No graph generated at all', function() {
            expect(graph).toBeNull();
        });
    });

    // Two files derive from one file each through a shared step. Each file and derived from files in a replicate.
    // Total of two replicates with three nodes each
    describe('Two graphs in two replicates', function() {
        var experimentGraph, graph, files;

        beforeEach(function() {
            var context_graph = _.clone(context);
            context_graph.accession = 'ENCTS000REP';
            context_graph.files = files = [require('../testdata/file/bam-vuq'), require('../testdata/file/bam-vus'), require('../testdata/file/bed-3cos'), require('../testdata/file/bed-4cos')];
            files[0].replicate = files[2].replicate = files[2].derived_from[0].replicate = require('../testdata/replicate/human');
            files[1].replicate = files[3].replicate = files[3].derived_from[0].replicate = require('../testdata/replicate/mouse');

            graph = assembleGraph(context_graph, '', files, true);
        });

        it('Has the correct number of nodes and edges', function() {
            var subNodes = 0;

            expect(graph.nodes.length).toEqual(2);
            graph.nodes.forEach(function(node) {
                subNodes += node.nodes.length;
            });
            expect(subNodes).toEqual(6);
            expect(graph.edges.length).toEqual(4);
        });

        it('has the right nodes', function() {
            expect(containsNodes(graph, ["rep:1", "rep:2", "file:ENCFF000VUQ", "file:ENCFF000VUS", "file:ENCFF003COS", "file:ENCFF004COS",
                "step:ENCFF000VUQ/analysis-steps/1b7bec83-dd21-4086-8673-2e08cf8f1c0f/", "step:ENCFF000VUS/analysis-steps/1b7bec83-dd21-4086-8673-2e08cf8f1c0f/"])).toBeTruthy();
        });

        it('has the right relationships between edges and nodes', function() {
            expect(hasParents(graph, "step:ENCFF000VUQ/analysis-steps/1b7bec83-dd21-4086-8673-2e08cf8f1c0f/", ["file:ENCFF000VUQ"])).toBeTruthy();
            expect(hasParents(graph, "file:ENCFF003COS", ["step:ENCFF000VUQ/analysis-steps/1b7bec83-dd21-4086-8673-2e08cf8f1c0f/"])).toBeTruthy();
            expect(hasParents(graph, "step:ENCFF000VUS/analysis-steps/1b7bec83-dd21-4086-8673-2e08cf8f1c0f/", ["file:ENCFF000VUS"])).toBeTruthy();
            expect(hasParents(graph, "file:ENCFF004COS", ["step:ENCFF000VUS/analysis-steps/1b7bec83-dd21-4086-8673-2e08cf8f1c0f/"])).toBeTruthy();
        });
    });

    // Two files derive from one file each through a shared step. Each file and derived from files in a replicate.
    // Total of two replicates with three ndoes each
    describe('Two graphs in two replicates; one derived-from missing', function() {
        var experimentGraph, graph, files;
    
        beforeEach(function() {
            var context_graph = _.clone(context);
            context_graph.accession = 'ENCTS000RPM';
            context_graph.files = files = [require('../testdata/file/bam-vuq'), require('../testdata/file/bed-3cos'), require('../testdata/file/bed-4cos')];
            files[0].replicate = files[1].replicate = files[1].derived_from[0].replicate = require('../testdata/replicate/human');
            files[2].replicate = files[2].derived_from[0].replicate = require('../testdata/replicate/mouse');

            graph = assembleGraph(context_graph, '', files, true);
        });

        it('Has the correct number of nodes and edges', function() {
            var subNodes = 0;

            expect(graph.nodes.length).toEqual(1);
            graph.nodes.forEach(function(node) {
                subNodes += node.nodes.length;
            });
            expect(subNodes).toEqual(3);
            expect(graph.edges.length).toEqual(2);
        });

        it('has the right nodes', function() {
            expect(containsNodes(graph, ["rep:1", "file:ENCFF000VUQ", "file:ENCFF003COS",
                "step:ENCFF000VUQ/analysis-steps/1b7bec83-dd21-4086-8673-2e08cf8f1c0f/"])).toBeTruthy();
            expect(containsNodes(graph, ["rep:2"])).toBeFalsy();
        });

        it('has the right relationships between edges and nodes', function() {
            expect(hasParents(graph, "step:ENCFF000VUQ/analysis-steps/1b7bec83-dd21-4086-8673-2e08cf8f1c0f/", ["file:ENCFF000VUQ"])).toBeTruthy();
            expect(hasParents(graph, "file:ENCFF003COS", ["step:ENCFF000VUQ/analysis-steps/1b7bec83-dd21-4086-8673-2e08cf8f1c0f/"])).toBeTruthy();
        });
    });

});
