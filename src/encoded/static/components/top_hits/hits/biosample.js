import Hit from './base';


class BiosampleHit extends Hit {
    /**
    * Overrides parent definition.
    * @return {array} [[field, value], ...] array from item.
    */
    getValues() {
        return [
            ['name', this.formatName()],
            ['description', this.formatDescription()],
        ];
    }
}


export default BiosampleHit;
