import Adapter from '@wojtekmaj/enzyme-adapter-react-17';
import Enzyme, { mount } from 'enzyme';

import {
    Input,
    InputWithIcon,
} from '../input';

// Temporary use of adapter until Enzyme is compatible with React 17.
Enzyme.configure({ adapter: new Adapter() });


describe('Input', () => {
    test('Input renders and responds to focus and blur', () => {
        const func = jest.fn();
        const inputBox = mount(
            <Input
                input="hello"
                onChange={func}
            />
        );
        expect(
            inputBox.find('input').props().value
        ).toEqual('hello');
        expect(inputBox.find('i')).toHaveLength(0);
        expect(
            inputBox.find('input').props().className
        ).toBeNull();
        inputBox.simulate('focus');
        expect(
            inputBox.find('input').props().className
        ).toEqual('selected');
        inputBox.simulate('blur');
        expect(
            inputBox.find('input').props().className
        ).toEqual('selected');
        inputBox.setProps({ input: '' });
        inputBox.simulate('blur');
        expect(
            inputBox.find('input').props().className
        ).toBeNull();
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
    test('InputWithIcon renders and contains icon', () => {
        const func = jest.fn();
        const inputBox = mount(
            <InputWithIcon
                input="hello"
                onChange={func}
            />
        );
        expect(inputBox.find('i')).toHaveLength(1);
    });
});
