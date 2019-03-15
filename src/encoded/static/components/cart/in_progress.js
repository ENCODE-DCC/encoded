/**
 * Function to indicate that a cart operation is in progress.
 */
import { cartOperationInProgress } from './actions';


/**
 * Indicate in the cart store that a cart operation is in progress. This lets components disable
 * themselves if needed during long cart operations.
 * @param {bool} inProgress True if cart operation is in progress
 * @param {func} dispatch Redux dispatch function for the cart store
 */
const cartSetOperationInProgress = (inProgress, dispatch) => {
    dispatch(cartOperationInProgress(inProgress));
};

export default cartSetOperationInProgress;
