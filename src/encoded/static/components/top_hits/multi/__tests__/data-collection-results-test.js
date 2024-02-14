import Adapter from '@wojtekmaj/enzyme-adapter-react-17';
import Enzyme, {
    mount,
    shallow,
} from 'enzyme';

import Results,
{
    Section,
} from '../results';

// Temporary use of adapter until Enzyme is compatible with React 17.
Enzyme.configure({ adapter: new Adapter() });


const fakeResults = [
    {
        '@type': ['DataCollection'],
        '@id': '/things/abc123/',
        searchUrl: '/things/abc123/?format=json',
        total: 6,
        title: 'abc123',
    },
];


describe('Results', () => {
    describe('Section', () => {
        test('contains Items component', () => {
            const section = shallow(
                <Section
                    items={fakeResults}
                />
            );
            expect(section.find('Items')).toHaveLength(1);
        });
    });
    describe('Results', () => {
        const rawResults = [
            {
                key: 'DataCollection',
                hits: fakeResults,
            },
        ];
        test('maps results to Sections', () => {
            const func = jest.fn();
            const results = shallow(
                <Results
                    results={rawResults}
                    handleClickAway={func}
                />
            );
            expect(results.find('Section')).toHaveLength(1);
            expect(
                results.props().className
            ).toEqual('multisearch__results');
        });
        test('handle click away', () => {
            // Mock document event listener.
            const listeners = {};
            document.addEventListener = jest.fn((event, callback) => {
                listeners[event] = callback;
            });
            document.removeEventListener = jest.fn((event) => {
                listeners[event] = undefined;
            });
            const func = jest.fn();
            const results = mount(
                <Results
                    results={rawResults}
                    handleClickAway={func}
                />
            );
            expect(func).toHaveBeenCalledTimes(0);
            listeners.click();
            expect(func).toHaveBeenCalledTimes(1);
            expect(
                document.removeEventListener
            ).toHaveBeenCalledTimes(0);
            results.unmount();
            results.setProps(); // Forces useEffect cleanup function to be called.
            expect(
                document.removeEventListener
            ).toHaveBeenCalledTimes(1);
        });
    });
});
