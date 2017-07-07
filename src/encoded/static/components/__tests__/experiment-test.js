import React from 'react';
import { mount } from 'enzyme';
import _ from 'underscore';
import url from 'url';

// Import test component and data.
import Experiment from '../experiment';
import context from '../testdata/experiment';


describe('Experiment Page', () => {
    describe('Minimal Experiment', () => {
        let experiment;
        let summary;

        beforeAll(() => {
            const contextMin = _.clone(context);
            contextMin.references = [require('../testdata/publication/PMID16395128'), require('../testdata/publication/PMID23000965')];
            experiment = mount(
                <Experiment context={context} />
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
            expect(desc.at(0).text()).toEqual('2011-10-29');
        });

        test('has one experiment status element in header', () => {
            const statusList = experiment.find('.status-list');
            expect(statusList.children().exists()).toBeTruthy();
            expect(statusList.children()).toHaveLength(1);
        });
    });

    describe('Document Panel', () => {
        let experiment;
        let doc;

        beforeAll(() => {
            const contextDoc = _.clone(context);
            contextDoc.documents = [require('../testdata/document/myerschipseq')];
            experiment = mount(
                <Experiment context={contextDoc} />
            );
            doc = experiment.find('.type-Document');
        });

        test('has one document panel with a PDF image anchor', () => {
            const figures = doc.find('figure');
            expect(figures).toHaveLength(1);
            const anchors = figures.find('.file-pdf');
            expect(anchors).toHaveLength(1);
        });

        test('has a single proper download link', () => {
            const dlBar = doc.find('.document__file');
            expect(dlBar).toHaveLength(1);
            const anchors = dlBar.find('a');
            expect(anchors).toHaveLength(1);
            expect(url.parse(anchors.at(0).prop('href')).pathname).toEqual('/documents/df9dd0ec-c1cf-4391-a745-a933ab1af7a7/@@download/attachment/Myers_Lab_ChIP-seq_Protocol_v042211.pdf');
        });

        test('has two key-value pairs, and proper DL link', () => {
            const trigger = doc.find('.document__file-detail-switch');
            trigger.at(0).simulate('click');

            const docKeyValue = doc.find('.key-value-doc');
            expect(docKeyValue).toHaveLength(1);
            const defTerms = docKeyValue.at(0).find('dt');
            expect(defTerms).toHaveLength(3);
            const defDescs = docKeyValue.at(0).find('dd');
            expect(defDescs).toHaveLength(3);
        });
    });

    describe('Document Panel References', () => {
        let experiment;
        let doc;

        beforeAll(() => {
            const contextDoc = _.clone(context);
            contextDoc.documents = [require('../testdata/document/wgEncodeSydhHist-refs')];
            experiment = mount(
                <Experiment context={contextDoc} />
            );
            doc = experiment.find('.type-Document');
        });

        test('has five key-value pairs, and two good references links', () => {
            const docKeyValue = doc.find('.key-value-doc');
            expect(docKeyValue).toHaveLength(1);
            const defTerms = docKeyValue.at(0).find('dt');
            expect(defTerms).toHaveLength(3);
            const defDescs = docKeyValue.at(0).find('dd');
            expect(defDescs).toHaveLength(3);
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
            contextRep.files = [require('../testdata/file/fastq')];
            experiment = mount(
                <Experiment context={contextRep} />
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
            experiment = mount(
                <Experiment context={contextAlt} />
            );
            alt = experiment.find('.repl-acc');
        });

        test('displays two alternate accessions', () => {
            expect(alt.text()).toEqual('Replaces ENCSR000ACT, ENCSR999NOF');
        });
    });
});
