import React from 'react';
import PropTypes from 'prop-types';
import _ from 'underscore';
import * as globals from './globals';

const GlossaryTerm = (props) => {
    const { term, definition } = props.glossaryEntry;
    return (
        <div className="glossary-element">
            <h4 className="glossary-term">{term}</h4>
            <p className="glossary-definition">{definition}</p>
            {props.glossaryEntry.file_formats ?
                <p className="glossary-extra-info">
                    <span className="glossary-label">File formats: </span>
                    <span className="glossary-field">{props.glossaryEntry.file_formats}</span>
                </p>
            : null}
            {props.glossaryEntry.additional_information ?
                <p className="glossary-extra-info">
                    <span className="glossary-label">Additional information: </span>
                    {props.glossaryEntry.additional_information.map((href, hrefIndex) => (
                        <span className="glossary-field" key={href.url}>
                            <a href={href.url}>{href.title}</a>
                            <span>{((props.glossaryEntry.additional_information.length > 1) && hrefIndex < (props.glossaryEntry.additional_information.length - 1)) ? ', ' : ''}</span>
                        </span>
                    ))}
                </p>
            : null}
        </div>
    );
};

GlossaryTerm.propTypes = {
    glossaryEntry: PropTypes.object.isRequired,
};

// Optional links appended to section headers
const sectionHeaderLinks = {
    'Target categories': {
        link: 'https://www.encodeproject.org/target-categorization/',
        text: 'Category assignment details',
    },
};

const Glossary = (props) => {
    const { context } = props;
    const glossary = require('./glossary/glossary.json');
    const glossaryBySection = _(glossary).groupBy((entry) => entry.section || 'General terms');

    return (
        <div className="layout">
            <div className="layout__block layout__block--100">
                <div className="richtextblock block" data-pos="0,0,0">
                    <center>
                        <h1>{context.title}</h1>
                    </center>
                    <h4 className="directory">
                        {Object.keys(glossaryBySection).map((section, sectionIdx) => (
                            <React.Fragment key={`${section}-link`}>
                                <a href={`#${section.toLowerCase().split(' ').join('-')}`}>{section}</a>
                                {(sectionIdx < Object.keys(glossaryBySection).length - 1) ?
                                    <span> | </span>
                                : null}
                            </React.Fragment>
                        ))}
                    </h4>
                    {Object.keys(glossaryBySection).map((section) => (
                        <div className="glossary-block" key={section} id={section}>
                            <h2 id={`${section.toLowerCase().split(' ').join('-')}`}>
                                {section}
                                {sectionHeaderLinks[section] ?
                                    <span className="section-header-link"><a href={sectionHeaderLinks[section].link}>{sectionHeaderLinks[section].text}</a></span>
                                : null}
                            </h2>
                            {(section === undefined) ?
                                <h4>{section}</h4>
                            : null}
                            {glossaryBySection[section]
                                .sort((a, b) => {
                                    if (a.term.toLowerCase() < b.term.toLowerCase()) { return -1; }
                                    if (a.term.toLowerCase() > b.term.toLowerCase()) { return 1; }
                                    return 0;
                                })
                                .map((entry) => <GlossaryTerm glossaryEntry={entry} key={entry.term} id={entry.term} />)
                            }
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

Glossary.propTypes = {
    context: PropTypes.object.isRequired,
};

globals.contentViews.register(Glossary, 'Glossary');
