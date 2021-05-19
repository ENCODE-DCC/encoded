import {
    Query as TopHitsQuery,
    CollectionsQuery,
} from '../query';
import TopHitsResults from '../results';
import CollectionsResults from './results';


export const queries = [
    ['dataCollections', CollectionsQuery, CollectionsResults, 'Data collections'],
    ['topHits', TopHitsQuery, TopHitsResults, 'Top results by type'],
];
