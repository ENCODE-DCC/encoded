// Spinner based on https://codepen.io/aurer/pen/jEGbA
const spinner = (style) => (
    <svg
        id="Spinner"
        data-name="Spinner"
        version="1.1"
        xmlns="http://www.w3.org/2000/svg"
        width="100%"
        height="100%"
        viewBox="0 0 50 50"
        style={style}
        className="svg-icon svg-icon-spinner"
    >
        <path fill="#000" d="M43.935,25.145c0-10.318-8.364-18.683-18.683-18.683c-10.318,0-18.683,8.365-18.683,18.683h4.068c0-8.071,6.543-14.615,14.615-14.615c8.072,0,14.615,6.543,14.615,14.615H43.935z" />
    </svg>
);

const search = (style) => (
    <svg id="Search" data-name="Search" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024" width="17" height="17" style={style} className="svg-icon svg-icon-search">
        <path d="M1006.16,96H17.84C7.99,96,0,88.01,0,78.16V17.84C0,7.99,7.99,0,17.84,0h988.32c9.85,0,17.84,7.99,17.84,17.84 v60.32C1024,88.01,1016.01,96,1006.16,96z" />
        <path d="M1006.16,1024H17.84C7.99,1024,0,1016.01,0,1006.16v-60.32C0,935.99,7.99,928,17.84,928h988.32 c9.85,0,17.84,7.99,17.84,17.84v60.32C1024,1016.01,1016.01,1024,1006.16,1024z" />
        <path d="M1006.16,560H17.84C7.99,560,0,552.01,0,542.16v-60.32C0,471.99,7.99,464,17.84,464h988.32 c9.85,0,17.84,7.99,17.84,17.84v60.32C1024,552.01,1016.01,560,1006.16,560z" />
        <path d="M1006.16,328H17.84C7.99,328,0,320.01,0,310.16v-60.32C0,239.99,7.99,232,17.84,232h988.32 c9.85,0,17.84,7.99,17.84,17.84v60.32C1024,320.01,1016.01,328,1006.16,328z" />
        <path d="M1006.16,792H17.84C7.99,792,0,784.01,0,774.16v-60.32C0,703.99,7.99,696,17.84,696h988.32 c9.85,0,17.84,7.99,17.84,17.84v60.32C1024,784.01,1016.01,792,1006.16,792z" />
    </svg>
);

const matrix = (style) => (
    <svg id="Matrix" xmlns="http://www.w3.org/2000/svg" width="17" height="17" viewBox="0 0 1024 1024" cstyle={style} className="svg-icon svg-icon-matrix">
        <path d="M1006.16,1024H849.84c-9.85,0-17.84-7.99-17.84-17.84V849.84c0-9.85,7.99-17.84,17.84-17.84h156.32 c9.85,0,17.84,7.99,17.84,17.84v156.32C1024,1016.01,1016.01,1024,1006.16,1024z" />
        <path d="M1006.16,756H849.84c-9.85,0-17.84-7.99-17.84-17.84V581.84c0-9.85,7.99-17.84,17.84-17.84h156.32 c9.85,0,17.84,7.99,17.84,17.84v156.32C1024,748.01,1016.01,756,1006.16,756z" />
        <path d="M1006.16,488H849.84c-9.85,0-17.84-7.99-17.84-17.84V313.84c0-9.85,7.99-17.84,17.84-17.84h156.32 c9.85,0,17.84,7.99,17.84,17.84v156.32C1024,480.01,1016.01,488,1006.16,488z" />
        <path d="M1006.56,220H849.44c-9.85,0-17.84-7.99-17.84-17.84V17.84C831.6,7.99,839.58,0,849.44,0h157.13 c9.85,0,17.84,7.99,17.84,17.84v184.32C1024.4,212.01,1016.42,220,1006.56,220z" />
        <path d="M738.16,1024H581.84c-9.85,0-17.84-7.99-17.84-17.84V849.84c0-9.85,7.99-17.84,17.84-17.84h156.32 c9.85,0,17.84,7.99,17.84,17.84v156.32C756,1016.01,748.01,1024,738.16,1024z" />
        <path d="M738.16,756H581.84c-9.85,0-17.84-7.99-17.84-17.84V581.84c0-9.85,7.99-17.84,17.84-17.84h156.32 c9.85,0,17.84,7.99,17.84,17.84v156.32C756,748.01,748.01,756,738.16,756z" />
        <path d="M738.16,488H581.84c-9.85,0-17.84-7.99-17.84-17.84V313.84c0-9.85,7.99-17.84,17.84-17.84h156.32 c9.85,0,17.84,7.99,17.84,17.84v156.32C756,480.01,748.01,488,738.16,488z" />
        <path d="M738.56,220H581.44c-9.85,0-17.84-7.99-17.84-17.84V17.84C563.6,7.99,571.58,0,581.44,0h157.13 c9.85,0,17.84,7.99,17.84,17.84v184.32C756.4,212.01,748.42,220,738.56,220z" />
        <path d="M470.16,1024H313.84c-9.85,0-17.84-7.99-17.84-17.84V849.84c0-9.85,7.99-17.84,17.84-17.84h156.32 c9.85,0,17.84,7.99,17.84,17.84v156.32C488,1016.01,480.01,1024,470.16,1024z" />
        <path d="M470.16,756H313.84c-9.85,0-17.84-7.99-17.84-17.84V581.84c0-9.85,7.99-17.84,17.84-17.84h156.32 c9.85,0,17.84,7.99,17.84,17.84v156.32C488,748.01,480.01,756,470.16,756z" />
        <path d="M470.16,488H313.84c-9.85,0-17.84-7.99-17.84-17.84V313.84c0-9.85,7.99-17.84,17.84-17.84h156.32 c9.85,0,17.84,7.99,17.84,17.84v156.32C488,480.01,480.01,488,470.16,488z" />
        <path d="M470.56,220H313.44c-9.85,0-17.84-7.99-17.84-17.84V17.84C295.6,7.99,303.58,0,313.44,0h157.13 c9.85,0,17.84,7.99,17.84,17.84v184.32C488.4,212.01,480.42,220,470.56,220z" />
        <path d="M219.98,313.44v157.13c0,9.85-7.99,17.84-17.84,17.84H17.82c-9.85,0-17.84-7.99-17.84-17.84V313.44 c0-9.85,7.99-17.84,17.84-17.84h184.32C211.99,295.6,219.98,303.58,219.98,313.44z" />
        <path d="M219.98,581.44v157.13c0,9.85-7.99,17.84-17.84,17.84H17.82c-9.85,0-17.84-7.99-17.84-17.84V581.44 c0-9.85,7.99-17.84,17.84-17.84h184.32C211.99,563.6,219.98,571.58,219.98,581.44z" />
        <path d="M219.98,849.44v157.13c0,9.85-7.99,17.84-17.84,17.84H17.82c-9.85,0-17.84-7.99-17.84-17.84V849.44 c0-9.85,7.99-17.84,17.84-17.84h184.32C211.99,831.6,219.98,839.58,219.98,849.44z" />
    </svg>
);

const table = (style) => (
    <svg id="Table" xmlns="http://www.w3.org/2000/svg" width="17" height="17" viewBox="0 0 1024 1024" style={style} className="svg-icon svg-icon-table">
        <path d="M0,0v1024h1024V0H0z M46.42,220.82H488v152.68H46.42V220.82z M46.42,421.49H488v152.89H46.42V421.49z
            M46.42,622.39H488v152.89H46.42V622.39z M46.42,823.28H488v154.3H46.42V823.28z M977.58,977.58H536v-154.3h441.58V977.58z
            M977.58,775.28H536V622.39h441.58V775.28z M977.58,574.39H536V421.49h441.58V574.39z M977.58,373.49H536V220.82h441.58V373.49z"
        />
    </svg>
);

const largeArrow = (style) => (
    <svg id="Large arrow" data-name="Large arrow" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 49 17" style={style} className="svg-icon svg-icon-large-arrow">
        <polygon points="39.98,0 38.56,1.52 44.95,7.46 -0.02,7.46 -0.02,9.54 44.95,9.54 38.56,15.48 39.98,17 49.12,8.5 " />
    </svg>
);

const genomeBrowser = (style) => (
    <svg version="1.1" data-name="Genome browser" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000" style={style} className="svg-icon svg-icon-genome-browser">
        <polygon points="500.06,232.95 0.11,1000 1000,1000" />
        <rect x="267" width="466" height="153.41" />
    </svg>
);

const cellGroup = (style) => (
    <svg aria-hidden="true" focusable="false" data-prefix="fas" data-icon="download" className="svg-inline--fa fa-download fa-w-16" role="img" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 30 30" style={style}>
        <ellipse cx="2" cy="2" rx="12" ry="9" className="js-cell" />
        <ellipse cx="2" cy="2" rx="6.5" ry="6" className="js-cell" />
        <ellipse cx="-5" cy="10" rx="12" ry="9" className="js-cell" />
        <ellipse cx="-5" cy="10" rx="6.5" ry="5" className="js-cell" />
        <ellipse cx="10" cy="10" rx="12" ry="9" className="js-cell" />
        <ellipse cx="10" cy="10" rx="6.5" ry="5" className="js-cell" />
    </svg>
);

const expandArrows = (style) => (
    <svg className="expand-arrows" width="1em" height="1em" viewBox="0 0 16 16" style={style} fill="currentColor" xmlns="http://www.w3.org/2000/svg">
        <path fillRule="evenodd" d="M1.464 10.536a.5.5 0 0 1 .5.5v3h3a.5.5 0 0 1 0 1h-3.5a.5.5 0 0 1-.5-.5v-3.5a.5.5 0 0 1 .5-.5z" />
        <path fillRule="evenodd" d="M5.964 10a.5.5 0 0 1 0 .707l-4.146 4.147a.5.5 0 0 1-.707-.708L5.257 10a.5.5 0 0 1 .707 0zm8.854-8.854a.5.5 0 0 1 0 .708L10.672 6a.5.5 0 0 1-.708-.707l4.147-4.147a.5.5 0 0 1 .707 0z" />
        <path fillRule="evenodd" d="M10.5 1.5A.5.5 0 0 1 11 1h3.5a.5.5 0 0 1 .5.5V5a.5.5 0 0 1-1 0V2h-3a.5.5 0 0 1-.5-.5zm4 9a.5.5 0 0 0-.5.5v3h-3a.5.5 0 0 0 0 1h3.5a.5.5 0 0 0 .5-.5V11a.5.5 0 0 0-.5-.5z" />
        <path fillRule="evenodd" d="M10 9.964a.5.5 0 0 0 0 .708l4.146 4.146a.5.5 0 0 0 .708-.707l-4.147-4.147a.5.5 0 0 0-.707 0zM1.182 1.146a.5.5 0 0 0 0 .708L5.328 6a.5.5 0 0 0 .708-.707L1.889 1.146a.5.5 0 0 0-.707 0z" />
        <path fillRule="evenodd" d="M5.5 1.5A.5.5 0 0 0 5 1H1.5a.5.5 0 0 0-.5.5V5a.5.5 0 0 0 1 0V2h3a.5.5 0 0 0 .5-.5z" />
    </svg>
);

const collapseArrows = (style) => (
    <svg className="collapse-arrows" width="1em" height="1em" viewBox="0 0 16 16" style={style} fill="currentColor" xmlns="http://www.w3.org/2000/svg">
        <path fillRule="evenodd" d="M9.5 2.036a.5.5 0 0 1 .5.5v3.5h3.5a.5.5 0 0 1 0 1h-4a.5.5 0 0 1-.5-.5v-4a.5.5 0 0 1 .5-.5z" />
        <path fillRule="evenodd" d="M14.354 1.646a.5.5 0 0 1 0 .708l-4.5 4.5a.5.5 0 1 1-.708-.708l4.5-4.5a.5.5 0 0 1 .708 0zm-7.5 7.5a.5.5 0 0 1 0 .708l-4.5 4.5a.5.5 0 0 1-.708-.708l4.5-4.5a.5.5 0 0 1 .708 0z" />
        <path fillRule="evenodd" d="M2.036 9.5a.5.5 0 0 1 .5-.5h4a.5.5 0 0 1 .5.5v4a.5.5 0 0 1-1 0V10h-3.5a.5.5 0 0 1-.5-.5z" />
    </svg>
);

const lockOpen = (style) => (
    <svg version="1.1" data-name="Lock open" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 249 249" style={style} className="svg-icon svg-icon-lock-open">
        <path d="M180.7,3.5c-30.2,0-54.77,24.57-54.77,54.77v57.41h-95.9c-8.8,0-16,7.2-16,16V229c0,8.8,7.2,16,16,16h116.27
            c8.8,0,16-7.2,16-16v-97.32c0-8.8-7.2-16-16-16h-3.37V58.27c0-20.82,16.94-37.77,37.77-37.77s37.77,16.94,37.77,37.77v40.18
            c0,4.69,3.81,8.5,8.5,8.5s8.5-3.81,8.5-8.5V58.27C235.47,28.07,210.9,3.5,180.7,3.5z"
        />
    </svg>
);

const lockClosed = (style) => (
    <svg version="1.1" data-name="Lock closed" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 249 249" style={style} className="svg-icon svg-icon-lock-open">
        <path d="M182.89,115.15h-3.37V82.74c0-30.2-24.57-54.77-54.77-54.77c-30.2,0-54.77,24.57-54.77,54.77v32.41h-3.37
            c-8.8,0-16,7.2-16,16v97.32c0,8.8,7.2,16,16,16h116.27c8.8,0,16-7.2,16-16v-97.32C198.89,122.35,191.69,115.15,182.89,115.15z
            M86.98,82.74c0-20.82,16.94-37.77,37.77-37.77s37.77,16.94,37.77,37.77v32.41H86.98V82.74z"
        />
    </svg>
);

const chevronLeft = () => (
    <svg version="1.1" xmlns="http://www.w3.org/2000/svg" width="7.359" height="12" viewBox="0 0 7.281 12">
        <path d="M0.192,5.534l5.341-5.341c0.258-0.258,0.676-0.258,0.931,0l0.624,0.624c0.258,0.258,0.258,0.673,0,0.931l-4.231,4.25 l4.231,4.253c0.255,0.258,0.255,0.673,0,0.931l-0.624,0.624c-0.258,0.258-0.676,0.258-0.931,0L0.192,6.466 C-0.064,6.207-0.064,5.79,0.192,5.534z" />
    </svg>
);

const chevronRight = () => (
    <svg version="1.1" xmlns="http://www.w3.org/2000/svg" width="7.359" height="12" viewBox="0 0 7.359 12">
        <path d="M7.165,6.466l-5.341,5.341c-0.258,0.258-0.676,0.258-0.931,0L0.27,11.183c-0.258-0.258-0.258-0.673,0-0.931L4.5,6.001 L0.27,1.749c-0.255-0.258-0.255-0.673,0-0.931l0.624-0.624c0.258-0.258,0.676-0.258,0.931,0l5.341,5.341 C7.423,5.79,7.423,6.207,7.165,6.466z" />
    </svg>
);

const clipboard = (style) => (
    <svg version="1.1" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 249 249" style={style} className="svg-icon svg-icon-clipboard">
        <path d="M164,24.5h26.54c6.31,0,11.46,5.05,11.46,11.23v190.05c0,6.17-5.16,11.23-11.46,11.23H57.46
            C51.16,237,46,231.95,46,225.77V35.73c0-6.17,5.16-11.23,11.46-11.23H84"
        />
        <rect x="84" y="11" width="80" height="46" />
    </svg>
);

const checkbox = (style) => (
    <svg version="1.1" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" style={style} className="svg-icon svg-icon-checkbox">
        <path d="M173.898 439.404l-166.4-166.4c-9.997-9.997-9.997-26.206
            0-36.204l36.203-36.204c9.997-9.998 26.207-9.998 36.204 0L192 312.69 432.095
            72.596c9.997-9.997 26.207-9.997 36.204 0l36.203 36.204c9.997 9.997 9.997 26.206 0
            36.204l-294.4 294.401c-9.998 9.997-26.207 9.997-36.204-.001z"
        />
    </svg>
);

const dataset = (style) => (
    <svg version="1.1" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 500" style={style} className="svg-icon svg-icon-archive">
        <polygon points="354.26,235.5 314.26,235.5 314.26,277.69 185.74,277.69 185.74,235.5 145.74,235.5 145.74,317.69 354.26,317.69" />
        <path d="M500.5,37.5h-501v148h38v278h425v-278h38V37.5z M39.5,77.5h421v68h-421V77.5z M422.5,423.5h-345v-238h345V423.5z" />
        <polygon points="354.26,317.69 145.74,317.69 145.74,235.5 185.74,235.5 185.74,277.69 314.26,277.69 314.26,235.5 354.26,235.5" />
    </svg>
);

const file = (style) => (
    <svg version="1.1" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 500" style={style} className="svg-icon svg-icon-file">
        <g>
            <path d="M156.73,187.92c-28.12,0-44.92-18.83-44.92-50.31v-16.64c0-31.48,16.8-50.31,44.92-50.31s44.92,18.83,44.92,50.31v16.64
                C201.65,169.09,184.85,187.92,156.73,187.92z M172.51,137.29v-16.02c0-18.44-4.92-26.88-15.78-26.88s-15.78,8.44-15.78,26.88v16.02
                c0,18.44,4.92,26.88,15.78,26.88S172.51,155.73,172.51,137.29z"
            />
            <path d="M211.28,185.65v-22.27h28.12V98.77h-1.48l-26.64,18.36V92.45l28.12-19.53h27.89v90.47h26.72v22.27H211.28z" />
            <path d="M343.43,187.92c-28.12,0-44.92-18.83-44.92-50.31v-16.64c0-31.48,16.8-50.31,44.92-50.31s44.92,18.83,44.92,50.31v16.64
                C388.36,169.09,371.56,187.92,343.43,187.92z M359.22,137.29v-16.02c0-18.44-4.92-26.88-15.78-26.88s-15.78,8.44-15.78,26.88v16.02
                c0,18.44,4.92,26.88,15.78,26.88S359.22,155.73,359.22,137.29z"
            />
            <path d="M118.68,325.65v-22.27h28.12v-64.61h-1.48l-26.64,18.36v-24.69l28.12-19.53h27.89v90.47h26.72v22.27H118.68z" />
            <path d="M211.2,325.65v-22.27h28.12v-64.61h-1.48l-26.64,18.36v-24.69l28.12-19.53h27.89v90.47h26.72v22.27H211.2z" />
            <path d="M343.35,327.92c-28.12,0-44.92-18.83-44.92-50.31v-16.64c0-31.48,16.8-50.31,44.92-50.31s44.92,18.83,44.92,50.31v16.64
                C388.28,309.09,371.48,327.92,343.35,327.92z M359.14,277.29v-16.02c0-18.44-4.92-26.88-15.78-26.88s-15.78,8.44-15.78,26.88v16.02
                c0,18.44,4.92,26.88,15.78,26.88S359.14,295.73,359.14,277.29z"
            />
        </g>
        <path d="M0,0v500h349h40.98H390v-0.02L499.98,390H500v-0.02V350V0H0z M40,40h420v310H350v110H40V40z M390,443.41V390h53.41 L390,443.41z" />
    </svg>
);

const download = (style) => (
    <svg aria-hidden="true" focusable="false" data-prefix="fas" data-icon="download" className="svg-inline--fa fa-download fa-w-16" role="img" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" style={style}>
        <path fill="currentColor" d="M216 0h80c13.3 0 24 10.7 24 24v168h87.7c17.8 0 26.7 21.5 14.1 34.1L269.7 378.3c-7.5 7.5-19.8 7.5-27.3 0L90.1 226.1c-12.6-12.6-3.7-34.1 14.1-34.1H192V24c0-13.3 10.7-24 24-24zm296 376v112c0 13.3-10.7 24-24 24H24c-13.3 0-24-10.7-24-24V376c0-13.3 10.7-24 24-24h146.7l49 49c20.1 20.1 52.5 20.1 72.6 0l49-49H488c13.3 0 24 10.7 24 24zm-124 88c0-11-9-20-20-20s-20 9-20 20 9 20 20 20 20-9 20-20zm64 0c0-11-9-20-20-20s-20 9-20 20 9 20 20 20 20-9 20-20z" />
    </svg>
);

const venus = (style) => (
    <svg version="1.1" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024" style={style} className="svg-icon svg-icon-venus">
        <path d="M818.38,332.69c0-168.94-137.44-306.38-306.38-306.38S205.62,163.75,205.62,332.69
            c0,156.06,117.32,285.15,268.38,303.93v130.69H314.88v71.25H474v159.12h71.25V838.56h159.12v-71.25H545.25V637.23
            C698.6,620.6,818.38,490.39,818.38,332.69z M286.38,332.69c0-124.41,101.22-225.62,225.62-225.62s225.62,101.22,225.62,225.62
            S636.41,558.31,512,558.31S286.38,457.1,286.38,332.69z"
        />
    </svg>
);

const mars = (style) => (
    <svg version="1.1" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024" style={style} className="svg-icon svg-icon-mars">
        <path d="M628.38,136.75v80.75H749.4L629.19,337.71c-51.63-39.6-116.13-63.21-186.07-63.21
            c-168.94,0-306.38,137.44-306.38,306.38s137.44,306.38,306.38,306.38S749.5,749.81,749.5,580.88c0-69.94-23.61-134.44-63.21-186.07
            L806.5,274.6v121.03h80.75V136.75H628.38z M443.12,806.5c-124.41,0-225.62-101.22-225.62-225.62s101.22-225.62,225.62-225.62
            s225.62,101.22,225.62,225.62S567.53,806.5,443.12,806.5z"
        />
    </svg>
);

const edit = (style) => (
    <svg version="1.1" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 250 250" style={style} className="svg-icon svg-icon-edit">
        <path d="M78.7,160c-1.7,5.7,3.6,11,9.3,9.3l45.8-13.3l86.4-86.4l-41.8-41.8L92,114.2L78.7,160z M204.7,1.5l-13.3,13.3l41.8,41.8
            l13.3-13.3c5.3-5.3,5.3-13.9,0-19.2L223.9,1.5C218.6-3.8,210-3.8,204.7,1.5z"
        />
        <polygon points="171.7,164.1 171.7,223.8 26.4,223.8 26.4,78.5 86,78.5 112,52.5 0.4,52.5 0.4,249.8 197.7,249.8 197.7,138.1" />
    </svg>
);

const magnifyingGlass = (style) => (
    <svg version="1.1" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" style={style} className="svg-icon svg-icon-magnifying-glass">
        <path d="M505,442.7L405.3,343c-4.5-4.5-10.6-7-17-7H372c27.6-35.3,44-79.7,44-128C416,93.1,322.9,0,208,0S0,93.1,0,208
            s93.1,208,208,208c48.3,0,92.7-16.4,128-44v16.3c0,6.4,2.5,12.5,7,17l99.7,99.7c9.4,9.4,24.6,9.4,33.9,0l28.3-28.3
            C514.3,467.3,514.3,452.1,505,442.7z M208,336c-70.7,0-128-57.2-128-128c0-70.7,57.2-128,128-128c70.7,0,128,57.2,128,128
            C336,278.7,278.8,336,208,336z"
        />
    </svg>
);

const questionCircle = (style) => (
    <svg version="1.1" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" style={style} className="svg-icon svg-icon-question-circle">
        <path d="M504,256c0,137-111,248-248,248S8,393,8,256C8,119.1,119,8,256,8S504,119.1,504,256z M262.7,90c-54.5,0-89.3,23-116.5,63.8
            c-3.5,5.3-2.4,12.4,2.7,16.3l34.7,26.3c5.2,3.9,12.6,3,16.7-2.1c17.9-22.7,30.1-35.8,57.3-35.8c20.4,0,45.7,13.1,45.7,33
            c0,15-12.4,22.7-32.5,34C247.1,238.5,216,254.9,216,296v4c0,6.6,5.4,12,12,12h56c6.6,0,12-5.4,12-12v-1.3
            c0-28.5,83.2-29.6,83.2-106.7C379.2,134,319,90,262.7,90z M256,338c-25.4,0-46,20.6-46,46c0,25.4,20.6,46,46,46s46-20.6,46-46
            C302,358.6,281.4,338,256,338z"
        />
    </svg>
);

const user = (style) => (
    <svg version="1.1" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512" style={style} className="svg-icon svg-icon-user">
        <path d="M224,256c70.7,0,128-57.3,128-128S294.7,0,224,0S96,57.3,96,128S153.3,256,224,256z M134.4,288C85,297,0,348.2,0,422.4V464
            c0,26.5,0,48,48,48h352c48,0,48-21.5,48-48v-41.6c0-74.2-92.8-125.4-134.4-134.4S183.8,279,134.4,288z"
        />
    </svg>
);

const twitter = (style) => (
    <svg version="1.1" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" style={style} className="svg-icon svg-icon-twitter">
        <path d="M24,4.6c-0.9,0.4-1.8,0.7-2.8,0.8c1-0.6,1.8-1.6,2.2-2.7c-1,0.6-2,1-3.1,1.2c-0.9-1-2.2-1.6-3.6-1.6c-3.2,0-5.5,3-4.8,6
            C7.7,8.1,4.1,6.1,1.7,3.1C0.4,5.4,1,8.3,3.2,9.7C2.4,9.7,1.6,9.5,1,9.1c-0.1,2.3,1.6,4.4,3.9,4.9c-0.7,0.2-1.5,0.2-2.2,0.1
            c0.6,2,2.4,3.4,4.6,3.4c-2.1,1.6-4.7,2.3-7.3,2c2.2,1.4,4.8,2.2,7.5,2.2c9.1,0,14.3-7.7,14-14.6C22.5,6.4,23.3,5.5,24,4.6z"
        />
    </svg>
);

const icons = {
    disclosure: (style) => <svg id="Disclosure" data-name="Disclosure" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 480 480" style={style} className="svg-icon svg-icon-disclosure"><circle cx="240" cy="240" r="240" /><polyline points="401.79 175.66 240 304.34 78.21 175.66" /></svg>,
    table,
    matrix,
    search,
    orientV: (style) => <svg id="Orient Vertically" data-name="Orient Vertically" xmlns="http://www.w3.org/2000/svg" width="29" height="17" viewBox="0 0 360 220" style={style} className="svg-icon svg-icon-orient-v"><path d="M326,0H230a18.05,18.05,0,0,0-18,18V44a18.06,18.06,0,0,0,18,18h38.41l-41,67.18-9.69-5.92L216.91,158l30.47-16.61-9.69-5.91L282.51,62H326a18,18,0,0,0,18-18V18A18,18,0,0,0,326,0Zm6,44a6,6,0,0,1-6,6H230a6,6,0,0,1-6-6V18a6,6,0,0,1,6-6h96a6,6,0,0,1,6,6V44ZM228,158H132a18,18,0,0,0-18,18v26a18,18,0,0,0,18,18h96a18,18,0,0,0,18-18V176A18,18,0,0,0,228,158Zm6,44a6,6,0,0,1-6,6H132a6,6,0,0,1-6-6V176a6,6,0,0,1,6-6h96a6,6,0,0,1,6,6v26Zm-90.91-44.05-0.84-34.69-9.69,5.92L91.55,62H130a18.06,18.06,0,0,0,18-18V18A18.05,18.05,0,0,0,130,0H34A18,18,0,0,0,16,18V44A18,18,0,0,0,34,62H77.49l44.82,73.43-9.69,5.91ZM136,44a6,6,0,0,1-6,6H34a6,6,0,0,1-6-6V18a6,6,0,0,1,6-6h96a6,6,0,0,1,6,6V44Z" /></svg>,
    orientH: (style) => <svg id="Orient Horizontally" data-name="Orient Horizontally" xmlns="http://www.w3.org/2000/svg" width="29" height="17" viewBox="0 0 360 220" style={style} className="svg-icon svg-icon-orient-v"><path d="M342,79H246a18,18,0,0,0-17.34,13.23L209.38,64.55l-4.83,10.28L132,40.8V31.33A18.3,18.3,0,0,0,114,13H18A18.32,18.32,0,0,0,0,31.33v26A17.75,17.75,0,0,0,18,75h96a17.72,17.72,0,0,0,18-17.67V54.06l67.45,31.63L194.64,96l33.8-2.88A18,18,0,0,0,228,97v26a17.91,17.91,0,0,0,.58,4.47l-33.94-2.9,4.81,10.28L132,166.48v-3.82A17.73,17.73,0,0,0,114,145H18A17.75,17.75,0,0,0,0,162.67v26A18.32,18.32,0,0,0,18,207h96a18.3,18.3,0,0,0,18-18.33v-8.93l72.55-34L209.37,156l19.39-27.82A18,18,0,0,0,246,141h96a18,18,0,0,0,18-18V97A18,18,0,0,0,342,79ZM120,57a6,6,0,0,1-6,6H18a6,6,0,0,1-6-6V31a6,6,0,0,1,6-6h96a6,6,0,0,1,6,6V57Zm0,132a6,6,0,0,1-6,6H18a6,6,0,0,1-6-6V163a6,6,0,0,1,6-6h96a6,6,0,0,1,6,6v26Zm228-66a6,6,0,0,1-6,6H246a6,6,0,0,1-6-6V97a6,6,0,0,1,6-6h96a6,6,0,0,1,6,6v26Z" /></svg>,
    cart: (style) => <svg id="Cart" data-name="Cart" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" style={style}><path d="M12,12.23H6.5a1.5,1.5,0,0,0,.11.13,1.48,1.48,0,0,1,.31.79,1.42,1.42,0,0,1-.3,1,1.46,1.46,0,0,1-2.23.12,1.31,1.31,0,0,1-.4-.8,1.46,1.46,0,0,1,.33-1.17,1.43,1.43,0,0,1,.35-.3s0,0,0-.08c-.18-.88-.37-1.77-.55-2.65s-.29-1.45-.44-2.18-.33-1.61-.5-2.41C3.11,4.14,3,3.58,2.88,3c0-.06,0-.08-.1-.08H1.05a.69.69,0,0,1-.4-.11.65.65,0,0,1-.27-.51V1.85a.64.64,0,0,1,.54-.6h.19c.84,0,1.68,0,2.51,0a.68.68,0,0,1,.75.62c.06.33.13.67.2,1,0,.06,0,.07.09.07H14.91a.64.64,0,0,1,.66.78c-.17.76-.34,1.52-.52,2.28s-.37,1.63-.55,2.44l-.18.79a.64.64,0,0,1-.6.47H6.05c-.08,0-.08,0-.07.08,0,.23.1.46.14.69a.09.09,0,0,0,.11.08h7a.65.65,0,0,1,.44.15.62.62,0,0,1,.21.65c0,.19-.08.38-.13.57,0,0,0,.06,0,.07A1.43,1.43,0,0,1,14.51,13a1.37,1.37,0,0,1-.32,1.18,1.39,1.39,0,0,1-.81.5,1.45,1.45,0,0,1-1.25-.29,1.46,1.46,0,0,1-.54-.94,1.44,1.44,0,0,1,.33-1.16Z" /></svg>,
    asterisk: (style) => <svg id="Asterisk" data-name="Asterisk" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" style={style}><polygon points="15.68 5.3 14.18 2.7 8.94 6.38 9.5 0 6.5 0 7.06 6.38 1.82 2.7 0.32 5.3 6.13 8 0.32 10.7 1.82 13.3 7.06 9.62 6.5 16 9.5 16 8.94 9.62 14.18 13.3 15.68 10.7 9.87 8 15.68 5.3" /></svg>,
    chevronDown: (style) => <svg id="Chevron Down" data-name="Chevron Down" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 249 124" className="svg-icon svg-icon-chevron-down" style={style}><polygon points="249,57 124.5,124 0,57 0,0 124.5,67 249,0" /></svg>,
    chevronUp: (style) => <svg id="Chevron Up" data-name="Chevron Up" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 249 124" className="svg-icon svg-icon-chevron-up" style={style}><polygon points="249,67 124.5,0 0,67 0,124 124.5,57 249,124" /></svg>,
    circle: (style) => <svg version="1.1" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 500" style={style} className="svg-icon svg-icon-circle"><circle cx="250" cy="250" r="250" /></svg>,
    multiplication: (style) => <svg version="1.1" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 500" style={style} className="svg-icon svg-icon-multiplication"><polygon points="500,99 401,0 250,151.01 99,0 0,99 151.01,250 0,401 99,500 250,348.99 401,500 500,401 348.99,250" /></svg>,
    chevronLeft,
    chevronRight,
    spinner,
    largeArrow,
    genomeBrowser,
    collapseArrows,
    expandArrows,
    lockOpen,
    lockClosed,
    clipboard,
    checkbox,
    dataset,
    file,
    download,
    cellGroup,
    venus,
    mars,
    edit,
    magnifyingGlass,
    questionCircle,
    user,
    twitter,
};

/**
 * Render an SVG icon specified by `icon` which must match a property of the `icons` variable above.
 * Can optionally add css styles as a React style object to the SVG element.
 * @param {string} icon Specifies which icon to show; property of `icons`
 * @param {object} style React CSS styles (not classes) to add to svg
 */
export const svgIcon = (icon, style) => icons[icon](style);

/**
 * Render the icon used to collapse a panel from the title bar.
 * @param {boolean} collapsed - True if the icon should be rendered for the collapsed state
 * @param {string} addClasses - CSS classes to add to <SVG> icon element
 */
export const collapseIcon = (collapsed, addClasses) => (
    <svg className={`collapsing-title-control${addClasses ? ` ${addClasses}` : ''}`} data-name="Collapse Icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
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
