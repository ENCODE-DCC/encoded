import QueryString from '../../libs/query_string';


describe('QueryString Class', () => {
    it('Returns given query string unmodified', () => {
        const query = new QueryString('type=Experiment&assay_term_id=OBI:0000716&type=ReferenceEpigenome&assay_title=Histone+ChIP-seq');
        expect(query.format()).toEqual('type=Experiment&assay_term_id=OBI:0000716&type=ReferenceEpigenome&assay_title=Histone+ChIP-seq');
    });

    it('Finds all values matching a key', () => {
        const query = new QueryString('type=Experiment&assay_term_id=OBI:0000716&type=ReferenceEpigenome&assay_title=Histone+ChIP-seq');
        const matchingValues = query.getKeyValues('type');
        expect(matchingValues).toHaveLength(2);
        expect(matchingValues[0]).toEqual('Experiment');
        expect(matchingValues[1]).toEqual('ReferenceEpigenome');
    });

    it('Finds all key/value pairs not matching a key', () => {
        const query = new QueryString('type=Experiment&assay_term_id=OBI:0000716&type=ReferenceEpigenome&assay_title=Histone+ChIP-seq');
        let matchingElements = query.getNotKeyElements('type');
        expect(typeof matchingElements).toEqual('object');
        expect(Object.keys(matchingElements)).toHaveLength(2);
        expect(matchingElements.assay_term_id).toEqual('OBI:0000716');
        expect(matchingElements.assay_title).toEqual('Histone ChIP-seq');

        matchingElements = query.getNotKeyElements('assay_term_id');
        expect(typeof matchingElements).toEqual('object');
        expect(Object.keys(matchingElements)).toHaveLength(2);
        expect(matchingElements.assay_title).toEqual('Histone ChIP-seq');
        expect(typeof matchingElements.type).toEqual('object');
        expect(Array.isArray(matchingElements.type)).toBeTruthy();
        expect(matchingElements.type[0]).toEqual('Experiment');
        expect(matchingElements.type[1]).toEqual('ReferenceEpigenome');
    });

    it('Adds a key/value pair', () => {
        const query = new QueryString('type=Experiment');
        query.addKeyValue('assay_term_id', 'OBI:0000716');
        expect(query.format()).toEqual('type=Experiment&assay_term_id=OBI:0000716');
    });

    it('Deletes all keys of a value', () => {
        let query = new QueryString('type=Experiment&assay_term_id=OBI:0000716&type=Annotation');
        query.deleteKeyValue('type');
        expect(query.format()).toEqual('assay_term_id=OBI:0000716');

        query = new QueryString('type=Experiment&assay_term_id=OBI:0000716&type=Annotation');
        query.deleteKeyValue('type', 'Experiment');
        expect(query.format()).toEqual('assay_term_id=OBI:0000716&type=Annotation');
    });

    it('Replaces all keys with a new value', () => {
        let query = new QueryString('type=Experiment&assay_term_id=OBI:0000716&type=Annotation');
        query.replaceKeyValue('type', 'Biosample');
        expect(query.format()).toEqual('assay_term_id=OBI:0000716&type=Biosample');

        query = new QueryString('type=Experiment&assay_term_id=OBI:0000716&type=Annotation');
        query.replaceKeyValue('assay_term_id', 'OBI:0001919');
        expect(query.format()).toEqual('type=Experiment&type=Annotation&assay_term_id=OBI:0001919');
    });
});
