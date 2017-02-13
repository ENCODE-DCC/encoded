import React from 'react';


// Display a summary sentence for a single treatment.
export function singleTreatment(treatment) {
    let treatmentText = '';

    if (treatment.amount) {
        treatmentText += `${treatment.amount}${treatment.amount_units ? ` ${treatment.amount_units}` : ''} `;
    }
    treatmentText += `${treatment.treatment_term_name}${treatment.treatment_term_id ? ` (${treatment.treatment_term_id})` : ''} `;
    if (treatment.duration) {
        treatmentText += `for ${treatment.duration} ${treatment.duration_units ? treatment.duration_units : ''}`;
    }
    return treatmentText;
}


// Display a treatment definition list.
export function treatmentDisplay(treatment) {
    const treatmentText = singleTreatment(treatment);
    return (
        <dl key={treatment.uuid} className="key-value">
            <div data-test="treatment">
                <dt>Treatment</dt>
                <dd>{treatmentText}</dd>
            </div>

            <div data-test="type">
                <dt>Type</dt>
                <dd>{treatment.treatment_type}</dd>
            </div>
        </dl>
    );
}


// Do a search of the specific files whose @ids are listed in the `fileIds` parameter. Because we
// have to specify the @id of each file in the URL of the GET request, the URL can get quite long,
// so if the number of `fileIds` @ids goes beyond the `chunkSize` constant, we break the
// searches into chunks, and the maximum number of @ids in each chunk is `chunkSize`. We
// then send out all the search GET requests at once, combine them into one array of
// files returned as a promise.
//
// You can also supply an array of file objects in the filteringFiles parameter. Any file @ids in
// `fileIds` that matches a file['@id'] in `filteringFiles` doesn't get included in the GET
// request.
//
// Note: this function calls `fetch`, so you can't call this function from code that runs on the
// server or it'll complain that `fetch` isn't defined. If called from a React component, make sure
// you only call it when you know the component is mounted, like from the componentDidMount method.
//
// fileIds: array of file @ids.
// filteringFiles: Array of files to filter out of the array of file @ids in the fileIds parameter.
export function requestFiles(fileIds, filteringFiles) {
    const chunkSize = 100; // Maximum # of files to search for at once
    const filteringFileIds = {}; // @ids of files we've searched for and don't need retrieval
    let filteredFileIds = {}; // @ids of files we need to retrieve

    // Make a searchable object of file IDs for files to filter out of our list.
    if (filteringFiles && filteringFiles.length) {
        filteringFiles.forEach((filteringFile) => {
            filteringFileIds[filteringFile['@id']] = filteringFile;
        });

        // Filter the given file @ids to exclude those files we already have in data.@graph,
        // just so we don't use bandwidth getting things we already have.
        filteredFileIds = fileIds.filter(fileId => !filteringFileIds[fileId]);
    } else {
        // The caller didn't supply an array of files to filter out, so filtered files are just
        // all of them.
        filteredFileIds = fileIds;
    }

    // Break fileIds into an array of arrays of <= `chunkSize` @ids so we don't generate search
    // URLs that are too long for the server to handle.
    const fileChunks = [];
    for (let start = 0, chunkIndex = 0; start < filteredFileIds.length; start += chunkSize, chunkIndex += 1) {
        fileChunks[chunkIndex] = filteredFileIds.slice(start, start + chunkSize);
    }

    // Going to send out all search chunk GET requests at once, and then wait for all of them to
    // complete.
    return Promise.all(fileChunks.map((fileChunk) => {
        // Build URL containing file search for specific files for each chunk of files.
        const url = '/search/?type=File&limit=all&status!=deleted&status!=revoked&status!=replaced'.concat(fileChunk.reduce((combined, current) => `${combined}&@id=${current}`, ''));
        return fetch(url, {
            method: 'GET',
            headers: {
                Accept: 'application/json',
            },
        }).then((response) => {
            // Convert each response response to JSON
            if (response.ok) {
                return response.json();
            }
            return Promise.resolve(null);
        });
    })).then((chunks) => {
        // All search chunks have resolved or errored. We get an array of search results in
        // `chunks` -- one per chunk. Now collect their files from their @graphs into one array of
        // files and return them as the promise result.
        if (chunks && chunks.length) {
            return chunks.reduce((files, chunk) => (chunk && chunk['@graph'].length ? files.concat(chunk['@graph']) : files), []);
        }

        // Didn't get any good chucks back, so just return no results.
        return [];
    });
}


// Given a dataset (for now, only ReferenceEpigenome), return the donor diversity of that dataset.
export function donorDiversity(dataset) {
    let diversity = 'none';

    if (dataset.related_datasets && dataset.related_datasets.length) {
        // Get all non-deleted related experiments; empty array if none.
        const experiments = dataset.related_datasets.filter(experiment => experiment.status !== 'deleted');

        // From list list of non-deleted experiments, get all non-deleted replicates into one
        // array.
        if (experiments.length) {
            // Make an array of replicate arrays, one replicate array per experiment. Only include
            // non-deleted replicates.
            const replicatesByExperiment = experiments.map(experiment => (
                (experiment.replicates && experiment.replicates.length) ?
                    experiment.replicates.filter(replicate => replicate.status !== 'deleted')
                : []),
            );

            // Merge all replicate arrays into one non-deleted replicate array.
            const replicates = replicatesByExperiment.reduce((replicateCollection, replicatesForExperiment) => replicateCollection.concat(replicatesForExperiment), []);

            // Look at the donors in each replicate's biosample. If we see at least two different
            // donors, we know we have a composite. If only one unique donor after examining all
            // donors, we have a single. "None" if no donors found in all replicates.
            if (replicates.length) {
                const donorAtIdCollection = [];
                replicates.every((replicate) => {
                    if (replicate.library && replicate.library.status !== 'deleted' &&
                            replicate.library.biosample && replicate.library.biosample.status !== 'deleted' &&
                            replicate.library.biosample.donor && replicate.library.biosample.donor.status !== 'deleted') {
                        const donorAccession = replicate.library.biosample.donor.accession;

                        // If we haven't yet seen this donor @id, add it to our collection
                        if (donorAtIdCollection.indexOf(donorAccession) === -1) {
                            donorAtIdCollection.push(donorAccession);
                        }

                        // If we have two, we know have a composite, and we can exit the loop by
                        // returning false, which makes the replicates.every function end.
                        return donorAtIdCollection.length !== 2;
                    }

                    // No donor to examine in this replicate. Keep the `every` loop going.
                    return true;
                });

                // Now determine the donor diversity.
                if (donorAtIdCollection.length > 1) {
                    diversity = 'composite';
                } else if (donorAtIdCollection.length === 1) {
                    diversity = 'single';
                } // Else keep its original value of 'none'.
            }
        }
    }
    return diversity;
}


// Return `true` if the given dataset is viewable by people not logged in, or people logged in
// but not as admin.
export function publicDataset(dataset) {
    return dataset.status === 'released' || dataset.status === 'archived' || dataset.status === 'revoked';
}
