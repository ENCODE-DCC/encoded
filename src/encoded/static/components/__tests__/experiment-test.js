import React from 'react';
import { mount } from 'enzyme';
import configureStore from 'redux-mock-store';
import { Provider } from 'react-redux';
import _ from 'underscore';

// Import test component and data.
import Experiment from '../experiment';
import context from '../testdata/experiment';

// Create the Redux mock store.
const initialCart = { cart: [], name: 'Untitled' };
const mockStore = configureStore();


describe('Experiment Page', () => {
    describe('Minimal Experiment', () => {
        let experiment;
        let summary;

        beforeAll(() => {
            const contextMin = _.clone(context);
            contextMin.references = [require('../testdata/publication/PMID16395128'), require('../testdata/publication/PMID23000965')];
            const store = mockStore(initialCart);
            experiment = mount(
                <Provider store={store}><Experiment context={context} /></Provider>
            );

            summary = experiment.find('.data-display');
        });

        test('has proper links in dbxrefs key-value', () => {
            const item = summary.at(0).find('[data-test="external-resources"]');
            const desc = item.find('dd');
            const dbxrefs = desc.at(0).find('a');
            expect(dbxrefs).toHaveLength(2);
            expect(dbxrefs.at(0).prop('href')).toEqual('http://genome.ucsc.edu/cgi-bin/hgTracks?tsCurTab=advancedTab&tsGroup=Any&tsType=Any&hgt_mdbVar1=dccAccession&hgt_tSearch=search&hgt_tsDelRow=&hgt_tsAddRow=&hgt_tsPage=&tsSimple=&tsName=&tsDescr=&db=hg19&hgt_mdbVal1=wgEncodeEH003317');
            expect(dbxrefs.at(1).prop('href')).toEqual('https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSM1010811');
        });

        test('has proper release date', () => {
            const item = summary.at(0).find('[data-test="date-released"]');
            const desc = item.find('dd');
            expect(desc.at(0).text()).toEqual('October 29, 2011');
        });
    });

    describe('Replicate Panels', () => {
        let experiment;
        let summary;

        beforeAll(() => {
            const contextRep = _.clone(context);
            contextRep.replicates = [require('../testdata/replicate/human'), require('../testdata/replicate/mouse')];
            contextRep.replicates[0].library = require('../testdata/library/sid38806');
            contextRep.replicates[1].library = require('../testdata/library/sid38807');
            contextRep.files = [require('../testdata/file/fastq')[0]];
            const store = mockStore(initialCart);
            experiment = mount(
                <Provider store={store}><Experiment context={contextRep} /></Provider>
            );
            summary = experiment.find('.data-display');
        });

        test('has proper treatment', () => {
            const item = summary.find('[data-test="treatments"]');
            const desc = item.find('dd');
            expect(desc.text()).toEqual('97.2 nM doxycycline hyclate (CHEBI:34730) for 6 hour [1-1]');
        });

        test('has proper strand specificity', () => {
            const item = summary.find('[data-test="strandspecificity"]');
            const desc = item.find('dd');
            expect(desc.text()).toEqual('Strand-specific');
        });

        test('has proper spikeins', () => {
            const item = summary.find('[data-test="spikeins"]');
            const desc = item.find('dd');
            expect(desc.text()).toEqual('ENCSR000AJW [1-1]');
        });
    });

    describe('Alternate accession display', () => {
        let experiment;
        let alt;

        beforeAll(() => {
            const contextAlt = _.clone(context);
            contextAlt.alternate_accessions = ['ENCSR000ACT', 'ENCSR999NOF'];
            const store = mockStore(initialCart);
            experiment = mount(
                <Provider store={store}><Experiment context={contextAlt} store={store} /></Provider>
            );
            alt = experiment.find('.repl-acc');
        });

        test('displays two alternate accessions', () => {
            expect(alt.text()).toEqual('Alternate accessions: ENCSR000ACT, ENCSR999NOF');
        });
    });
});
