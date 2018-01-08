import React from 'react';
import { mount } from 'enzyme';
import moment from 'moment';

// Import test component.
import { SortTablePanel, SortTable } from '../sorttable';


describe('Software', () => {
    const tableConfig = {
        accession: {
            title: 'Accession',
        },
        file_type: {
            title: 'File type',
        },
        output_type: {
            title: 'Output type',
        },
        biological_replicates: {
            title: 'Biological replicates',
            getValue: item => (item.biological_replicates ? item.biological_replicates.sort((a, b) => a - b).join(', ') : ''),
        },
        technical_replicate_number: {
            title: 'Technical replicate',
            getValue: item => (item.replicate ? item.replicate.technical_replicate_number : null),
        },
        assembly: {
            title: 'Mapping assembly',
        },
        genome_annotation: {
            title: 'Genome annotation',
        },
        title: {
            title: 'Lab',
            getValue: item => (item.lab && item.lab.title ? item.lab.title : null),
        },
        date_created: {
            title: 'Date added',
            getValue: item => moment.utc(item.date_created).format('YYYY-MM-DD'),
            sorter: (a, b) => {
                if (a.date_created && b.date_created) {
                    return Date.parse(a.date_created) - Date.parse(b.date_created);
                }
                // Arguably better as a nested ternary with parens, but eslint currently has no
                // option for this.
                // https://github.com/eslint/eslint/issues/3480
                if (a.date_created) {
                    return -1;
                }
                if (b.date_created) {
                    return 1;
                }
                return 0;
            },
        },
    };

    describe('Make a table and verify row and column counts', () => {
        let table;
        let tableOutput;
        let rows;

        beforeAll(() => {
            const file0 = require('../testdata/file/fastq.js')[0];
            file0.replicate = require('../testdata/replicate/human.js');
            const files = [file0];
            table = mount(
                <SortTablePanel>
                    <SortTable list={files} columns={tableConfig} />
                </SortTablePanel>
            );

            tableOutput = table.find('table');
            rows = tableOutput.find('tr');
        });

        it('has the correct number of rows', () => {
            expect(tableOutput).toHaveLength(1);
            expect(rows).toHaveLength(3);
        });

        it('has the correct number of columns', () => {
            const cells = rows.at(1).find('td');
            expect(cells).toHaveLength(9);
        });
    });
});
