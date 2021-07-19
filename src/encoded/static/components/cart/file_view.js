import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { Checkbox, isFileVisualizable } from '../objectutils';
import { addToFileViewAndSave, removeFromFileViewAndSave } from './actions';


/**
 * Displays and reacts to clicks in the 'In file view' checkbox.
 */
const CartFileViewToggleComponent = ({
    filePath,
    selected,
    disabled,
    inProgress,
    cartLocked,
    onAddToFileViewClick,
    onRemoveFromFileViewClick,
}) => {
    const handleClick = (e) => {
        // Checkbox lies on top of the link to the file, so have to stop the click here.
        e.stopPropagation();
        if (selected) {
            onRemoveFromFileViewClick();
        } else {
            onAddToFileViewClick();
        }
    };

    return (
        <Checkbox
            label="In file view"
            id={`file-view-check-${filePath}`}
            checked={selected}
            disabled={disabled || inProgress || cartLocked}
            clickHandler={handleClick}
            css="cart-file-view-checkbox"
        />
    );
};

CartFileViewToggleComponent.propTypes = {
    /** @id of the file this toggle controls */
    filePath: PropTypes.string.isRequired,
    /** True if file's view is selected */
    selected: PropTypes.bool.isRequired,
    /** True if file view toggle should appear disabled */
    disabled: PropTypes.bool.isRequired,
    /** True if cart operation in progress */
    inProgress: PropTypes.bool.isRequired,
    /** True if cart is locked */
    cartLocked: PropTypes.bool.isRequired,
    /** Called when the user clicks the file-view checkbox to add file to file view */
    onAddToFileViewClick: PropTypes.func.isRequired,
    /** Called when the user clicks the file-view checkbox to remove file from file view */
    onRemoveFromFileViewClick: PropTypes.func.isRequired,
};

CartFileViewToggleComponent.mapStateToProps = (state, ownProps) => ({
    filePath: ownProps.file['@id'],
    fileViewName: ownProps.fileViewName,
    inProgress: state.inProgress,
    cartLocked: state.locked,
});

CartFileViewToggleComponent.mapDispatchToProps = (dispatch, ownProps) => ({
    onAddToFileViewClick: () => dispatch(addToFileViewAndSave(ownProps.fileViewName, [ownProps.file['@id']], ownProps.fetch)),
    onRemoveFromFileViewClick: () => dispatch(removeFromFileViewAndSave(ownProps.fileViewName, [ownProps.file['@id']], ownProps.fetch)),
});

const CartFileViewToggleInternal = connect(
    CartFileViewToggleComponent.mapStateToProps,
    CartFileViewToggleComponent.mapDispatchToProps,
)(CartFileViewToggleComponent);

export const CartFileViewToggle = ({ file, fileViewName, selected, disabled }, reactContext) => (
    <CartFileViewToggleInternal
        file={file}
        fileViewName={fileViewName}
        selected={selected}
        disabled={disabled}
        fetch={reactContext.fetch}
    />
);

CartFileViewToggle.propTypes = {
    /** File being added */
    file: PropTypes.object.isRequired,
    /** Name of the current file view */
    fileViewName: PropTypes.string.isRequired,
    /** True if file's view is selected */
    selected: PropTypes.bool.isRequired,
    /** True if file view control should appear disabled */
    disabled: PropTypes.bool.isRequired,
};

CartFileViewToggle.contextTypes = {
    fetch: PropTypes.func,
};


/**
 * Displays and reacts to clicks in the 'Add selected files to file view' button.
 */
const CartFileViewAddAllComponent = ({ locked, inProgress, disabled, onAddAllToFileViewClick }) => (
    <button type="button" className="btn btn-info btn-sm file-view-controls__add" disabled={disabled || locked || inProgress} onClick={onAddAllToFileViewClick}>
        Add selected files to file view
    </button>
);

CartFileViewAddAllComponent.propTypes = {
    /** True if button should appear disabled for higher-level reasons */
    disabled: PropTypes.bool.isRequired,
    /** True if cart is locked */
    locked: PropTypes.bool.isRequired,
    /** True if cart operation in progress */
    inProgress: PropTypes.bool.isRequired,
    /** Function to call when the user clicks the 'Add all to file view' button */
    onAddAllToFileViewClick: PropTypes.func.isRequired,
};

CartFileViewAddAllComponent.mapStateToProps = (state) => ({
    inProgress: state.inProgress,
    locked: state.locked,
});

CartFileViewAddAllComponent.mapDispatchToProps = (dispatch, ownProps) => ({
    onAddAllToFileViewClick: () => dispatch(addToFileViewAndSave(
        ownProps.fileViewName,
        ownProps.filePaths,
        ownProps.fetch,
    )),
});

const CartFileViewAddAllInternal = connect(
    CartFileViewAddAllComponent.mapStateToProps,
    CartFileViewAddAllComponent.mapDispatchToProps
)(CartFileViewAddAllComponent);

export const CartFileViewAddAll = ({ files, fileViewName, disabled }, reactContext) => {
    const filePaths = files.filter((file) => isFileVisualizable(file)).map((file) => file['@id']);
    return (
        <CartFileViewAddAllInternal
            filePaths={filePaths}
            fileViewName={fileViewName}
            fetch={reactContext.fetch}
            disabled={disabled}
        />
    );
};

CartFileViewAddAll.propTypes = {
    files: PropTypes.array.isRequired,
    fileViewName: PropTypes.string.isRequired,
    disabled: PropTypes.bool,
};

CartFileViewAddAll.defaultProps = {
    disabled: false,
};

CartFileViewAddAll.contextTypes = {
    fetch: PropTypes.func,
};
