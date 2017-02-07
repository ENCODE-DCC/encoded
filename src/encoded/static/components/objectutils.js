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


// Do a search of the specific objects whose @ids are listed in the `atIds` parameter. Because we
// have to specify the @id of each object in the URL of the GET request, the URL can get quite
// long, so if the number of `atIds` @ids goes beyond the `chunkSize` constant, we break thev
// searches into chunks, and the maximum number of @ids in each chunk is `chunkSize`. We
// then send out all the search GET requests at once, combine them into one array of
// files returned as a promise.
//
// You can also supply an array of objects in the filteringObjects parameter. Any file @ids in
// `atIds` that matches an object['@id'] in `filteringObjects` doesn't get included in the GET
// request.
//
// Note: this function calls `fetch`, so you can't call this function from code that runs on the
// server or it'll complain that `fetch` isn't defined. If called from a React component, make sure
// you only call it when you know the component is mounted, like from the componentDidMount method.
//
// atIds: array of file @ids.
// uri: Base URI specifying the type and statuses of the objects we want to get. The list of object
//      @ids gets added to this URI.
// filteringObjects: Array of files to filter out of the array of file @ids in the fileIds parameter.
export function requestObjects(atIds, uri, filteringObjects) {
    const chunkSize = 100; // Maximum # of files to search for at once
    const filteringFileIds = {}; // @ids of files we've searched for and don't need retrieval
    let filteredObjectIds = {}; // @ids of files we need to retrieve

    // Make a searchable object of file IDs for files to filter out of our list.
    if (filteringObjects && filteringObjects.length) {
        filteringObjects.forEach((filteringObject) => {
            filteringFileIds[filteringObject['@id']] = filteringObject;
        });

        // Filter the given file @ids to exclude those files we already have in data.@graph,
        // just so we don't use bandwidth getting things we already have.
        filteredObjectIds = atIds.filter(atId => !filteringFileIds[atId]);
    } else {
        // The caller didn't supply an array of files to filter out, so filtered files are just
        // all of them.
        filteredObjectIds = atIds;
    }

    // Break fileIds into an array of arrays of <= `chunkSize` @ids so we don't generate search
    // URLs that are too long for the server to handle.
    const objectChunks = [];
    for (let start = 0, chunkIndex = 0; start < filteredObjectIds.length; start += chunkSize, chunkIndex += 1) {
        objectChunks[chunkIndex] = filteredObjectIds.slice(start, start + chunkSize);
    }

    // Going to send out all search chunk GET requests at once, and then wait for all of them to
    // complete.
    return Promise.all(objectChunks.map((objectChunk) => {
        // Build URL containing file search for specific files for each chunk of files.
        const url = uri.concat(objectChunk.reduce((combined, current) => `${combined}&@id=${current}`, ''));
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
            return chunks.reduce((objects, chunk) => (chunk && chunk['@graph'].length ? objects.concat(chunk['@graph']) : objects), []);
        }

        // Didn't get any good chucks back, so just return no results.
        return [];
    });
}


// Do a search of the specific files whose @ids are listed in the `fileIds` parameter.
//
// You can also supply an array of objects in the filteringFiles parameter. Any file @ids in
// `atIds` that matches an object['@id'] in `filteringFiles` doesn't get included in the GET
// request.
//
// Note: this function calls requestObjects which calls `fetch`, so you can't call this function
// from code that runs on the server or it'll complain that `fetch` isn't defined. If called from a
// React component, make sure you only call it when you know the component is mounted, like from
// the componentDidMount method.
//
// fileIds: array of file @ids.
// filteringFiles: Array of files to filter out of the array of file @ids in the fileIds parameter.
export function requestFiles(fileIds, filteringFiles) {
    return requestObjects(fileIds, '/search/?type=File&limit=all&status!=deleted&status!=revoked&status!=replaced', filteringFiles);
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
