import PropTypes from 'prop-types';

const SVG = ({ handleClick, handleHighlight, BodyList }) => (
    <svg id="BodyMap" className="human-map" data-name="Layer 1" xmlns="http://www.w3.org/2000/svg" xmlnsXlink="http://www.w3.org/1999/xlink" viewBox="0 0 607 768" onClick={handleClick ? (e) => handleClick(e) : null} onMouseOver={handleHighlight ? (e) => handleHighlight(e, BodyList) : null}>

        <defs>
            <linearGradient id="linear-gradient" x1="347.47" y1="671.06" x2="347.47" y2="547.97" gradientUnits="userSpaceOnUse"><stop offset="0" stopColor="#fff" /><stop offset="1" /></linearGradient><linearGradient id="linear-gradient-2" x1="226.81" y1="657.42" x2="252.04" y2="535.07" xlinkHref="#linear-gradient" /><mask id="mask" x="71.78" y="187.87" width="442.93" height="920.88" maskUnits="userSpaceOnUse"><polygon className="cls-1" points="390.83 519.74 304.11 582.31 304.11 744.38 390.83 744.38 390.83 519.74" /></mask><mask id="mask-2" x="182.7" y="450.91" width="111.06" height="538.6" maskUnits="userSpaceOnUse"><rect className="cls-2" x="182.7" y="531.12" width="96.3" height="213.4" /></mask><clipPath id="clip-path"><rect id="SVGID" className="cls-3" x="288.4" y="553.94" width="54.76" height="119.56" /></clipPath><clipPath id="clip-path-2"><polygon id="SVGID-2" data-name="SVGID" className="cls-3" points="206.14 671.39 288.4 673.5 288.4 553.94 206.14 551.83 206.14 671.39" /></clipPath><clipPath id="clip-path-3"><path id="SVGID-3" data-name="SVGID" className="cls-3" d="M328.53,50.57A14.06,14.06,0,0,1,330.62,60c-.69,5.63,2.46,4.41,2.43,6.6s-2.88,5.61-4.76,5.59-1.94,5.93-6.65,6.81-18.17.74-18.5,2.3,2.05,12.24-3.93,15-9.81,9-15.13,8.61-5.7,5.88-10.1,7.4-2.25,5.3-10.08,5.21-9.1,2.1-15.34-.17-7.15-5.09-7.14-6.34-14.64-7-13.28-16.74c0-4.7-7.13-6-1.54-16.62.82-2.81-3.17-10.37,4.08-14.36,2.21-1.86-1.14-11,8.6-13.69,2.84-1.22,1-6.56,7.6-7.43s6.34-7.13,13.23-7.06,6-.24,8.48-2.1,6.3-2.74,8.48-2.09,6-1.89,9.4-.09,4.42-3,10-.52,11.27,0,13.72,4.73,5.61,2.88,9.35,4.8,3.37,6.93,4.62,7.26S328.53,50.57,328.53,50.57Z" /></clipPath><clipPath id="clip-path-4"><path className="cls-4" d="M322.77,83.39s11.17-2.38,14.11-4.34c0,0,.82,6.4-1.59,8.61C335.29,87.66,329,89.1,322.77,83.39Z" /></clipPath><clipPath id="clip-path-5"><path id="SVGID-4" data-name="SVGID" className="cls-3" d="M406.11,406.52s24.34-15,36.79-10.13c0,0,12,36.56,17.25,59.59s18.39,125.77,18.39,125.77-11.16,7-23,4.35C455.55,586.1,415.31,482.34,406.11,406.52Z" /></clipPath><clipPath id="clip-path-7"><path className="cls-3" d="M372.92,234.93s-46,135,73,120c0,0,5-98-27-111S372.92,234.93,372.92,234.93Z" /></clipPath><linearGradient id="linear-gradient-3" x1="461.73" y1="539.76" x2="457.57" y2="518.97" gradientTransform="translate(-0.46 -0.47) rotate(-0.12)" gradientUnits="userSpaceOnUse"><stop offset="0%" stopColor="#fff" /><stop offset="100%" stopColor="#266ba2" /></linearGradient><linearGradient id="linear-gradient-4" x1="423.48" y1="413.95" x2="426.16" y2="439.5" gradientTransform="translate(-0.46 -0.47) rotate(-0.12)" gradientUnits="userSpaceOnUse"><stop offset="0%" stopColor="#266ba2" /><stop offset="9%" stopColor="#3978aa" /><stop offset="27%" stopColor="#6b9ac0" /><stop offset="53%" stopColor="#bbd0e2" /><stop offset="73%" stopColor="#fff" /><stop offset="83%" stopColor="#fdfefe" /><stop offset="87%" stopColor="#f6f9fb" /><stop offset="9%" stopColor="#eaf1f6" /><stop offset="92%" stopColor="#d9e5ef" /><stop offset="94%" stopColor="#c3d6e5" /><stop offset="95%" stopColor="#a7c3d9" /><stop offset="97%" stopColor="#86adcb" /><stop offset="98%" stopColor="#6093bb" /><stop offset="100%" stopColor="#3676a9" /><stop offset="100%" stopColor="#266ba2" /></linearGradient><linearGradient id="linear-gradient-5" x1="440.41" y1="535.31" x2="443.55" y2="576.14" gradientTransform="translate(-0.46 -0.47) rotate(-0.12)" gradientUnits="userSpaceOnUse"><stop offset="0%" stopColor="#266ba2" /><stop offset="53" stopColor="#fff" /><stop offset="100%" stopColor="#266ba2" /></linearGradient><clipPath id="clip-path-8"><circle className="cls-3" cx="520.17" cy="407.18" r="32.75" /></clipPath>
        </defs>

        <title>Homo sapiens clickable body map</title>
    </svg>
);

SVG.propTypes = {
    handleClick: PropTypes.func,
    handleHighlight: PropTypes.func,
    BodyList: PropTypes.object.isRequired,
};

SVG.defaultProps = {
    handleClick: null,
    handleHighlight: null,
};

export default SVG;
