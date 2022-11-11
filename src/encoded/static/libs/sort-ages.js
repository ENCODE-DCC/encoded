import _ from 'underscore';


/**
 * Greater than the greatest reasonable number of days in an organism's life, useful for sorting
 * items at the end.
 */
const MAX_AGE_IN_DAYS = 100000000;


/**
 * Sort the array of ages combined with age units by their real age values -- least amount of time
 * to most. The `ages` array contains objects with this form:
 *
 * {
 *    age: '2',
 *    age_units: 'year',
 * }
 *
 * This works with much of the data in the portal. The returned array elements comprise strings like
 * "1 week" or "2 years". Note that `ages.age` can contain "90 or above" (treated as just 90) or
 * "unknown" (gets sorted at the end).
 * @param {array} ages Array of objects of the form { age: <number string>, age_units: <string> }
 * @param {object} options Options object with the following properties:
 * @param {boolean} options.dedupe Set to true to deduplicate the returned array. Default is true.
 * @returns {array} Sorted, deduplicated array of "{age} {age_units}" strings
 */
const sortAges = (ages, options = { dedupe: true }) => {
    // Calculate the total number of days in each age/age_units pair, and generate a parallel array
    // of these ages-in-days to use as a sorting key.
    const agesInDays = ages.map((ageParts) => {
        let ageNum;
        if (ageParts.age === '90 or above') {
            ageNum = 90 * 365;
        } else if (ageParts.age === 'unknown') {
            ageNum = MAX_AGE_IN_DAYS;
        } else {
            ageNum = parseInt(ageParts.age, 10);
            switch (ageParts.age_units) {
            case 'year':
            case 'years':
                ageNum *= 365;
                break;
            case 'month':
            case 'months':
                ageNum *= 30;
                break;
            case 'week':
            case 'weeks':
                ageNum *= 7;
                break;
            case 'day':
            case 'days':
            default:
                break;
            }
        }
        return ageNum;
    });

    // Sort the age/age_units pairs array using the ages-in-days array.
    const sortedAges = _(ages).sortBy((ageParts, index) => agesInDays[index]);

    // Convert the sorted age/age_units pairs array to an array of composed strings.
    const composedAges = sortedAges.map((ageParts) => {
        if (ageParts.age === '90 or above') {
            return '90 or above years';
        }
        if (ageParts.age === 'unknown') {
            return 'unknown';
        }

        // Properly pluralize the age unit if it's not "1" and not already plural.
        const ageUnitString = ageParts.age_units
            ? ` ${ageParts.age_units}${ageParts.age !== '1' && ageParts.age_units.slice(-1) !== 's' ? 's' : ''}`
            : '';

        return `${ageParts.age}${ageUnitString}`;
    });

    // Remove duplicates if requested.
    return options.dedupe ? _.uniq(composedAges) : composedAges;
};


export default sortAges;
