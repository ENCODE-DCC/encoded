'use strict';
var React = require('react');
var cloneWithProps = require('react/lib/cloneWithProps');


var Panel = module.exports.Panel = React.createClass({
    propTypes: {
        addClasses: React.PropTypes.string // Classes to add to outer panel div
    },

    render: function() {
        return (
            <div className={'panel panel-default' + (this.props.addClasses ? ' ' + this.props.addClasses : '')}>
                {this.props.children}
            </div>
        );
    }
});


var PanelBody = module.exports.PanelBody = React.createClass({
    propTypes: {
        addClasses: React.PropTypes.string // Classes to add to outer panel div
    },

    render: function() {
        return (
            <div className={'panel-body' + (this.props.addClasses ? ' ' + this.props.addClasses : '')}>
                {this.props.children}
            </div>
        );
    }
});


var PanelHeading = module.exports.PanelHeading = React.createClass({
    propTypes: {
        addClasses: React.PropTypes.string // Classes to add to outer panel div
    },

    render: function() {
        return (
            <div className={'panel-heading' + (this.props.addClasses ? ' ' + this.props.addClasses : '')}>
                {this.props.children}
            </div>
        );
    }
});


var TabPanel = module.exports.TabPanel = React.createClass({
    propTypes: {
        tabs: React.PropTypes.object.isRequired // Object with tab=>pane specifications
    },

    getInitialState: function() {
        return {currentTab: ''}
    },

    handleClick: function(tab) {
        if (tab !== this.state.currentTab) {
            this.setState({currentTab: tab});
        }
    },

    render: function() {
        var children = [];
        var tabs = this.props.tabs;

        // We expect to find <TabPanelPane> child elements inside <TabPanel>. For any we find, get the React `key` value and
        // copy it to an `id` value that we add to each child component. That lets each child get an HTML ID matching `key`
        // without having to pass both a key and id with the same value.
        if (this.props.children) {
            children = React.Children.map(this.props.children, (child, i) => {
                console.log('IND: ' + i);
                if (child.type === TabPanelPane.type) {
                    return cloneWithProps(child, {id: child.key, active: this.state.currentTab ? this.state.currentTab === child.key : i === 0});
                }
                return child;
            });
        }

        return (
            <div>
                <ul className="nav nav-tabs" role="tablist">
                    {Object.keys(tabs).map((tab, i) => {
                        var currentTab = (i === 0 && this.state.currentTab === '') ? tab : this.state.currentTab;

                        return (
                            <li key={tab} role="presentation" aria-controls={tab} className={currentTab === tab ? 'active' : ''}>
                                <a href={'#' + tab} ref={tab} onClick={this.handleClick.bind(this, tab)} data-trigger="tab" aria-controls={tab} role="tab" data-toggle="tab">{tabs[tab]}</a>
                            </li>
                        );
                    })}
                </ul>
                <div className="tab-content">
                    {children}
                </div>
            </div>
        );
    }
});


var TabPanelPane = module.exports.TabPanelPane = React.createClass({
    propTypes: {
        id: React.PropTypes.string, // ID of the pane <div> to correspond to the tab navigation <a> aria-controls value
        active: React.PropTypes.bool // True if this panel is the active one
    },

    render: function() {
        return (
            <div role="tabpanel" className={'tab-pane' + (this.props.active ? ' active' : '')} id={this.props.id}>
                {this.props.children}
            </div>
        );
    }
});
