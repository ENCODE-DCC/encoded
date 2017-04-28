import React from 'react';
import globals from './globals';

export function dbxref(attributes) {
    const value = attributes.value || '';
    const sep = value.indexOf(':');
    let prefix = attributes.prefix;
    let local;
    let id;

    if (prefix) {
        local = value;
    } else if (sep !== -1) {
        prefix = value.slice(0, sep);
        local = globals.encodedURIComponent(value.slice(sep + 1), '_');
    }

    // Handle two different kinds of GEO -- GSM/GSE vs SAMN
    if (prefix === 'GEO' && local.substr(0, 4) === 'SAMN') {
        prefix = 'GEOSAMN';
    }

    // Handle two different kinds of WormBase IDs -- Target vs Strain
    if (prefix === 'WormBase' && attributes.target_ref) {
        prefix = 'WormBaseTargets';
    }

    // Handle two different kinds of FlyBase IDs -- Target vs Stock
    if (prefix === 'FlyBase' && !attributes.target_ref) {
        prefix = 'FlyBaseStock';
    }

    const base = prefix && globals.dbxref_prefix_map[prefix];
    if (!base) {
        return <span>{value}</span>;
    }
    if (prefix === 'HGNC') {
        local = attributes.target_gene;

    // deal with UCSC links
    } else if (prefix === 'UCSC-ENCODE-cv') {
        local = `"${local}"`;
    } else if (prefix === 'MGI') {
        local = value;
    } else if (prefix === 'MGI.D') {
        id = value.substr(sep + 1);
        local = `${id}.shtml`;
    } else if (prefix === 'CGC') {
        id = value.substr(sep + 1);
        local = `${id}&field=all&exst=&exfield=all`;
    } else if (prefix === 'DSSC') {
        id = value.substr(sep + 1);
        local = `${id}&table=Species&submit=Search`;
    } else if (prefix === 'RBPImage') {
        if (attributes.cell_line) {
            local = `${attributes.cell_line}&targets=${local}`;
        } else {
            return <span>{value}</span>;
        }
    }

    return <a href={base + local}>{value}</a>;
}

export const DbxrefList = React.createClass({
    render: function () {
        const props = this.props;
        return (
            <ul className={props.className}>
                {props.values.map((value, index) =>
                    <li key={index}>{dbxref({ value: value, prefix: props.prefix, target_gene: props.target_gene, target_ref: props.target_ref, cell_line: props.cell_line })}</li>,
                )}
            </ul>
        );
    },
});
