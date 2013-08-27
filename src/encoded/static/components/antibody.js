/** @jsx React.DOM */
define(['exports', 'react', 'uri', 'globals'],
function (antibody, React, URI, globals) {
    'use strict';

    var Approval = antibody.Approval = React.createClass({
        render: function() {
            var context = this.props.context;
            var statusClass = 'status-' + (context.status || '').toLowerCase();
            var validations = context.validations.map(function (item) {
                return globals.panel_views.lookup(item)({context: item, key: item['@id']});
            });
            // Missing enncode
            return (
                <div class={'type-antibody_approval view-item ' + statusClass}>
                    <header class="row">
                        <div class="span12">
                            <h2>Approval for {context.antibody.accession}</h2>
                            <h3>Antibody against {context.target.organism.name}
                                {' '}{context.target.label}
                                <span class={'label ' + statusClass}>
                                    {context.status}
                                </span>
                            </h3>
                        </div>
                    </header>

                    <div class="panel data-display">
                        <dl class="key-value">
                            <dt>Source (vendor)</dt>
                            <dd><a href={context.antibody.source.url}>{context.antibody.source.title}</a></dd>
                            
                            <dt>Product ID</dt>
                            <dd><a href={context.antibody.url}>{context.antibody.product_id}</a></dd>
                            
                            <dt>Lot ID</dt>
                            <dd>{context.antibody.lot_id}</dd>

                            {context.antibody.lot_id_alias.length ? <dt>Lot ID aliases</dt> : null }
                            {context.antibody.lot_id_alias.length ? <dd>{context.antibody.lot_id_alias.join(', ')}</dd> : null }

                            <dt>Target</dt>
                            <dd><a href={context.target['@id']}>{context.target.label}</a></dd>
                            
                            <dt>Host</dt>
                            <dd>{context.antibody.host_organism.name}</dd>
                            
                            <dt>Clonality</dt>
                            <dd>{context.antibody.clonality}</dd>
                            
                            <dt>Purification</dt>
                            <dd>{context.antibody.purifications.join(', ')}</dd>
                            
                            <dt>Isotype</dt>
                            <dd>{context.antibody.isotype}</dd>
                            
                            <dt>Antigen description</dt>
                            <dd>{context.antibody.antigen_description}</dd>

                            {context.antibody.antigen_sequence ? <dt>Antigen sequence</dt> : null}
                            {context.antibody.antigen_sequence ? <dd>{context.antibody.antigen_sequence}</dd> : null}
                        </dl>
                    </div>

                    <div class="validations">
                        {validations}
                    </div>
                </div>
            );
        }
    });

    globals.content_views.register(Approval, 'antibody_approval');


    var Validation = antibody.Validation = React.createClass({
        render: function() {
            var context = this.props.context;
            var statusClass = 'status-' + (context.status || '').toLowerCase();
            var attachmentHref, attachmentUri;
            var figure, download, src, imgClass, alt;
            var imgClass = "validation-img validation-file";
            var height = "100";
            var width = "100";
            if (context.attachment) {
                attachmentUri = URI(context.attachment.href, URI(context['@id']).href);
                attachmentHref = attachmentUri.pathname + attachmentUri.search;
                if (context.attachment.type.split('/', 1)[0] == 'image') {
                    imgClass = 'validation-img';
                    src = attachmentHref;
                    height = context.attachment.height;
                    width = context.attachment.width;
                    alt = "Validation Image"
                } else if (context.attachment.type == "application/pdf"){
                    src = "/static/img/file-pdf.svg";
                    alt = "Validation PDF Icon";
                } else {
                    src = "/static/img/file.svg";
                    alt = "Validation Icon";
                }
                figure = (
                    <a data-bypass="true" href={attachmentHref}>
                        <img class={imgClass} src={src} height={height} width={width} alt={alt} />
                    </a>
                );
                download = (
                    <a data-bypass="true" href={attachmentHref} download={context.attachment.download}>
                        {context.attachment.download}
                    </a>
                );
            } else {
                src = "/static/img/file-broken.png";
                alt = "Validation File Broken Icon";
                figure = (
                    <img class={imgClass} src={src} height={height} width={width} alt={alt} />
                );
                download = (
                    <em>Document not available</em>
                );
            }

            return (
                <section class={'type-validation view-detail panel ' + statusClass}>
                    <div class="container">
                        <div class="row">
                            <div class="span6">
                                <figure>
                                    {figure}
                                    <figcaption>
                                        <span>{context.status}</span>
                                    </figcaption>
                                </figure>
                            </div>
                            <div class="span5">
                                <dl class="validation-meta-data key-value">
                                    <dt class="h3">Method</dt>
                                    <dd class="h3">{context.validation_method}</dd>

                                    <dt class="h4">Target species</dt>
                                    <dd class="h4">{context.target.organism.name}</dd>

                                    <dt hidden="hidden">Caption</dt>
                                    <dd>{context.caption}</dd>

                                    <dt>Submitted By</dt>
                                    <dd>{context.submitted_by.first_name}{' '}{context.submitted_by.last_name}</dd>

                                    <dt>Lab</dt>
                                    <dd>{context.lab.title}</dd>

                                    <dt>Grant</dt>
                                    <dd>{context.award.name}</dd>

                                    <dt>Approver</dt>
                                    <dd>{context.validated_by}</dd>

                                    <dt>Image</dt>
                                    <dd><span class={'label '+ statusClass}>{context.status}</span></dd>

                                    <dt><i class="icon-download-alt"></i> Download</dt>
                                    <dd>{download}</dd>
                                </dl>
                            </div>
                        </div>
                    </div>
                </section>
            );
        }
    });

    globals.panel_views.register(Validation, 'antibody_validation');


    // XXX Should move to Python code.
    var antibody_approval_title = function (props) {
        var context = props.context;
        var accession = context.antibody.accession;
        var organism_name = context.target.organism.name;
        var target_label = context.target.label;
        return accession + ' in ' + organism_name + ' ' + target_label;
    };

    globals.listing_titles.register(antibody_approval_title, 'antibody_approval');


    return antibody;
});
