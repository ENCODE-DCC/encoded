'use strict';
var React = require('react');

var icons = {
    table: <svg id="Table" data-name="Table" xmlns="http://www.w3.org/2000/svg" width="29" height="17" viewBox="0 0 29 17"><title>table-tab-icon</title><path className="svg-icon svg-icon-table" d="M22,0H0V17H29V0H22ZM21,4.33V8H15V4.33h6ZM15,9h6v3H15V9Zm-1,3H8V9h6v3Zm0-7.69V8H8V4.33h6Zm-13,0H7V8H1V4.33ZM1,9H7v3H1V9Zm0,7V13H7v3H1Zm7,0V13h6v3H8Zm7,0V13h6v3H15Zm13,0H22V13h6v3Zm0-4H22V9h6v3Zm0-4H22V4.33h6V8Z"/></svg>,
    matrix: <svg className="svg-icon svg-icon-matrix" id="Matrix" data-name="Matrix" xmlns="http://www.w3.org/2000/svg" width="29" height="17" viewBox="0 0 29 17"><title>matrix-icon</title><rect x="22" y="14" width="3" height="3"/><rect x="22" y="10" width="3" height="3"/><rect x="22" y="6" width="3" height="3"/><rect x="18" y="14" width="3" height="3"/><rect x="18" y="10" width="3" height="3"/><rect x="18" y="6" width="3" height="3"/><rect x="14" y="14" width="3" height="3"/><rect x="14" y="10" width="3" height="3"/><rect x="14" y="6" width="3" height="3"/><rect x="10" y="14" width="3" height="3"/><rect x="10" y="10" width="3" height="3"/><rect x="10" y="6" width="3" height="3"/><polygon points="25 5 22 5 25.98 0 28.98 0 25 5"/><polygon points="21 5 18 5 21.98 0 24.98 0 21 5"/><polygon points="17 5 14 5 17.98 0 20.98 0 17 5"/><polygon points="13 5 10 5 13.98 0 16.98 0 13 5"/><rect y="14" width="9" height="3"/><rect y="10" width="9" height="3"/><rect y="6" width="9" height="3"/></svg>,
    search: <svg className="svg-icon svg-icon-search" id="Search" data-name="Search" xmlns="http://www.w3.org/2000/svg" width="29" height="17" viewBox="0 0 29 17"><title>search-icon</title><rect x="26" y="14" width="3" height="3"/><rect x="10" y="14" width="15.03" height="3"/><rect x="26" y="9.33" width="3" height="3"/><rect x="10" y="9.33" width="15.03" height="3"/><rect x="26" y="4.67" width="3" height="3"/><rect x="10" y="4.67" width="15.03" height="3"/><rect x="26" width="3" height="3"/><rect x="10" width="15.03" height="3"/><path d="M0,0V17H9V0H0ZM7.9,15.55H1.1v-2H7.9v2Zm0-4H1.1v-2H7.9v2Zm0-4H1.1v-2H7.9v2Zm0-4H1.1v-2H7.9v2Z"/></svg>
};


var SvgIcon = function(icon) {
    return icons[icon];
};

module.exports = SvgIcon;
