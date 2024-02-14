import Adapter from '@wojtekmaj/enzyme-adapter-react-17';
import Enzyme, {
    shallow,
} from 'enzyme';

import Group, {
    Title,
} from '../group';
import Results from '../results';

// Temporary use of adapter until Enzyme is compatible with React 17.
Enzyme.configure({ adapter: new Adapter() });


describe('Group', () => {
    test('returns title', () => {
        const title = shallow(
            <Title
                title="xyz"
            />
        );
        expect(
            title.props().className
        ).toEqual('group-title');
        expect(
            title.text()
        ).toEqual('xyz');
    });
    test('returns group', () => {
        const group = shallow(
            <Group
                title="xyz"
                input="a549"
                results={[]}
                handleClickAway={() => {}}
                component={Results}
            />
        );
        expect(
            group.find(Title).props().title
        ).toEqual('xyz');
        expect(
            group.find(Results)
        ).toHaveLength(1);
    });
});
