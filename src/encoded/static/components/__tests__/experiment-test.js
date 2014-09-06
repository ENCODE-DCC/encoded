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
            experiment = TestUtils.renderIntoDocument(
                <Experiment context={context} />
            );

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
            experiment = TestUtils.renderIntoDocument(
                <Experiment context={context_fs} />
            );

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

    describe('Replicate Panels', function() {
        var experiment, replicates;

        beforeEach(function() {
            var context_rep = _.clone(context);
            context_rep.replicates = [require('../testdata/replicate/human'), require('../testdata/replicate/mouse')];
            experiment = TestUtils.renderIntoDocument(
                <Experiment context={context_rep} />
            );
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
    });
});
