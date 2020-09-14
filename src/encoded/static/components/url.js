import React from 'react';


export default function urlList(values) {
    // Render each of the links, with null for each value without an identifier property
    if (values && values.length > 0) {
        const links = values.map((value) => {
            return (
                <li>
                    <a href={value}>{value}</a>
                </li>
            );
        });

        return (
            <ul>{links}</ul>
        );
    }
    return null;
}
