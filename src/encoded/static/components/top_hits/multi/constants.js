import TopHitsQuery, {
    CollectionsQuery,
} from '../query';
import TopHitsResults from '../results';
import CollectionsResults from './results';


const QUERIES = [
    ['dataCollections', CollectionsQuery, CollectionsResults, 'Data collections'],
    ['topHits', TopHitsQuery, TopHitsResults, 'Top results by type'],
];


export default QUERIES;
