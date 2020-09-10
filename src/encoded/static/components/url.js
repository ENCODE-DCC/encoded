import React from 'react';
import _ from 'underscore';


export default function urlList(values) {
    // Render each of the links, with null for each value without an identifier property
    if (values && values.length > 0) {
        const links = _.compact(values.map((value) => {
            return values.map((value, index) =>
                <li key={index}>
                    <a href={value}>{value}</a>
                </li>
            );
        }));

        // Render any links into a ul. Just return null if no links to render.
        if (links.length > 0) {
            return (
                <ul>{links}</ul>
            );
        }
    }
    return null;
}
