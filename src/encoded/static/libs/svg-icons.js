import React from 'react';

const icons = {
    disclosure: <svg id="Disclosure" data-name="Disclosure" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 480 480" className="svg-icon svg-icon-disclosure"><circle class="cls-1" cx="240" cy="240" r="240"/><polyline class="cls-2" points="401.79 175.66 240 304.34 78.21 175.66"/></svg>,
    table: <svg id="Table" data-name="Table" xmlns="http://www.w3.org/2000/svg" width="29" height="17" viewBox="0 0 29 17" className="svg-icon svg-icon-table"><path d="M22,0H0V17H29V0H22ZM21,4.33V8H15V4.33h6ZM15,9h6v3H15V9Zm-1,3H8V9h6v3Zm0-7.69V8H8V4.33h6Zm-13,0H7V8H1V4.33ZM1,9H7v3H1V9Zm0,7V13H7v3H1Zm7,0V13h6v3H8Zm7,0V13h6v3H15Zm13,0H22V13h6v3Zm0-4H22V9h6v3Zm0-4H22V4.33h6V8Z"/></svg>,
    matrix: <svg id="Matrix" data-name="Matrix" xmlns="http://www.w3.org/2000/svg" width="29" height="17" viewBox="0 0 29 17" className="svg-icon svg-icon-matrix"><rect x="22" y="14" width="3" height="3"/><rect x="22" y="10" width="3" height="3"/><rect x="22" y="6" width="3" height="3"/><rect x="18" y="14" width="3" height="3"/><rect x="18" y="10" width="3" height="3"/><rect x="18" y="6" width="3" height="3"/><rect x="14" y="14" width="3" height="3"/><rect x="14" y="10" width="3" height="3"/><rect x="14" y="6" width="3" height="3"/><rect x="10" y="14" width="3" height="3"/><rect x="10" y="10" width="3" height="3"/><rect x="10" y="6" width="3" height="3"/><polygon points="25 5 22 5 25.98 0 28.98 0 25 5"/><polygon points="21 5 18 5 21.98 0 24.98 0 21 5"/><polygon points="17 5 14 5 17.98 0 20.98 0 17 5"/><polygon points="13 5 10 5 13.98 0 16.98 0 13 5"/><rect y="14" width="9" height="3"/><rect y="10" width="9" height="3"/><rect y="6" width="9" height="3"/></svg>,
    search: <svg id="Search" data-name="Search" xmlns="http://www.w3.org/2000/svg" width="29" height="17" viewBox="0 0 29 17" className="svg-icon svg-icon-search"><rect x="26" y="14" width="3" height="3"/><rect x="10" y="14" width="15.03" height="3"/><rect x="26" y="9.33" width="3" height="3"/><rect x="10" y="9.33" width="15.03" height="3"/><rect x="26" y="4.67" width="3" height="3"/><rect x="10" y="4.67" width="15.03" height="3"/><rect x="26" width="3" height="3"/><rect x="10" width="15.03" height="3"/><path d="M0,0V17H9V0H0ZM7.9,15.55H1.1v-2H7.9v2Zm0-4H1.1v-2H7.9v2Zm0-4H1.1v-2H7.9v2Zm0-4H1.1v-2H7.9v2Z"/></svg>,
    summary: <svg id="Summary" data-name="Summary" xmlns="http://www.w3.org/2000/svg" width="29" height="17" viewBox="0 0 29 17" className="svg-icon svg-icon-summary"><polygon points="18.06 10 9.72 7.09 1.05 16 1 16 1 0 0 0 0 17 29.03 17 29.03 0 18.06 10"/></svg>,
    orientV: <svg id="Orient Vertically" data-name="Orient Vertically" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 360 220" className="svg-icon svg-icon-orient-v"><path d="M326,0H230a18.05,18.05,0,0,0-18,18V44a18.06,18.06,0,0,0,18,18h38.41l-41,67.18-9.69-5.92L216.91,158l30.47-16.61-9.69-5.91L282.51,62H326a18,18,0,0,0,18-18V18A18,18,0,0,0,326,0Zm6,44a6,6,0,0,1-6,6H230a6,6,0,0,1-6-6V18a6,6,0,0,1,6-6h96a6,6,0,0,1,6,6V44ZM228,158H132a18,18,0,0,0-18,18v26a18,18,0,0,0,18,18h96a18,18,0,0,0,18-18V176A18,18,0,0,0,228,158Zm6,44a6,6,0,0,1-6,6H132a6,6,0,0,1-6-6V176a6,6,0,0,1,6-6h96a6,6,0,0,1,6,6v26Zm-90.91-44.05-0.84-34.69-9.69,5.92L91.55,62H130a18.06,18.06,0,0,0,18-18V18A18.05,18.05,0,0,0,130,0H34A18,18,0,0,0,16,18V44A18,18,0,0,0,34,62H77.49l44.82,73.43-9.69,5.91ZM136,44a6,6,0,0,1-6,6H34a6,6,0,0,1-6-6V18a6,6,0,0,1,6-6h96a6,6,0,0,1,6,6V44Z"/></svg>,
    orientH: <svg id="Orient Horizontally" data-name="Orient Horizontally" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 360 220" className="svg-icon svg-icon-orient-v"><path d="M342,79H246a18,18,0,0,0-17.34,13.23L209.38,64.55l-4.83,10.28L132,40.8V31.33A18.3,18.3,0,0,0,114,13H18A18.32,18.32,0,0,0,0,31.33v26A17.75,17.75,0,0,0,18,75h96a17.72,17.72,0,0,0,18-17.67V54.06l67.45,31.63L194.64,96l33.8-2.88A18,18,0,0,0,228,97v26a17.91,17.91,0,0,0,.58,4.47l-33.94-2.9,4.81,10.28L132,166.48v-3.82A17.73,17.73,0,0,0,114,145H18A17.75,17.75,0,0,0,0,162.67v26A18.32,18.32,0,0,0,18,207h96a18.3,18.3,0,0,0,18-18.33v-8.93l72.55-34L209.37,156l19.39-27.82A18,18,0,0,0,246,141h96a18,18,0,0,0,18-18V97A18,18,0,0,0,342,79ZM120,57a6,6,0,0,1-6,6H18a6,6,0,0,1-6-6V31a6,6,0,0,1,6-6h96a6,6,0,0,1,6,6V57Zm0,132a6,6,0,0,1-6,6H18a6,6,0,0,1-6-6V163a6,6,0,0,1,6-6h96a6,6,0,0,1,6,6v26Zm228-66a6,6,0,0,1-6,6H246a6,6,0,0,1-6-6V97a6,6,0,0,1,6-6h96a6,6,0,0,1,6,6v26Z"/></svg>
};

export const svgIcon = icon => icons[icon];

// Render the icon used to collapse a panel from the title bar.
//   collapsed: T if the icon should be rendered for the collapsed steate
//   handlecollapse: function to call when the icon is clicked
export const collapseIcon = (collapsed, addClasses) => (
    <svg className={`collapsing-title-control ${(addClasses ? ` ${addClasses}` : '')}`} data-name="Collapse Icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
        {collapsed ?
                <g>
                    <title>Panel collapsed</title>
                    <circle className="bg" cx="256" cy="256" r="240" />
                    <line className="content-line" x1="151.87" y1="256" x2="360.13" y2="256" />
                    <line className="content-line" x1="256" y1="151.87" x2="256" y2="360.13" />
                </g>
            :
                <g>
                    <title>Panel open</title>
                    <circle className="bg" cx="256" cy="256" r="240" />
                    <line className="content-line" x1="151.87" y1="256" x2="360.13" y2="256" />
                </g>
        }
    </svg>
);
