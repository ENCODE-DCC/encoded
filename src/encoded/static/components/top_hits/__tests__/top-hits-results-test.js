import Adapter from '@wojtekmaj/enzyme-adapter-react-17';
import Enzyme, {
    mount,
    shallow,
} from 'enzyme';

import Results,
{
    makeTitle,
    Items,
    Section,
} from '../results';

// Temporary use of adapter until Enzyme is compatible with React 17.
Enzyme.configure({ adapter: new Adapter() });


const fakeResults = [
    {
        '@type': ['someSubType', 'someType'],
        '@id': '/things/abc123/',
        assay_title: 'my assay title',
        target: {
            title: 'target1 title',
        },
        accession: 'abc123',
        summary: 'something and somehow',
        file_type: 'fastq',
    },
    {
        '@type': ['someSubType', 'someType'],
        '@id': '/things/def456/',
        assay_title: 'my assay other title',
        target: {
            title: 'target2 title',
        },
        accession: 'def456',
        summary: 'something and another way',
        file_type: 'bam',
    },
];


describe('Results', () => {
    describe('makeTitle', () => {
        test('returns string with key and count', () => {
            const item = {
                key: 'Experiment',
                count: 10,
            };
            expect(
                makeTitle(item)
            ).toEqual('Experiment (10)');
        });
    });
    describe('Items', () => {
        test('maps results to Item components', () => {
            const items = mount(
                <Items items={fakeResults} />
            );
            expect(items.find('Item')).toHaveLength(2);
            expect(
                items.find('Item').get(0).props.href
            ).toEqual('/things/abc123/');
            expect(
                items.find('Item').get(1).props.href
            ).toEqual('/things/def456/');
            expect(
                items.find('Item').get(0).props.item
            ).toEqual(fakeResults[0]);
            expect(
                items.find('Item').get(1).props.item
            ).toEqual(fakeResults[1]);
        });
    });
    describe('Section', () => {
        test('contains a Title and Items component', () => {
            const section = shallow(
                <Section
                    title="Experiment (10)"
                    href="?types=Experiment&searchTerm=abc"
                    items={fakeResults}
                />
            );
            expect(section.find('Title')).toHaveLength(1);
            expect(
                section.find('Title').props().value
            ).toEqual('Experiment (10)');
            expect(section.find('Items')).toHaveLength(1);
        });
    });
    describe('Results', () => {
        const rawResults = [
            {
                key: 'Experiment',
                count: 10,
                hits: fakeResults,
            },
            {
                key: 'File',
                count: 4,
                hits: fakeResults,
            },
        ];
        test('maps results to Sections', () => {
            const func = jest.fn();
            const results = shallow(
                <Results
                    input="a549"
                    results={rawResults}
                    handleClickAway={func}
                />
            );
            expect(results.find('Section')).toHaveLength(2);
            expect(
                results.find('Section').get(0).props.title
            ).toEqual('Experiment (10)');
            expect(
                results.find('Section').get(1).props.title
            ).toEqual('File (4)');
            expect(
                results.find('Section').get(0).props.href
            ).toEqual('/search/?type=Experiment&searchTerm=a549');
            expect(
                results.find('Section').get(1).props.href
            ).toEqual('/search/?type=File&searchTerm=a549');
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
                    input="a549"
                    results={rawResults}
                    handleClickAway={func}
                />
            );
            expect(
                document.addEventListener
            ).toHaveBeenCalledTimes(1);
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
