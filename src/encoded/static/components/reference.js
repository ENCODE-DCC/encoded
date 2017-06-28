import React from 'react';
import _ from 'underscore';


export default function pubReferenceList(values) {
    // Render each of the links, with null for each value without an identifier property
    if (values && values.length) {
        const links = _.compact(values.map((value) => {
            if (value.identifiers) {
                return value.identifiers.map((identifier, index) =>
                    <li key={index}>
                        <a href={value['@id']}>{identifier}</a>
                    </li>
                );
            }
            return null;
        }));

        // Render any links into a ul. Just return null if no links to render.
        if (links.length) {
            return (
                <ul>{links}</ul>
            );
        }
    }
    return null;
}
