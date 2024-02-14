import Adapter from '@wojtekmaj/enzyme-adapter-react-17';
import Enzyme, { mount } from 'enzyme';
import Input from '../input';


// Temporary use of adapter until Enzyme is compatible with React 17.
Enzyme.configure({ adapter: new Adapter() });


describe('Gene search input', () => {
    test('Input renders, contains text and ref', () => {
        const func = jest.fn();
        let inputRef = null;
        const inputBox = mount(
            <Input
                input="ep300"
                onChange={func}
                ref={(current) => { inputRef = current; }}
            />
        );
        expect(
            inputBox.find('input').props().value
        ).toEqual('ep300');
        expect(
            inputBox.find('input').props().placeholder
        ).toEqual('Enter gene name here');
        expect(
            inputRef.value
        ).toEqual('ep300');
        inputRef.value = 'new value';
        expect(
            inputRef.value
        ).toEqual('new value');
    });
    test('Input fires function on change', () => {
        const func = jest.fn();
        const inputBox = mount(
            <Input
                input="hello"
                onChange={func}
            />
        );
        expect(func).toHaveBeenCalledTimes(0);
        inputBox.simulate('change');
        expect(func).toHaveBeenCalledTimes(1);
    });
});
