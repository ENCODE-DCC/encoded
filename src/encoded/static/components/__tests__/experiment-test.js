/** @jsx React.DOM */
'use strict';

// Fixes https://github.com/facebook/jest/issues/78
jest.dontMock('react');
jest.dontMock('underscore');
jest.dontMock('url');
jest.dontMock('../../libs/registry.js');
jest.dontMock('../../libs/origin.js');

jest.dontMock('../experiment.js');
jest.dontMock('../globals.js');
jest.dontMock('../dbxref.js');
jest.dontMock('../dataset.js');
jest.dontMock('../antibody.js');
jest.dontMock('../biosample.js');
jest.dontMock('../image.js');
jest.dontMock('../fetched.js');
jest.dontMock('../mixins.js');

jest.dontMock('../jestdata/experiment.js');
jest.dontMock('../jestdata/file.js');
jest.dontMock('../jestdata/document.js');
jest.dontMock('../jestdata/replicate.js');
jest.dontMock('../jestdata/platform.js');
jest.dontMock('../jestdata/library.js');
jest.dontMock('../jestdata/biosample.js');
jest.dontMock('../jestdata/human_donor.js');
jest.dontMock('../jestdata/mouse_donor.js');
jest.dontMock('../jestdata/organism.js');
jest.dontMock('../jestdata/source.js');


describe('experiment', function() {
    var React = require('react');
    var url = require('url');
    var TestUtils = require('react/lib/ReactTestUtils');
    require('../biosample.js');

    // Load up a single experiment with test data
    var Experiment = require('../experiment.js').Experiment;
    var context = require('../jestdata/experiment.js').experiment_basic;
    context.files = require('../jestdata/file.js').file_basic;
    context.documents = require('../jestdata/document.js').document_basic;
    context.replicates = require('../jestdata/replicate.js').replicate_basic;
    context.replicates[0].platform = context.replicates[1].platform = require('../jestdata/platform.js').platform[0];
    var library = require('../jestdata/library.js').library;
    var biosamples = require('../jestdata/biosample.js').biosample;
    var human_donor = require('../jestdata/human_donor.js').human_donors[0];
    var mouse_donor = require('../jestdata/mouse_donor.js').mouse_donors[0];
    var source = require('../jestdata/source.js').sources[0];
    var organisms = require('../jestdata/organism.js').organisms;
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

    it('displays proper variants of experiments', function() {
        // Render a basic experiment
        var experiment = <Experiment context={context} />;
        TestUtils.renderIntoDocument(experiment);

        // Seven key-value elements in summary section
        var summary = TestUtils.scryRenderedDOMComponentsWithClass(experiment, 'data-display');
        expect(summary.length).toEqual(1);
        var defTerms = summary[0].getDOMNode().getElementsByTagName('dt');
        expect(defTerms.length).toEqual(8);
        var defDescs = summary[0].getDOMNode().getElementsByTagName('dd');
        expect(defDescs.length).toEqual(8);
        expect(defDescs[2].textContent).toContain('Homo sapiens and Mus musculus');

        // Proper links in dbxrefs key-value
        var dbxrefs = defDescs[7].getElementsByTagName('a');
        expect(dbxrefs.length).toEqual(2);
        expect(dbxrefs[0].getAttribute('href')).toEqual('http://genome.ucsc.edu/cgi-bin/hgTracks?tsCurTab=advancedTab&tsGroup=Any&tsType=Any&hgt_mdbVar1=dccAccession&hgt_tSearch=search&hgt_tsDelRow=&hgt_tsAddRow=&hgt_tsPage=&tsSimple=&tsName=&tsDescr=&db=hg19&hgt_mdbVal1=wgEncodeEH003317');
        expect(dbxrefs[1].getAttribute('href')).toEqual('http://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSM1010811');

        // Two experiment status elements in header
        var statusList = TestUtils.scryRenderedDOMComponentsWithClass(experiment, 'status-list')[0].getDOMNode();
        expect(statusList.hasChildNodes()).toEqual(true);
        expect(statusList.childNodes.length).toEqual(2);

        // Two rows in the file list, and two proper download links
        var fileList = TestUtils.findRenderedDOMComponentWithTag(experiment, 'tbody').getDOMNode();
        expect(fileList.hasChildNodes()).toEqual(true);
        expect(fileList.childNodes.length).toEqual(2);
        var fileDl = fileList.getElementsByTagName('a');
        expect(fileDl.length).toEqual(2);
        expect(fileDl[0].getAttribute('href')).toEqual('http://encodedcc.sdsc.edu/warehouse/2013/6/14/ENCFF001REL.txt.gz');
        expect(fileDl[1].getAttribute('href')).toEqual('http://encodedcc.sdsc.edu/warehouse/2013/6/14/ENCFF001REQ.fastq.gz');

        // One document panel with a PDF image anchor
        var doc = TestUtils.findRenderedDOMComponentWithClass(experiment, 'type-document').getDOMNode();
        var figure = doc.getElementsByTagName('figure');
        expect(figure.length).toEqual(1);
        var anchors = figure[0].getElementsByClassName('file-pdf');
        expect(anchors.length).toEqual(1);

        // Document panel has four key-value pairs, and proper DL link
        var docKeyValue = doc.getElementsByClassName('key-value');
        expect(docKeyValue.length).toEqual(1);
        defTerms = docKeyValue[0].getElementsByTagName('dt');
        expect(defTerms.length).toEqual(4);
        defDescs = docKeyValue[0].getElementsByTagName('dd');
        expect(defDescs.length).toEqual(4);
        anchors = defDescs[3].getElementsByTagName('a');
        expect(anchors.length).toEqual(1);
        expect(url.parse(anchors[0].getAttribute('href')).pathname).toEqual('/documents/df9dd0ec-c1cf-4391-a745-a933ab1af7a7/@@download/attachment/Myers_Lab_ChIP-seq_Protocol_v042211.pdf');
    });
});