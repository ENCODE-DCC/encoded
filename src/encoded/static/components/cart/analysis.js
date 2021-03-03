import _ from 'underscore';
import { computeAssemblyAnnotationValue } from '../objectutils';


/** Lab path we see for the ENCODE uniform processing pipeline */
const UNIFORM_PIPELINE_LAB = '/labs/encode-processing-pipeline/';

/** Order that all possible lab strings should sort. */
const labSortOrder = [
    'ENCODE4',
    'ENCODE3',
    'Uniform',
    'Lab custom',
];


/**
 * Compile the usable experiment analysis objects into a form for rendering a dropdown of pipeline
 * labs.
 * @param {object} experiment Contains the analyses to convert into an pipeline labs dropdown
 * @param {array} files Array of all files from all datasets in the cart.
 *
 * @return {array} Compiled analyses information, each element with the form:
 * {
 *      title: Analysis dropdown title
 *      status: Analysis object submission status
 *      lab: Generally ENCODE or other
 *      version: Pipeline version number -- "major.minor.patch"
 *      assembly: Assembly string matching assembly facet terms
 *      annotation: Genome annotation string
 *      assemblyAnnotationValue: Value used to sort assembly/annotation
 *      files: Array of files selected with the pipeline lab and assembly
 * }
 */
const compileAnalysesByTitle = (experiment, files = []) => {
    let compiledAnalyses = [];
    if (experiment.analysis_objects && experiment.analysis_objects.length > 0) {
        // Get all the analysis objects that qualify for inclusion in the Pipeline facet.
        const qualifyingAnalyses = experiment.analysis_objects.filter((analysis) => {
            const rfas = _.uniq(analysis.pipeline_award_rfas);

            // More than one lab OK, as long as none of them is `UNIFORM_PIPELINE_LAB` --
            // `UNIFORM_PIPELINE_LAB` is only valid if alone.
            return (
                analysis.assembly
                && analysis.assembly !== 'mixed'
                && analysis.genome_annotation !== 'mixed'
                && analysis.pipeline_award_rfas.length === 1
                && analysis.pipeline_labs.length > 0
                && !(analysis.pipeline_labs.length === 1 && analysis.pipeline_labs[0] === UNIFORM_PIPELINE_LAB && rfas.length > 1)
            );
        });

        if (qualifyingAnalyses.length > 0) {
            // Group all the qualifying analyses' files by their title so we can consolidate their
            // data into one compiled analysis object per title.
            const analysesByTitle = _(qualifyingAnalyses).groupBy((analysis) => analysis.title);

            // Fill in the compiled object with the labs that group the files.
            const fileIds = files.map((file) => file['@id']);
            compiledAnalyses = Object.keys(analysesByTitle).reduce((analyses, title) => {
                // Combine all files under all analysis objects sharing the same title.
                const assemblyFiles = _.uniq(analysesByTitle[title].reduce((accFiles, analysis) => accFiles.concat(analysis.files), []).filter((file) => fileIds.includes(file)));
                if (assemblyFiles.length > 0) {
                    // Extract the lab name from the title. All analyses under one title should
                    // have all the same characteristics, so pick the first one to use as a source.
                    const representativeAnalysis = analysesByTitle[title][0];
                    const lab = labSortOrder.map((labName) => `${labName} `).find((labName) => representativeAnalysis.title.startsWith(labName));

                    // Add a new compiled analysis object.
                    return analyses.concat({
                        title: representativeAnalysis.title,
                        status: representativeAnalysis.status,
                        lab: lab ? lab.slice(0, -1) : '', // Trim last matching space
                        version: representativeAnalysis.pipeline_version || '',
                        assembly: representativeAnalysis.assembly || '',
                        annotation: representativeAnalysis.genome_annotation || '',
                        assemblyAnnotationValue: computeAssemblyAnnotationValue(representativeAnalysis.assembly, representativeAnalysis.genome_annotation),
                        files: assemblyFiles,
                        analysisObjects: analysesByTitle[title],
                    });
                }

                // Don't add compiled analysis objects with no files.
                return analyses;
            }, []);
        }
    }
    return compiledAnalyses;
};


/**
 * [].sort() callback to compare two compiled-analysis version numbers of the form
 * "major.minor.patch" with optional "minor" and "patch."
 * @param {object} aAnalysis First compiled analysis object to compare
 * @param {object} bAnalysis Second compiled analysis object to compare
 *
 * @return {number} [].sort() result to determine ordering
 */
const compareAnalysisVersions = (aAnalysis, bAnalysis) => {
    /**
     * Break a string version number into a corresponding vector of numbers. Examples:
     * "0.3.75" => [0, 3, 75]
     * "10.81" => [10, 81]
     * "2.0.0" => [2, 0, 0]
     * @param {string} version Version number in the form "major.minor.patch".
     *
     * @return {array} Version number converted to numeric vector
     */
    const deconstructVersion = (version) => (
        version.match(/(\d+)(\.(\d+))*?(\.(\d+))*?/g).map((versionElement) => +versionElement)
    );

    // If either or both analyses have no version number, sort the empty version number after a
    // non-empty one.
    if (aAnalysis.version === '' || bAnalysis.version === '') {
        if (aAnalysis.version !== bAnalysis.version) {
            return aAnalysis.version === '' ? 1 : -1;
        }

        // Both empty version numbers.
        return 0;
    }

    // Deconstruct the version numbers so we can compare numerically. This avoids having "10" sort
    // before "2."
    const aDeconstructed = deconstructVersion(aAnalysis.version);
    const bDeconstructed = deconstructVersion(bAnalysis.version);

    // Compare each deconstructed element of the version numbers. Use "-1" for non-existent minor
    // and patch version elements so they sort before "0."
    return (
        (bDeconstructed[0] - aDeconstructed[0])
            || ((bDeconstructed[1] ?? -1) - (aDeconstructed[1] ?? -1))
            || ((bDeconstructed[2] ?? -1) - (aDeconstructed[2] ?? -1))
    );
};


/**
 * Sort an array of compiled-analysis objects by version number, returning a sorted copy of the
 * given array. The compiled-analysis objects within do not get cloned.
 * @param {array} Compiled-analysis objects to sort.
 *
 * @return {array} Sorted copy of `compiledAnalyses`.
 */
const sortDatasetAnalysesByVersion = (compiledAnalyses) => {
    const compiledAnalysesCopy = [...compiledAnalyses];
    return compiledAnalysesCopy.sort(compareAnalysisVersions);
};


/**
 * Sorts the given compiled analysis objects by multiple criteria, with version number least
 * significant, and status most significant.
 * @param {array} compiledAnalyses Array of compiled analyses to sort
 *
 * @return {array} New copy of `compiledAnalyses` but sorted
 */
export const sortDatasetAnalyses = (compiledAnalyses) => {
    const compiledAnalysisByVersion = sortDatasetAnalysesByVersion(compiledAnalyses);
    return _.chain(compiledAnalysisByVersion)
        .sortBy((analysis) => labSortOrder.findIndex((lab) => lab === analysis.lab))
        .sortBy((analysis) => -analysis.assemblyAnnotationValue)
        .sortBy((analysis) => (analysis.status === 'released' ? 0 : 1))
        .value();
};


/**
 * Compile the analyses_objects for all the given datasets and combine them into an array of
 * compiled analyses applying to all the given datasets. No duplicate analyses get generated, and
 * any duplicates found get their files combined into one compiled analysis object.
 * @param {array} datasets All datasets whose analysis_objects need extracting
 *
 * @return {array} Compiled analyses applying to all datasets and combining their files
 */
export const compileDatasetAnalyses = (datasets) => {
    // Collect all compiled analyses from all datasets. `compiledAnalyses` can contain multiple
    // compiled analyses with the same titles but different file arrays.
    const compiledAnalyses = datasets.reduce((acc, dataset) => {
        const datasetCompiledAnalyses = compileAnalysesByTitle(dataset, dataset.files);
        return datasetCompiledAnalyses.length > 0 ? acc.concat(datasetCompiledAnalyses) : acc;
    }, []);

    // Combine all compiled analysis objects that share a title, and concatenate their files
    // together.
    const groupedAnalyses = _(compiledAnalyses).groupBy((compiledAnalysis) => compiledAnalysis.title);
    const combinedAnalyses = [];
    Object.keys(groupedAnalyses).forEach((analysisTitle, index) => {
        // Use the first of the grouped compiled analyses for the final compiled analysis, as all
        // compiled analyses under each group all share the same contents except for their `files`
        // array.
        combinedAnalyses[index] = groupedAnalyses[analysisTitle][0];

        // Combine all group files and analysis objects under one compiled analysis together and
        // put into the final compiled analysis object for the title.
        combinedAnalyses[index].files = groupedAnalyses[analysisTitle].reduce((acc, compiledAnalysis) => (
            acc.concat(compiledAnalysis.files)
        ), []);
        combinedAnalyses[index].analysisObjects = groupedAnalyses[analysisTitle].reduce((acc, compiledAnalysis) => (
            acc.concat(compiledAnalysis.analysisObjects)
        ), []);
    });
    return compiledAnalyses;
};
