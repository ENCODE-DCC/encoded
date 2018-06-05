
/**
* Takes a magnitude and unit (singular form) and returns the measurement
* with the proper unit in singular or plural, depending on magnitude.
* Invalid measurements are turned as- Unknown
* @param {number} magnitude - Measured value
* @param {string} unit - Measurement system in singular form
*/
export default function formatMeasurement(magnitude, unit) {
    // parseFloat used because parseInt only keeps integer
    const magnitudeAsFloat = parseFloat(magnitude);

    if (Number.isNaN(magnitudeAsFloat)) {
        return 'Unknown';
    }

    if (magnitudeAsFloat === 0) {
        return '0';
    }

    const measurement = `${magnitudeAsFloat} ${unit || ''}`.trim();

    return magnitudeAsFloat === 1
          ? measurement
          : `${measurement}s`;
}
