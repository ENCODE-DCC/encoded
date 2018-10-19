/**
 * Function to indicate that a cart operation is in progress.
 */
import { cartOperationInProgress } from './actions';


/**
 * Indicate in the cart store that a cart operation is in progress. This lets components disable
 * themselves if needed during long cart operations.
 * @param {object} cartObj Saved cart object to be cached
 * @param {func} dispatch Redux dispatch function for the cart store
 */
const cartSetOperationInProgress = (inProgress, dispatch) => {
    dispatch(cartOperationInProgress(inProgress));
};

export default cartSetOperationInProgress;
