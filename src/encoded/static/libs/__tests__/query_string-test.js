import QueryString from '../../libs/query_string';


describe('QueryString Class', () => {
    it('Returns given query string unmodified', () => {
        let query = new QueryString('type=Experiment&assay_term_id=OBI:0000716&type=ReferenceEpigenome&assay_title=Histone+ChIP-seq');
        expect(query.format()).toEqual('type=Experiment&assay_term_id=OBI:0000716&type=ReferenceEpigenome&assay_title=Histone+ChIP-seq');
        query = new QueryString('type=Experiment&assay_term_id=OBI:0000716&type!=ReferenceEpigenome&assay_title=Histone+ChIP-seq');
        expect(query.format()).toEqual('type=Experiment&assay_term_id=OBI:0000716&type!=ReferenceEpigenome&assay_title=Histone+ChIP-seq');
    });

    it('Finds all values matching a key', () => {
        const query = new QueryString('type=Experiment&assay_term_id=OBI:0000716&type=ReferenceEpigenome&assay_title!=Histone+ChIP-seq');
        let matchingValues = query.getKeyValues('type');
        expect(matchingValues).toHaveLength(2);
        expect(matchingValues[0]).toEqual('Experiment');
        expect(matchingValues[1]).toEqual('ReferenceEpigenome');

        matchingValues = query.getKeyValues('assay_title', true);
        expect(matchingValues).toHaveLength(1);
        expect(matchingValues[0]).toEqual('Histone ChIP-seq');
    });

    it('Adds a key/value pair', () => {
        const query = new QueryString('type=Experiment');
        query.addKeyValue('assay_term_id', 'OBI:0000716');
        expect(query.format()).toEqual('type=Experiment&assay_term_id=OBI:0000716');
        query.addKeyValue('type', 'Annotation', true);
        expect(query.format()).toEqual('type=Experiment&assay_term_id=OBI:0000716&type!=Annotation');
    });

    it('Deletes all keys of a value', () => {
        let query = new QueryString('type=Experiment&assay_term_id=OBI:0000716&type=Annotation');
        query.deleteKeyValue('type');
        expect(query.format()).toEqual('assay_term_id=OBI:0000716');

        query = new QueryString('type=Experiment&assay_term_id=OBI:0000716&type=Annotation');
        query.deleteKeyValue('type', 'Experiment');
        expect(query.format()).toEqual('assay_term_id=OBI:0000716&type=Annotation');

        query = new QueryString('type=Experiment&assay_term_id=OBI:0000716&type!=Annotation');
        query.deleteKeyValue('type');
        expect(query.format()).toEqual('assay_term_id=OBI:0000716');

        query = new QueryString('type=Experiment&assay_term_id=OBI:0000716&type!=Annotation');
        query.deleteKeyValue('type', 'Annotation');
        expect(query.format()).toEqual('type=Experiment&assay_term_id=OBI:0000716');
    });

    it('Replaces all keys with a new value', () => {
        let query = new QueryString('type=Experiment&assay_term_id=OBI:0000716&type=Annotation');
        query.replaceKeyValue('type', 'Biosample');
        expect(query.format()).toEqual('assay_term_id=OBI:0000716&type=Biosample');

        query = new QueryString('type=Experiment&assay_term_id=OBI:0000716&type=Annotation');
        query.replaceKeyValue('assay_term_id', 'OBI:0001919');
        expect(query.format()).toEqual('type=Experiment&type=Annotation&assay_term_id=OBI:0001919');

        query = new QueryString('type=Experiment&assay_term_id=OBI:0000716&type!=Annotation');
        query.replaceKeyValue('type', 'Biosample');
        expect(query.format()).toEqual('assay_term_id=OBI:0000716&type=Biosample');

        query = new QueryString('type=Experiment&assay_term_id=OBI:0000716&type!=Annotation');
        query.replaceKeyValue('type', 'Biosample', true);
        expect(query.format()).toEqual('assay_term_id=OBI:0000716&type!=Biosample');
    });

    it('Creates an independent clone', () => {
        const query = new QueryString('type=Experiment&assay_term_id=OBI:0000716&type!=Annotation');
        const queryCopy = query.clone();
        queryCopy.addKeyValue('assay_title', 'Histone ChIP-seq', true);
        expect(query.format()).toEqual('type=Experiment&assay_term_id=OBI:0000716&type!=Annotation');
        expect(queryCopy.format()).toEqual('type=Experiment&assay_term_id=OBI:0000716&type!=Annotation&assay_title!=Histone+ChIP-seq');
    });

    it('Counts the number of query keys', () => {
        const query = new QueryString('type=Experiment&assay_term_id=OBI:0000716&type!=Annotation');
        const allKeysCount = query.queryCount();
        expect(allKeysCount).toEqual(3);
        const typeKeyCount = query.queryCount('type');
        expect(typeKeyCount).toEqual(2);
        const otherKeyCount = query.queryCount('other');
        expect(otherKeyCount).toEqual(0);
    });
});
