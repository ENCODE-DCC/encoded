import Adapter from '@wojtekmaj/enzyme-adapter-react-17';
import Enzyme, { mount } from 'enzyme';
import Search, {
    makeSearchUrl,
} from '../search';


// Temporary use of adapter until Enzyme is compatible with React 17.
Enzyme.configure({ adapter: new Adapter() });


describe('Gene search', () => {
    test('makeSearchUrl', () => {
        expect(
            makeSearchUrl('ep300', 'GRCh38')
        ).toEqual(
            '/search/?type=Gene&field=title&field=@id' +
            '&field=locations&field=synonyms&field=dbxrefs' +
            '&limit=50&searchTerm=ep300&locations.assembly=GRCh38'
        );
    });
    describe('Search component', () => {
        test('renders correctly', () => {
            const func = jest.fn();
            const search = mount(
                <Search
                    assembly="GRCh38"
                    handleClick={func}
                />
            );
            expect(
                search.find('input')
            ).toHaveLength(1);
        });
    });
});
