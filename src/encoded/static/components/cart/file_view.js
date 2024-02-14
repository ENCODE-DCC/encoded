import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import BooleanToggle from '../../libs/ui/boolean-toggle';
import { Modal, ModalHeader, ModalBody, ModalFooter } from '../../libs/ui/modal';
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
    <button type="button" className="btn btn-info btn-sm file-view-controls__control" disabled={disabled || locked || inProgress} onClick={onAddAllToFileViewClick}>
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

const CartFileViewAddAll = ({ files, fileViewName, disabled }, reactContext) => {
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


/**
 * Displays and reacts to clicks in the 'Remove selected files from file view' button.
 */
const CartFileViewRemoveAllComponent = ({
    locked,
    inProgress,
    disabled,
    isFileViewOnly,
    onRemoveAllFromFileViewClick,
}) => {
    const [isWarningVisible, setIsWarningVisible] = React.useState(false);

    /**
     * Called when the user clicks the Remove button to remove all selected files from the file
     * view and close the alert.
     */
    const handleSubmitClick = () => {
        setIsWarningVisible(false);
        onRemoveAllFromFileViewClick();
    };

    /**
     * Handle the user closing the alert.
     */
    const handleClose = () => {
        setIsWarningVisible(false);
    };

    return (
        <>
            <button
                type="button"
                className="btn btn-info btn-sm file-view-controls__control"
                disabled={disabled || locked || inProgress}
                onClick={() => { setIsWarningVisible(true); }}
            >
                {`Remove ${isFileViewOnly ? 'all' : 'selected'} files from file view`}
            </button>
            {isWarningVisible &&
                <Modal
                    labelId="remove-from-file-view-label"
                    descriptionId="remove-from-file-view-description"
                    focusId="remove-from-file-view-close"
                    closeModal={handleClose}
                >
                    <ModalHeader labelId="remove-from-file-view-label" title="Remove from file view" closeModal={handleClose} />
                    <ModalBody>
                        <p>{`Remove ${isFileViewOnly ? 'all' : 'currently selected'} files from the file view.`}</p>
                    </ModalBody>
                    <ModalFooter
                        closeModal={<button type="button" id="remove-from-file-view-close" onClick={handleClose} className="btn btn-default">Cancel</button>}
                        submitBtn={
                            <button
                                type="button"
                                onClick={handleSubmitClick}
                                disabled={inProgress}
                                className="btn btn-danger"
                                id="remove-from-file-view-submit"
                            >
                                Remove
                            </button>
                        }
                    />
                </Modal>
            }
        </>
    );
};

CartFileViewRemoveAllComponent.propTypes = {
    /** True if button should appear disabled for higher-level reasons */
    disabled: PropTypes.bool.isRequired,
    /** True if cart is locked */
    locked: PropTypes.bool.isRequired,
    /** True if cart operation in progress */
    inProgress: PropTypes.bool.isRequired,
    /** True if file view switch is enabled */
    isFileViewOnly: PropTypes.bool.isRequired,
    /** Function to call when the user clicks the 'Remove all from file view' button */
    onRemoveAllFromFileViewClick: PropTypes.func.isRequired,
};

CartFileViewRemoveAllComponent.mapStateToProps = (state) => ({
    inProgress: state.inProgress,
    locked: state.locked,
});

CartFileViewRemoveAllComponent.mapDispatchToProps = (dispatch, ownProps) => ({
    onRemoveAllFromFileViewClick: () => dispatch(removeFromFileViewAndSave(
        ownProps.fileViewName,
        ownProps.filePaths,
        ownProps.fetch,
    )),
});

const CartFileViewRemoveAllInternal = connect(
    CartFileViewRemoveAllComponent.mapStateToProps,
    CartFileViewRemoveAllComponent.mapDispatchToProps
)(CartFileViewRemoveAllComponent);

const CartFileViewRemoveAll = ({ files, fileViewName, disabled, isFileViewOnly }, reactContext) => {
    const filePaths = files.filter((file) => isFileVisualizable(file)).map((file) => file['@id']);
    return (
        <CartFileViewRemoveAllInternal
            filePaths={filePaths}
            fileViewName={fileViewName}
            fetch={reactContext.fetch}
            disabled={disabled}
            isFileViewOnly={isFileViewOnly}
        />
    );
};

CartFileViewRemoveAll.propTypes = {
    files: PropTypes.array.isRequired,
    fileViewName: PropTypes.string.isRequired,
    disabled: PropTypes.bool,
    isFileViewOnly: PropTypes.bool,
};

CartFileViewRemoveAll.defaultProps = {
    disabled: false,
    isFileViewOnly: false,
};

CartFileViewRemoveAll.contextTypes = {
    fetch: PropTypes.func,
};


/**
 * Display the toggle to show only files within the file view, or the normal display.
 */
export const CartFileViewOnlyToggle = ({ isFileViewOnly, updateFileViewOnly, selectedFilesInFileView }) => (
    <BooleanToggle
        id="file-view-toggle"
        state={isFileViewOnly}
        title={
            <>
                {selectedFilesInFileView.length > 0
                    ? <div className="cart-tab__count">{selectedFilesInFileView.length} </div>
                    : null}
                <>File view</>
            </>
        }
        voice={`File view containing ${selectedFilesInFileView.length} file${selectedFilesInFileView.length === 1 ? '' : 's'}`}
        triggerHandler={() => { updateFileViewOnly(); }}
        disabled={selectedFilesInFileView.length === 0}
        options={{
            cssSwitch: 'file-view-toggle',
            cssTitle: 'file-view-toggle__title',
        }}
    />
);

CartFileViewOnlyToggle.propTypes = {
    /** True if files view only enabled */
    isFileViewOnly: PropTypes.bool.isRequired,
    /** Called when the user clicks the toggle */
    updateFileViewOnly: PropTypes.func.isRequired,
    /** Array of files within the current file view */
    selectedFilesInFileView: PropTypes.array.isRequired,
};


/**
 * Show the file-view controls, which currently only includes a button to add all selected
 * visualizable files to the current cart's file view.
 */
export const FileViewControl = ({ files, fileViewName, fileViewControlsEnabled, isFileViewOnly, disabled }) => (
    <div className="file-view-controls">
        {fileViewControlsEnabled
            ? (
                <>
                    <CartFileViewAddAll
                        files={files}
                        fileViewName={fileViewName}
                        disabled={disabled || files.length === 0 || isFileViewOnly}
                    />
                    <CartFileViewRemoveAll
                        files={files}
                        fileViewName={fileViewName}
                        isFileViewOnly={isFileViewOnly}
                        disabled={disabled || files.length === 0}
                    />
                </>
            ) : null}
    </div>
);

FileViewControl.propTypes = {
    /** File objects to add to file view */
    files: PropTypes.array,
    /** Name of the current file view */
    fileViewName: PropTypes.string,
    /** True to enable the "Add all to file view" button */
    fileViewControlsEnabled: PropTypes.bool,
    /** True if "File view" switch selected */
    isFileViewOnly: PropTypes.bool,
    /** True if control should appear disabled */
    disabled: PropTypes.bool,
};

FileViewControl.defaultProps = {
    files: [],
    fileViewName: '',
    fileViewControlsEnabled: false,
    isFileViewOnly: false,
    disabled: false,
};
