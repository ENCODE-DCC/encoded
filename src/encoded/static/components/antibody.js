/** @jsx React.DOM */
define(['exports', 'react', 'uri', 'globals'],
function (antibody, React, URI, globals) {
    'use strict';

    var Approval = antibody.Approval = React.createClass({
        render: function() {
            var context = this.props.context;
            var statusClass = 'status-' + (context.approval_status || '').toLowerCase();
            var validations = context.validations.map(function (item) {
                return globals.panel_views.lookup(item)({context: item});
            });
            return (
                <div class={'type-antibody_approval view-item ' + statusClass}>
                    <header class="row">
                        <div class="span12">
                            <h2>Approval for {context.antibody_lot.antibody_accession}</h2>
                            <h3>Antibody against {context.target.organism.organism_name}
                                {' '}{context.target.target_label}
                                <span class={'label ' + statusClass}>
                                    {context.approval_status}
                                </span>
                            </h3>
                        </div>
                    </header>

                    <div class="panel data-display">
                        <dl class="key-value">
                            <dt>Source (vendor)</dt>
                            <dd><a href={context.antibody_lot.source.url}>{context.antibody_lot.source.source_name}</a></dd>
                            
                            <dt>Product ID</dt>
                            <dd><a href={context.antibody_lot.url}>{context.antibody_lot.product_id}</a></dd>
                            
                            <dt>Lot ID</dt>
                            <dd>{context.antibody_lot.lot_id}</dd>
                            
                            <dt>Target</dt>
                            <dd><a href={context.target['@id']}>{context.target.target_label}</a></dd>
                            
                            <dt>Host</dt>
                            <dd>{context.antibody_lot.host_organism}</dd>
                            
                            <dt>Clonality</dt>
                            <dd>{context.antibody_lot.clonality}</dd>
                            
                            <dt>Purification</dt>
                            <dd>{context.antibody_lot.purification}</dd>
                            
                            <dt>Isotype</dt>
                            <dd>{context.antibody_lot.isotype}</dd>
                            
                            <dt>Antigen description</dt>
                            <dd>{context.antibody_lot.antigen_description}</dd>
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
            var statusClass = 'status-' + (context.validation_status || '').toLowerCase();
            var documentHref, documentUri;
            var figure, download, src, imgClass, alt;
            var imgClass = "validation-img validation-file";
            var height = "100";
            var width = "100";
            if (context.document) {
                documentUri = URI(context.document.href, URI(context['@id']).href);
                documentHref = documentUri.pathname + documentUri.search;
                if (context.document.type.split('/', 1)[0] == 'image') {
                    imgClass = 'validation-img';
                    src = documentHref;
                    height = context.document.height;
                    width = context.document.width;
                    alt = "Validation Image"
                } else if (context.document.type == "application/pdf"){
                    src = "/static/img/file-pdf.svg";
                    alt = "Validation PDF Icon";
                } else {
                    src = "/static/img/file.svg";
                    alt = "Validation Icon";
                }
                figure = (
                    <a data-bypass="true" href={documentHref}>
                        <img class={imgClass} src={src} height={height} width={width} alt={alt} />
                    </a>
                );
                download = (
                    <a data-bypass="true" href={documentHref} download={context.document.download}>
                        {context.document.download}
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
                                        <span>{context.validation_status}</span>
                                    </figcaption>
                                </figure>
                            </div>
                            <div class="span5">
                                <dl class="validation-meta-data key-value">
                                    <dt class="h3">Method</dt>
                                    <dd class="h3">{context.validation_method}</dd>

                                    <dt class="h4">Target species</dt>
                                    <dd class="h4">{context.target.organism.organism_name}</dd>

                                    <dt hidden="hidden">Caption</dt>
                                    <dd>{context.caption}</dd>

                                    <dt>Submitted By</dt>
                                    <dd>{context.submitter.first_name} {context.submitter.last_name}</dd>

                                    <dt>Lab</dt>
                                    <dd>{context.lab.name}</dd>

                                    <dt>Grant</dt>
                                    <dd>{context.award.number}</dd>

                                    <dt>Approver</dt>
                                    <dd>{context.validated_by}</dd>

                                    <dt>Image</dt>
                                    <dd><span class={'label '+ statusClass}>{context.validation_status}</span></dd>

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


    var antibody_lot_title = function (props) {
        return props.context.antibody_accession;
    };

    globals.listing_titles.register(antibody_lot_title, 'antibody_lot');


    var antibody_approval_title = function (props) {
        var context = props.context;
        var antibody_accession = context.antibody_lot.antibody_accession;
        var organism_name = context.target.organism.organism_name;
        var target_label = context.target.target_label;
        return antibody_accession + ' in ' + organism_name + ' ' + target_label;
    };

    globals.listing_titles.register(antibody_approval_title, 'antibody_approval');


    return antibody;
});
