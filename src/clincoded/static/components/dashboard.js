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

    // Retrieve the GDMs and other objects related to user via search
    getData: function(userid) {
        this.getRestDatas(['/search/?type=gdm&limit=10&owner=' + userid,'/search/?limit=10&owner=' + userid], [function() {}, function() {}]).then(data => {
            // Search objects successfully retrieved; clean up results
            // GDM List panel results
            var tempGdmList = [], tempRecentHistory = [];
            for (var i = 0; i < data[0]['@graph'].length; i++) {
                var temp = data[0]['@graph'][i];
                tempGdmList.push({
                    url: temp['@id'],
                    gene: temp['gene']['symbol'],
                    disease: temp['disease']['term'],
                    datetime: temp['annotations']['dateTime']
                });
            }
            // Recent History panel results
            for (var i = 0; i < data[1]['@graph'].length; i++) {
                var temp = data[1]['@graph'][i];
                var tempDisplayName = 'Item';
                switch (temp['@type'][0]) {
                    case 'annotation':
                        tempDisplayName = 'Annotation for PMID:' + temp['article']['pmid'];
                        break;
                    case 'assessment':
                        tempDisplayName = temp['value'] + ' Assessment';
                        break;
                    case 'gdm':
                        tempDisplayName = 'GDM:' + temp['gene']['symbol'] + ':' + temp['disease']['term'];
                        break;
                    default:
                        tempDisplayName = 'Item';
                }
                tempRecentHistory.push({
                    url: temp['@id'],
                    displayName: tempDisplayName,
                    dateTime: temp['dateTime']
                });
            }
            // Set states for cleaned results
            this.setState({
                userName: this.props.session['user_properties']['first_name'],
                userStatus: this.props.session['user_properties']['groups'][0].charAt(0).toUpperCase() + this.props.session['user_properties']['groups'][0].substring(1),
                lastLogin: '',
                recentHistory: tempRecentHistory,
                gdmList: tempGdmList
            });
        }).catch(parseAndLogError.bind(undefined, 'putRequest'));
    },

    componentWillReceiveProps: function(nextProps) {
        if (nextProps.session['auth.userid'] !== this.props.session['auth.userid']) {
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
                            <h3>Recent history</h3>
                            {this.state.recentHistory.length > 0 ?
                            <ul>
                                {this.state.recentHistory.map(function(item) {
                                    return <li><a href={item.url}>{item.displayName}</a> (modified {moment(item.dateTime).format( "YYYY/MM/DD h:mma")})</li>
                                })}
                            </ul>
                            : "You have no activity to display."}
                        </Panel>
                    </div>
                    <div className="col-md-6">
                        <Panel panelClassName="panel-dashboard">
                            <h3>Your Gene-Disease records</h3>
                            {this.state.gdmList.length > 0 ?
                            <ul>
                                {this.state.gdmList.map(function(item) {
                                    return <li><a href={item.url}>{item.gene}:{item.disease}</a></li>
                                })}
                            </ul>
                            : "You have not created any GDMs."}
                        </Panel>
                    </div>
                </div>
            </div>
        );
    }
});

globals.curator_page.register(Dashboard, 'curator_page', 'dashboard');
