// based off https://stackoverflow.com/a/31615643/178550
/**
 * Gets the number along with an  ordinal from the set (th, st, nd, rd).
 *
 * @param {number or string} number (Implicitly converted to the number type if not already of type number)
 * @returns Number with ordinal suffix
 */
const getNumberWithOrdinal = (number) => {
    const suffix = ['th', 'st', 'nd', 'rd'];
    const percentage = number % 100;

    return number + (suffix[(percentage - 20) % 10] || suffix[percentage] || suffix[0]);
};

export default getNumberWithOrdinal;
