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
                    <div className="col-sm-12">
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

                        {context.antibody.lot_id_alias.length ? <dt>Lot ID aliases</dt> : null}
                        {context.antibody.lot_id_alias.length ? <dd>{context.antibody.lot_id_alias.join(', ')}</dd> : null}

                        <dt>Target</dt>
                        <dd><a href={context.target['@id']}>{context.target.label}</a></dd>

                        {context.antibody.host_organism ? <dt>Host</dt> : null}
                        {context.antibody.host_organism ? <dd className="sentence-case">{context.antibody.host_organism.name}</dd> : null}
        
                        {context.antibody.clonality ? <dt>Clonality</dt> : null}
                        {context.antibody.clonality ? <dd className="sentence-case">{context.antibody.clonality}</dd> : null}

                        {context.antibody.purifications.length ? <dt>Purification</dt> : null}
                        {context.antibody.purifications.length ? <dd className="sentence-case">{context.antibody.purifications.join(', ')}</dd> : null}

                        {context.antibody.isotype ? <dt>Isotype</dt> : null}
                        {context.antibody.isotype ? <dd className="sentence-case">{context.antibody.isotype}</dd> : null}

                        {context.antibody.antigen_description ? <dt>Antigen description</dt> : null}
                        {context.antibody.antigen_description ? <dd>{context.antibody.antigen_description}</dd> : null}

                        {context.antibody.antigen_sequence ? <dt>Antigen sequence</dt> : null}
                        {context.antibody.antigen_sequence ? <dd>{context.antibody.antigen_sequence}</dd> : null}

                        {context.antibody.aliases.length ? <dt>Aliases</dt> : null}
                        {context.antibody.aliases.length ? <dd>{context.antibody.aliases.join(", ")}</dd> : null}
                        
                        {context.antibody.dbxrefs.length ? <dt>External resources</dt> : null}
                        {context.antibody.dbxrefs.length ? <dd><DbxrefList values={context.antibody.dbxrefs} /></dd> : null}
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
        var figure, download, src, alt;
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
                alt = "Characterization Image";
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
                <div class="row">
                    <div className="col-sm-4 col-md-6">
                        <figure>
                            {figure}
                            <figcaption>
                                <span>{context.status}</span>
                            </figcaption>
                        </figure>
                    </div>
                    <div className="col-sm-8 col-md-6">
                        <dl className="characterization-meta-data key-value">
                            <dt className="h3">Method</dt>
                            <dd className="h3">{context.characterization_method}</dd>

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
