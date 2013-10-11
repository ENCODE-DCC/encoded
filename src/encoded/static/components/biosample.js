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
            var aliasList = context.aliases.join(", ");
            
            // set up construct documents panels
            var constructs = _.sortBy(context.constructs, function(item) {
                return item.uuid;
            });
            var construct_documents = {};
            constructs.forEach(function (construct) {
                construct.documents.forEach(function (doc) {
                    construct_documents[doc['@id']] = Panel({context: doc});
                });
            })
            
            // set up RNAi documents panels
            var rnais = _.sortBy(context.rnais, function(item) {
                return item.uuid; //may need to change
            });
            var rnai_documents = {};
            rnais.forEach(function (rnai) {
                rnai.documents.forEach(function (doc) {
                    rnai_documents[doc['@id']] = Panel({context: doc});
                });
            })

            return (
                <div class={itemClass}>
                    <header class="row">
                        <div class="span12">
                            <ul class="breadcrumb">
                                <li>Biosamples <span class="divider">/</span></li>
                                <li>{context.biosample_type}{' '}<span class="divider">/</span></li>{' '}
                                {context.donor ?
                                    <li class="active">{context.donor.organism.name}</li>
                                : null }
                            </ul>
                            <h2>{context.accession}{' / '}<span class="cap-me-once">{context.biosample_type}</span></h2>
                        </div>
                    </header>
                    <div class="panel data-display">
                        <dl class="key-value">
                            <dt>Term name</dt>
                            <dd>{context.biosample_term_name}</dd>

                            <dt>Term ID</dt>
                            <dd>{context.biosample_term_id}</dd>
                            
                            <dt hidden={!context.description}>Description</dt>
                            <dd hidden={!context.description}>{context.description}</dd>
                            
                            <dt>Source</dt>
                            <dd><a href={context.source.url}>{context.source.title}</a></dd>

                            <dt hidden={!context.product_id}>Product ID</dt>
                            <dd hidden={!context.product_id}><maybe_link href={context.url}>{context.product_id}</maybe_link></dd>

                            <dt hidden={!context.lot_id}>Lot ID</dt>
                            <dd hidden={!context.lot_id}>{context.lot_id}</dd>

                            <dt>Project</dt>
                            <dd>{context.award.rfa}</dd>

                            <dt>Submitted by</dt>
                            <dd>{context.submitted_by.title}</dd>

                            <dt>Lab</dt>
                            <dd>{context.lab.title}</dd>
                            
                            <dt hidden={!context.aliases.length}>Aliases</dt>
                            <dd hidden={!context.aliases.length}>{aliasList}</dd>

                            <dt>Grant</dt>
                            <dd>{context.award.name}</dd>

                            <dt hidden={!context.note}>Note</dt>
                            <dd hidden={!context.note}>{context.note}</dd>

                        </dl>
                        
                        {(context.donor && (context.biosample_type != "immortalized cell line")) ?
                            <section>
                                <hr />
                                <h4>Donor information</h4>
                                <Panel context={context.donor} biosample={context} />
                            </section>
                        : null}
                        
                         {context.derived_from.length ?
                            <section>
                                <hr />
                                <h4>Derived from biosamples</h4>
                                <ul class="non-dl-list">
									{context.derived_from.map(function (biosample) {
										return (
											<li key={biosample['@id']}>
												<a href={biosample['@id']}>{biosample.accession}</a>								
											</li>
										);
									})}
								</ul>
                                
                            </section>
                        : null}
                        
                        {context.pooled_from.length ?
                            <section>
                                <hr />
                                <h4>Pooled from biosamples</h4>
                                <ul class="non-dl-list">
									{context.pooled_from.map(function (biosample) {
										return (
											<li key={biosample['@id']}>
												<a href={biosample['@id']}>{biosample.accession}</a>								
											</li>
										);
									})}
								</ul>
                                
                            </section>
                        : null}

                        {context.treatments.length ?
                            <section>
                                <hr />
                                <h4>Treatment details</h4>
                                {context.treatments.map(Panel)}
                            </section>
                        : null}

                        {context.constructs.length ?
                            <section>
                                <hr />
                                <h4>Construct details</h4>
                                {context.constructs.map(Panel)}
                            </section>
                        : null}
                        
                    	{context.rnais.length ?
                            <section>
                                <hr />
                                <h4>RNAi details</h4>
                                {context.rnais.map(Panel)}
                            </section>
                        : null}

                    </div>

                    {context.protocol_documents.length ?
                        <div>
                            <h3>Protocol documents</h3>
                            {context.protocol_documents.map(Panel)}
                        </div>
                    : null}

                    {context.characterizations.length ?
                        <div>
                            <h3>Characterizations</h3>
                            {context.characterizations.map(Panel)}
                        </div>
                    : null}
                    
                    <div hidden={!Object.keys(construct_documents).length}>
                        <h3>Construct documents</h3>
                        {construct_documents}
                    </div>
                    
                    <div hidden={!Object.keys(rnai_documents).length}>
                        <h3>RNAi documents</h3>
                        {rnai_documents}
                    </div>
                    
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
	
    var HumanDonor = biosample.HumanDonor = React.createClass({
        render: function() {
            var context = this.props.context;
            var biosample = this.props.biosample;
            return (
                <dl class="key-value">
                    <dt>Accession</dt>
                    <dd>{context.accession}</dd>
                    
                    <dt hidden={!context.aliases.length}>Aliases</dt>
                    <dd hidden={!context.aliases.length}>{context.aliases.join(", ")}</dd>

                    {context.organism.name ? <dt>Species</dt> : null}
                    {context.organism.name ? <dd>{context.organism.name}</dd> : null}

                    {biosample && biosample.life_stage ? <dt>Life stage</dt> : null}
                    {biosample && biosample.life_stage ? <dd>{biosample.life_stage}</dd> : null}

                    {biosample && biosample.age ? <dt>Age</dt> : null}
                    {biosample && biosample.age ? <dd>{biosample.age}{' '}{biosample.age_units}</dd> : null}

                    <dt>Sex</dt>
                    <dd>{context.sex}</dd>

                    {biosample && biosample.health_status ? <dt>Health status</dt> : null}
                    {biosample && biosample.health_status ? <dd>{biosample.health_status}</dd> : null}

                    <dt>Ethnicity</dt>
                    <dd>{context.ethnicity}</dd>
                </dl>
            );
        }
    });

    globals.panel_views.register(HumanDonor, 'human_donor');


    var MouseDonor = biosample.MouseDonor = React.createClass({
        render: function() {
            var context = this.props.context;
            var biosample = this.props.biosample;
            return (
                <dl class="key-value">
                    <dt>Accession</dt>
                    <dd>{context.accession}</dd>
                    
                    <dt hidden={!context.aliases.length}>Aliases</dt>
                    <dd hidden={!context.aliases.length}>{context.aliases.join(", ")}</dd>

                    {context.organism.name ? <dt>Species</dt> : null}
                    {context.organism.name ? <dd>{context.organism.name}</dd> : null}

                    {biosample && biosample.life_stage ? <dt>Life stage</dt> : null}
                    {biosample && biosample.life_stage ? <dd>{biosample.life_stage}</dd> : null}

                    {biosample && biosample.age ? <dt>Age</dt> : null}
                    {biosample && biosample.age ? <dd>{biosample.age}{' '}{biosample.age_units}</dd> : null}

                    <dt>Sex</dt>
                    <dd>{context.sex}</dd>

                    {biosample && biosample.health_status ? <dt>Health status</dt> : null}
                    {biosample && biosample.health_status ? <dd>{biosample.health_status}</dd> : null}

                    <dt>Strain background</dt>
                    <dd>{context.strain_background}</dd>

                    {context.strain_name ? <dt>Strain name</dt> : null}
                    {context.strain_name ? <dd>{context.strain_name}</dd> : null}
                </dl>
            );
        }
    });

    globals.panel_views.register(MouseDonor, 'mouse_donor');


    var Treatment = biosample.Treatment = React.createClass({
        render: function() {
            var context = this.props.context;
            var title = '';
            if (context.concentration) {
                title += context.concentration + ' ' + context.concentration_units + ' ';
            }
            title += context.treatment_term_name + ' (' + context.treatment_term_id + ') ';
            if (context.duration) {
                title += 'for ' + context.duration + ' ' + context.duration_units;
            }
            return (
                <dl class="key-value">
                    <dt>Treatment</dt>
                    <dd>{title}</dd>

                    <dt>Type</dt>
                    <dd>{context.treatment_type}</dd>

                </dl>
            );
        }
    });

    globals.panel_views.register(Treatment, 'treatment');


    var Construct = biosample.Construct = React.createClass({
        render: function() {
            var context = this.props.context;
            return (
                <dl class="key-value">
                	{context.target ? <dt>Target</dt> : null}
                    {context.target ? <dd class="no-cap"><a href={context.target['@id']}>{context.target.name}</a></dd> : null}

                    {context.vector_backbone_name ? <dt>Vector</dt> : null}
                    {context.vector_backbone_name ? <dd>{context.vector_backbone_name}</dd> : null}

                    {context.construct_type ? <dt>Construct Type</dt> : null}
                    {context.construct_type ? <dd>{context.construct_type}</dd> : null}

                   	{context.description ?  <dt>Description</dt> : null}
                    {context.description ? <dd>{context.description}</dd> : null}
                    
                    <dt hidden={!context.tags.length}>Tags</dt>
					<dd hidden={!context.tags.length}>
						<ul>
							{context.tags.map(function (tag, index) {
								return (
									<li key={index}>
										{tag.name} (Location: {tag.location})								
									</li>
								);
							})}
						</ul>
                    </dd>

                    
                    {context.source.title ? <dt>Source</dt> : null}
                    {context.source.title ? <dd>{context.source.title}</dd> : null}

                    {context.product_id ? <dt>Product ID</dt> : null}
                    {context.product_id ? <dd><maybe_link href={context.url}>{context.product_id}</maybe_link></dd> : null}
                </dl>
            );
        }
    });

    globals.panel_views.register(Construct, 'construct');
    
    
    var RNAi = biosample.RNAi = React.createClass({
        render: function() {
            var context = this.props.context;
            return (
                <dl class="key-value">
                	{context.rnai_type ? <dt>RNAi type</dt> : null}
                    {context.rnai_type ? <dd class="no-cap">{context.rnai_type}</dd> : null}
                    
                    {context.product_id ? <dt>Product ID</dt> : null}
                    {context.product_id ? <dd class="no-cap">{context.product_id}</dd> : null}
                    
                    {context.target ? <dt>Target</dt> : null}
                    {context.target ? <dd class="no-cap"><a href={context.target}>{context.target}</a></dd> : null}
                    
                    {context.rnai_target_sequence ? <dt>Target sequence</dt> : null}
                    {context.rnai_target_sequence ? <dd class="no-cap">{context.rnai_target_sequence}</dd> : null}
                    
                    {context.vector_backbone_name ? <dt>Vector backbone</dt> : null}
                    {context.vector_backbone_name ? <dd class="no-cap">{context.vector_backbone_name}</dd> : null}

                    {context.source.title ? <dt>Source</dt> : null}
                    {context.source.title ? <dd><a href={context.source.url}>{context.source.title}</a></dd> : null}
                </dl>
            );
        }
    });

    globals.panel_views.register(RNAi, 'rnai');


    var Document = biosample.Document = React.createClass({
        render: function() {
            var context = this.props.context;
            var attachmentHref, attachmentUri;
            var figure, download, src, imgClass, alt;
            var imgClass = "characterization-img characterization-file";
            var height = "100";
            var width = "100";
            if (context.attachment) {
                attachmentUri = URI(context.attachment.href, URI(context['@id']).href);
                attachmentHref = attachmentUri.pathname + attachmentUri.search;
                if (context.attachment.type.split('/', 1)[0] == 'image') {
                    imgClass = 'characterization-img';
                    src = attachmentHref;
                    height = context.attachment.height;
                    width = context.attachment.width;
                    alt = "Characterization Image"
                } else if (context.attachment.type == "application/pdf"){
                    src = "/static/img/file-pdf.svg";
                    alt = "Characterization PDF Icon";
                } else {
                    src = "/static/img/file.svg";
                    alt = "Characterization Icon";
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
                alt = "Characterization File Broken Icon";
                figure = (
                    <img class={imgClass} src={src} height={height} width={width} alt={alt} />
                );
                download = (
                    <em>Document not available</em>
                );
            }

            return (
                <section class="type-document view-detail panel status-none">
                    <div class="container">
                        <div class="row">
                            <div class="span6">
                                <figure>
                                    {figure}
                                </figure>
                            </div>
                            <div class="span5">
                                <h3 class="cap-me-once">{context.document_type}</h3>
                                <p>{context.description}</p>
                                <dl class="key-value">
                                	{context.caption ? <dt>Caption</dt> : null}
                                    {context.caption ? <dd>{context.caption}</dd> : null}

                                    <dt>Submitted by</dt>
                                    <dd>{context.submitted_by.title}</dd>

                                    <dt>Lab</dt>
                                    <dd>{context.lab.title}</dd>

                                    <dt>Grant</dt>
                                    <dd>{context.award.name}</dd>

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

    globals.panel_views.register(Document, 'document');
    globals.panel_views.register(Document, 'biosample_characterization');


    return biosample;
});
