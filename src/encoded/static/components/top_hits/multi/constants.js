import TopHitsQuery, {
    CollectionsQuery,
} from '../query';
import TopHitsResults from '../results';
import CollectionsResults from './results';


/**
* Used for specifying query objects and result components for multisearch.
* Format:
* [
*      {string} name - key used to store results in React state,
*      {object} query - query object that has getResults method,
*      {element} results - React component that knows how to render results returned by query,
*      {string} title - Title used to display group of results,
* ]
*/
const QUERIES = [
    ['dataCollections', CollectionsQuery, CollectionsResults, 'Data collections'],
    ['topHits', TopHitsQuery, TopHitsResults, 'Top results by type'],
];


export default QUERIES;
