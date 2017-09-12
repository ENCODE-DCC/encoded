import React from 'react';
import PropTypes from 'prop-types';
import _ from 'underscore';
import { Panel } from '../libs/bootstrap/panel';
import { svgIcon } from '../libs/svg-icons';
import { BrowserFeat } from './browserfeat';
import * as globals from './globals';


// Zoom slider constants
const minZoom = 0; // Minimum zoom slider level
const maxZoom = 100; // Maximum zoom slider level
const graphWidthMargin = 40; // Margin on horizontal edges of graph SVG
const graphHeightMargin = 40; // Margin on vertical edges of graph SVG
const MINIMUM_COALESCE_COUNT = 5; // Minimum number of files in a coalescing group


// The JsonGraph object helps build JSON graph objects. Create a new object
// with the constructor, then add edges and nodes with the methods.
// This merges the hierarchical structure from the JSON Graph structure described in:
// http://rtsys.informatik.uni-kiel.de/confluence/display/KIELER/JSON+Graph+Format
// and the overall structure of https://github.com/jsongraph/json-graph-specification.
// In this implementation, all edges are in the root object, not in the nodes array.
// This allows edges to cross between children and parents.

export class JsonGraph {

    constructor(id) {
        this.id = id;
        this.root = true;
        this['@type'] = [];
        this.label = [];
        this.shape = '';
        this.metadata = {};
        this.nodes = [];
        this.edges = [];
        this.subnodes = [];
    }

    // Add node to the graph architecture. The caller must keep track that all node IDs
    // are unique -- this code doesn't verify this.
    // id: uniquely identify the node
    // label: text to display in the node; it can be an array to display a list of labels
    // options: Object containing options to save in the node that can be used later when displayed
    // subnodes: Array of nodes to use as subnodes of a regular node.
    addNode(id, label, options, subnodes) {
        const newNode = {};
        newNode.id = id;
        newNode['@type'] = [];
        newNode['@type'][0] = options.type;
        newNode.label = [];
        if (typeof label === 'string' || typeof label === 'number') {
            // label is a string; assign to first array element
            newNode.label[0] = label;
        } else {
            // Otherwise, assume label is an array; clone it
            newNode.label = label.slice(0);
        }
        newNode.metadata = _.clone(options);
        newNode.nodes = [];
        newNode.subnodes = subnodes;
        const target = (options.parentNode && options.parentNode.nodes) || this.nodes;
        target.push(newNode);
    }

    // Add edge to the graph architecture
    // source: ID of node for the edge to originate; corresponds to 'id' parm of addNode
    // target: ID of node for the edge to terminate
    addEdge(source, target) {
        const newEdge = {};
        newEdge.id = '';
        newEdge.source = source;
        newEdge.target = target;
        this.edges.push(newEdge);
    }

    // Return the JSON graph node matching the given ID. This function finds the node
    // regardless of where it is in the hierarchy of nodes.
    // id: ID of the node to search for
    // parent: Optional parent node to begin the search; graph root by default
    getNode(id, parent) {
        const nodes = (parent && parent.nodes) || this.nodes;

        for (let i = 0; i < nodes.length; i += 1) {
            if (nodes[i].id === id) {
                return nodes[i];
            }
            if (nodes[i].nodes.length) {
                const matching = this.getNode(id, nodes[i]);
                if (matching) {
                    return matching;
                }
            }
            if (nodes[i].subnodes && nodes[i].subnodes.length) {
                const matching = nodes[i].subnodes.find(subnode => id === subnode.id);
                if (matching) {
                    return matching;
                }
            }
        }
        return undefined;
    }

    getSubnode(id, parent) {
        const nodes = (parent && parent.nodes) || this.nodes;

        for (let i = 0; i < nodes.length; i += 1) {
            const node = nodes[i];
            if (node.subnodes && node.subnodes.length) {
                for (let j = 0; j < node.subnodes.length; j += 1) {
                    if (node.subnodes[j].id === id) {
                        return node.subnodes[j];
                    }
                }
            } else if (nodes[i].nodes.length) {
                const matching = this.getSubnode(id, nodes[i]);
                if (matching) {
                    return matching;
                }
            }
        }
        return undefined;
    }

    getEdge(source, target) {
        if (this.edges && this.edges.length) {
            const matching = _(this.edges).find(edge =>
                (source === edge.source) && (target === edge.target)
            );
            return matching;
        }
        return undefined;
    }

    // Return array of function results for each node in the graph. The supplied function, fn, gets called with each node
    // in the graph. An array of these function results is returned.
    map(fn, context, nodes) {
        const thisNodes = nodes || this.nodes;
        let returnArray = [];

        for (let i = 0; i < thisNodes.length; i += 1) {
            const node = thisNodes[i];

            // Call the given function and add its return value to the array we're collecting
            returnArray.push(fn.call(context, node));

            // If the node has its own nodes, recurse
            if (node.nodes && node.nodes.length) {
                returnArray = returnArray.concat(this.map(fn, context, node.nodes));
            }
        }
        return returnArray;
    }

}


// Handle graphing throws. Exported for Jest tests.
export function GraphException(message, file0, file1) {
    this.message = message;
    if (file0) {
        this.file0 = file0;
    }
    if (file1) {
        this.file1 = file1;
    }
}


// Map a QC object to its corresponding two-letter abbreviation for the graph.
function qcAbbr(qc) {
    // As we add more QC object types, add to this object.
    const qcAbbrMap = {
        BigwigcorrelateQualityMetric: 'BC',
        BismarkQualityMetric: 'BK',
        ChipSeqFilterQualityMetric: 'CF',
        ComplexityXcorrQualityMetric: 'CX',
        CorrelationQualityMetric: 'CN',
        CpgCorrelationQualityMetric: 'CC',
        DuplicatesQualityMetric: 'DS',
        EdwbamstatsQualityMetric: 'EB',
        EdwcomparepeaksQualityMetric: 'EP',
        Encode2ChipSeqQualityMetric: 'EC',
        FastqcQualityMetric: 'FQ',
        FilteringQualityMetric: 'FG',
        GenericQualityMetric: 'GN',
        HotspotQualityMetric: 'HS',
        IDRQualityMetric: 'ID',
        IdrSummaryQualityMetric: 'IS',
        MadQualityMetric: 'MD',
        SamtoolsFlagstatsQualityMetric: 'SF',
        SamtoolsStatsQualityMetric: 'SS',
        StarQualityMetric: 'SR',
        TrimmingQualityMetric: 'TG',
    };

    let abbr = qcAbbrMap[qc['@type'][0]];
    if (!abbr) {
        // 'QC' is the generic, unmatched abbreviation if qcAbbrMap doesn't have a match.
        abbr = 'QC';
    }
    return abbr;
}


/**
 * Assembly a graph of files, the QC objects that belong to them, and the steps that connect them.
 * @param {object} dataset - Dataset object containing the files to graph.
 * @param {object} session - Current login session information.
 * @param {string} infoNodeId - Graph node ID of the currently selected node, whether file, step,
 *        or coalesced contributing file.
 * @param {array} files - Files to graph. This is the *real* source of data. Usually retrieved from
 *        a GET request for qualifying files.
 * @param {string} filterAssembly - Assembly to restrict graphed files to, or '' to not filter any
 *        of those.
 * @param {string} filterAnnotation - Annotation to restrict graphed files to, or '' to not filter
 *        any of those.
 * @param {boolean} colorize - True to add CSS classes to colorize the nodes based on their status.
 */
export function assembleGraph(files, dataset, options) {
    // Calculate a step ID from a file's derived_from array.
    function rDerivedFileIds(file) {
        if (file.derived_from && file.derived_from.length) {
            return file.derived_from.sort().join();
        }
        return '';
    }

    // Calculate a QC node ID.
    function rGenQcId(metric, file) {
        return `qc:${metric['@id'] + file['@id']}`;
    }

    /**
     * Generate a string of CSS classes for a file node. Plass the result into a `className` property of a component.
     *
     * @param {object-required} file - File we're generating the statuses for.
     * @param {bool} active - True if the file is active and should be highlighted as such.
     * @param (bool) colorize - True to colorize the nodes according to their status by adding a CSS class for their status
     * @param {string} addClasses - CSS classes to add in addition to the ones generated by the file statuses.
     */
    function fileCssClassGen(file, active, colorizeNode, addClasses) {
        let statusClass;
        if (colorizeNode) {
            statusClass = file.status.replace(/ /g, '-');
        }
        return `pipeline-node-file${active ? ' active' : ''}${colorizeNode ? ` ${statusClass}` : ''}${addClasses ? ` ${addClasses}` : ''}`;
    }

    const { infoNodeId, filterAssembly, filterAnnotation, colorize } = options;
    const derivedFileIds = _.memoize(rDerivedFileIds, file => file['@id']);
    const genQcId = _.memoize(rGenQcId, (metric, file) => metric['@id'] + file['@id']);

    // Begin collecting up information about the files from the search result, and gathering their
    // QC and analysis pipeline information.
    const allFiles = {}; // All searched files, keyed by file @id
    let matchingFiles = {}; // All files that match the current assembly/annotation, keyed by file @id
    const fileQcMetrics = {}; // List of all file QC metrics indexed by file @id
    const allPipelines = {}; // List of all pipelines indexed by step @id
    files.forEach((file) => {
        // allFiles gets all files from search regardless of filtering.
        allFiles[file['@id']] = file;

        // matchingFiles gets just the files matching the given filtering assembly/annotation.
        // Note that if all assemblies and annotations are selected, this function isn't called
        // because no graph gets displayed in that case.
        if ((file.assembly === filterAssembly) && ((!file.genome_annotation && !filterAnnotation) || (file.genome_annotation === filterAnnotation))) {
            // Note whether any files have an analysis step
            const fileAnalysisStep = file.analysis_step_version && file.analysis_step_version.analysis_step;
            if (!fileAnalysisStep || (file.derived_from && file.derived_from.length)) {
                // File has no analysis step or derives from other files, so it can be included in
                // the graph.
                matchingFiles[file['@id']] = file;

                // Collect any QC info that applies to this file and make it searchable by file
                // @id.
                if (file.quality_metrics && file.quality_metrics.length) {
                    fileQcMetrics[file['@id']] = file.quality_metrics;
                }

                // Save the pipeline array used for each step used by the file.
                if (fileAnalysisStep) {
                    allPipelines[fileAnalysisStep['@id']] = fileAnalysisStep.pipelines;
                }
            } // else file has analysis step but no derived from -- can't include in graph.
        }
    });

    // Generate a list of file @ids that other files (matching the current assembly and annotation)
    // derive from (i.e. files referenced in other files' derived_from). allDerivedFroms is keyed
    // by the derived-from file @id (whether it matches the current assembly and annotation or not)
    // and has an array of all files that derive from it for its value. So for example:
    //
    // allDerivedFroms = {
    //     /files/<matching accession>: [matching file, matching file],
    //     /files/<contributing accession>: [matching file, matching file],
    //     /files/<missing accession>: [matching file, matching file],
    // }
    const allDerivedFroms = {};
    Object.keys(matchingFiles).forEach((matchingFileId) => {
        const matchingFile = matchingFiles[matchingFileId];
        if (matchingFile.derived_from && matchingFile.derived_from.length) {
            matchingFile.derived_from.forEach((derivedFromAtId) => {
                // Copy reference to allFiles copy of file. Will be undefined for missing and
                // contributing files.
                if (allDerivedFroms[derivedFromAtId]) {
                    // Already saw a file derive from this one, so add the new reference to the end
                    // of the array of derived-from files.
                    allDerivedFroms[derivedFromAtId].push(matchingFile);
                } else {
                    // Never saw a file derive from this one, so make a new array with a reference
                    // to it.
                    allDerivedFroms[derivedFromAtId] = [matchingFile];
                }
            });
        }
    });
    // Remember, at this stage allDerivedFroms includes keys for missing files, files not matching
    // the chosen assembly/annotation, and contributing files.

    // Filter any "island" files out of matchingFiles -- that is, files that derive from no other
    // files, and no other files derive from it.
    matchingFiles = (function matchingFilesFunc() {
        const noIslandFiles = {};
        Object.keys(matchingFiles).forEach((matchingFileId) => {
            const matchingFile = matchingFiles[matchingFileId];
            if ((matchingFile.derived_from && matchingFile.derived_from.length) || allDerivedFroms[matchingFileId]) {
                // This file either has derived_from set, or other files derive from it. Copy it to
                // our destination object.
                noIslandFiles[matchingFileId] = matchingFile;
            }
        });
        return noIslandFiles;
    }());
    if (Object.keys(matchingFiles).length === 0) {
        throw new GraphException('No graph: no file relationships for the selected assembly/annotation');
    }
    // At this stage, any files in matchingFiles will be rendered. We just have to figure out what
    // other files need rendering, like raw sequencing files, contributing files, and derived-from
    // files that have a non-matching annotation and assembly.

    const allReplicates = {}; // All file's replicates as keys; each key references an array of files
    Object.keys(matchingFiles).forEach((matchingFileId) => {
        // If the file is part of a single biological replicate, add it to an array of files, where
        // the arrays are in an object keyed by their relevant biological replicate number.
        const matchingFile = matchingFiles[matchingFileId];
        let replicateNum = (matchingFile.biological_replicates && matchingFile.biological_replicates.length === 1) ? matchingFile.biological_replicates[0] : undefined;
        if (replicateNum) {
            if (allReplicates[replicateNum]) {
                allReplicates[replicateNum].push(matchingFile);
            } else {
                allReplicates[replicateNum] = [matchingFile];
            }
        }

        // Add each file that a matching file derives from to the replicates.
        if (matchingFile.derived_from && matchingFile.derived_from.length) {
            matchingFile.derived_from.forEach((derivedFromAtId) => {
                const file = allFiles[derivedFromAtId];
                if (file) {
                    replicateNum = (file.biological_replicates && file.biological_replicates.length === 1) ? file.biological_replicates[0] : undefined;
                    if (replicateNum) {
                        if (allReplicates[replicateNum]) {
                            allReplicates[replicateNum].push(matchingFile);
                        } else {
                            allReplicates[replicateNum] = [matchingFile];
                        }
                    }
                }
            });
        }
    });

    // Make a list of contributing files that matchingFiles files derive from.
    const usedContributingFiles = {};
    if (dataset.contributing_files && dataset.contributing_files.length) {
        dataset.contributing_files.forEach((contributingFileAtId) => {
            if (contributingFileAtId in allDerivedFroms) {
                usedContributingFiles[contributingFileAtId] = allDerivedFroms[contributingFileAtId];
            }
        });
    }

    // Go through each used contributing file and set a property within it showing which files
    // derive from it. We'll need that for coalescing contributing files.
    const allCoalesced = {};
    let coalescingGroups = {};
    if (Object.keys(usedContributingFiles).length) {
        // Now use the derivedFiles property of every contributing file to group them into potential
        // coalescing nodes. `coalescingGroups` gets assigned an object keyed by dataset file ids
        // hashed to a stringified 32-bit integer, and mapped to an array of contributing files they
        // derive from.
        coalescingGroups = _(Object.keys(usedContributingFiles)).groupBy((contributingFileAtId) => {
            const derivedFiles = usedContributingFiles[contributingFileAtId];
            return globals.hashCode(derivedFiles.map(derivedFile => derivedFile['@id']).join(',')).toString();
        });

        // Set a `coalescingGroup` property in each contributing file with its coalescing group's hash
        // value. That'll be important when we add step nodes.
        const coalescingGroupKeys = Object.keys(coalescingGroups);
        if (coalescingGroupKeys && coalescingGroupKeys.length) {
            coalescingGroupKeys.forEach((groupHash) => {
                const group = coalescingGroups[groupHash];
                if (group.length >= MINIMUM_COALESCE_COUNT) {
                    // Number of files in the coalescing group is at least the minimum number of files we
                    // allow in a coalescing group. Mark every contributing file in the group with the
                    // group's hash value in a `coalescingGroup` property that step node can connnect to.
                    group.forEach((contributingFileAtId) => {
                        allCoalesced[contributingFileAtId] = groupHash;

                        // Remove coalesced files from usedContributingFiles because we don't want
                        // to render individual files that have been coalesced.
                        delete usedContributingFiles[contributingFileAtId];
                    });
                } else {
                    // The number of contributing files in a coalescing group isn't above our
                    // threshold. Don't use this coalescingGroup anymore and just render them the
                    // same as normal files.
                    delete coalescingGroups[groupHash];
                }
            });
        }
    }

    // See if we have any derived_from files that we have no information on, likely because they're
    // not released and we're not logged in. We'll render them with information-less dummy nodes.
    const allMissingFiles = [];
    Object.keys(allDerivedFroms).forEach((derivedFromFileAtId) => {
        if (!allFiles[derivedFromFileAtId] && !allCoalesced[derivedFromFileAtId]) {
            // The derived-from file isn't in our dataset file list, nor in coalesced contributing
            // files. Now see if it's in non-coalesced contributing files.
            if (!usedContributingFiles[derivedFromFileAtId]) {
                allMissingFiles.push(derivedFromFileAtId);
            }
        }
    });

    // Create an empty graph architecture that we fill in next.
    const jsonGraph = new JsonGraph(dataset.accession);

    // Create nodes for the replicates.
    Object.keys(allReplicates).forEach((replicateNum) => {
        if (allReplicates[replicateNum] && allReplicates[replicateNum].length) {
            jsonGraph.addNode(`rep:${replicateNum}`, `Replicate ${replicateNum}`, {
                cssClass: 'pipeline-replicate',
                type: 'Rep',
                shape: 'rect',
                cornerRadius: 0,
            });
        }
    });

    // Go through each file matching the currently selected assembly/annotation and add it to our
    // graph.
    Object.keys(matchingFiles).forEach((fileId) => {
        const file = matchingFiles[fileId];
        const fileNodeId = `file:${file['@id']}`;
        const fileNodeLabel = `${file.title} (${file.output_type})`;
        const fileCssClass = fileCssClassGen(file, infoNodeId === fileNodeId, colorize);
        const fileRef = file;
        const replicateNode = (file.biological_replicates && file.biological_replicates.length === 1) ? jsonGraph.getNode(`rep:${file.biological_replicates[0]}`) : null;
        let metricsInfo;

        // Add QC metrics info from the file to the list to generate the nodes later.
        if (fileQcMetrics[fileId] && fileQcMetrics[fileId].length) {
            const sortedMetrics = fileQcMetrics[fileId].sort((a, b) => (a['@type'][0] > b['@type'][0] ? 1 : (a['@type'][0] < b['@type'][0] ? -1 : 0)));
            metricsInfo = sortedMetrics.map((metric) => {
                const qcId = genQcId(metric, file);
                return {
                    id: qcId,
                    label: qcAbbr(metric),
                    '@type': ['QualityMetric'],
                    class: `pipeline-node-qc-metric${infoNodeId === qcId ? ' active' : ''}`,
                    tooltip: true,
                    ref: metric,
                    parent: file,
                };
            });
        }

        // Add a node for a regular searched file.
        jsonGraph.addNode(fileNodeId, fileNodeLabel, {
            cssClass: fileCssClass,
            type: 'File',
            shape: 'rect',
            cornerRadius: 16,
            parentNode: replicateNode,
            ref: fileRef,
        }, metricsInfo);

        // Figure out the analysis step we need to render between the node we just rendered and its
        // derived_from.
        let stepId;
        let label;
        let pipelineInfo;
        let error;
        const fileAnalysisStep = file.analysis_step_version && file.analysis_step_version.analysis_step;
        if (fileAnalysisStep) {
            // Make an ID and label for the step
            stepId = `step:${derivedFileIds(file) + fileAnalysisStep['@id']}`;
            label = fileAnalysisStep.analysis_step_types;
            pipelineInfo = allPipelines[fileAnalysisStep['@id']];
            error = false;
        } else if (derivedFileIds(file)) {
            // File derives from others, but no analysis step; make dummy step.
            stepId = `error:${derivedFileIds(file)}`;
            label = 'Software unknown';
            pipelineInfo = null;
            error = true;
        } else {
            // No analysis step and no derived_from; don't add a step.
            stepId = '';
        }

        // If we have a step to render, do that here.
        if (stepId) {
            // Add the step to the graph only if we haven't for this derived-from set already
            if (!jsonGraph.getNode(stepId)) {
                jsonGraph.addNode(stepId, label, {
                    cssClass: `pipeline-node-analysis-step${(infoNodeId === stepId ? ' active' : '') + (error ? ' error' : '')}`,
                    type: 'Step',
                    shape: 'rect',
                    cornerRadius: 4,
                    parentNode: replicateNode,
                    ref: fileAnalysisStep,
                    pipelines: pipelineInfo,
                    fileId: file['@id'],
                    fileAccession: file.title,
                    stepVersion: file.analysis_step_version,
                });
            }

            // Connect the file to the step, and the step to the derived_from files
            jsonGraph.addEdge(stepId, fileNodeId);
            file.derived_from.forEach((derivedFromAtId) => {
                const derivedFromFile = allFiles[derivedFromAtId] || allMissingFiles.some(missingFileId => missingFileId === derivedFromAtId);
                if (derivedFromFile) {
                    // Not derived from a contributing file; just add edges normally.
                    const derivedFileId = `file:${derivedFromAtId}`;
                    if (!jsonGraph.getEdge(derivedFileId, stepId)) {
                        jsonGraph.addEdge(derivedFileId, stepId);
                    }
                } else {
                    // File derived from a contributing file; add edges to a coalesced node
                    // that we'll add to the graph later.
                    const coalescedContributing = allCoalesced[derivedFromAtId];
                    if (coalescedContributing) {
                        // Rendering a coalesced contributing file.
                        const derivedFileId = `coalesced:${coalescedContributing}`;
                        if (!jsonGraph.getEdge(derivedFileId, stepId)) {
                            jsonGraph.addEdge(derivedFileId, stepId);
                        }
                    } else if (usedContributingFiles[derivedFromAtId]) {
                        const derivedFileId = `file:${derivedFromAtId}`;
                        if (!jsonGraph.getEdge(derivedFileId, stepId)) {
                            jsonGraph.addEdge(derivedFileId, stepId);
                        }
                    }
                }
            });
        }
    });

    // Go through each derived-from file and add it to our graph.
    Object.keys(allDerivedFroms).forEach((fileId) => {
        const file = allFiles[fileId];
        if (file && !matchingFiles[fileId]) {
            const fileNodeId = `file:${file['@id']}`;
            const fileNodeLabel = `${file.title} (${file.output_type})`;
            const fileCssClass = fileCssClassGen(file, infoNodeId === fileNodeId, colorize);
            const fileRef = file;
            const replicateNode = (file.biological_replicates && file.biological_replicates.length === 1) ? jsonGraph.getNode(`rep:${file.biological_replicates[0]}`) : null;

            jsonGraph.addNode(fileNodeId, fileNodeLabel, {
                cssClass: fileCssClass,
                type: 'File',
                shape: 'rect',
                cornerRadius: 16,
                parentNode: replicateNode,
                ref: fileRef,
            });
        }
    });

    // Go through each derived-from contributing file and add it to our graph.
    Object.keys(usedContributingFiles).forEach((fileAtId) => {
        const fileNodeId = `file:${fileAtId}`;
        const fileNodeLabel = `${globals.atIdToAccession(fileAtId)}`;
        const fileCssClass = `pipeline-node-file contributing${infoNodeId === fileNodeId ? ' active' : ''}`;

        jsonGraph.addNode(fileNodeId, fileNodeLabel, {
            cssClass: fileCssClass,
            type: 'File',
            shape: 'rect',
            cornerRadius: 16,
            contributing: fileAtId,
            ref: {},
        });
    });

    // Now add coalesced nodes to the graph.
    Object.keys(coalescingGroups).forEach((groupHash) => {
        const coalescingGroup = coalescingGroups[groupHash];
        if (coalescingGroup.length) {
            const fileNodeId = `coalesced:${groupHash}`;
            const fileCssClass = `pipeline-node-file contributing${infoNodeId === fileNodeId ? ' active' : ''}`;
            jsonGraph.addNode(fileNodeId, `${coalescingGroup.length} contributing files`, {
                cssClass: fileCssClass,
                type: 'File',
                shape: 'stack',
                cornerRadius: 16,
                contributing: groupHash,
                ref: coalescingGroup,
            });
        }
    });

    // Add missing-file nodes to the graph.
    allMissingFiles.forEach((missingFileAtId) => {
        const fileNodeAccession = globals.atIdToAccession(missingFileAtId);
        const fileNodeId = `file:${missingFileAtId}`;
        const fileNodeLabel = `${fileNodeAccession} (unknown)`;
        const fileCssClass = 'pipeline-node-file error';

        jsonGraph.addNode(fileNodeId, fileNodeLabel, {
            cssClass: fileCssClass,
            type: 'File',
            shape: 'rect',
            cornerRadius: 16,
        });
    });

    return jsonGraph;
}


export class Graph extends React.Component {
    // Take a JsonGraph object and convert it to an SVG graph with the Dagre-D3 library.
    // jsonGraph: JsonGraph object containing nodes and edges.
    // graph: Initialized empty Dagre-D3 graph.
    static convertGraph(jsonGraph, graph) {
        // graph: dagre graph object
        // parent: JsonGraph node to insert nodes into
        function convertGraphInner(subgraph, parent) {
            // For each node in parent node (or top-level graph)
            parent.nodes.forEach((node) => {
                subgraph.setNode(node.id, {
                    label: node.label.length > 1 ? node.label : node.label[0],
                    rx: node.metadata.cornerRadius,
                    ry: node.metadata.cornerRadius,
                    class: node.metadata.cssClass,
                    shape: node.metadata.shape,
                    paddingLeft: '20',
                    paddingRight: '20',
                    paddingTop: '10',
                    paddingBottom: '10',
                    subnodes: node.subnodes,
                });
                if (!parent.root) {
                    subgraph.setParent(node.id, parent.id);
                }
                if (node.nodes.length) {
                    convertGraphInner(subgraph, node);
                }
            });
        }

        // Convert the nodes
        convertGraphInner(graph, jsonGraph);

        // Convert the edges
        jsonGraph.edges.forEach((edge) => {
            graph.setEdge(edge.source, edge.target, { lineInterpolate: 'basis' });
        });
    }

    constructor() {
        super();

        // Set initial React component state.
        this.state = {
            dlDisabled: false, // Download button disabled because of IE
            verticalGraph: false, // True for vertically oriented graph, false for horizontal
            zoomLevel: null, // Graph zoom level; null to indicate not set
        };

        // Component state variables we don't want to cause a rerender.
        this.cv = {
            graph: null, // Currently rendered JSON graph object
            viewBoxWidth: 0, // Width of the SVG's viewBox
            viewBoxHeight: 0, // Height of the SVG's viewBox
            aspectRatio: 0, // Aspect ratio of graph -- width:height
            zoomMouseDown: false, // Mouse currently controlling zoom slider
            dagreLoaded: false, // Dagre JS library has been loaded
            zoomFactor: 0, // Amount zoom slider value changes should change width of graph
        };

        // Bind `this` to non-React methods.
        this.setInitialZoomLevel = this.setInitialZoomLevel.bind(this);
        this.drawGraph = this.drawGraph.bind(this);
        this.bindClickHandlers = this.bindClickHandlers.bind(this);
        this.handleOrientationClick = this.handleOrientationClick.bind(this);
        this.handleDlClick = this.handleDlClick.bind(this);
        this.rangeChange = this.rangeChange.bind(this);
        this.rangeMouseDown = this.rangeMouseDown.bind(this);
        this.rangeMouseUp = this.rangeMouseUp.bind(this);
        this.rangeDoubleClick = this.rangeDoubleClick.bind(this);
    }

    componentDidMount() {
        if (BrowserFeat.getBrowserCaps('svg')) {
            // Delay loading dagre for Jest testing compatibility;
            // Both D3 and Jest have their own conflicting JSDOM instances
            require.ensure(['dagre-d3', 'd3'], (require) => {
                if (this.refs.graphdisplay) {
                    this.d3 = require('d3');
                    this.dagreD3 = require('dagre-d3');

                    const el = this.refs.graphdisplay;

                    // Add SVG element to the graph component, and assign it classes, sizes, and a group
                    const svg = this.d3.select(el).insert('svg', '#graph-node-info')
                        .attr('id', 'pipeline-graph')
                        .attr('preserveAspectRatio', 'none')
                        .attr('version', '1.1');
                    this.cv.savedSvg = svg;

                    // Draw the graph into the panel; get the graph's view box and save it for
                    // comparisons later
                    const { viewBoxWidth, viewBoxHeight } = this.drawGraph(el);
                    this.cv.viewBoxWidth = viewBoxWidth;
                    this.cv.viewBoxHeight = viewBoxHeight;

                    // Based on the size of the graph and view box, set the initial zoom level to
                    // something that fits well.
                    const initialZoomLevel = this.setInitialZoomLevel(el, svg);
                    this.setState({ zoomLevel: initialZoomLevel });

                    // Bind node/subnode click handlers to parent component handlers
                    this.bindClickHandlers(this.d3, el);
                }
            });
        } else {
            // Output text indicating that graphs aren't supported.
            let el = this.refs.graphdisplay;
            const para = document.createElement('p');
            para.className = 'browser-error';
            para.innerHTML = 'Graphs not supported in your browser. You need a more modern browser to view it.';
            el.appendChild(para);

            // Disable the download button
            el = this.refs.dlButton;
            el.setAttribute('disabled', 'disabled');
        }

        // Disable download button if running on Trident (IE non-Spartan) browsers
        if (BrowserFeat.getBrowserCaps('uaTrident') || BrowserFeat.getBrowserCaps('uaEdge')) {
            this.setState({ dlDisabled: true });
        }
    }

    // State change; redraw the graph
    componentDidUpdate() {
        if (this.dagreD3 && !this.cv.zoomMouseDown) {
            const el = this.refs.graphdisplay; // Change in React 0.14
            const { viewBoxWidth, viewBoxHeight } = this.drawGraph(el);

            // Bind node/subnode click handlers to parent component handlers
            this.bindClickHandlers(this.d3, el);

            // If the viewbox has changed since the last time, need to recalculate the zooming
            // parameters.
            if (Math.abs(viewBoxWidth - this.cv.viewBoxWidth) > 10 || Math.abs(viewBoxHeight - this.cv.viewBoxHeight) > 10) {
                // Based on the size of the graph and view box, set the initial zoom level to
                // something that fits well.
                const initialZoomLevel = this.setInitialZoomLevel(el, this.cv.savedSvg);
                this.setState({ zoomLevel: initialZoomLevel });
            }

            this.cv.viewBoxWidth = viewBoxWidth;
            this.cv.viewBoxHeight = viewBoxHeight;
        }
    }

    // For the given container element and its svg, calculate an initial zoom level that fits the
    // graph into the container element. Returns the zoom level appropriate for the initial zoom.
    // Also sets component variables for later zoom calculations, and sets the "width" and "height"
    // of the SVG to scale it to fit the container element.
    setInitialZoomLevel(el, svg) {
        let svgWidth;
        let svgHeight;
        const viewBox = svg.attr('viewBox').split(' ');
        const viewBoxWidth = viewBox[2];
        const viewBoxHeight = viewBox[3];

        // Calculate minimum and maximum pixel width, and zoom factor which is the amount each
        // slider value gets multiplied by to get a new graph width. Save all these in component
        // variables.
        const minZoomWidth = viewBoxWidth / 4;
        const maxZoomWidth = viewBoxWidth * 2;
        this.cv.zoomFactor = (maxZoomWidth - minZoomWidth) / 100;
        this.cv.minZoomWidth = minZoomWidth;
        this.cv.aspectRatio = viewBoxWidth / viewBoxHeight;

        // Get the width of the graph panel
        if (el.clientWidth >= viewBoxWidth) {
            svgWidth = viewBoxWidth;
            svgHeight = viewBoxHeight;
        } else {
            svgWidth = el.clientWidth;
            svgHeight = svgWidth / this.cv.aspectRatio;
        }
        const zoomLevel = (svgWidth - this.cv.minZoomWidth) / this.cv.zoomFactor;
        svg.attr('width', svgWidth).attr('height', svgHeight);
        return zoomLevel;
    }

    // Draw the graph on initial draw as well as on state changes. An <svg> element to draw into
    // must already exist in the HTML element in the el parm. This also sets the viewBox of the
    // SVG to its natural height. eslint exception for dagreD3.render call.
    /* eslint new-cap: ["error", { "newIsCap": false }] */
    drawGraph(el) {
        const d3 = this.d3;
        const dagreD3 = this.dagreD3;
        d3.selectAll('svg#pipeline-graph > *').remove(); // http://stackoverflow.com/questions/22452112/nvd3-clear-svg-before-loading-new-chart#answer-22453174
        const svg = d3.select(el).select('svg');

        // Clear `width` and `height` attributes if they exist
        svg.attr('width', null).attr('height', null).attr('viewBox', null);

        // Create a new empty graph
        const g = new dagreD3.graphlib.Graph({ multigraph: true, compound: true })
            .setGraph({ rankdir: this.state.verticalGraph ? 'TB' : 'LR' })
            .setDefaultEdgeLabel(() => ({}));
        const render = new dagreD3.render();

        // Convert from given node architecture to the dagre nodes and edges
        Graph.convertGraph(this.cv.graph, g);

        // Run the renderer. This is what draws the final graph.
        render(svg, g);

        // Get the natural (unscaled) width and height of the graph
        const graphWidth = Math.ceil(g.graph().width);
        const graphHeight = Math.ceil(g.graph().height);

        // Get the unscaled width and height of the graph including margins, and make a viewBox
        // for the graph so it'll render with the margins. The SVG's viewBox is always the
        // unscaled coordinates and immutable
        const viewBoxWidth = graphWidth + (graphWidthMargin * 2);
        const viewBoxHeight = graphHeight + (graphHeightMargin * 2);
        const viewBox = [-graphWidthMargin, -graphHeightMargin, viewBoxWidth, viewBoxHeight];

        // Set the viewBox of the SVG based on its unscaled extents
        this.cv.savedSvg.attr('viewBox', viewBox.join(' '));

        // Now set the `width` and `height` attributes based on the current zoom level
        if (this.state.zoomLevel && this.cv.zoomFactor) {
            const width = (this.state.zoomLevel * this.cv.zoomFactor) + this.cv.minZoomWidth;
            const height = width / this.cv.aspectRatio;
            svg.attr('width', width).attr('height', height);
        }

        // Return the SVG so callers can do more with this after drawing the unscaled graph
        return { viewBoxWidth, viewBoxHeight };
    }

    bindClickHandlers(d3, el) {
        // Add click event listeners to each node rendering. Node's ID is its ENCODE object ID
        const svg = d3.select(el);
        const nodes = svg.selectAll('g.node');
        const subnodes = svg.selectAll('g.subnode circle');

        nodes.on('click', (nodeId) => {
            this.props.nodeClickHandler(nodeId);
        });
        subnodes.on('click', (subnode) => {
            d3.event.stopPropagation();
            this.props.nodeClickHandler(subnode.id);
        });
    }

    handleOrientationClick() {
        this.setState({ verticalGraph: !this.state.verticalGraph });
    }

    handleDlClick() {
        // Collect CSS styles that apply to the graph and insert them into the given SVG element
        function attachStyles(el) {
            let stylesText = '';
            const sheets = document.styleSheets;

            // Search every style in the style sheet(s) for those applying to graphs.
            // Note: Not using ES5 looping constructs because these aren’t real arrays.
            if (sheets) {
                for (let i = 0; i < sheets.length; i += 1) {
                    const rules = sheets[i].cssRules;
                    if (rules) {
                        for (let j = 0; j < rules.length; j += 1) {
                            const rule = rules[j];

                            // If a style rule starts with 'g.' (svg group), we know it applies to the graph.
                            // Note: In some browsers, indexOf is a bit faster; on others substring is a bit faster.
                            // FF(31)'s substring is much faster than indexOf.
                            if (typeof (rule.style) !== 'undefined' && rule.selectorText && rule.selectorText.substring(0, 2) === 'g.') {
                                // If any elements use this style, add the style's CSS text to our style text accumulator.
                                const elems = el.querySelectorAll(rule.selectorText);
                                if (elems.length) {
                                    stylesText += `${rule.selectorText} { ${rule.style.cssText} }\n`;
                                }
                            }
                        }
                    }
                }
            }

            // Insert the collected SVG styles into a new style element
            const styleEl = document.createElement('style');
            styleEl.setAttribute('type', 'text/css');
            styleEl.innerHTML = `/* <![CDATA[ */\n${stylesText}\n/* ]]> */`;

            // Insert the new style element into the beginning of the given SVG element
            el.insertBefore(styleEl, el.firstChild);
        }

        // Going to be manipulating the SVG node, so make a clone to make GC’s job harder
        const svgNode = this.cv.savedSvg.node().cloneNode(true);

        // Reset the SVG's size to its natural size
        const viewBox = this.cv.savedSvg.attr('viewBox').split(' ');
        svgNode.setAttribute('width', viewBox[2]);
        svgNode.setAttribute('height', viewBox[3]);

        // Attach graph CSS to SVG node clone
        attachStyles(svgNode);

        // Turn SVG node clone into a data url and attach to a new Image object. This begins "loading" the image.
        const serializer = new XMLSerializer();
        const svgXml = `<?xml version="1.0" standalone="no"?><!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">${serializer.serializeToString(svgNode)}`;
        const img = new Image();
        img.src = `data:image/svg+xml;base64,${window.btoa(svgXml)}`;

        // Once the svg is loaded into the image (purely in memory, not in DOM), draw it into a <canvas>
        img.onload = function onload() {
            // Make a new memory-based canvas and draw the image into it.
            const canvas = document.createElement('canvas');
            canvas.width = img.width;
            canvas.height = img.height;
            const context = canvas.getContext('2d');
            context.drawImage(img, 0, 0, img.width, img.height);

            // Make the image download by making a fake <a> and pretending to click it.
            const a = document.createElement('a');
            a.download = this.props.graph.id ? `${this.props.graph.id}.png` : 'graph.png';
            a.href = canvas.toDataURL('image/png');
            a.setAttribute('data-bypass', 'true');
            document.body.appendChild(a);
            a.click();
        }.bind(this);
    }

    rangeChange(e) {
        // Called when the user clicks/drags the zoom slider; value comes from the slider 0-100
        const value = e.target.value;

        // Calculate the new graph width and height for the new zoom value
        const width = (value * this.cv.zoomFactor) + this.cv.minZoomWidth;
        const height = width / this.cv.aspectRatio;

        // Get the SVG in the DOM and update its width and height
        const svgEl = document.getElementById('pipeline-graph');
        svgEl.setAttribute('width', width);
        svgEl.setAttribute('height', height);

        // Remember zoom level as a state -- causes rerender remember!
        this.setState({ zoomLevel: value });
    }

    rangeMouseDown() {
        // Mouse clicked in zoom slider
        this.cv.zoomMouseDown = true;
    }

    rangeMouseUp(e) {
        // Mouse released from zoom slider
        this.cv.zoomMouseDown = false;
        this.rangeChange(e); // Fix for IE11 as onChange doesn't get called; at least call this after dragging
        // For IE11 fix, see https://github.com/facebook/react/issues/554#issuecomment-188288228
    }

    rangeDoubleClick() {
        // Handle a double click in the zoom slider
        const el = this.refs.graphdisplay;
        const zoomLevel = this.setInitialZoomLevel(el, this.cv.savedSvg);
        this.setState({ zoomLevel });
    }

    render() {
        const { dataset, files, selectedAssembly, selectedAnnotation } = this.props;
        const orientBtnAlt = `Orient graph ${this.state.verticalGraph ? 'horizontally' : 'vertically'}`;
        const currOrientKey = this.state.verticalGraph ? 'orientH' : 'orientV';
        const noDefaultClasses = this.props.noDefaultClasses;

        // Build node graph of the files and analysis steps with this experiment
        if (files.length) {
            try {
                this.cv.graph = assembleGraph(
                    dataset,
                    files,
                    {
                        infoNodeId: this.state.infoNodeId,
                        selectedAssembly,
                        selectedAnnotation,
                        colorize: this.state.colorize,
                    }
                );
            } catch (e) {
                console.warn(e.message + (e.file0 ? ` -- file0:${e.file0}` : '') + (e.file1 ? ` -- file1:${e.file1}` : ''));
            }
        }

        return (
            <Panel noDefaultClasses={noDefaultClasses}>
                <div className="zoom-control-area">
                    <table className="zoom-control">
                        <tbody>
                            <tr>
                                <td className="zoom-indicator"><i className="icon icon-minus" /></td>
                                <td className="zomm-controller"><input type="range" className="zoom-slider" min={minZoom} max={maxZoom} value={this.state.zoomLevel === null ? 0 : this.state.zoomLevel} onChange={this.rangeChange} onDoubleClick={this.rangeDoubleClick} onMouseUp={this.rangeMouseUp} onMouseDown={this.rangeMouseDown} /></td>
                                <td className="zoom-indicator"><i className="icon icon-plus" /></td>
                            </tr>
                        </tbody>
                    </table>
                </div>
                <div ref="graphdisplay" className="graph-display" onScroll={this.scrollHandler} />
                <div className="graph-dl clearfix">
                    <button className="btn btn-info btn-sm btn-orient" title={orientBtnAlt} onClick={this.handleOrientationClick}>{svgIcon(currOrientKey)}<span className="sr-only">{orientBtnAlt}</span></button>
                    <button ref="dlButton" className="btn btn-info btn-sm" value="Test" onClick={this.handleDlClick} disabled={this.state.dlDisabled}>Download Graph</button>
                </div>
                {this.props.children}
            </Panel>
        );
    }
}

Graph.propTypes = {
    files: PropTypes.array.isRequired, // Array of files to render
    dataset: PropTypes.object.isRequired, // Dataset object the graph is being rendered into
    selectedAssembly: PropTypes.string, // Selected assembly to display
    selectedAnnotation: PropTypes.string, // Selected annotation to display
    nodeClickHandler: PropTypes.func.isRequired, // Function to call to handle clicks in a node
    noDefaultClasses: PropTypes.bool, // True to supress default CSS classes on <Panel> components
    children: PropTypes.node,
};

Graph.defaultProps = {
    selectedAssembly: '',
    selectedAnnotation: '',
    children: null,
    noDefaultClasses: false,
};


class FileGraph extends React.Component {
    constructor() {
        super();

        // Initialize React state variables.
        this.state = {
            contributingFiles: {}, // List of contributing file objects we've requested; acts as a cache too
            coalescedFiles: {}, // List of coalesced files we've requested; acts as a cache too
            infoModalOpen: false, // Graph information modal open
        };
    }

    render() {
        const { files, dataset, selectedAssembly, selectedAnnotation, handleNodeClick } = this.props;

        // Build node graph of the files and analysis steps with this experiment
        if (files && files.length && (selectedAssembly || selectedAnnotation)) {
            return <Graph files={files} dataset={dataset} nodeClickHandler={handleNodeClick} />;
        }
        return <p className="browser-error">Graph not applicable.</p>;
    }
}

FileGraph.propTypes = {
    files: PropTypes.array.isRequired, // Array of files we're graphing
    dataset: PropTypes.object.isRequired, // dataset these files are being rendered into
    selectedAssembly: PropTypes.string, // Currently selected assembly
    selectedAnnotation: PropTypes.string, // Currently selected annotation
    handleNodeClick: PropTypes.func.isRequired, // Parent function to call when a graph node is clicked
};

FileGraph.defaultProps = {
    selectedAssembly: '',
    selectedAnnotation: '',
};
