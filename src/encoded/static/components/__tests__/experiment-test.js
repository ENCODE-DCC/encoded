/** @jsx React.DOM */
'use strict';

// Modules needed for all tests
jest.dontMock('react');
jest.dontMock('underscore');
jest.dontMock('url');
jest.dontMock('../../libs/registry.js');
jest.dontMock('../../libs/origin.js');

// Modules experiments depend on
jest.dontMock('../experiment.js');
jest.dontMock('../globals.js');
jest.dontMock('../dbxref.js');
jest.dontMock('../dataset.js');
jest.dontMock('../antibody.js');
jest.dontMock('../biosample.js');
jest.dontMock('../image.js');
jest.dontMock('../fetched.js');
jest.dontMock('../mixins.js');

// Experiment test data
jest.dontMock('../testdata/experiment.js');
jest.dontMock('../testdata/file.js');
jest.dontMock('../testdata/document.js');
jest.dontMock('../testdata/replicate.js');
jest.dontMock('../testdata/platform.js');
jest.dontMock('../testdata/library.js');
jest.dontMock('../testdata/biosample.js');
jest.dontMock('../testdata/human_donor.js');
jest.dontMock('../testdata/mouse_donor.js');
jest.dontMock('../testdata/organism.js');
jest.dontMock('../testdata/source.js');
jest.dontMock('../testdata/award.js');


describe('Experiment Page', function() {
    var TestUtils, Experiment;
    var experiment, context, library, biosamples, human_donor, mouse_donor, source, organisms;

    beforeEach(function() {
        var React = require('react');
        TestUtils = require('react/lib/ReactTestUtils');
        require('../biosample.js');

        // Load up a single experiment with test data
        Experiment = require('../experiment.js').Experiment;
        context = require('../testdata/experiment.js');
        context.files = require('../testdata/file.js');
        context.documents = require('../testdata/document.js');
        context.replicates = require('../testdata/replicate.js');
        context.replicates[0].platform = context.replicates[1].platform = require('../testdata/platform.js');
        context.award = require('../testdata/award.js')[0];
        library = require('../testdata/library.js');
        biosamples = require('../testdata/biosample.js');
        human_donor = require('../testdata/human_donor.js')[0];
        mouse_donor = require('../testdata/mouse_donor.js')[0];
        source = require('../testdata/source.js')[0];
        organisms = require('../testdata/organism.js');
        human_donor.organism = organisms[0];
        mouse_donor.organism = organisms[1];
        biosamples[0].donor = human_donor;
        biosamples[1].donor = mouse_donor;
        biosamples[0].source = biosamples[1].source = source;
        biosamples[0].organism = human_donor.organism;
        biosamples[1].organism = mouse_donor.organism;
        library[0].biosample = biosamples[0];
        library[1].biosample = biosamples[1];
        context.replicates[0].library = library[0];
        context.replicates[1].library = library[1];

        experiment = <Experiment context={context} />;
        TestUtils.renderIntoDocument(experiment);
    });

    describe('Header and Summary', function() {
        var summary, defTerms, defDescs;

        beforeEach(function() {
            summary = TestUtils.scryRenderedDOMComponentsWithClass(experiment, 'data-display');
            defTerms = summary[0].getDOMNode().getElementsByTagName('dt');
            defDescs = summary[0].getDOMNode().getElementsByTagName('dd');
        });

        it('Has correct summary panel and key-value elements within it', function() {
            expect(summary.length).toEqual(1);
            expect(defTerms.length).toEqual(8);
            expect(defDescs.length).toEqual(8);
        });

        it('has correct text for Biosample Summary', function() {
            expect(defDescs[2].textContent).toContain('Homo sapiens and Mus musculus');
        });

        it('has proper links in dbxrefs key-value', function() {
            var dbxrefs = defDescs[7].getElementsByTagName('a');
            expect(dbxrefs.length).toEqual(2);
            expect(dbxrefs[0].getAttribute('href')).toEqual('http://genome.ucsc.edu/cgi-bin/hgTracks?tsCurTab=advancedTab&tsGroup=Any&tsType=Any&hgt_mdbVar1=dccAccession&hgt_tSearch=search&hgt_tsDelRow=&hgt_tsAddRow=&hgt_tsPage=&tsSimple=&tsName=&tsDescr=&db=hg19&hgt_mdbVal1=wgEncodeEH003317');
            expect(dbxrefs[1].getAttribute('href')).toEqual('http://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSM1010811');
        });

        it('has two experiment status elements in header', function() {
            var statusList = TestUtils.scryRenderedDOMComponentsWithClass(experiment, 'status-list')[0].getDOMNode();
            expect(statusList.hasChildNodes()).toBeTruthy();
            expect(statusList.childNodes.length).toEqual(2);
        });
    });

    describe('File List', function() {
        var fileList, fileDl;

        beforeEach(function(){
            fileList = TestUtils.findRenderedDOMComponentWithTag(experiment, 'tbody').getDOMNode();
            fileDl = fileList.getElementsByTagName('a');
        });

        it('has two rows in the file list', function() {
            expect(fileList.hasChildNodes()).toBeTruthy();
            expect(fileList.childNodes.length).toEqual(2);
        });

        it('has two proper download links', function() {
            expect(fileDl.length).toEqual(2);
            expect(fileDl[0].getAttribute('href')).toEqual('http://encodedcc.sdsc.edu/warehouse/2013/6/14/ENCFF001REL.txt.gz');
            expect(fileDl[1].getAttribute('href')).toEqual('http://encodedcc.sdsc.edu/warehouse/2013/6/14/ENCFF001REQ.fastq.gz');
        });
    });

    describe('Document Panel', function() {
        var doc; // Element for the document panel

        beforeEach(function() {
            doc = TestUtils.findRenderedDOMComponentWithClass(experiment, 'type-document').getDOMNode();
        });

        it('has one document panel with a PDF image anchor', function() {
            var figures = doc.getElementsByTagName('figure');
            expect(figures.length).toEqual(1);
            var anchors = figures[0].getElementsByClassName('file-pdf');
            expect(anchors.length).toEqual(1);
        });

        it('has four key-value pairs, and proper DL link', function() {
            var url = require('url');
            var docKeyValue = doc.getElementsByClassName('key-value');
            expect(docKeyValue.length).toEqual(1);
            var defTerms = docKeyValue[0].getElementsByTagName('dt');
            expect(defTerms.length).toEqual(4);
            var defDescs = docKeyValue[0].getElementsByTagName('dd');
            expect(defDescs.length).toEqual(4);
            var anchors = defDescs[3].getElementsByTagName('a');
            expect(anchors.length).toEqual(1);
            expect(url.parse(anchors[0].getAttribute('href')).pathname).toEqual('/documents/df9dd0ec-c1cf-4391-a745-a933ab1af7a7/@@download/attachment/Myers_Lab_ChIP-seq_Protocol_v042211.pdf');
        });
    });
});