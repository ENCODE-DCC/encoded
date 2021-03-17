import Hit from './base';


class FileHit extends Hit {
    /**
    * @return {string} Formatted string with file type and output type.
    */
    makeFileDescription() {
        return `${this.item.file_type} ${this.item.output_type}`;
    }

    /**
    * Overrides parent definition.
    * @return {string|undefined} File-specific description pulled from item.
    */
    formatDescription() {
        return (
            this.item.output_type &&
            this.item.file_type &&
            this.makeFileDescription()
        );
    }

    /**
    * Overrides parent definition.
    * @return {array} [[field, value], ...] array from item.
    */
    getValues() {
        return [
            ['name', this.formatName()],
            ['annotationType', this.formatAnnotationType()],
            ['title', this.formatTitle()],
            ['biosample', this.formatBiosample()],
            ['target', this.formatTarget()],
            ['details', this.formatDetails()],
            ['organism', this.formatOrganism()],
            ['description', this.formatDescription()],
        ];
    }
}

export default FileHit;
