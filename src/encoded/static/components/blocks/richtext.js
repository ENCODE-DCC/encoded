import React from 'react';
import PropTypes from 'prop-types';
import * as globals from '../globals';


export default class RichTextBlockView extends React.Component {
    constructor(props) {
        super(props);

        // Set initial React component state.
        this.state = {
            value: this.props.value,
        };

        // Bind this to non-React components.
        this.setupEditor = this.setupEditor.bind(this);
        this.handleClickableFAQ = this.handleClickableFAQ.bind(this);
    }

    componentDidMount() {
        const $script = require('scriptjs');
        if (this.context.editable) {
            $script('ckeditor/ckeditor.js', this.setupEditor);
        }
        // Polyfill for 'closest' for IE
        const elementPrototype = window.Element.prototype;
        if (!elementPrototype.closest) {
            elementPrototype.closest = function closest(s) {
                let el = this;
                do {
                    if (el.matches(s)) return el;
                    el = el.parentElement || el.parentNode;
                } while (el !== null && el.nodeType === 1);
                return null;
            };
        }
        this.handleClickableFAQ();
    }

    /* eslint-disable camelcase */
    UNSAFE_componentWillReceiveProps(nextProps) {
        this.setState({ value: nextProps.value });
    }
    /* eslint-enable camelcase */

    shouldComponentUpdate(nextProps, nextState) {
        return (!this.editor || nextState.value.body !== this.editor.getData());
    }

    // How to use the clickable FAQ function:
    // There should be one <div> with the class name "faq" and it must contain all clickable questions and answers
    // Every question container should have the class name "faq-question"
    // Every answer container should have the class name "faq-answer"
    // Each question container should have a unique id "faq#-question" where "#" is unique and an actual number, like "faq1-question"
    // Each corresponding answer container must have a corresponding unique id "faq#-answer" where "#" is an actual number and matches the question container number, like "faq1-answer"
    handleClickableFAQ() {
        if (this.state.value.body.includes('faq')) {
            const faqContainer = document.getElementsByClassName('faq')[0];
            if (faqContainer) {
                // Add caret icon before every question and check URL to see if we should expand one of the questions
                const faqQuestions = faqContainer.querySelectorAll('.faq-question');
                const currentURL = window.location.href;
                faqQuestions.forEach((faqQuestion) => {
                    // If the URL contains a link to a question, that question should have its answer expanded and we append a caret pointing down
                    if (currentURL.indexOf(faqQuestion.id) !== -1) {
                        document.getElementById(faqQuestion.id.replace('question', 'answer')).classList.add('show');
                        faqQuestion.innerHTML = `<i class="icon icon-caret-down"></i>${faqQuestion.innerHTML}`;
                    // If the URL does not contain a link to a question, we append a caret pointing right
                    } else {
                        faqQuestion.innerHTML = `<i class="icon icon-caret-right"></i>${faqQuestion.innerHTML}`;
                    }
                });
                // One event listener on the 'faq' container handles all click events
                faqContainer.addEventListener('click', (e) => {
                    // Determine which question the user clicked on
                    const target = e.target.closest('.faq-question');
                    if (target) {
                        // Toggle whether corresponding answer is displayed or hidden
                        const infoId = target.id.split('faq')[1].split('-question')[0];
                        const infoElement = document.getElementById(`faq${infoId}-answer`);
                        infoElement.classList.toggle('show');
                        // Toggle direction caret is pointing
                        const iconElement = target.getElementsByTagName('i')[0];
                        if (iconElement.className.indexOf('icon-caret-right') > -1) {
                            iconElement.classList.add('icon-caret-down');
                            iconElement.classList.remove('icon-caret-right');
                        } else {
                            iconElement.classList.remove('icon-caret-down');
                            iconElement.classList.add('icon-caret-right');
                        }
                    }
                });
            }
        }
    }

    setupEditor() {
        require('ckeditor4');
        /* eslint-disable no-undef */
        CKEDITOR.disableAutoInline = true;
        this.editor = CKEDITOR.inline(this.domNode, {
            /* eslint-enable no-undef */
            language: 'en',
            toolbar: [
                { name: 'basicstyles', groups: ['basicstyles', 'cleanup'], items: ['Bold', 'Italic', 'Underline', 'Strike', '-', 'RemoveFormat'] },
                { name: 'styles', items: ['Format'] },
                { name: 'paragraph', groups: ['list', 'indent', 'align'], items: ['NumberedList', 'BulletedList'] },
                { name: 'links', items: ['Link', 'Unlink', 'Anchor'] },
                { name: 'undo', groups: ['undo'], items: ['Undo', 'Redo'] },
                { name: 'document', groups: ['mode'], items: ['Source'] },
            ],
            format_tags: 'p;h1;h2;h3;h4;h5;h6;pre;code;cite',
            format_code: { name: 'Inline Code', element: 'code' },
            format_cite: { name: 'Citation', element: 'cite' },
            allowedContent: true,
        });
        this.editor.on('change', () => {
            this.state.value.body = this.editor.getData();
            this.setState((state) => ({ ...state }));
            this.props.onChange(this.state.value);
        });
    }

    render() {
        return (
            <div contentEditable={this.context.editable} dangerouslySetInnerHTML={{ __html: this.state.value.body }} ref={(comp) => { this.domNode = comp; }} />
        );
    }
}

RichTextBlockView.propTypes = {
    onChange: PropTypes.func.isRequired,
    value: PropTypes.object,
};

RichTextBlockView.defaultProps = {
    value: null,
};

RichTextBlockView.contextTypes = {
    editable: PropTypes.bool,
};


globals.blocks.register({
    label: 'rich text block',
    icon: 'icon icon-file-text',
    schema: {
        type: 'object',
        properties: {
            body: {
                title: 'HTML Source',
                type: 'string',
                formInput: <textarea rows="10" />,
            },
            className: {
                title: 'CSS Class',
                type: 'string',
            },
        },
    },
    view: RichTextBlockView,
    initial: {
        body: '<p>This is a new block.</p>',
    },
}, 'richtextblock');
