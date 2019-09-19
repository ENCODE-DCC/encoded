import Hit from './base';


class ExperimentHit extends Hit {
    /**
    * Overrides parent definition.
    * @return {array} [[field, value], ...] array from item.
    */
    getValues() {
        return [
            ['name', this.formatName()],
            ['title', this.formatTitle()],
            ['target', this.formatTarget()],
            ['details', this.formatDetails()],
            ['description', this.formatDescriptionWithOrganism()],
        ];
    }
}


export default ExperimentHit;
