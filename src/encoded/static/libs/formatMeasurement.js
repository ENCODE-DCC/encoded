
/**
* Takes a magnitude and unit (singular form) and returns the measurement
* with the proper unit in singular or plural, depending on magnitude.
* Invalid measurements are turned as- Unknown
* @param {number} magnitude - Measured value
* @param {string} unit - Measurement system in singular form
*/
const formatMeasurement = (magnitude, unit) => {
    if (!magnitude || (magnitude.toLowerCase && magnitude.toLowerCase()) === 'unknown') {
        return 'Unknown';
    }

    // parseFloat used because parseInt only keeps integer
    const magnitudeAsFloat = parseFloat(magnitude);
    const isMagnitudeNumeric = !Number.isNaN(magnitudeAsFloat);
    const isUnitSingular = !isMagnitudeNumeric || magnitudeAsFloat === 1;

    const measurement = `${magnitude} ${unit || ''}`.trim();

    return isUnitSingular
          ? measurement
          : `${measurement}s`;
};

export default formatMeasurement;
