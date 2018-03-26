import React from 'react';
import { mount } from 'enzyme';

// Import test component and data.
import Antibody from '../antibody';
import context from '../testdata/antibody/ENCAB000AUZ';


describe('Antibody', () => {
    beforeAll(() => {
        // Set up context object to be rendered
        context.host_organism = require('../testdata/organism/rabbit');
        context.source = require('../testdata/source/aviva');
        context.characterizations = [require('../testdata/characterization/antibody-367a6fdd0cef')];
        context.characterizations[0].submitted_by = require('../testdata/submitter');
        context.characterizations[0].documents = [require('../testdata/document/antibodyStandards')];
        context.characterizations[0].lab = require('../testdata/lab');
        context.characterizations[0].award = require('../testdata/award');
        context.characterizations[0].target = require('../testdata/target/HNRNPA1-human');
        context.characterizations[0].target.organism = require('../testdata/organism/human');
        context.lot_reviews = [require('../testdata/lot_review/EFO-0002791')];
        context.lot_reviews[0].organisms = [require('../testdata/organism/human')];
        context.lot_reviews[0].targets = [require('../testdata/target/HNRNPA1-human')];
        context.lot_reviews[0].targets[0].organisms = [require('../testdata/organism/human')];
    });

    describe('Typical antibody', () => {
        let antibody;

        beforeAll(() => {
            // Render antibody into jsnode
            antibody = mount(
                <Antibody context={context} />
            );
        });

        test('has a good header', () => {
            let headerLine = antibody.find('h2');
            expect(headerLine.text()).toEqual('ENCAB000AUZ');
            headerLine = antibody.find('h3');
            expect(headerLine.text()).toEqual('Antibody against Homo sapiens HNRNPA1');
        });

        test('has a good status panel', () => {
            const panel = antibody.find('.type-antibody-status');
            const row = panel.find('.status-organism-row');
            const element = row.at(0).find('.status-status');
            expect(element).toHaveLength(1);
            expect(element.text()).toEqual('awaiting characterization');
            expect(row.find('.status-organism').text()).toEqual('Homo sapiens');
            expect(row.find('.status-terms').text()).toEqual('HeLa-S3');
        });

        test('has a good summary panel', () => {
            const panel = antibody.find('.data-display');

            let item = panel.find('[data-test="source"]');
            let itemDescription = item.find('dd');
            let anchor = itemDescription.at(0).find('a');
            expect(itemDescription.text()).toEqual('Aviva');
            expect(anchor.prop('href')).toEqual('http://www.avivasysbio.com');

            item = panel.find('[data-test="productid"]');
            itemDescription = item.find('dd');
            anchor = itemDescription.find('a');
            expect(itemDescription.text()).toEqual('ARP40383_T100');
            expect(anchor.at(0).prop('href')).toEqual('http://www.avivasysbio.com/anti-hnrpa1-antibody-n-terminal-region-arp40383-t100.html');

            item = panel.find('[data-test="lotid"]');
            itemDescription = item.find('dd');
            expect(itemDescription.text()).toEqual('QC9473-091124');

            item = panel.find('[data-test="targets"]');
            itemDescription = item.find('dd');
            anchor = itemDescription.find('a');
            expect(itemDescription.text()).toEqual('HNRNPA1 (Homo sapiens)');
            expect(anchor.at(0).prop('href')).toEqual('/targets/HNRNPA1-human/');

            item = panel.find('[data-test="host"]');
            itemDescription = item.find('dd');
            expect(itemDescription.text()).toEqual('rabbit');

            item = panel.find('[data-test="clonality"]');
            itemDescription = item.find('dd');
            expect(itemDescription.text()).toEqual('polyclonal');

            item = panel.find('[data-test="isotype"]');
            itemDescription = item.find('dd');
            expect(itemDescription.text()).toEqual('IgG');

            item = panel.find('[data-test="antigensequence"]');
            itemDescription = item.find('dd');
            expect(itemDescription.text()).toEqual('MSKSESPKEPEQLRKLFIGGLSFETTDESLRSHFEQWGTLTDCVVMRDPN');
        });
    });
});
