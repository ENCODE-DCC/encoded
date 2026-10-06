import { Panel, PanelBody } from '../libs/ui/panel';
import * as globals from './globals';

const RegionSearch = () => (
    <div className="layout">
        <div className="layout__block layout__block--100">
            <div className="block series-search">
                <div className="encyclopedia-info-wrapper">
                    <div className="badge-container">
                        <h1>Region Search</h1>
                    </div>
                </div>

                <Panel>
                    <PanelBody>
                        Disabled due to lack of funds.
                    </PanelBody>
                </Panel>
            </div>
        </div>
    </div>
);

globals.contentViews.register(RegionSearch, 'region-search');
