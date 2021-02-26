import Hit, {
    maybeConvertArrayToString,
    uniqueAndDefinedValues,
} from './base';
import {
    WHITESPACE,
} from '../constants';


class DonorHit extends Hit {
    /**
    * @return {string|undefined} Formatted string with donor strain and genotype.
    */
    makeDonorDescription() {
        return maybeConvertArrayToString(
            uniqueAndDefinedValues(
                [
                    this.item.strain_name,
                    this.item.genotype,
                ]
            ),
            WHITESPACE
        );
    }

    /**
    * Overrides parent definition.
    * @return {string|undefined} Donor-specific description pulled from item.
    */
    formatDescription() {
        return this.makeDonorDescription();
    }

    /**
    * Overrides parent definition.
    * @return {array} [[field, value], ...] array from item.
    */
    getValues() {
        return [
            ['name', this.formatName()],
            ['description', this.formatDescriptionWithOrganism()],
        ];
    }
}


export default DonorHit;
