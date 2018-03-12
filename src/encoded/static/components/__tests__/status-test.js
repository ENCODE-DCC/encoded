import { getObjectStatuses } from '../statuslabel';


describe('Statuses', () => {
    describe('getObjectStatuses successful', () => {
        test('has the proper number of statuses at each access level for Experiments', () => {
            let statuses = getObjectStatuses('Experiment', 'external');
            expect(statuses).toHaveLength(3);
            statuses = getObjectStatuses('Experiment', 'consortium');
            expect(statuses).toHaveLength(6);
            statuses = getObjectStatuses('Experiment', 'admin');
            expect(statuses).toHaveLength(8);
            statuses = getObjectStatuses('Experiment');
            expect(statuses).toHaveLength(8);
        });
    });

    describe('getObjectStatuses failures', () => {
        test('test failure conditions', () => {
            let statuses = getObjectStatuses('Assay', 'public');
            expect(statuses).toHaveLength(0);
            statuses = getObjectStatuses('Experiment', 'faculty');
            expect(statuses).toHaveLength(0);
        });
    });
});
