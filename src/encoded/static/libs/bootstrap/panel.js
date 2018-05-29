import React from 'react';
import PropTypes from 'prop-types';


/* eslint-disable react/prefer-stateless-function */
class Panel extends React.Component {
    render() {
        const { addClasses, noDefaultClasses, ...other } = this.props;

        return (
            <div {...other} className={(noDefaultClasses ? '' : 'panel panel-default') + (addClasses ? ` ${addClasses}` : '')}>
                {this.props.children}
            </div>
        );
    }
}
/* eslint-enable react/prefer-stateless-function */

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


/* eslint-disable react/prefer-stateless-function */
class PanelBody extends React.Component {
    render() {
        return (
            <div className={`panel-body${this.props.addClasses ? ` ${this.props.addClasses}` : ''}`}>
                {this.props.children}
            </div>
        );
    }
}
/* eslint-enable react/prefer-stateless-function */

PanelBody.propTypes = {
    addClasses: PropTypes.string, // Classes to add to outer panel div
    children: PropTypes.node,
};

PanelBody.defaultProps = {
    addClasses: '',
    children: null,
};


/* eslint-disable react/prefer-stateless-function */
class PanelHeading extends React.Component {
    render() {
        return (
            <div className={`panel-heading${this.props.addClasses ? ` ${this.props.addClasses}` : ''}`}>
                {this.props.children}
            </div>
        );
    }
}
/* eslint-enable react/prefer-stateless-function */

PanelHeading.propTypes = {
    addClasses: PropTypes.string, // Classes to add to outer panel div
    children: PropTypes.node,
};

PanelHeading.defaultProps = {
    addClasses: '',
    children: null,
};

const PanelFooter = props => (
    <div className={`panel-footer${props.addClasses ? ` ${props.addClasses}` : ''}`}>
        {props.children}
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

const TabPanelPane = (props) => {
    const { id, active } = props;
    return (
        <div role="tabpanel" className={`tab-pane${active ? ' active' : ''}`} id={id}>
            {active ? <div>{props.children}</div> : null}
        </div>
    );
};

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
            currentTab: props.selectedTab ? props.selectedTab : '',
        };

        this.handleClick = this.handleClick.bind(this);
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

    render() {
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
                if (child.type === TabPanelPane) {
                    firstPaneIndex = firstPaneIndex === -1 ? i : firstPaneIndex;

                    // Replace the existing child <TabPanelPane> component
                    return React.cloneElement(child, { id: child.key, active: this.props.selectedTab ? this.props.selectedTab === child.key : this.state.currentTab ? this.state.currentTab === child.key : firstPaneIndex === i });
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
    }
}

TabPanel.propTypes = {
    tabs: PropTypes.object.isRequired, // Object with tab=>pane specifications
    selectedTab: PropTypes.string, // key of tab to select (must provide handleTabClick) too.
    addClasses: PropTypes.string, // Classes to add to navigation <ul>
    moreComponents: PropTypes.object, // Other components to render in the tab bar
    moreComponentsClasses: PropTypes.string, // Classes to add to moreComponents wrapper <div>
    tabFlange: PropTypes.bool, // True to show a small full-width strip under active tab
    decoration: PropTypes.object, // Component to render in the tab bar
    decorationClasses: PropTypes.string, // CSS classes to wrap decoration in
    handleTabClick: PropTypes.func, // If selectedTab is provided, then parent must keep track of it
    children: PropTypes.node,
};

TabPanel.defaultProps = {
    selectedTab: '',
    addClasses: '',
    moreComponents: null,
    moreComponentsClasses: '',
    tabFlange: false,
    decoration: null,
    decorationClasses: '',
    handleTabClick: null,
    children: null,
};


class TabItem extends React.Component {
    constructor(props) {
        super(props);

        this.clickHandler = this.clickHandler.bind(this);
    }

    clickHandler() {
        this.props.handleClick(this.props.tab);
    }

    render() {
        const tab = this.props.tab;

        return (
            <a href={`#${tab}`} ref={tab} onClick={this.clickHandler} data-trigger="tab" aria-controls={tab} role="tab" data-toggle="tab">
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
