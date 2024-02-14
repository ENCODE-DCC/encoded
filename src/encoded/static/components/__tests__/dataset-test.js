import Adapter from '@wojtekmaj/enzyme-adapter-react-17';
import Enzyme, { mount } from 'enzyme';

// Import test component and data.
import { annotationBiosampleSummary } from '../dataset';

// Temporary use of adapter until Enzyme is compatible with React 17.
Enzyme.configure({ adapter: new Adapter() });

describe('Annotation biosample summary', () => {
    test('it works for just scientific name, life stage', () => {
        const context = {
            organism: {
                scientific_name: 'Mus musculus',
            },
            relevant_life_stage: 'adult',
        };
        const summary = mount(
            annotationBiosampleSummary(context)
        );

        const summaryOutput = summary.find('.biosample-summary');
        expect(summaryOutput.text()).toEqual('Mus musculus, adult');
    });

    test('it works for just scientific name, unknown life stage', () => {
        const context = {
            organism: {
                scientific_name: 'Mus musculus',
            },
            relevant_life_stage: 'unknown',
        };
        const summary = mount(
            annotationBiosampleSummary(context)
        );

        const summaryOutput = summary.find('.biosample-summary');
        expect(summaryOutput.text()).toEqual('Mus musculus');
    });

    test('it works for just scientific name, life stage, timepoint', () => {
        const context = {
            organism: {
                scientific_name: 'Mus musculus',
            },
            relevant_life_stage: 'adult',
            relevant_timepoint: '11.5',
        };
        const summary = mount(
            annotationBiosampleSummary(context)
        );

        const summaryOutput = summary.find('.biosample-summary');
        expect(summaryOutput.text()).toEqual('Mus musculus, adult, 11.5');
    });

    test('it works for just scientific name, life stage, timepoint, timepoint units', () => {
        const context = {
            organism: {
                scientific_name: 'Mus musculus',
            },
            relevant_life_stage: 'adult',
            relevant_timepoint: '11.5',
            relevant_timepoint_units: 'year',
        };
        const summary = mount(
            annotationBiosampleSummary(context)
        );

        const summaryOutput = summary.find('.biosample-summary');
        expect(summaryOutput.text()).toEqual('Mus musculus, adult, 11.5 year');
    });
});
