import React from 'react';
import cloneWithProps from 'react/lib/cloneWithProps';


const Panel = React.createClass({
    propTypes: {
        addClasses: React.PropTypes.string, // Classes to add to outer panel div
        noDefaultClasses: React.PropTypes.bool, // T to not include default panel classes
        children: React.PropTypes.node,
    },

    render: function () {
        const { addClasses, noDefaultClasses, ...other } = this.props;

        return (
            <div {...other} className={(noDefaultClasses ? '' : 'panel panel-default') + (addClasses ? ` ${addClasses}` : '')}>
                {this.props.children}
            </div>
        );
    },
});


const PanelBody = React.createClass({
    propTypes: {
        addClasses: React.PropTypes.string, // Classes to add to outer panel div
        children: React.PropTypes.node,
    },

    render: function () {
        return (
            <div className={`panel-body ${this.props.addClasses ? ` ${this.props.addClasses}` : ''}`}>
                {this.props.children}
            </div>
        );
    },
});


const PanelHeading = React.createClass({
    propTypes: {
        addClasses: React.PropTypes.string, // Classes to add to outer panel div
        children: React.PropTypes.node,
    },

    render: function () {
        return (
            <div className={`panel-heading ${this.props.addClasses ? ` ${this.props.addClasses}` : ''}`}>
                {this.props.children}
            </div>
        );
    },
});


const PanelFooter = React.createClass({
    propTypes: {
        addClasses: React.PropTypes.string, // Classes to add to outer panel div
        children: React.PropTypes.node,
    },

    render: function () {
        return (
            <div className={`panel-footer${this.props.addClasses ? ` ${this.props.addClasses}` : ''}`}>
                {this.props.children}
            </div>
        );
    },
});


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

const TabPanelPane = React.createClass({
    propTypes: {
        id: React.PropTypes.string.isRequired, // ID of the pane; not passed explicitly -- comes from `key` of <TabPanelPane>
        active: React.PropTypes.bool, // True if this panel is the active one
        children: React.PropTypes.node,
    },

    render: function () {
        const { id, active, tabFlange } = this.props;
        return (
            <div role="tabpanel" className={`tab-pane${active ? ' active' : ''}`} id={id}>
                {active ? <div>{this.props.children}</div> : null}
            </div>
        );
    },
});


const TabPanel = React.createClass({
    propTypes: {
        tabs: React.PropTypes.object.isRequired, // Object with tab=>pane specifications
        selectedTab: React.PropTypes.string, // key of tab to select (must provide handleTabClick) too.
        addClasses: React.PropTypes.string, // Classes to add to navigation <ul>
        moreComponents: React.PropTypes.object, // Other components to render in the tab bar
        moreComponentsClasses: React.PropTypes.string, // Classes to add to moreComponents wrapper <div>
        tabFlange: React.PropTypes.bool, // True to show a small full-width strip under active tab
        decoration: React.PropTypes.object, // Component to render in the tab bar
        decorationClasses: React.PropTypes.string, // CSS classes to wrap decoration in
        handleTabClick: React.PropTypes.func, // If selectedTab is provided, then parent must keep track of it
        children: React.PropTypes.node,
    },

    getInitialState: function () {
        return { currentTab: this.props.selectedTab ? this.props.selectedTab : '' };
    },

    // Handle a click on a tab
    handleClick: function (tab) {
        if (this.props.handleTabClick) {
            this.props.handleTabClick(tab);  // must keep parent aware of selectedTab.
        }
        if (tab !== this.state.currentTab) {
            this.setState({ currentTab: tab });
        }
    },

    render: function () {
        const { tabs, addClasses, moreComponents, moreComponentsClasses, tabFlange, decoration, decorationClasses } = this.props;
        let children = [];
        let firstPaneIndex = -1; // React.Children.map index of first <TabPanelPane> component

        // We expect to find <TabPanelPane> child elements inside <TabPanel>. For any we find, get
        // the React `key` value and copy it to an `id` value that we add to each child component.
        // That lets each child get an HTML ID matching `key` without having to pass both a key and
        // id with the same value. We also set the `active` property in the TabPanelPane component
        // here too so that each pane knows whether it's the active one or not. ### React14
        if (this.props.children) {
            children = React.Children.map(this.props.children, (child, i) => {
                if (child.type === TabPanelPane.type) {
                    firstPaneIndex = firstPaneIndex === -1 ? i : firstPaneIndex;

                    // Replace the existing child <TabPanelPane> component
                    return cloneWithProps(child, { id: child.key, active: this.props.selectedTab ? this.props.selectedTab === child.key : this.state.currentTab ? this.state.currentTab === child.key : firstPaneIndex === i });
                }
                return child;
            });
        }

        return (
            <div>
                <div className="tab-nav">
                    <ul className={`nav nav-tabs${addClasses ? ` ${addClasses}` : ''}`} role="tablist">
                        {Object.keys(tabs).map((tab, i) => {
                            const currentTab = this.props.selectedTab ? this.props.selectedTab : this.state.currentTab ? this.state.currentTab : i === 0 ? tab : '';

                            return (
                                <li key={tab} role="presentation" aria-controls={tab} className={currentTab === tab ? 'active' : ''}>
                                    <TabItem tab={tab} handleClick={this.handleClick}>
                                        {tabs[tab]}
                                    </TabItem>
                                </li>
                            );
                        })}
                        {moreComponents ? <div className={moreComponentsClasses}>{moreComponents}</div> : null}
                    </ul>
                    {decoration ? <div className={decorationClasses}>{decoration}</div> : null}
                    {tabFlange ? <div className="tab-flange" /> : null}
                </div>
                <div className="tab-content">
                    {children}
                </div>
            </div>
        );
    },
});


const TabItem = React.createClass({
    propTypes: {
        tab: React.PropTypes.string, // Text of tab
        handleClick: React.PropTypes.func, // Handle a click on the link
        children: React.PropTypes.node,
    },

    clickHandler: function () {
        this.props.handleClick(this.props.tab);
    },

    render: function () {
        const tab = this.props.tab;

        return (
            <a href={`#${tab}`} ref={tab} onClick={this.clickHandler} data-trigger="tab" aria-controls={tab} role="tab" data-toggle="tab">
                {this.props.children}
            </a>
        );
    },
});


export {
    Panel,
    PanelBody,
    PanelHeading,
    PanelFooter,
    TabPanel,
    TabPanelPane
};
