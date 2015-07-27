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

    cleanGdmGeneDiseaseName: function(gene, disease) {
        return gene + "–" + disease;
    },

    cleanGdmModelName: function(model) {
        // remove (HP:#######) from model name
        return model.indexOf('(') > -1 ? model.substring(0, model.indexOf('(') - 1) : model;
    },

    setUserData: function(props) {
        // sets the display name and curator status
        this.setState({
            userName: props['first_name'],
            userStatus: props['groups'][0].charAt(0).toUpperCase() + props['groups'][0].substring(1),
            lastLogin: ''
        });
    },

    getData: function(userid) {
        // Retrieve all GDMs and other objects related to user via search
        this.getRestDatas(['/search/?type=gdm&limit=all', '/search/?limit=all&owner=' + userid], [function() {}, function() {}]).then(data => {
            // Search objects successfully retrieved; process results

            // Sort results by time. Ideally this would be done by the search function, but until
            // I can figure out how to set sorting for it, this will have to do
            var sortedGdmData = _(data[0]['@graph']).sortBy(function(item) {
                return -moment(item.dateTime).format("X");
            });
            var sortedHistoryData = _(data[1]['@graph']).sortBy(function(item) {
                return -moment(item.dateTime).format("X");
            }).slice(0,10);

            // GDM results; finds GDMs created by user, and also creates PMID-GDM mapping table
            // (stopgap measure until article -> GDM mapping ability is incorporated)
            var tempGdmList = [], tempRecentHistory = [];
            var pmidGdmMapping = {};
            for (var i = 0; i < sortedGdmData.length; i++) {
                var temp = sortedGdmData[i];
                var tempDisplayName =  "()";
                if (temp['owner'] == userid) {
                    tempGdmList.push({
                        uuid: temp['uuid'],
                        gdmGeneDisease: this.cleanGdmGeneDiseaseName(temp['gene']['symbol'], temp['disease']['term']),
                        gdmModel: this.cleanGdmModelName(temp['modeInheritance']),
                        status: temp['status'],
                        dateTime: temp['dateTime']
                    });
                }
                if (temp['annotations'].length > 0) {
                    for (var j = 0; j < temp['annotations'].length; j++) {
                        pmidGdmMapping[temp['annotations'][j]['uuid']] = {
                            uuid: temp['uuid'],
                            displayName: this.cleanGdmGeneDiseaseName(temp['gene']['symbol'], temp['disease']['term']),
                            displayName2: this.cleanGdmModelName(temp['modeInheritance'])
                        };
                    }
                }
            }
            // Recent History panel results; only displays annotation(article) addition and GDM
            // creation history for the time being.
            for (var i = 0; i < sortedHistoryData.length; i++) {
                var display = false;
                var temp = sortedHistoryData[i];
                var tempDisplayText = '';
                var tempUrl = '';
                var tempTimestamp = '';
                var tempDateTime = moment(temp['dateTime']).format( "YYYY MMM DD, h:mm a");
                switch (temp['@type'][0]) {
                    case 'annotation':
                        tempUrl = "/curation-central/?gdm=" + pmidGdmMapping[temp['uuid']]['uuid'] + "&pmid=" + temp['article']['pmid'];
                        tempDisplayText = <span><a href={tempUrl}>PMID:{temp['article']['pmid']}</a> added to <strong>{pmidGdmMapping[temp['uuid']]['displayName']}</strong>–<i>{pmidGdmMapping[temp['uuid']]['displayName2']}</i></span>;
                        tempTimestamp = "added " + tempDateTime;
                        display = true;
                        break;
                    case 'assessment':
                        tempDisplayText = temp['value'] + ' Assessment';
                        break;
                    case 'gdm':
                        tempUrl = "/curation-central/?gdm=" + temp['uuid'];
                        tempDisplayText = <span><a href={tempUrl}><strong>{this.cleanGdmGeneDiseaseName(temp['gene']['symbol'], temp['disease']['term'])}</strong>–<i>{this.cleanGdmModelName(temp['modeInheritance'])}</i></a></span>;
                        tempTimestamp = "created " + tempDateTime;
                        display = true;
                        break;
                    default:
                        tempDisplayText = 'Item';
                }
                if (display === true) {
                    tempRecentHistory.push({
                        uuid: temp['uuid'],
                        displayText: tempDisplayText,
                        timestamp: tempTimestamp
                    });
                }
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
                                <li><a href="/create-gene-disease/">Create Gene-Disease Record</a></li>
                                <li><a href="/gdm/">View list of all Gene-Disease Records</a></li>
                            </ul>
                        </Panel>
                        <Panel panelClassName="panel-dashboard">
                            <h3>Your Recent History</h3>
                            {this.state.recentHistory.length > 0 ?
                            <ul>
                                {this.state.recentHistory.map(function(item) {
                                    return <li key={item.uuid}>{item.displayText}; <i>{item.timestamp}</i></li>;
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
                                        <div className="gdm-item" key={item.uuid}>
                                            <a href={"/curation-central/?gdm=" + item.uuid}><strong>{item.gdmGeneDisease}</strong>–<i>{item.gdmModel}</i></a><br />
                                            <strong>Status</strong>: {item.status}<br />
                                            <strong>Creation Date</strong>: {moment(item.dateTime).format( "YYYY MMM DD, h:mm a")}
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
