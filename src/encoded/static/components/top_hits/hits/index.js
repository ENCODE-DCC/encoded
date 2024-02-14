import BiosampleHit from './biosample';
import DonorHit from './donor';
import ExperimentHit from './experiment';
import FileHit from './file';
import Hit from './base';
import {
    BIOSAMPLE,
    DONOR,
    EXPERIMENT,
    FILE,
} from '../constants';


/**
* Dynamic creation of Hit based on @type of item. This allows
* encapsulation of item-specific formatting in a Hit subtype.
* If no subtype matches then the default Hit class is returned.
* @return {Hit} Item-specific Hit class that knows how to format that type.
*/
const hitFactory = (item) => {
    const itemTypes = item['@type'];
    if (itemTypes.includes(EXPERIMENT)) {
        return new ExperimentHit(item);
    }
    if (itemTypes.includes(FILE)) {
        return new FileHit(item);
    }
    if (itemTypes.includes(BIOSAMPLE)) {
        return new BiosampleHit(item);
    }
    if (itemTypes.includes(DONOR)) {
        return new DonorHit(item);
    }
    return new Hit(item);
};


export default hitFactory;
