import React from 'react';
import PropTypes from 'prop-types';
import _ from 'underscore';
import FallbackBlockEdit from './blocks/fallback';
import closest from '../libs/closest';
import offset from '../libs/offset';
import { Modal, ModalHeader, ModalBody, ModalFooter } from '../libs/bootstrap/modal';
import * as globals from './globals';


const LAYOUT_CONTEXT = {
    dragStart: PropTypes.func,
    dragOver: PropTypes.func,
    dragEnd: PropTypes.func,
    change: PropTypes.func,
    remove: PropTypes.func,
    editable: PropTypes.bool,
    src_pos: PropTypes.array,
    dst_pos: PropTypes.array,
    dst_quad: PropTypes.string,
    blocks: PropTypes.object,
};

const MODAL_CONTEXT = {
    // Persona
    fetch: PropTypes.func,
    session: PropTypes.object,
    session_properties: PropTypes.object,
    // HistoryAndTriggers
    adviseUnsavedChanges: PropTypes.func,
    navigate: PropTypes.func,
    // App
    listActionsFor: PropTypes.func,
    currentResource: PropTypes.func,
    location_href: PropTypes.string,
    portal: PropTypes.object,
};

class BlockEditModal extends React.Component {
    constructor(props) {
        super(props);

        // Set the initial React state
        this.state = { value: this.props.value };

        // Bind this to non-React methods.
        this.onChange = this.onChange.bind(this);
        this.openModal = this.openModal.bind(this);
        this.cancel = this.cancel.bind(this);
        this.save = this.save.bind(this);
    }

    getChildContext() {
        return this.props.modalcontext;
    }

    onChange(value) {
        this.setState({ value });
    }

    openModal() {
        this.modal.openModal();
    }

    cancel() {
        if (this.props.onCancel !== undefined) {
            this.props.onCancel();
        }
    }

    save() {
        this.props.onChange(this.state.value);
    }

    render() {
        const blocktype = globals.blocks.lookup(this.props.value);
        const BlockEdit = blocktype.edit || FallbackBlockEdit;
        return (
            <Modal ref={(c) => { this.modal = c; }} actuator={this.props.actuator}>
                <ModalHeader title={`Edit ${blocktype.label}`} closeModal={this.cancel} />
                <ModalBody>
                    <BlockEdit schema={blocktype.schema} value={this.state.value} onChange={this.onChange} />
                </ModalBody>
                <ModalFooter
                    closeBtn={<button className="btn btn-default" onClick={this.cancel}>Cancel</button>}
                    submitBtn={this.save}
                />
            </Modal>
        );
    }
}

BlockEditModal.propTypes = {
    modalcontext: PropTypes.object,
    value: PropTypes.any,
    onCancel: PropTypes.func,
    onChange: PropTypes.func,
    actuator: PropTypes.element,
};

BlockEditModal.defaultProps = {
    modalcontext: null,
    value: '',
    onCancel: undefined,
    onChange: undefined,
    actuator: undefined,
};

BlockEditModal.childContextTypes = MODAL_CONTEXT;


class Block extends React.Component {
    constructor() {
        super();

        // Set initial React state.
        this.state = { hover: false, focused: false };

        // Bind this to non-React methods.
        this.onChange = this.onChange.bind(this);
        this.onCancelEdit = this.onCancelEdit.bind(this);
        this.mouseEnter = this.mouseEnter.bind(this);
        this.mouseLeave = this.mouseLeave.bind(this);
        this.focus = this.focus.bind(this);
        this.blur = this.blur.bind(this);
        this.dragStart = this.dragStart.bind(this);
        this.dragOver = this.dragOver.bind(this);
        this.remove = this.remove.bind(this);
    }

    componentDidMount() {
        if (this.props.value.is_new) { this.modal.openModal(); }
    }

    componentDidUpdate() {
        if (this.props.value.is_new) { this.modal.openModal(); }
    }

    onChange(value) {
        delete value.is_new;
        this.context.change(value);
    }

    onCancelEdit() {
        if (this.props.value.is_new) {
            this.remove();
        }
    }

    mouseEnter() { this.setState({ hover: true }); }
    mouseLeave() { this.setState({ hover: false }); }
    focus() { this.setState({ focused: true }); }
    blur() { this.setState({ focused: false }); }

    dragStart(e) { this.context.dragStart(e, this.props.value, this.props.pos); }
    dragOver(e) { this.context.dragOver(e, this); }

    remove() {
        this.context.remove(this.props.value, this.props.pos);
    }

    renderToolbar() {
        const modal = (<BlockEditModal
            ref={(c) => { this.modal = c; }}
            modalcontext={_.pick(this.context, Object.keys(MODAL_CONTEXT))}
            value={this.props.value}
            onChange={this.onChange}
            onCancel={this.onCancelEdit}
            actuator={<a className="edit"><i className="icon icon-edit" /></a>}
        />);
        return (
            <div className="block-toolbar">
                {modal}
                {' '}
                <button
                    type="button" className="remove"
                    onClick={this.remove}
                ><i className="icon icon-trash-o" /></button>
            </div>
        );
    }

    render() {
        const block = this.props.value;
        if (typeof block['@type'] === 'string') {
            block['@type'] = [block['@type'], 'block'];
        }
        const BlockView = globals.blocks.lookup(block).view;

        const classes = {
            block: true,
            clearfix: true,
        };
        if (_.isEqual(this.props.pos, this.context.src_pos)) {
            classes.dragging = true;
        }
        if (this.state.hover) {
            classes.hover = true;
        }
        if (block.className !== undefined) {
            classes[block.className] = true;
        }
        if (_.isEqual(this.props.pos, this.context.dst_pos)) {
            classes[`drop-${this.context.dst_quad}`] = true;
        }
        const classStr = Object.keys(classes).join(' ');
        return (<div
            className={`${block['@type'][0]} ${classStr}`}
            data-pos={this.props.pos}
            draggable={this.context.editable && !this.state.focused}
            onDragStart={this.dragStart}
            onDragOver={this.dragOver}
            onDragEnd={this.context.dragEnd}
            onMouseEnter={this.mouseEnter}
            onMouseLeave={this.mouseLeave}
            onFocus={this.focus}
            onBlur={this.blur}
            ref={(comp) => { this.domNode = comp; }}
        >
            {this.context.editable ? this.renderToolbar() : ''}
            <BlockView value={block} onChange={this.onChange} />
        </div>);
    }
}

Block.propTypes = {
    value: PropTypes.any.isRequired,
    pos: PropTypes.array,
};

Block.defaultProps = {
    pos: null,
};

Block.contextTypes = Object.assign({}, MODAL_CONTEXT, LAYOUT_CONTEXT);


class BlockAddButton extends React.Component {
    static click(e) { e.preventDefault(); }

    constructor() {
        super();

        // Bind this to non-React methods.
        this.dragStart = this.dragStart.bind(this);
    }

    dragStart(e) {
        let block = {
            '@type': [this.props.blocktype, 'block'],
            is_new: true,
        };
        if (this.props.blockprops.initial !== undefined) {
            delete block.is_new;
            block = _.extend({}, block, this.props.blockprops.initial);
        }
        this.context.dragStart(e, block);
    }

    render() {
        const classes = `icon-lg ${this.props.blockprops.icon}`;
        return (
            <span>
                <button
                    className="btn btn-primary navbar-btn btn-sm"
                    onClick={BlockAddButton.click}
                    draggable="true" onDragStart={this.dragStart} onDragEnd={this.context.dragEnd}
                    title={this.props.blockprops.label}
                >
                    <span className={classes} />
                </button>
                {' '}
            </span>
        );
    }
}

BlockAddButton.propTypes = {
    blocktype: PropTypes.string.isRequired,
    blockprops: PropTypes.object.isRequired,
};

BlockAddButton.contextTypes = LAYOUT_CONTEXT;


// "sticky" toolbar for editing layout
class LayoutToolbar extends React.Component {
    constructor() {
        super();

        // Set initial React state.
        this.state = { fixed: false };

        // Bind this to non-React methods.
        this.scrollspy = this.scrollspy.bind(this);
    }

    componentDidMount() {
        this.origTop = offset(this.domNode).top;
        globals.bindEvent(window, 'scroll', this.scrollspy);
    }

    componentWillUnmount() {
        globals.unbindEvent(window, 'scroll', this.scrollspy);
    }

    scrollspy() {
        this.setState({ fixed: window.pageYOffset > this.origTop });
    }

    render() {
        const blocks = globals.blocks.getAll();
        const toolbar = (
            <div className={'layout-toolbar navbar navbar-default'} ref={(comp) => { this.domNode = comp; }}>
              <div className="container-fluid">
                <div className="navbar-left">
                    {Object.keys(blocks).map((b) => {
                        const blockprops = blocks[b];
                        if (blockprops.edit !== null) {
                            return <BlockAddButton key={b} blocktype={b} blockprops={blocks[b]} />;
                        }
                        return null;
                    })}
                </div>
                <div className="navbar-right">
                    <a href="" className="btn btn-default navbar-btn">Cancel</a>
                    {' '}
                    <button onClick={this.context.onTriggerSave} disabled={!this.context.canSave()} className="btn btn-success navbar-btn">Save</button>
                </div>
              </div>
            </div>
        );
        if (this.state.fixed) {
            return (
                <div>
                    <div className="layout-toolbar navbar navbar-fixed-top">
                        <div className="container"><div className="col-md-12">{toolbar}</div></div>
                    </div>
                    <div className="layout-toolbar navbar navbar-default" />
                </div>
            );
        }
        return toolbar;
    }
}

LayoutToolbar.contextTypes = {
    canSave: PropTypes.func,
    onTriggerSave: PropTypes.func,
};


class Col extends React.Component {
    constructor() {
        super();

        // Bind this to non-React methods.
        this.dragOver = this.dragOver.bind(this);
    }

    dragOver(e) { this.context.dragOver(e, this); }

    renderBlock(blockId, k) {
        const pos = this.props.pos.concat([k]);
        if (typeof blockId === 'string') {
            const block = this.context.blocks[blockId];
            return <Block value={block} key={blockId} pos={pos} />;
        }
        const row = blockId;
        return <Row value={row} key={k} pos={pos} />;
    }

    render() {
        const classes = {};
        classes[this.props.className] = true;
        if (_.isEqual(this.props.pos, this.context.dst_pos)) {
            classes[`drop-${this.context.dst_quad}`] = true;
        }
        const blocks = this.props.value.blocks;
        const classStr = Object.keys(classes).join(' ');
        return (
            <div
                className={classStr} onDragOver={this.dragOver}
                ref={(comp) => { this.domNode = comp; }}
            >
                {blocks.map((blockId, k) => this.renderBlock(blockId, k))}
            </div>
        );
    }
}

Col.propTypes = {
    pos: PropTypes.array,
    className: PropTypes.string,
    value: PropTypes.any,
};

Col.contextTypes = LAYOUT_CONTEXT;


class Row extends React.Component {
    constructor() {
        super();

        // Bind this to non-React methods.
        this.dragOver = this.dragOver.bind(this);
    }

    dragOver(e) { this.context.dragOver(e, this); }

    render() {
        const classes = {
            row: true,
        };
        if (_.isEqual(this.props.pos, this.context.dst_pos)) {
            classes[`drop-${this.context.dst_quad}`] = true;
        }
        const classStr = Object.keys(classes).join(' ');
        const cols = this.props.value.cols;
        let colClass;
        switch (cols.length) {
        case 2:
            colClass = 'col-md-6'; break;
        case 3:
            colClass = 'col-md-4'; break;
        case 4:
            colClass = 'col-md-3'; break;
        default:
            colClass = 'col-md-12'; break;
        }
        return (
            <div
                className={classStr} onDragOver={this.dragOver}
                ref={(comp) => { this.domNode = comp; }}
            >
                {cols.map((col, j) => <Col
                    value={col} className={col.className || colClass}
                    key={j} pos={this.props.pos.concat([j])}
                />)}
            </div>
        );
    }
}

Row.propTypes = {
    pos: PropTypes.array,
    value: PropTypes.any,
};

Row.contextTypes = LAYOUT_CONTEXT;


export default class Layout extends React.Component {
    static stateFromProps(props) {
        let value = props.value;

        const blockMap = {};
        let nextBlockNum = 2;
        value.blocks.forEach((block) => {
            const blockId = block['@id'];
            blockMap[blockId] = block;
            const blockNum = parseInt(blockId.replace(/\D/g, ''), 10);
            if (blockNum >= nextBlockNum) nextBlockNum = blockNum + 1;
        });
        value = Object.assign({}, value, { blocks: blockMap });

        return {
            nextBlockNum,
            value,
            src_pos: null,
            dst_pos: null,
            dst_quad: null,
        };
    }

    static isBlockDragEvent(e) {
        const types = e.dataTransfer.types;
        if (types.indexOf && types.indexOf('application/x-encoded-block') !== -1) {
            return true;
        } else if (types.contains && types.contains('application/x-encoded-block')) {
            return true;
        }
        e.preventDefault();
        return false;
    }

    static drop(e) {
        if (Layout.isBlockDragEvent(e)) {
            e.preventDefault();
        }
    }

    constructor(props) {
        super(props);

        // Set initial React state.
        this.state = Layout.stateFromProps(this.props);

        // Bind this to non-React methods.
        this.onChange = this.onChange.bind(this);
        this.dragStart = this.dragStart.bind(this);
        this.traverse = this.traverse.bind(this);
        this.dragEnd = this.dragEnd.bind(this);
        this.dragOver = this.dragOver.bind(this);
        this.change = this.change.bind(this);
        this.remove = this.remove.bind(this);
        this.filter = this.filter.bind(this);
        this.cleanup = this.cleanup.bind(this);
        this.mapBlocks = this.mapBlocks.bind(this);
    }

    getChildContext() {
        return {
            dragStart: this.dragStart,
            dragOver: this.dragOver,
            dragEnd: this.dragEnd,
            change: this.change,
            remove: this.remove,
            editable: this.props.editable,
            src_pos: this.state.src_pos,
            dst_pos: this.state.dst_pos,
            dst_quad: this.state.dst_quad,
            blocks: this.state.value.blocks,
        };
    }

    componentWillReceiveProps(nextProps) {
        this.setState(Layout.stateFromProps(nextProps));
    }

    onChange() {
        let value = this.state.value;
        const blockList = Object.keys(value.blocks).map(
            blockId => value.blocks[blockId]);
        value = _.extend({}, value, { blocks: blockList });
        this.props.onChange(value);
    }

    dragStart(e, block, pos) {
        if (!this.props.editable) {
            return;
        }
        if (closest(e.target, '[contenteditable]')) {
            // cancel drag to avoid interfering with dragging text
            return;
        }

        e.dataTransfer.effectAllowed = 'move';
        e.dataTransfer.setData('text/plain', JSON.stringify(block, null, 4));
        e.dataTransfer.setData('application/json', JSON.stringify(block));
        e.dataTransfer.setData('application/x-encoded-block', '1');
        e.dataTransfer.setDragImage(document.getElementById('drag-marker'), 15, 15);

        this.dragged_block = block;
        this.setState({ src_pos: pos });
    }

    traverse(pos) {
        const layout = this.state.value;
        const path = [{ type: 'layout', obj: layout }];
        let target = path[path.length - 1];
        let targetIdx = 0;
        for (let i = 0; i < pos.length; i += 1) {
            targetIdx = pos[i];
            if (target.type === 'layout') {
                path.push({ type: 'row', obj: target.obj.rows[targetIdx] });
            } else if (target.type === 'row') {
                path.push({ type: 'col', obj: target.obj.cols[targetIdx] });
            } else if (target.type === 'col') {
                const obj = target.obj.blocks[targetIdx];
                if (typeof obj === 'string') {
                    path.push({ type: 'block', obj });
                } else {
                    path.push({ type: 'row', obj });
                }
            }
            target = path[path.length - 1];
        }
        return {
            path,
            target,
            container: path[path.length - 2],
            target_idx: targetIdx,
        };
    }

    dragEnd(e) {
        const dstPos = this.state.dst_pos;
        if (dstPos === undefined || dstPos === null) {
            return;
        }
        e.preventDefault();
        const srcPos = this.state.src_pos;
        if (!_.isEqual(srcPos, dstPos)) {
            let block;
            if (srcPos) {
                // cut block from current position
                const src = this.traverse(srcPos);
                block = src.container.obj.blocks.splice(src.target_idx, 1, 'CUT')[0];
            } else {
                block = this.dragged_block;
                if (typeof block === 'object') {
                    // new block; give it an id and store it
                    block['@id'] = `#block${this.state.nextBlockNum}`;
                    this.state.nextBlockNum += 1;
                    this.state.value.blocks[block['@id']] = block;
                }
                block = block['@id'];
            }

            // add to new position
            const newCol = { blocks: [block] };
            const newRow = { cols: [newCol] };
            const quad = this.state.dst_quad;
            const dest = this.traverse(dstPos);
            let row;
            if (dest.target.type === 'block') {
                if (quad === 'top') { // add block above in same col
                    dest.container.obj.blocks.splice(dest.target_idx, 0, block);
                } else if (quad === 'bottom') { // add block below in same col
                    dest.container.obj.blocks.splice(dest.target_idx + 1, 0, block);
                } else if (quad === 'left') { // split block into a new row
                    row = { cols: [newCol, { blocks: [dest.container.obj.blocks[dest.target_idx]] }] };
                    dest.container.obj.blocks.splice(dest.target_idx, 1, row);
                } else if (quad === 'right') { // split block into a new row
                    row = { cols: [{ blocks: [dest.container.obj.blocks[dest.target_idx]] }, newCol] };
                    dest.container.obj.blocks.splice(dest.target_idx, 1, row);
                }
            } else if (dest.target.type === 'col') {
                if (quad === 'top') { // add block at top of col
                    dest.target.obj.blocks.splice(0, 0, block);
                } else if (quad === 'bottom') { // add block at bottom of col
                    dest.target.obj.blocks.push(block);
                } else if (quad === 'left') { // add col to left
                    dest.container.obj.cols.splice(dest.target_idx, 0, newCol);
                } else if (quad === 'right') { // add col to right
                    dest.container.obj.cols.splice(dest.target_idx + 1, 0, newCol);
                }
            } else if (dest.target.type === 'row') {
                const container = dest.container.obj.rows || dest.container.obj.blocks;
                if (quad === 'top') { // add new row above
                    container.splice(dest.target_idx, 0, newRow);
                } else if (quad === 'bottom') { // add new row below
                    container.splice(dest.target_idx + 1, 0, newRow);
                } else if (quad === 'left') { // add col at left of row
                    dest.target.obj.cols.splice(0, 0, newCol);
                } else if (quad === 'right') { // add col at right of row
                    dest.target.obj.cols.push(newCol);
                }
            } else if (dest.target.type === 'layout') {
                dest.target.obj.rows.push(newRow);
            }
        }

        this.cleanup();
        this.state.src_pos = null;
        this.state.dst_pos = null;
        this.state.dst_quad = null;

        // make sure we re-render and notify form of new value
        this.setState(this.state);
        this.onChange(this.state.value);
    }

    dragOver(e, target) {
        if (Layout.isBlockDragEvent(e)) {
            e.preventDefault();
        }
        e.stopPropagation();

        if (target && target.render === undefined) {
            // somehow we got something other than a React element
            return;
        }
        // eslint-disable-next-line react/no-find-dom-node
        const targetNode = (target || this).domNode;
        if (!targetNode.childNodes.length) return;
        const targetOffset = offset(targetNode);
        const x = e.pageX - targetOffset.left;
        const y = e.pageY - targetOffset.top;
        const h = targetNode.clientHeight;
        const w = targetNode.clientWidth;
        const swNe = (h * x) / w;
        const nwSe = h * (1 - (x / w));
        let quad;
        if (y >= swNe && y >= nwSe) {
            quad = 'bottom';
        } else if (y >= swNe && y < nwSe) {
            quad = 'left';
        } else if (y < swNe && y >= nwSe) {
            quad = 'right';
        } else {
            quad = 'top';
        }

        const pos = target.props.pos;
        if (pos.length === 0) {
            if (this.state.value.rows.length === 0) {
                quad = 'bottom'; // first block in layout; always show indicator on bottom
            } else {
                return;
            }
        }

        if (this.state.dst_quad !== quad || !_.isEqual(this.state.dst_pos, pos)) {
            console.log(`${pos} ${quad}`);
        }
        this.setState({
            dst_pos: pos,
            dst_quad: quad,
        });
    }

    change(value) {
        this.state.value.blocks[value['@id']] = value;
        this.setState(this.state);
        this.onChange(this.state.value);
    }

    remove(block, pos) {
        delete this.state.value.blocks[block['@id']];
        const dest = this.traverse(pos);
        dest.container.obj.blocks.splice(dest.target_idx, 1);
        this.cleanup();
        this.setState(this.state);
        this.onChange(this.state.value);
    }

    filter(objs) {
        return objs.filter((obj) => {
            if (obj === 'CUT') {  // block
                return false;
            } else if (obj.blocks !== undefined) {  // col
                delete obj.droptarget;
                obj.blocks = this.filter(obj.blocks);
                if (obj.blocks.length === 1 && obj.blocks[0].cols !== undefined && obj.blocks[0].cols.length === 1) {
                    // flatten nested row & col
                    obj.blocks = obj.blocks[0].cols[0].blocks;
                }
                return obj.blocks.length;
            } else if (obj.cols !== undefined) {
                obj.cols = this.filter(obj.cols);
                return obj.cols.length;
            }
            return true;
        });
    }

    cleanup() {
        // remove empty rows and cols
        this.state.value.rows = this.filter(this.state.value.rows);
    }

    mapBlocks(func) {
        Object.keys(this.state.value.blocks).forEach((blockId) => {
            func.call(this, this.state.value.blocks[blockId]);
        });
    }

    render() {
        const classes = { layout: true };
        if (this.props.editable) {
            classes.editable = true;
        }
        if (_.isEqual(this.state.dst_pos, [])) {
            classes[`drop-${this.state.dst_quad}`] = true;
        }
        const classStr = Object.keys(classes).join(' ');
        return (
            <div className={classStr} onDragOver={this.dragOver} onDrop={Layout.drop} ref={(comp) => { this.domNode = comp; }}>
                {this.props.editable ? <LayoutToolbar /> : ''}
                {this.state.value.rows.map((row, i) => <Row value={row} key={i} pos={[i]} />)}
                <canvas id="drag-marker" height="1" width="1" />
            </div>
        );
    }
}

Layout.propTypes = {
    editable: PropTypes.bool,
    onChange: PropTypes.func,
};

Layout.childContextTypes = LAYOUT_CONTEXT;

Layout.defaultProps = {
    editable: false,
    pos: [],
};

