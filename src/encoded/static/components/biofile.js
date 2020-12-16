import React from 'react';

import { Panel, PanelBody, PanelHeading } from '../libs/ui/panel';
import * as globals from './globals';
import { Breadcrumbs } from './navigation';
import Status from './status';
import CollapsiblePanel from './collapsiblePanel';


class Biofile extends React.Component {
    constructor(props) {
        super(props);


    }
    render() {
        const context = this.props.context;
        const itemClass = globals.itemClass(context, 'view-item');
        // Set up breadcrumbs
        const crumbs = [
            { id: 'Biofiles' },
            { id: <i>{context.accession}</i> },
        ];
        const crumbsReleased = (context.status === 'released');


        return (
            <div className={itemClass}>
                <header className="row">
                    <div className="col-sm-12">
                        <Breadcrumbs root="/search/?type=Biofile" crumbs={crumbs} crumbsReleased={crumbsReleased} />
                        <h2>{context.accession}</h2>

                    </div>

                </header>
                <Panel>
                    <PanelHeading>
                        <h4>File Information</h4>
                    </PanelHeading>
                    <PanelBody>
                    <dl className="key-value">
                        <div data-test="status">
                            <dt>Status</dt>
                            <dd><Status item={context} inline /></dd>
                        </div>
                        <div data-test="file_format">
                            <dt>File format</dt>
                            <dd>{context.file_format}</dd>
                        </div>
                        <div data-test="output_type">
                            <dt>Output type</dt>
                            <dd>{context.output_type}</dd>
                        </div>

                        {/* <div data-test="biolibrary">
                            <dt>Library</dt>
                            <dd>{context.biolibrary.accession}</dd>
                        </div> */}

                        {/* <div data-test="biospecimen">
                            <dt>Biospecimen</dt>
                            <dd><a href={context.biolibrary.biospecimen}>{context.biolibrary.biospecimen.split("/")[2]}</a></dd>
                        </div> */}

                        <div data-test="md5sum">
                            <dt>MD5sum</dt>
                            <dd>{context.md5sum}</dd>
                        </div>

                        {/* {context.biolibrary.biological_replicate_number && <div data-test="biological_replicate_number">
                            <dt>Biological replicate number</dt>
                            <dd>{context.biolibrary.biological_replicate_number}</dd>
                        </div>}
                        {context.biolibrary.technical_replicate_number && <div data-test="technical_replicate_number">
                            <dt>Technical replicate number</dt>
                            <dd>{context.biolibrary.technical_replicate_number}</dd>
                        </div>} */}
                        {context.sequencing_replicate_number && <div data-test="sequencing_replicate_number">
                            <dt>Sequencing replicate number</dt>
                            <dd>{context.sequencing_replicate_number}</dd>
                        </div>}
                        {context.content_md5sum && <div data-test="content_md5sum">
                            <dt>Content MD5sum</dt>
                            <dd>{context.content_md5sum}</dd>
                        </div>}
                        {context.read_count && <div data-test="read_count">
                            <dt>Read count</dt>
                            <dd>{context.read_count}</dd>
                        </div>}
                        {context.read_length && <div data-test="read_length">
                            <dt>Read length</dt>
                            <dd>{context.read_length}</dd>
                        </div>}
                        {context.file_size && <div data-test="file_size">
                            <dt>File size</dt>
                            <dd>{context.file_size}</dd>
                        </div>}
                    </dl>
                    </PanelBody>
                </Panel>



            </div>
        )
    }
}

globals.contentViews.register(Biofile, 'Biofile');
