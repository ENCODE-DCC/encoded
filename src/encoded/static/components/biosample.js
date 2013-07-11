/** @jsx React.DOM */
define(['exports', 'react', 'uri', 'globals'],
function (biosample, React, URI, globals) {
    'use strict';

    var Panel = function (props) {
        // XXX not all panels have the same markup
        var context;
        if (props['@id']) {
            context = props;
            props = {context: context, key: context['@id']};
        }
        return globals.panel_views.lookup(props.context)(props);
    };


    var Biosample = biosample.Biosample = React.createClass({
        render: function() {
            var context = this.props.context;
            var itemClass = globals.itemClass(context, 'view-item');
            return (
                <div class={itemClass}>
                    <header class="row">
                        <div class="span12">
                            <ul class="breadcrumb">
                                <li>Biosamples <span class="divider">/</span></li>
                                <li>{context.biosample_type}{' '}<span class="divider">/</span></li>{' '}
                                <li class="active">{context.donor.organism.organism_name}</li>
                            </ul>
                            <h2>{context.accession}{' / '}{context.biosample_type}</h2>
                        </div>
                    </header>
                    <div class="panel data-display">
                        <dl class="key-value">
                            <dt>Term name</dt>
                            <dd>{context.biosample_term_name}</dd>

                            <dt>Term ID</dt>
                            <dd>{context.biosample_term_id}</dd>

                            <dt hidden={!context.biosample_description}>Description</dt>
                            <dd hidden={!context.biosample_description}>{context.biosample_description}</dd>

                            <dt>Source</dt>
                            <dd><a href={context.source.url}>{context.source.source_name}</a></dd>

                            <dt hidden={!context.product_id}>Product ID</dt>
                            <dd hidden={!context.product_id}><maybe_link href={context.product_url}>{context.product_id}</maybe_link></dd>

                            <dt hidden={!context.lot_id}>Lot ID</dt>
                            <dd hidden={!context.lot_id}>{context.lot_id}</dd>

                            <dt>Project</dt>
                            <dd>{context.award.project}</dd>

                            <dt>Submitted by</dt>
                            <dd>{context.submitter.first_name}{' '}{context.submitter.last_name}</dd>

                            <dt>Lab</dt>
                            <dd>{context.lab.name}</dd>

                            <dt>Grant</dt>
                            <dd>{context.award.number}</dd>

                            <dt hidden={!context.note}>Note</dt>
                            <dd hidden={!context.note}>{context.note}</dd>
                        </dl>

                        {context.biosample_type != 'Immortalized cell line' ?
                            <section>
                                <hr />
                                <h4>Donor Information</h4>
                                <Panel context={context.donor} />
                            </section>
                        : null}

                        {context.treatments.length ?
                            <section>
                                <hr />
                                <h4>Treatment Details</h4>
                                {context.treatments.map(Panel)}
                            </section>
                        : null}

                        {context.constructs.length ?
                            <section>
                                <hr />
                                <h4>Construct Details</h4>
                                {context.constructs.map(Panel)}
                            </section>
                        : null}

                    </div>

                    {context.documents.length ?
                        <div>
                            <h3>Protocols and supporting documents</h3>
                            {context.documents.map(Panel)}
                        </div>
                    : null}

                    <h3 hidden={!context.related_biosample_uuid}>Related Biosamples</h3>
                    {context.related_biosample_uuid ?
                        <div class="panel data-display">
                            <h4>Derived From Biosample</h4>
                            <dl class="key-value">
                                <dt>Accession</dt>
                                <dd><a href={'/biosamples/' + context.related_biosample_uuid + '/'}>{context.related_biosample_accession}</a></dd>
                           </dl>
                        </div>
                    : null}
                </div>
            );
        }
    });

    globals.content_views.register(Biosample, 'biosample');


    var maybe_link = function (props, children) {
        if (props.href == 'N/A') {
            return children;
        } else {
            return (
                <a href={props.href}>{children}</a>
            );
        }
    };

    var Donor = biosample.Donor = React.createClass({
        render: function() {
            var context = this.props.context;
            return (
                <dl class="key-value">
                    <dt>Donor ID</dt>
                    <dd>{context.donor_id}</dd>

                    <dt>Age</dt>
                    <dd>{context.age}</dd>

                    <dt>Sex</dt>
                    <dd>{context.sex}</dd>

                    <dt hidden={!context.strain_background}>Strain</dt>
                    <dd hidden={!context.strain_background}>{context.strain_background}</dd>

                    <dt>Health status</dt>
                    <dd>{context.health_status}</dd>
                </dl>
            );
        }
    });

    globals.panel_views.register(Donor, 'donor');


    var Treatment = biosample.Treatment = React.createClass({
        render: function() {
            var context = this.props.context;
            var condition = '';
            if (context.condition_id) {
                if (context.concentration) {
                    condition += context.concentration + ' ' + context.concentration_units + ' ';
                }
                condition += context.condition_term + ' (' + context.condition_id + ') ';
                if (context.duration) {
                    condition += 'for ' + context.duration + ' ' + context.duration_units;
                }
            }
            return (
                <dl class="key-value">
                    <dt>Treatment</dt>
                    <dd>{context.treatment_name}</dd>

                    <dt>Type</dt>
                    <dd>{context.treatment_type}</dd>

                    {condition ? <dt>Condition</dt> : undefined}
                    {condition ? <dd>{condition}</dd> : undefined}
                </dl>
            );
        }
    });

    globals.panel_views.register(Treatment, 'biosample_treatment');


    var Construct = biosample.Construct = React.createClass({
        render: function() {
            var context = this.props.context;
            return (
                <dl class="key-value">
                    <dt>Vector</dt>
                    <dd>{context.vector_name}</dd>

                    <dt>Vector Type</dt>
                    <dd>{context.transfection_type}</dd>

                    <dt>Description</dt>
                    <dd>{context.construct_description}</dd>

                    <dt>Source</dt>
                    <dd>{context.source.source_name}</dd>

                    <dt>Product ID</dt>
                    <dd><maybe_link href={context.product_url}>{context.product_id}</maybe_link></dd>

                </dl>
            );
        }
    });

    globals.panel_views.register(Construct, 'biosample_construct');


    var Document = biosample.Document = React.createClass({
        render: function() {
            var context = this.props.context;
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
                <section class="type-document view-detail panel">
                    <div class="container">
                        <div class="row">
                            <div class="span6">
                                <figure>
                                    {figure}
                                </figure>
                            </div>
                            <div class="span5">
                                <h3 style={{'text-transform': 'capitalize'}}>{context.document_type}</h3>
                                <p>{context.description}</p>
                                <dl class="key-value">
                                    <dt>Submitted By</dt>
                                    <dd>{context.submitter.first_name}{' '}{context.submitter.last_name}</dd>

                                    <dt>Lab</dt>
                                    <dd>{context.lab.name}</dd>

                                    <dt>Grant</dt>
                                    <dd>{context.award.number}</dd>

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

    globals.panel_views.register(Document, 'biosample_document');


    return biosample;
});
