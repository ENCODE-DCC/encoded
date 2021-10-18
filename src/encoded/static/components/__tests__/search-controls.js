import Adapter from '@wojtekmaj/enzyme-adapter-react-17';
import Enzyme, { mount } from 'enzyme';
import { PropTypes } from 'prop-types';
import _ from 'underscore';

// Import test component and data.
import { SearchControls } from '../search';
import context from '../testdata/experiment-search';

// Temporary use of adapter until Enzyme is compatible with React 17.
Enzyme.configure({ adapter: new Adapter() });

describe('View controls for search with Experiments', () => {
    describe('Minimal Experiment', () => {
        let searchControls;

        beforeAll(() => {
            const contextResults = _.clone(context.single_type);
            searchControls = mount(
                <SearchControls context={contextResults} />,
                { context: { location_href: '/search/?type=Experiment' } }
            );
        });

        test('has proper view control buttons', () => {
            const viewControls = searchControls.find('.btn-attached');
            const links = viewControls.find('a');
            expect(links).toHaveLength(2);
            expect(links.at(0).prop('href')).toEqual('/report/?type=Experiment&status=released&assay_slims=DNA+accessibility');
            expect(links.at(1).prop('href')).toEqual('/matrix/?type=Experiment&status=released&assay_slims=DNA+accessibility');
        });

        test('has Download, Visualize, and JSON buttons', () => {
            const buttons = searchControls.find('button');
            expect(buttons).toHaveLength(3);
            expect(buttons.at(0).text()).toEqual('Download');
            expect(buttons.at(1).text()).toEqual('Visualize');
            expect(buttons.at(2).text()).toEqual('{ ; }');
        });
    });

    describe('Multiple searched types', () => {
        let searchControls;

        beforeAll(() => {
            const contextResults = _.clone(context.multiple_types);
            searchControls = mount(
                <SearchControls context={contextResults} />,
                {
                    context: {
                        location_href: '/search/?type=FunctionalCharacterizationExperiment&type=FunctionalCharacterizationSeries',
                        profilesTitles: {
                            FunctionalCharacterizationExperiment: 'Functional characterization experiment',
                            FunctionalCharacterizationSeries: 'Functional characterization series',
                        },
                    },
                    childContextTypes: {
                        location_href: PropTypes.toString,
                        profilesTitles: PropTypes.object,
                    },
                },
            );
        });

        test('has a single view control button', () => {
            const viewControls = searchControls.find('.btn-attached');
            const buttons = viewControls.find('button');
            expect(buttons).toHaveLength(1);
            expect(buttons.at(0).text()).toEqual('Report');

            // Click the Report button dropdown and test its contents.
            buttons.at(0).simulate('click', { nativeEvent: { stopImmediatePropagation: _.noop } });
            const typeOptions = searchControls.find('#view-type-report-menu');
            const typeItems = typeOptions.find('li');
            expect(typeItems).toHaveLength(2);
            expect(typeItems.at(0).text()).toEqual('Functional characterization experiment');
            expect(typeItems.at(1).text()).toEqual('Functional characterization series');
        });
    });
});
