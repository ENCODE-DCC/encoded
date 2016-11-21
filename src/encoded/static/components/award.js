import React from 'react';
import { Panel, PanelHeading, PanelBody } from '../libs/bootstrap/panel';
import globals from './globals';
import { ProjectBadge } from './image';


const Award = React.createClass({
    propTypes: {
        context: React.PropTypes.object, // Award object being rendered
    },

    render: function () {
        const { context } = this.props;

        return (
            <div className={globals.itemClass(context, 'view-item')}>
                <header className="row">
                    <div className="col-sm-12">
                        <h2>{context.title || context.name}</h2>
                    </div>
                </header>

                <Panel>
                    <PanelHeading>
                        <h4>Description</h4>
                        <ProjectBadge award={context} addClasses="badge-heading" />
                    </PanelHeading>
                    <PanelBody>
                        <div className="two-column-long-text two-column-long-text--gap">
                            {context.description ? <p>{context.description}</p> : <p className="browser-error">Award has no description</p>}
                        </div>
                        {context.pi && context.pi.lab ?
                            <dl className="key-value">
                                <div data-test="pi">
                                    <dt>Main PI contact</dt>
                                    <dd>{context.pi.lab.title}</dd>
                                </div>
                            </dl>
                        : null}
                    </PanelBody>
                </Panel>
            </div>
        );
    }
});

globals.content_views.register(Award, 'Award');
