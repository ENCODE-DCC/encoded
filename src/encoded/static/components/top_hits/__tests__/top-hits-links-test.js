import Adapter from '@wojtekmaj/enzyme-adapter-react-17';
import Enzyme, { mount } from 'enzyme';

import { LinkWithHover } from '../links';

// Temporary use of adapter until Enzyme is compatible with React 17.
Enzyme.configure({ adapter: new Adapter() });


describe('LinkWithHover', () => {
    test('renders default value', () => {
        const link = mount(
            <LinkWithHover
                href="abc123"
                defaultValue="click me"
            />
        );
        expect(link.text()).toEqual('click me');
    });
    test('has correct href', () => {
        const link = mount(
            <LinkWithHover
                href="abc123"
                defaultValue="click me"
            />
        );
        expect(link.find('a').props().href).toEqual('abc123');
    });
    test('has null classname', () => {
        const link = mount(
            <LinkWithHover
                href="abc123"
                defaultValue="click me"
            />
        );
        expect(link.find('a').props().className).toBeNull();
    });
    test('renders default classname', () => {
        const link = mount(
            <LinkWithHover
                href="abc123"
                defaultValue="click me"
                defaultClass="default-class"
            />
        );
        expect(link.find('a').props().className).toEqual('default-class');
    });
    test('renders hover class when hovered', () => {
        const link = mount(
            <LinkWithHover
                href="abc123"
                defaultValue="click me"
                defaultClass="default-class"
                hoverClass="hover-class"
            />
        );
        expect(link.find('a').props().className).toEqual('default-class');
        link.simulate('mouseenter');
        expect(link.find('a').props().className).toEqual('hover-class');
    });
    test('renders hover value when hovered', () => {
        const link = mount(
            <LinkWithHover
                href="abc123"
                defaultValue="click me"
                hoverValue="hover me"
                defaultClass="default-class"
                hoverClass="hover-class"
            />
        );
        expect(link.text()).toEqual('click me');
        link.simulate('mouseenter');
        expect(link.text()).toEqual('hover me');
    });
});
