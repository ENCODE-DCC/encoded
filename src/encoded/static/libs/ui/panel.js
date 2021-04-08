import React from 'react';
import PropTypes from 'prop-types';


const Panel = ({ addClasses, noDefaultClasses, children, ...other }) => (
    <div {...other} className={(noDefaultClasses ? '' : 'panel panel-default') + (addClasses ? ` ${addClasses}` : '')}>
        {children}
    </div>
);

Panel.propTypes = {
    addClasses: PropTypes.string, // Classes to add to outer panel div
    noDefaultClasses: PropTypes.bool, // T to not include default panel classes
    children: PropTypes.node,
};

Panel.defaultProps = {
    addClasses: '', // Classes to add to outer panel div
    noDefaultClasses: false, // T to not include default panel classes
    children: null,
};


const PanelBody = ({ addClasses, children }) => (
    <div className={`panel-body${addClasses ? ` ${addClasses}` : ''}`}>
        {children}
    </div>
);

PanelBody.propTypes = {
    addClasses: PropTypes.string, // Classes to add to outer panel div
    children: PropTypes.node,
};

PanelBody.defaultProps = {
    addClasses: '',
    children: null,
};


const PanelHeading = ({ addClasses, children }) => (
    <div className={`panel-heading${addClasses ? ` ${addClasses}` : ''}`}>
        {children}
    </div>
);

PanelHeading.propTypes = {
    addClasses: PropTypes.string, // Classes to add to outer panel div
    children: PropTypes.node,
};

PanelHeading.defaultProps = {
    addClasses: '',
    children: null,
};

const PanelFooter = ({ addClasses, children }) => (
    <div className={`panel-footer${addClasses ? ` ${addClasses}` : ''}`}>
        {children}
    </div>
);

PanelFooter.propTypes = {
    addClasses: PropTypes.string, // Classes to add to outer panel div
    children: PropTypes.node,
};

PanelFooter.defaultProps = {
    addClasses: '',
    children: null,
};


// <TabPanel> components have tabs that select between panes, and so the main child components of
// <TabPanel> must be <TabPanelPane> components. The children of <TabPanelPane> components are the
// content you want to have rendered within a tab's pane. <TabPanel> takes a required `tabs`
// parameter -- an object that maps an identifier to a tab title. The identifier has to map to a
// child <TabPanelPane> `key` property. Here's an example tabbed panel.
//
// <TabPanel tabs={{panel1: 'Panel 1', panel2: 'Panel 2', panel3: 'Panel 3'}}>
//     <TabPanelPane key="panel1">
//         <div>Content for panel 1</div>
//     </TabPanelPane>
//     <TabPanelPane key="panel2">
//         <div>Content for panel 2</div>
//     </TabPanelPane>
//     <TabPanelPane key="panel3">
//         <div>Content for panel 3</div>
//     </TabPanelPane>
// </TabPanel>
//
// Note that <TabPanelPane> takes an `id` property, not a `key` property because components can't
// receive those. <TabPanel> copies the `key` property to an `id` property in any child <TabPanel>
// components so that <TabPanel> can see it.

const TabPanelPane = ({ id, active, children }) => (
    <div role="tabpanel" className={`tab-pane${active ? ' active' : ''}`} id={id}>
        {active ? <div>{children}</div> : null}
    </div>
);

TabPanelPane.propTypes = {
    id: PropTypes.string, // ID of the pane; not passed explicitly -- comes from `key` of <TabPanelPane>
    active: PropTypes.bool, // True if this panel is the active one
    children: PropTypes.node,
};

TabPanelPane.defaultProps = {
    id: '', // Actually required, but added within cloneElement, so requiring triggers warning
    active: false,
    children: null,
};


class TabPanel extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            currentTab: props.selectedTab || '',
        };

        this.handleClick = this.handleClick.bind(this);
        this.getCurrentTab = this.getCurrentTab.bind(this);
    }

    // Handle a click on a tab
    handleClick(tab) {
        if (this.props.handleTabClick) {
            this.props.handleTabClick(tab); // must keep parent aware of selectedTab.
        }
        if (tab !== this.state.currentTab) {
            this.setState({ currentTab: tab });
        }
    }

    /**
     * Get the currently selected tab from `selectedTab`, or the component state `currentTab`, or
     * just the first tab if neither of those is specified.
     *
     * @return {string} Key of selected tab
     */
    getCurrentTab() {
        const { selectedTab } = this.props;
        if (selectedTab === null || selectedTab) {
            return selectedTab;
        }
        if (this.state.currentTab) {
            return this.state.currentTab;
        }
        return Object.keys(this.props.tabs)[0];
    }

    render() {
        const { tabs, tabDisplay, tabPanelCss, tabCss, navCss, moreComponents, moreComponentsClasses, tabFlange, decoration, decorationClasses } = this.props;
        let children = [];
        let firstPaneIndex = -1; // React.Children.map index of first <TabPanelPane> component

        // We expect to find <TabPanelPane> child elements inside <TabPanel>. For any we find, get
        // the React `key` value and copy it to an `id` value that we add to each child component.
        // That lets each child get an HTML ID matching `key` without having to pass both a key and
        // id with the same value. We also set the `active` property in the TabPanelPane component
        // here too so that each pane knows whether it's the active one or not. ### React14
        if (this.props.children) {
            children = React.Children.map(this.props.children, (child, i) => {
                if (child !== null && child.type === TabPanelPane) {
                    firstPaneIndex = firstPaneIndex === -1 ? i : firstPaneIndex;

                    // Replace the existing child <TabPanelPane> component
                    const active = this.getCurrentTab() === child.key;
                    return React.cloneElement(child, { id: child.key, active });
                }
                return child;
            });
        }

        return (
            <div className={tabPanelCss}>
                <div className={`tab-nav tab-nav-${this.getCurrentTab() ? this.getCurrentTab().replace(/\s/g, '') : ''}`}>
                    <ul className={`nav-tabs${navCss ? ` ${navCss}` : ''}`} role="tablist">
                        {Object.keys(tabs).map((tab) => (
                            <li key={tab} role="presentation" aria-controls={tab} className={`${tab.replace(/\s/g, '')}-tab ${tabCss} ${this.getCurrentTab() === tab ? 'active' : ''}`}>
                                <TabItem tab={tab} handleClick={this.handleClick}>
                                    {tabDisplay[tab] || tabs[tab]}
                                </TabItem>
                            </li>
                        ))}
                        {moreComponents ? <div className={moreComponentsClasses}>{moreComponents}</div> : null}
                    </ul>
                    {decoration ? <div className={decorationClasses}>{decoration}</div> : null}
                    {tabFlange ? <div className="tab-flange" /> : null}
                    <div className="tab-border" />
                </div>
                <div className="tab-content">
                    {children}
                </div>
            </div>
        );
    }
}

TabPanel.propTypes = {
    /** Object with tab=>pane specifications */
    tabs: PropTypes.object.isRequired,
    /** Object with optional tab-rendering components */
    tabDisplay: PropTypes.object,
    /** CSS class for the entire tab panel <div> */
    tabPanelCss: PropTypes.string,
    /** CSS class for each tab */
    tabCss: PropTypes.string,
    /** key of tab to select (must provide handleTabClick) too; null for no selection */
    selectedTab: PropTypes.string,
    /** Classes to add to navigation <ul> */
    navCss: PropTypes.string,
    /** Other components to render in the tab bar */
    moreComponents: PropTypes.object,
    /** Classes to add to moreComponents wrapper <div> */
    moreComponentsClasses: PropTypes.string,
    /** True to show a small full-width strip under active tab */
    tabFlange: PropTypes.bool,
    /** Component to render in the tab bar */
    decoration: PropTypes.object,
    /** CSS classes to wrap decoration in */
    decorationClasses: PropTypes.string,
    /** If selectedTab is provided, then parent must keep track of it */
    handleTabClick: PropTypes.func,
    children: PropTypes.node,
};

TabPanel.defaultProps = {
    tabDisplay: {},
    selectedTab: '',
    tabPanelCss: null,
    tabCss: null,
    navCss: null,
    moreComponents: null,
    moreComponentsClasses: '',
    tabFlange: false,
    decoration: null,
    decorationClasses: null,
    handleTabClick: null,
    children: null,
};


// Check to see if child of tab has "disabled" class
const checkIfDisabled = (input) => input.children && input.children.props && input.children.props.className && input.children.props.className.includes('disabled');


class TabItem extends React.Component {
    constructor(props) {
        super(props);

        this.clickHandler = this.clickHandler.bind(this);
    }

    clickHandler() {
        if (!checkIfDisabled(this.props)) {
            this.props.handleClick(this.props.tab);
        }
    }

    render() {
        const { tab } = this.props;
        const isDisabled = checkIfDisabled(this.props);
        return (
            <a href={`#${tab}`} ref={tab} onClick={this.clickHandler} data-trigger="tab" aria-controls={tab} role="tab" data-toggle="tab" disabled={isDisabled}>
                {this.props.children}
            </a>
        );
    }
}

TabItem.propTypes = {
    tab: PropTypes.string.isRequired, // Text of tab
    handleClick: PropTypes.func, // Handle a click on the link
    children: PropTypes.node,
};

TabItem.defaultProps = {
    handleClick: null,
    children: null,
};


export {
    Panel,
    PanelBody,
    PanelHeading,
    PanelFooter,
    TabPanel,
    TabPanelPane,
};
