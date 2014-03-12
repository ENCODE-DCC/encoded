/** @jsx React.DOM */
'use strict';
var React = require('react');
var url = require('url');
var globals = require('./globals');
var dbxref = require('./dbxref');

var DbxrefList = dbxref.DbxrefList;


var StatusLabel = module.exports.StatusLabel = React.createClass({
    render: function() {
        var status = this.props.status;
        return (
            <span className={globals.statusClass(status, 'label')}>
                {status}
            </span>
        );
    }
});


var Approval = module.exports.Approval = React.createClass({
    render: function() {
        var context = this.props.context;
        var characterizations = context.characterizations.map(function (item) {
            return globals.panel_views.lookup(item)({context: item, key: item['@id']});
        });
    

        // Missing enncode
        return (
            <div className={globals.itemClass(context, 'view-item')}>
                <header className="row">
                    <div className="span12">
                        <h2>Approval for {context.antibody.accession}</h2>
                        <h3>Antibody against {context.target.organism.name}
                            {' '}{context.target.label}
                            <StatusLabel status={context.status} />
                        </h3>
                    </div>
                </header>

                <div className="panel data-display">
                    <dl className="key-value">
                        <dt>Source (vendor)</dt>
                        <dd><a href={context.antibody.source.url}>{context.antibody.source.title}</a></dd>

                        <dt>Product ID</dt>
                        <dd><a href={context.antibody.url}>{context.antibody.product_id}</a></dd>

                        <dt>Lot ID</dt>
                        <dd>{context.antibody.lot_id}</dd>

                        <dt hidden={!context.antibody.lot_id_alias.length}>Lot ID aliases</dt>
                        <dd hidden={!context.antibody.lot_id_alias.length}>{context.antibody.lot_id_alias.join(', ')}</dd>

                        <dt>Target</dt>
                        <dd><a href={context.target['@id']}>{context.target.label}</a></dd>

                        {context.antibody.host_organism ? <dt>Host</dt> : null}
                        {context.antibody.host_organism ? <dd className="sentence-case">{context.antibody.host_organism.name}</dd> : null}
        

                        <dt hidden={!context.antibody.clonality}>Clonality</dt>
                        <dd hidden={!context.antibody.clonality} className="sentence-case">{context.antibody.clonality}</dd>

                        <dt hidden={!context.antibody.purifications.length}>Purification</dt>
                        <dd hidden={!context.antibody.purifications.length} className="sentence-case">{context.antibody.purifications.join(', ')}</dd>

                        <dt hidden={!context.antibody.isotype}>Isotype</dt>
                        <dd hidden={!context.antibody.isotype} className="sentence-case">{context.antibody.isotype}</dd>

                        <dt hidden={!context.antibody.antigen_description}>Antigen description</dt>
                        <dd hidden={!context.antibody.antigen_description}>{context.antibody.antigen_description}</dd>

                        <dt hidden={!context.antibody.antigen_sequence}>Antigen sequence</dt>
                        <dd hidden={!context.antibody.antigen_sequence}>{context.antibody.antigen_sequence}</dd>

                        <dt hidden={!context.antibody.aliases.length}>Aliases</dt>
                        <dd hidden={!context.antibody.aliases.length}>{context.antibody.aliases.join(", ")}</dd>
                        
                        <dt hidden={!context.antibody.dbxrefs.length}>Other identifiers</dt>
                        <dd hidden={!context.antibody.dbxrefs.length}>
                        	<DbxrefList values={context.antibody.dbxrefs} />
                        </dd>
                    </dl>
                </div>

                <div className="characterizations">
                    {characterizations}
                </div>
            </div>
        );
    }
});

globals.content_views.register(Approval, 'antibody_approval');


var Characterization = module.exports.Characterization = React.createClass({
    render: function() {
        var context = this.props.context;
        var attachmentHref, attachmentUri;
        var figure, download, src, imgClass, alt;
        var imgClass = "characterization-img characterization-file";
        var height = "100";
        var width = "100";
        if (context.attachment) {
            attachmentHref = url.resolve(context['@id'], context.attachment.href);
            if (context.attachment.type.split('/', 1)[0] == 'image') {
                imgClass = 'characterization-img';
                src = attachmentHref;
                height = context.attachment.height;
                width = context.attachment.width;
                alt = "Characterization Image"
            } else if (context.attachment.type == "application/pdf"){
                src = "/static/img/file-pdf.png";
                alt = "Characterization PDF Icon";
            } else {
                src = "/static/img/file.png";
                alt = "Characterization Icon";
            }
            figure = (
                <a data-bypass="true" href={attachmentHref}>
                    <img className={imgClass} src={src} height={height} width={width} alt={alt} />
                </a>
            );
            download = (
                <a data-bypass="true" href={attachmentHref} download={context.attachment.download}>
                    {context.attachment.download}
                </a>
            );
        } else {
            src = "/static/img/file-broken.png";
            alt = "Characterization file broken icon";
            figure = (
                <img className={imgClass} src={src} height={height} width={width} alt={alt} />
            );
            download = (
                <em>Document not available</em>
            );
        }

        return (
            <section className={globals.itemClass(context, 'view-detail panel')}>
                <div className="container">
                    <div className="row">
                        <div className="span6">
                            <figure>
                                {figure}
                                <figcaption>
                                    <span>{context.status}</span>
                                </figcaption>
                            </figure>
                        </div>
                        <div className="span5">
                            <dl className="characterization-meta-data key-value">
                                <dt className="h3">Method</dt>
                                <dd>{context.characterization_method}</dd>

                                <dt className="h4">Target species</dt>
                                <dd className="h4 sentence-case">{context.target.organism.name}</dd>

                                {context.caption ? <dt>Caption</dt> : null}
                                {context.caption ? <dd className="sentence-case">{context.caption}</dd> : null}

                                <dt>Submitted by</dt>
                                <dd>{context.submitted_by.title}</dd>

                                <dt>Lab</dt>
                                <dd>{context.lab.title}</dd>

                                <dt>Grant</dt>
                                <dd>{context.award.name}</dd>

                                {/*
                                <dt>Approver</dt>
                                <dd>{context.validated_by}</dd>
                                */}

                                <dt>Image</dt>
                                <dd><StatusLabel status={context.status} /></dd>

                                <dt><i className="icon-download-alt"></i> Download</dt>
                                <dd>{download}</dd>
                            </dl>
                        </div>
                    </div>
                </div>
            </section>
        );
    }
});

globals.panel_views.register(Characterization, 'antibody_characterization');


// XXX Should move to Python code.
var antibody_approval_title = function (props) {
    var context = props.context;
    var accession = context.antibody.accession;
    var organism_name = context.target.organism.name;
    var target_label = context.target.label;
    return accession + ' in ' + organism_name + ' ' + target_label;
};

globals.listing_titles.register(antibody_approval_title, 'antibody_approval');
