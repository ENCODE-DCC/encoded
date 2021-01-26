/**
* Encapsulates all the formatting for a raw top hit result.
*/


class Hit {
    constructor(item) {
        this.item = item;
    }

    formatName() {
        return this.item.accession || this.item['@id'];
    }

    formatDescription() {
        return (
            this.item.description ||
            this.item.summary ||
            this.item.biosample_summary ||
            this.item.assay_term_name ||
            this.item.title
        );
    }

    formatDetails() {
        return (
            this.item.file_type ||
            this.item.antingen_description
        );
    }

    asString() {
        return [
            this.formatDescription(),
            this.formatDetails(),
            this.formatName(),
            this.item.status,
        ].filter(Boolean).join(' - ');
    }
}


export default Hit;
