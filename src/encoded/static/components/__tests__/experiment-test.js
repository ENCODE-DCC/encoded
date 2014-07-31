/** @jsx React.DOM */
'use strict';

jest.autoMockOff();

// Fixes https://github.com/facebook/jest/issues/78
jest.dontMock('react');
jest.dontMock('underscore');


describe('Experiment Page', function() {
    var React, TestUtils, Experiment, context, _;

    beforeEach(function() {
        React = require('react');
        TestUtils = require('react/lib/ReactTestUtils');
        _ = require('underscore');

        Experiment = require('../experiment').Experiment;
        context = require('../testdata/experiment');

    });

    describe('Minimal Experiment', function() {
        var experiment, summary, defTerms, defDescs;

        beforeEach(function() {
            experiment = <Experiment context={context} />;
            TestUtils.renderIntoDocument(experiment);

            summary = TestUtils.scryRenderedDOMComponentsWithClass(experiment, 'data-display');
            defTerms = summary[0].getDOMNode().getElementsByTagName('dt');
            defDescs = summary[0].getDOMNode().getElementsByTagName('dd');
        });

        it('has correct summary panel and key-value elements counts within it', function() {
            expect(summary.length).toEqual(1);
            expect(defTerms.length).toEqual(10);
            expect(defDescs.length).toEqual(10);
        });

        it('has proper biosample summary for no-biosample case (code adds space always)', function() {
            expect(defDescs[2].textContent).toEqual('K562 ');
        });

        it('has proper links in dbxrefs key-value', function() {
            var dbxrefs = defDescs[7].getElementsByTagName('a');
            expect(dbxrefs.length).toEqual(2);
            expect(dbxrefs[0].getAttribute('href')).toEqual('http://genome.ucsc.edu/cgi-bin/hgTracks?tsCurTab=advancedTab&tsGroup=Any&tsType=Any&hgt_mdbVar1=dccAccession&hgt_tSearch=search&hgt_tsDelRow=&hgt_tsAddRow=&hgt_tsPage=&tsSimple=&tsName=&tsDescr=&db=hg19&hgt_mdbVal1=wgEncodeEH003317');
            expect(dbxrefs[1].getAttribute('href')).toEqual('http://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSM1010811');
        });

        it('has proper links in References key-values', function() {
            var dbxrefs = defDescs[8].getElementsByTagName('a');
            expect(dbxrefs.length).toEqual(2);
            expect(dbxrefs[0].getAttribute('href')).toEqual('http://www.ncbi.nlm.nih.gov/pubmed/?term=23000965');
            expect(dbxrefs[1].getAttribute('href')).toEqual('http://www.ncbi.nlm.nih.gov/pubmed/?term=16395128');
        });

        it('has proper release date', function() {
            expect(defDescs[9].textContent).toEqual('2011-10-29');
        });

        it('has two experiment status elements in header', function() {
            var statusList = TestUtils.findRenderedDOMComponentWithClass(experiment, 'status-list').getDOMNode();
            expect(statusList.hasChildNodes()).toBeTruthy();
            expect(statusList.childNodes.length).toEqual(2);
        });
    });

    describe('Experiment with files', function() {
        var experiment, fileList, fileDl;

        beforeEach(function() {
            var context_fs = _.clone(context);
            context_fs.files = [require('../testdata/file/text'), require('../testdata/file/fastq')];
            experiment = <Experiment context={context_fs} />;
            TestUtils.renderIntoDocument(experiment);

            fileList = TestUtils.findRenderedDOMComponentWithTag(experiment, 'tbody').getDOMNode();
            fileDl = fileList.getElementsByTagName('a');
        });

        it('has two rows in the file list', function() {
            expect(fileList.hasChildNodes()).toBeTruthy();
            expect(fileList.childNodes.length).toEqual(2);
        });

        it('has two proper download links', function() {
            expect(fileDl.length).toEqual(2);
            expect(fileDl[0].getAttribute('href')).toEqual('/files/ENCFF001REL/@@download/ENCFF001REL.txt.gz');
            expect(fileDl[1].getAttribute('href')).toEqual('/files/ENCFF001REQ/@@download/ENCFF001REQ.fastq.gz');
        });
    });

    describe('Document Panel', function() {
        var experiment, doc;

        beforeEach(function() {
            require('../biosample.js').Document;
            var context_doc = _.clone(context);
            context_doc.documents = [require('../testdata/document/myerschipseq')];
            experiment = <Experiment context={context_doc} />;
            TestUtils.renderIntoDocument(experiment);
            doc = TestUtils.findRenderedDOMComponentWithClass(experiment, 'type-document').getDOMNode();
        });

        it('has one document panel with a PDF image anchor', function() {
            var figures = doc.getElementsByTagName('figure');
            expect(figures.length).toEqual(1);
            var anchors = figures[0].getElementsByClassName('file-pdf');
            expect(anchors.length).toEqual(1);
        });

        it('has a single proper download link', function() {
            var url = require('url');

            var dlBar = doc.getElementsByClassName('dl-bar');
            expect(dlBar.length).toEqual(1);
            var anchors = dlBar[0].getElementsByTagName('a');
            expect(anchors.length).toEqual(1);
            expect(url.parse(anchors[0].getAttribute('href')).pathname).toEqual('/documents/df9dd0ec-c1cf-4391-a745-a933ab1af7a7/@@download/attachment/Myers_Lab_ChIP-seq_Protocol_v042211.pdf');
        });

        it('has two key-value pairs, and proper DL link', function() {
            var trigger = doc.getElementsByTagName('a');
            TestUtils.Simulate.click(trigger[2]);

            var docKeyValue = doc.getElementsByClassName('key-value-left');
            expect(docKeyValue.length).toEqual(1);
            var defTerms = docKeyValue[0].getElementsByTagName('dt');
            expect(defTerms.length).toEqual(2);
            var defDescs = docKeyValue[0].getElementsByTagName('dd');
            expect(defDescs.length).toEqual(2);
        });
    });

    describe('Replicate Panels', function() {
        var experiment, replicates;

        beforeEach(function() {
            var context_rep = _.clone(context);
            context_rep.replicates = [require('../testdata/replicate/human'), require('../testdata/replicate/mouse')];
            experiment = <Experiment context={context_rep} />;
            TestUtils.renderIntoDocument(experiment);
            replicates = TestUtils.scryRenderedDOMComponentsWithClass(experiment, 'panel-replicate');
        });

        it('has proper biosample summary ', function() {
            var summary = TestUtils.scryRenderedDOMComponentsWithClass(experiment, 'data-display');
            var defDescs = summary[0].getDOMNode().getElementsByTagName('dd');
            expect(defDescs[2].textContent).toEqual('K562 (Homo sapiens and Mus musculus)');
            var italics = defDescs[2].getElementsByTagName('em');
            expect(italics.length).toEqual(2);
            expect(italics[0].textContent).toEqual('Homo sapiens');
            expect(italics[1].textContent).toEqual('Mus musculus');
        });

        it('has two replicate panels', function() {
            expect(replicates.length).toEqual(2);
        });

        it('has links to the proper biosamples in both replicate panels', function() {
            var anchors = replicates[0].getDOMNode().getElementsByTagName('a');
            expect(anchors.length).toEqual(1);
            expect(anchors[0].textContent).toEqual('ENCBS087RNA');
            expect(anchors[0].getAttribute('href')).toEqual('/biosamples/ENCBS087RNA/');
            anchors = replicates[1].getDOMNode().getElementsByTagName('a');
            expect(anchors.length).toEqual(1);
            expect(anchors[0].textContent).toEqual('ENCBS989WPD');
            expect(anchors[0].getAttribute('href')).toEqual('/biosamples/ENCBS989WPD/');
        });

        describe('Assay Panel', function() {
            var assay, defTerms, defDescs;

            beforeEach(function() {
                assay = TestUtils.scryRenderedDOMComponentsWithClass(experiment, 'panel-assay');
                defTerms = assay[0].getDOMNode().getElementsByTagName('dt');
                defDescs = assay[0].getDOMNode().getElementsByTagName('dd');
            });

            it('has one assay panel and seven key-value pairs', function() {
                expect(assay.length).toEqual(1);
                expect(defTerms.length).toEqual(7);
                expect(defDescs.length).toEqual(7);
            });

            it('has a proper link to a platform in the seventh key-value pair', function() {
                var anchors = defDescs[6].getElementsByTagName('a');
                expect(anchors.length).toEqual(1);
                expect(anchors[0].getAttribute('href')).toEqual('/platforms/NTR%3A0000007');
            });
        });
    });

    describe('Alternate accession display', function() {
        var experiment, alt;

        beforeEach(function() {
            var context_alt = _.clone(context);
            context_alt.alternate_accessions = ["ENCSR000ACT", "ENCSR999NOF"];
            experiment = <Experiment context={context_alt} />;
            TestUtils.renderIntoDocument(experiment);
            alt = TestUtils.findRenderedDOMComponentWithClass(experiment, 'repl-acc');
        });

        it('displays two alternate accessions', function() {
            expect(alt.getDOMNode().textContent).toEqual('Replaces ENCSR000ACT, ENCSR999NOF');
        });
    });
});
