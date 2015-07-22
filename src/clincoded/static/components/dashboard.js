'use strict';
var React = require('react');
var _ = require('underscore');
var moment = require('moment');
var globals = require('./globals');
var fetched = require('./fetched');
var form = require('../libs/bootstrap/form');
var panel = require('../libs/bootstrap/panel');
var parseAndLogError = require('./mixins').parseAndLogError;
var RestMixin = require('./rest').RestMixin;

var Form = form.Form;
var FormMixin = form.FormMixin;
var Input = form.Input;
var Panel = panel.Panel;
var external_url_map = globals.external_url_map;

var Dashboard = React.createClass({
    mixins: [RestMixin],

    getInitialState: function() {
        return {
            userName: '',
            userStatus: '',
            lastLogin: '',
            recentHistory: [],
            gdmList: []
        };
    },

    setUserData: function(props) {
        this.setState({
            userName: props['first_name'],
            userStatus: props['groups'][0].charAt(0).toUpperCase() + props['groups'][0].substring(1),
            lastLogin: ''
        });
    },

    // Retrieve the GDMs and other objects related to user via search
    getData: function(userid) {
        this.getRestDatas(['/search/?type=gdm&limit=10&owner=' + userid,'/search/?limit=10&owner=' + userid], [function() {}, function() {}]).then(data => {
            // Search objects successfully retrieved; clean up results
            // GDM List panel results
            var tempGdmList = [], tempRecentHistory = [];
            for (var i = 0; i < data[0]['@graph'].length; i++) {
                var temp = data[0]['@graph'][i];
                tempGdmList.push({
                    url: temp['uuid'],
                    displayName: temp['gene']['symbol'] + "-" + temp['disease']['term'] + " (" + temp['modeInheritance'] + ")",
                    status: temp['status'],
                    dateTime: temp['dateTime']
                });
            }
            // Recent History panel results
            for (var i = 0; i < data[1]['@graph'].length; i++) {
                var temp = data[1]['@graph'][i];
                var tempDisplayName = 'Item';
                var tempUrl = temp['@id'];
                switch (temp['@type'][0]) {
                    case 'annotation':
                        tempDisplayName = 'Added PMID: ' + temp['article']['pmid'];
                        tempUrl = external_url_map['PubMed'] + temp['article']['pmid'];
                        break;
                    case 'assessment':
                        tempDisplayName = temp['value'] + ' Assessment';
                        break;
                    case 'gdm':
                        tempDisplayName = temp['gene']['symbol'] + '-' + temp['disease']['term'] + " (" + temp['modeInheritance'] + ")";
                        tempUrl = "/curation-central/?gdm=" + temp['uuid'];
                        break;
                    default:
                        tempDisplayName = 'Item';
                }
                tempRecentHistory.push({
                    url: tempUrl,
                    displayName: tempDisplayName,
                    dateTime: temp['dateTime']
                });
            }
            // Set states for cleaned results
            this.setState({
                recentHistory: tempRecentHistory,
                gdmList: tempGdmList
            });
        }).catch(parseAndLogError.bind(undefined, 'putRequest'));
    },

    componentDidMount: function() {
        if (this.props.session['user_properties'] !== undefined) {
            this.setUserData(this.props.session['user_properties']);
            this.getData(this.props.session['auth.userid']);
        }
    },

    componentWillReceiveProps: function(nextProps) {
        if (typeof nextProps.session['user_properties'] !== undefined && nextProps.session['user_properties'] != this.props.session['user_properties']) {
            this.setUserData(nextProps.session['user_properties']);
            this.getData(nextProps.session['auth.userid']);
        }
    },

    render: function() {
        return (
            <div className="container">
                <h1>Welcome, {this.state.userName}!</h1>
                <h4>Your curator status: {this.state.userStatus}</h4>
                <div className="row">
                    <div className="col-md-6">
                        <Panel panelClassName="panel-dashboard">
                            <h3>Tools</h3>
                            <ul>
                                <li><a href="/create-gene-disease/">View/create gene-disease record</a></li>
                                <li><a href="/gdm/">View list of gene-disease records</a></li>
                            </ul>
                        </Panel>
                        <Panel panelClassName="panel-dashboard">
                            <h3>Recent History</h3>
                            {this.state.recentHistory.length > 0 ?
                            <ul>
                                {this.state.recentHistory.map(function(item) {
                                    return <li><a href={item.url}>{item.displayName}</a> (modified {moment(item.dateTime).format( "YYYY MMM DD, h:mm a")})</li>;
                                })}
                            </ul>
                            : "You have no activity to display."}
                        </Panel>
                    </div>
                    <div className="col-md-6">
                        <Panel panelClassName="panel-dashboard">
                            <h3>Your Gene-Disease Records</h3>
                            {this.state.gdmList.length > 0 ?
                            <div className="gdm-list">
                                {this.state.gdmList.map(function(item) {
                                    return (
                                        <div className="gdm-item">
                                            <a href={"/curation-central/?gdm=" + item.url}>{item.displayName}</a><br />
                                            Status: <strong>{item.status}</strong><br />
                                            Creation Date: <strong>{moment(item.dateTime).format( "YYYY MMM DD, h:mm a")}</strong>
                                        </div>
                                    );
                                })}
                            </div>
                            : "You have not created any Gene-Disease-Mode of Inheritance entries."}
                        </Panel>
                    </div>
                </div>
            </div>
        );
    }
});

globals.curator_page.register(Dashboard, 'curator_page', 'dashboard');
