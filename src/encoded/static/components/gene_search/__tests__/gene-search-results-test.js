import Adapter from '@wojtekmaj/enzyme-adapter-react-17';
import Enzyme, { mount } from 'enzyme';
import Results, {
    HighlightedText,
    NormalText,
    matchingOrNotToComponent,
    Result,
    shouldShowSearchResults,
} from '../results';
import fakeGeneItem from './gene-search-gene-test';


// Temporary use of adapter until Enzyme is compatible with React 17.
Enzyme.configure({ adapter: new Adapter() });


describe('Gene search results', () => {
    describe('HighlightedText', () => {
        test('renders correct value and classname', () => {
            const highlightedText = mount(
                <HighlightedText
                    value="ABC"
                />
            );
            expect(
                highlightedText.find('span').text()
            ).toEqual('ABC');
            expect(
                highlightedText.find('span').props().className
            ).toEqual('matching-text');
        });
    });
    describe('NormalText', () => {
        test('renders correct valuue', () => {
            const normalText = mount(
                <NormalText
                    value="ABC"
                />
            );
            expect(
                normalText.text()
            ).toEqual('ABC');
        });
    });
    test('matchingOrNotToComponent', () => {
        expect(
            matchingOrNotToComponent.match.name
        ).toEqual('HighlightedText');
        expect(
            matchingOrNotToComponent.mismatch.name
        ).toEqual('NormalText');
    });
    describe('Result', () => {
        test('renders highlighted components correctly', () => {
            const func = jest.fn();
            const result = mount(
                <Result
                    item={fakeGeneItem}
                    searchTerm="ep300"
                    handleClick={func}
                />
            );
            expect(
                result.find('HighlightedText')
            ).toHaveLength(1);
            expect(
                result.find('HighlightedText').text()
            ).toEqual('EP300');
            expect(
                result.find('NormalText')
            ).toHaveLength(1);
            expect(
                result.find('NormalText').text()
            ).toEqual(' (Homo sapiens)');
        });
        test('handles click', () => {
            const func = jest.fn();
            const result = mount(
                <Result
                    item={fakeGeneItem}
                    searchTerm="ep300"
                    handleClick={func}
                />
            );
            expect(func).toHaveBeenCalledTimes(0);
            result.find('button').simulate('click');
            expect(func).toHaveBeenCalledTimes(1);
        });
    });
    test('shouldShowSearchResults', () => {
        expect(
            shouldShowSearchResults(
                'ep300',
                ['a', 'b']
            )
        ).toBeTruthy();
        expect(
            shouldShowSearchResults(
                '',
                ['a', 'b']
            )
        ).toBeFalsy();
        expect(
            shouldShowSearchResults(
                'ep300',
                []
            )
        ).toBeFalsy();
    });
    describe('Results', () => {
        test('renders correctly', () => {
            const fakeGeneItem2 = {
                ...fakeGeneItem,
                '@id': '/genes/123/',
            };
            const func = jest.fn();
            const results = mount(
                <Results
                    searchTerm="ep300"
                    rawResults={
                        {
                            '@graph': [
                                fakeGeneItem,
                                fakeGeneItem2,
                            ],
                        }
                    }
                    handleClick={func}
                />
            );
            expect(
                results.find('Result')
            ).toHaveLength(2);
        });
    });
});

