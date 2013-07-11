/** @jsx React.DOM */
define(['exports', 'react', 'globals'],
function (experiment, React, globals) {
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


    var Experiment = experiment.Experiment = React.createClass({
        render: function() {
            var context = this.props.context;
            var itemClass = globals.itemClass(context, 'view-item');
            var replicates = _.sortBy(context.replicates, function(item) {
                return item.biological_replicate_number;
            });
            var replicate = replicates[0];
            var documents = replicate && replicate.library.documents || [];
            var control = context.controls[0];
            return (
                <div class={itemClass}>
                    <header class="row">
                        <div class="span12">
                            {replicate ?
                                <ul class="breadcrumb">
                                    <li>Experiment <span class="divider">/</span></li>
                                    <li class="active">{replicate.assay.assay_name}</li>
                                </ul>
                            : null}
                            <h2>Experiment summary for {context.dataset_accession}</h2>
                        </div>
                    </header>
                    <div class="panel data-display">
                        <dl class="key-value">
                            <dt>Accession</dt>
                            <dd>{context.dataset_accession}</dd>

                            <dt hidden={!context.dataset_description}>Description</dt>
                            <dd hidden={!context.dataset_description}>{context.dataset_description}</dd>

                            {replicate ? <dt>Target</dt> : null}
                            {replicate ? <dd>{replicate.target}</dd> : null}

                            {replicate ? <dt>Biosample</dt> : null}
                            {replicate ? <dd>{replicate.library.biosample.biosample_term_name}</dd> : null}

                            {replicate ? <dt>Biosample Type</dt> : null}
                            {replicate ? <dd>{replicate.library.biosample.biosample_type}</dd> : null}

                            <dt hidden={!context.encode2_dbxref_list}>ENCODE2 Alias</dt>
                            <dd hidden={!context.encode2_dbxref_list}>{context.encode2_dbxref_list}</dd>

                            <dt>Submitted by</dt>
                            <dd>{context.submitter.first_name}{' '}{context.submitter.last_name}</dd>

                            <dt>Project</dt>
                            <dd>{context.award.project}</dd>

                            {replicate ? <dt>Antibody</dt> : null}
                            {replicate ? <dd>{replicate.antibody_accession}</dd> : null}
                        </dl>
                    </div>

                    <BiosamplesUsed replicates={replicates} />
                    <AssayDetails replicates={replicates} />

                    {documents.length ?
                        <div>
                            <h3>Protocols</h3>
                            {documents.map(Panel)}
                        </div>
                    : null}

                    {replicates.map(function (replicate, index) {
                        return (
                            <Replicate control={control} replicate={replicate} key={index} />
                        );
                    })}

                    <FilesLinked context={context} />                    
                </div>
            );
        }
    });

    globals.content_views.register(Experiment, 'experiment');


    var BiosamplesUsed = experiment.BiosamplesUsed = function (props) {
        var replicates = props.replicates;
        if (!replicates.length) return (<div hidden={true}></div>);
        return (
            <div>
                <h3>Biosamples Used</h3>
                <table>
                    <thead>
                        <tr>
                            <th>Accession</th>
                            <th>Term</th>
                            <th>Biological Replicate</th>
                            <th>Type</th>
                            <th>Species</th>
                            <th>Source</th>
                            <th>Submitter</th>
                        </tr>
                    </thead>
                    <tbody>

                    {replicates.map(function (replicate, index) {
                        return (
                            <tr key={index}>
                                <td>{replicate.library.biosample.accession}</td>
                                <td>{replicate.library.biosample.biosample_term_name}</td>
                                <td>{replicate.biological_replicate_number}</td>
                                <td>{replicate.library.biosample.biosample_type}</td>
                                <td>{replicate.library.biosample.donor.organism.organism_name}</td>
                                <td>{replicate.library.biosample.source.source_name}</td>
                                <td>{replicate.library.biosample.submitter.first_name}{' '}
                                 {replicate.library.biosample.submitter.last_name}</td>
                            </tr>
                        );
                    })}
                    </tbody>
                    <tfoot>
                        <tr>
                            <td colSpan="7"></td>
                        </tr>
                    </tfoot>
                </table>
            </div>
        );
    };


    var AssayDetails = experiment.AssayDetails = function (props) {
        var replicates = props.replicates
        if (!replicates.length) return (<div hidden={true}></div>);
        var replicate = replicates[0];
        var library = replicate.library;
        var platform = replicate.platform;
        var titles = {
            nucleic_acid_type: 'Nucleic Acid Type',
            nucleic_acid_starting_quantity: 'NA Starting Quantity',
            lysis_method: 'Lysis Method',
            extraction_method: 'Extraction Method',
            fragmentation_method: 'Fragmentation Method',
            size_range: 'Size Range',
            library_size_selection_method: 'Size Selection Method',
        };
        var children = [];
        for (name in titles) {
            if (library[name]) {
                children.push(<dt key={'dt-' + name}>{titles[name]}</dt>);
                children.push(<dd key={'dd-' + name}>{library[name]}</dd>);
            }
        }
        if (platform.description) {
            children.push(<dt key="dt-platform">Platform</dt>);
            children.push(<dd key="dd-platform"><a href={platform['@id']}>{platform.description}</a></dd>);
        }
        return (
            <div>
                <h3>Assay Details</h3>
                <dl class="panel key-value">
                    {children}
                </dl>
            </div>
        );
    };


    var Replicate = experiment.Replicate = function (props) {
        var replicate = props.replicate;
        var control = props.control;
        var library = replicate.library;
        var biosample = library.biosample;
        return (
            <div key={props.key}>
                <h3>Biological Replicate - {replicate.biological_replicate_number}</h3>
                <dl class="panel key-value">
                    <dt>Technical Replicate</dt>
                    <dd>{replicate.technical_replicate_number}</dd>

                    <dt>Library</dt>
                    <dd>{library.accession} - ({library.library_description})</dd>

                    {control ? <dt>Control</dt> : null}
                    {control ?
                        <dd>
                            <a href={control['@id']}>
                                {control.dataset_accession}
                            </a>
                        </dd>
                    : null}


                    <dt>Biosample</dt>
                    <dd>
                        <a href={biosample['@id']}>
                            {biosample.accession}
                        </a>
                    </dd>
                </dl>
            </div>
        );
    };

    // Can't be a proper panel as the control must be passed in.
    //globals.panel_views.register(Replicate, 'replicate');


    var FilesLinked = experiment.FilesLinked = function (props) {
        var context = props.context;
        var files = context.files;
        if (!files.length) return (<div hidden={true}></div>);
        return (
            <div>
                <h3>Files linked to {context.dataset_accession}</h3>
                <table>
                    <thead>
                        <tr>
                            <th>Accession</th>
                            <th>File Type</th>
                            <th>Associated Replicates</th>
                            <th>Added By</th>
                            <th>Date Added</th>
                            <th>File Download</th>
                        </tr>
                    </thead>
                    <tbody>
                    {files.map(function (file, index) {
                        var href = 'http://encodedcc.sdsc.edu/warehouse/' + file.file_name_encode3;
                        return (
                            <tr key={index}>
                                <td>{file.file_accession}</td>
                                <td>{file.file_format}</td>
                                <td>{file.biological_replicate_number ?
                                    '(' + file.biological_replicate_number + ', ' + file.technical_replicate_number + ')'
                                    : null}
                                </td>
                                <td>{file.submitter.first_name}{' '}{file.submitter.last_name}</td>
                                <td>{file.date_passed_validation}</td>
                                <td><a href={href} download><i class="icon-download-alt"></i> Download</a></td>
                            </tr>
                        );
                    })}
                    </tbody>
                    <tfoot>
                        <tr>
                            <td colSpan="6"></td>
                        </tr>
                    </tfoot>
                </table>
            </div>
        );
    };


    return experiment;
});
