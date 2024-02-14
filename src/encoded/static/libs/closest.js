// eslint-disable-next-line consistent-return
export default function closest(el, selector) {
    while (el) {
        if (el.matches(selector)) return el;
        el = el.parentElement;
    }
}
