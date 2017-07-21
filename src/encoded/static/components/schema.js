import React from 'react';
import PropTypes from 'prop-types';
import marked from 'marked';
import { Param, FetchedData } from './fetched';
import * as globals from './globals';


const Markdown = (props) => {
    const html = marked(props.source, { sanitize: true });
    return <div dangerouslySetInnerHTML={{ __html: html }} />;
};

Markdown.propTypes = {
    source: PropTypes.string,
};

Markdown.defaultProps = {
    source: '',
};


const ChangeLog = props => (
    <section className="view-detail panel">
        <div className="container">
            <Markdown source={props.source} />
        </div>
    </section>
);

ChangeLog.propTypes = {
    source: PropTypes.string,
};

ChangeLog.defaultProps = {
    source: '',
};

class DisplayText extends React.Component {
    render() {
        const { dataObject } = this.props;
        // const dataArray = [];
        // const values = [];
        // const titles = [];
        const date = Object.keys(dataObject).map((term) => {
            const labels = term;
            return labels;
        });
        return (
            <div>
                {date.map((item, index) => <div key={index}>{item}</div>)}
            </div>
        );
    }
}

DisplayText.propTypes = {
    dataObject: PropTypes.object,
};

DisplayText.defaultProps = {
    dataObject: {},
};

const SchemaPage = (props) => {
    const context = props.context;
    const itemClass = globals.itemClass(context);
    const title = context.title;
    const changelog = context.changelog;
    return (
        <div className={itemClass}>
            <header className="row">
                <div className="col-sm-12">
                    <h2>{title}</h2>
                </div>
            </header>
            {typeof context.description === 'string' ? <p className="description">{context.description}</p> : null}
            <section className="view-detail panel">
                <div className="container">
                    <DisplayText dataObject={context} />
                    <pre>{JSON.stringify(context, null, 4)}</pre>
                </div>
            </section>
            {changelog && <FetchedData>
                <Param name="source" url={changelog} type="text" />
                <ChangeLog />
            </FetchedData>}
        </div>
    );
};

SchemaPage.propTypes = {
    context: PropTypes.object.isRequired,
};

globals.contentViews.register(SchemaPage, 'JSONSchema');
