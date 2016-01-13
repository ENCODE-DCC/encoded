'use strict';
var React = require('react/addons');
var _ = require('underscore');
var panel = require('../libs/bootstrap/panel');
var globals = require('./globals');

var {Panel, PanelBody} = panel;


// 'documents' Object
//
// This object is mostly an array of arrays. The inner arrays holds the list of documents
// of one type, while the outer array holds all the types of arrays along with their section titles.
//
// [
//     {
//         title: 'Section title',
//         documents: array of document objects
//     },
//     {
//         ...next one...
//     }
// ]

var DocumentPanel = modules.exports.DocumentPanel = React.createClass({
    propTypes: {
        documentList: React.PropTypes.array.isRequired // List of document arrays and their titles
    },

    render: function() {
        return (
            <Panel>
                {this.props.documentList.map(docObj => {
                    return docObj.documents.map(document => {
                        var PanelView = globals.panel_views.lookup(document);
                        return <PanelView key={document['@id']} context={document} />;
                    });
                })};
            </Panel>
        );
    }
});
