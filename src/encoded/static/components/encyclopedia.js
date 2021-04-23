import PropTypes from 'prop-types';
import url from 'url';
import { Panel, PanelBody } from '../libs/ui/panel';
import { ResultTable } from './search';
import * as globals from './globals';

const Encyclopedia = (props, context) => {
    const searchBase = url.parse(context.location_href).search || '';

    const currentRegion = (assembly, region) => {
        let lastRegion = {};
        if (assembly && region) {
            lastRegion = {
                assembly,
                region,
            };
        }
        return lastRegion;
    };

    return (
        <div className="layout">
            <div className="layout__block layout__block--100">
                <div className="block encyclopedia" data-pos="0,0,0">
                    <h1>{props.context.title}</h1>
                    <Panel>
                        <PanelBody>
                            <ResultTable
                                {...props}
                                searchBase={searchBase}
                                onChange={context.navigate}
                                currentRegion={currentRegion}
                                hideDocType
                            />
                        </PanelBody>
                    </Panel>
                </div>
            </div>
        </div>
    );
};

Encyclopedia.propTypes = {
    context: PropTypes.object.isRequired,
};

Encyclopedia.contextTypes = {
    location_href: PropTypes.string,
    navigate: PropTypes.func,
    fetch: PropTypes.func,
};

globals.contentViews.register(Encyclopedia, 'Encyclopedia');
