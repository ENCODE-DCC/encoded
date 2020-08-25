import React from 'react';
import PropTypes from 'prop-types';
import * as globals from './globals';

const Glossary = (props) => {
    const { context } = props;
    const glossary = require('./glossary/glossary.json');

    return (
        <div className="layout">
            <div className="layout__block layout__block--100">
                <div className="ricktextblock block" data-pos="0,0,0">
                    <center>
                        <h1>{context.title}</h1>
                    </center>
                    {glossary.map(g => (
                        <div key={g.term} className="glossary-element">
                            <h4 className="glossary-term">{g.term}</h4>
                            <p className="glossary-definition">{g.definition}</p>
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
