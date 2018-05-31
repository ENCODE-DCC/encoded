import React from 'react';
import { shallow } from 'enzyme';
import Status, { getObjectStatuses } from '../status';


describe('Status utility and component tests', () => {
    // Test getObjectStatuses function for success cases.
    describe('getObjectStatuses successful', () => {
        test('has the proper number of statuses at each access level for Datasets', () => {
            let statuses = getObjectStatuses('Dataset', 'external');
            expect(statuses).toHaveLength(3);
            statuses = getObjectStatuses('Dataset', 'consortium');
            expect(statuses).toHaveLength(5);
            statuses = getObjectStatuses('Dataset', 'administrator');
            expect(statuses).toHaveLength(7);
            statuses = getObjectStatuses('Dataset');
            expect(statuses).toHaveLength(3);
        });
    });

    // Make sure getObjectStatuses function fails properly.
    describe('getObjectStatuses failures', () => {
        test('fails by returning empty array', () => {
            let statuses = getObjectStatuses('Assay', 'public');
            expect(statuses).toHaveLength(0);
            statuses = getObjectStatuses('Dataset', 'faculty');
            expect(statuses).toHaveLength(0);
        });
    });

    // Test the <Status /> component.
    describe('Generate correct status badge components', () => {
        let context;

        beforeAll(() => {
            context = {
                '@type': ['FlyDonor', 'Donor', 'Item'],
                status: 'in progress',
            };
        });

        test('has an SVG, correct label, and correct status CSS class', () => {
            const status = shallow(
                <Status
                    item={context}
                />
            );
            const statusWrapper = status.find('.status');
            expect(statusWrapper.length).toBe(1);
            expect(status.find('.status--in-progress').length).toBe(1);

            // Make sure the Status component has an icon with an svg in it.
            const statusIcon = statusWrapper.find('.status__icon');
            expect(statusIcon.length).toBe(1);
            expect(statusIcon.find('svg').length).toBe(1);

            const statusLabel = statusWrapper.find('.status__label');
            expect(statusLabel.length).toBe(1);
            expect(statusLabel.text()).toEqual('in progress');
        });

        test('has optional tooltip', () => {
            const status = shallow(
                <Status
                    item={context}
                    title="This is a tooltip"
                />
            );
            expect(status.find({ title: 'This is a tooltip' }).length).toEqual(1);
        });

        test('has optional added CSS classes', () => {
            const status = shallow(
                <Status
                    item={context}
                    css="class1 class2"
                />
            );
            expect(status.find('.class1').length).toEqual(1);
            expect(status.find('.class2').length).toEqual(1);
        });

        test('missing label when requested', () => {
            const status = shallow(
                <Status
                    item={context}
                    noLabel
                />
            );
            const statusWrapper = status.find('.status');
            expect(statusWrapper.find('.status__label').length).toEqual(0);
        });

        test('missing icon when requested', () => {
            const status = shallow(
                <Status
                    item={context}
                    noIcon
                />
            );
            const statusWrapper = status.find('.status');
            expect(statusWrapper.find('.status__icon').length).toEqual(0);
        });
    });
});
