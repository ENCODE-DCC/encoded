'use strict';

jest.autoMockOff();

// Fixes https://github.com/facebook/jest/issues/78
jest.dontMock('react');
jest.dontMock('moment');

describe('Software', function() {
    var React, moment, TestUtils, SortTable, SortTablePanel;

    var tableConfig = {
        'accession': {
            title: 'Accession'
        },
        'file_type': {
            title: 'File type'
        },
        'output_type': {
            title: 'Output type'
        },
        'biological_replicates': {
            title: 'Biological replicates',
            getValue: function(item) {
                return item.biological_replicates ? item.biological_replicates.sort(function(a,b){ return a - b; }).join(', ') : '';
            }
        },
        'technical_replicate_number': {
            title: 'Technical replicate',
            getValue: function(item) {
                return item.replicate ? item.replicate.technical_replicate_number : null;
            }
        },
        'assembly': {
            title: 'Mapping assembly'
        },
        'genome_annotation': {
            title: 'Genome annotation'
        },
        'title': {
            title: 'Lab',
            getValue: function(item) {
                return item.lab && item.lab.title ? item.lab.title : null;
            }
        },
        'date_created': {
            title: 'Date added',
            getValue: function(item) {
                return moment.utc(item.date_created).format('YYYY-MM-DD');
            },
            sorter: function(a, b) {
                if (a.date_created && b.date_created) {
                    return Date.parse(a.date_created) - Date.parse(b.date_created);
                }
                return a.date_created ? -1 : (b.date_created ? 1 : 0);
            }
        }
    };

    beforeEach(function() {
        React = require('react');
        moment = require('moment');
        TestUtils = require('react/lib/ReactTestUtils');

        // Set up context object to be rendered
        var sorttable = require('../sorttable');
        SortTablePanel = sorttable.SortTablePanel;
        SortTable = sorttable.SortTable;
    });

    describe('Make a table and verify row and column counts', function() {
        var table, tableOutput, rows;

        beforeEach(function() {
            var file0 = require('../testdata/file/fastq.js');
            file0.replicate = require('../testdata/replicate/human.js');
            var files = [file0];
            table = TestUtils.renderIntoDocument(
                <SortTablePanel>
                    <SortTable list={files} config={tableConfig} />
                </SortTablePanel>
            );

            tableOutput = TestUtils.scryRenderedDOMComponentsWithClass(table, 'table');
            rows = tableOutput[0].getDOMNode().getElementsByTagName('tr');
        });

        it('has the correct number of rows', function() {
            expect(tableOutput.length).toEqual(1);
            expect(rows.length).toEqual(3);
        });

        it('has the correct number of columns', function() {
            var cells = rows[1].getElementsByTagName('td');
            expect(cells.length).toEqual(9);
        });
    });
});
