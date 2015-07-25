'use strict';
var React = require('react');
var FallbackBlockEdit = require('./blocks/fallback').FallbackBlockEdit;
var globals = require('./globals');
var closest = require('../libs/closest');
var offset = require('../libs/offset');
var _ = require('underscore');

var cx = require('react/lib/cx');
var ModalTrigger = require('react-bootstrap/lib/ModalTrigger');
var Modal = require('react-bootstrap/lib/Modal');

var LAYOUT_CONTEXT = {
    dragStart: React.PropTypes.func,
    dragOver: React.PropTypes.func,
    dragEnd: React.PropTypes.func,
    change: React.PropTypes.func,
    remove: React.PropTypes.func,
    editable: React.PropTypes.bool,
    src_pos: React.PropTypes.array,
    dst_pos: React.PropTypes.array,
    dst_quad: React.PropTypes.string,
    blocks: React.PropTypes.object
};

var MODAL_CONTEXT = {
    // Persona
    fetch: React.PropTypes.func,
    session: React.PropTypes.object,
    session_properties: React.PropTypes.object,
    // HistoryAndTriggers
    adviseUnsavedChanges: React.PropTypes.func,
    navigate: React.PropTypes.func,
    // App
    dropdownComponent: React.PropTypes.string,
    listActionsFor: React.PropTypes.func,
    currentResource: React.PropTypes.func,
    location_href: React.PropTypes.string,
    onDropdownChange: React.PropTypes.func,
    portal: React.PropTypes.object
};


var BlockEditModal = React.createClass({

    childContextTypes: MODAL_CONTEXT,

    getChildContext: function() {
        return this.props.modalcontext;
    },

    getInitialState: function() {
        return {value: this.props.value};
    },

    render: function() {
        var blocktype = globals.blocks.lookup(this.props.value);
        var schema = blocktype.schema();
        var BlockEdit = blocktype.edit || FallbackBlockEdit;
        return (
            <Modal {...this.props} title={'Edit ' + blocktype.label}>
                <div className="modal-body">
                    <BlockEdit schema={schema} value={this.state.value} onChange={this.onChange} />
                </div>
                <div className="modal-footer">
                    <button className="btn btn-default" onClick={this.cancel}>Cancel</button>
                    <button className="btn btn-primary" onClick={this.save}>Save</button>
                </div>
            </Modal>
        );
    },

    onChange: function(value) {
        if (value.toJS !== undefined) value = value.toJS();
        this.setState({value: value});
    },

    cancel: function() {
        if (this.props.onCancel !== undefined) {
            this.props.onCancel();
        }
        this.props.onRequestHide();
    },

    save: function() {
        this.props.onChange(this.state.value);
        this.props.onRequestHide();
    }

});


var Block = module.exports.Block = React.createClass({

    contextTypes: _.extend({}, MODAL_CONTEXT, LAYOUT_CONTEXT),

    getInitialState: function() {
        return {hover: false, focused: false};
    },

    renderToolbar: function() {
        var modal = <BlockEditModal
            modalcontext={_.pick(this.context, Object.keys(MODAL_CONTEXT))}
            value={this.props.value}
            onChange={this.onChange}
            onCancel={this.onCancelEdit} />;

        return (
            <div className="block-toolbar">
                <ModalTrigger ref="edit_trigger" modal={modal}>
                    <a className="edit"><i className="icon icon-edit"></i></a>
                </ModalTrigger>
                {' '}
                <a className="remove" onClick={this.remove}><i className="icon icon-trash-o"></i></a>
            </div>
        );
    },

    render: function() {
        var block = this.props.value;
        if (typeof block['@type'] == 'string') {
            block['@type'] = [block['@type'], 'block'];
        }
        var BlockView = globals.blocks.lookup(block).view;

        var classes = {
            block: true,
            clearfix: true,
            dragging: _.isEqual(this.props.pos, this.context.src_pos),
            hover: this.state.hover
        };
        if (block.className !== undefined) {
            classes[block.className] = true;
        }
        if (_.isEqual(this.props.pos, this.context.dst_pos)) {
            classes['drop-' + this.context.dst_quad] = true;
        }
        return (
            <div className={block['@type'][0] + ' ' + cx(classes)} data-pos={this.props.pos}
                 draggable={this.context.editable && !this.state.focused}
                 onDragStart={this.dragStart}
                 onDragOver={this.dragOver}
                 onDragEnd={this.context.dragEnd}
                 onMouseEnter={this.mouseEnter}
                 onMouseLeave={this.mouseLeave}
                 onFocus={this.focus}
                 onBlur={this.blur}>
                {this.context.editable ? this.renderToolbar() : ''}
                <BlockView value={block} onChange={this.onChange} />
            </div>
        );
    },

    componentDidMount: function() {
        if (this.props.value.is_new) { this.refs.edit_trigger.show(); }
    },
    componentDidUpdate: function() {
        if (this.props.value.is_new) { this.refs.edit_trigger.show(); }
    },

    mouseEnter: function() { this.setState({hover: true}); },
    mouseLeave: function() { this.setState({hover: false}); },
    focus: function() { this.setState({focused: true}); },
    blur: function() { this.setState({focused: false}); },

    dragStart: function(e) { this.context.dragStart(e, this.props.value, this.props.pos); },
    dragOver: function(e) { this.context.dragOver(e, this); },

    onChange: function(value) {
        delete value.is_new;
        this.context.change(value);
    },

    onCancelEdit: function() {
        if (this.props.value.is_new) {
            this.remove();
        }
    },

    remove: function() {
        this.context.remove(this.props.value, this.props.pos);
    }
});


var BlockAddButton = React.createClass({
    contextTypes: LAYOUT_CONTEXT,

    render: function() {
        var classes = 'icon-lg ' + this.props.blockprops.icon;
        return (
            <span>
                <span className="btn btn-primary navbar-btn btn-sm"
                      onClick={this.click}
                      draggable="true" onDragStart={this.dragStart} onDragEnd={this.context.dragEnd}
                      title={this.props.blockprops.label}><span className={classes}></span></span>
                {' '}
            </span>
        );
    },

    click: function(e) { e.preventDefault(); },

    dragStart: function(e) {
        var block = {
            '@type': [this.props.blocktype, 'block'],
            'is_new': true
        };
        if (this.props.blockprops.initial !== undefined) {
            delete block.is_new;
            block = _.extend({}, block, this.props.blockprops.initial);
        }
        this.context.dragStart(e, block);
    }
});


// "sticky" toolbar for editing layout
var LayoutToolbar = React.createClass({

    contextTypes: {
        canSave: React.PropTypes.func,
        onTriggerSave: React.PropTypes.func,
        formEvents: React.PropTypes.object
    },

    getInitialState: function() {
        return {fixed: false};
    },

    componentDidMount: function() {
        this.origTop = offset(this.getDOMNode()).top;
        globals.bindEvent(window, 'scroll', this.scrollspy);
        this.context.formEvents.addListener('update', this.scrollspy)
    },

    componentWillUnmount: function() {
        globals.unbindEvent(window, 'scroll', this.scrollspy);
        this.context.formEvents.removeListener('update', this.scrollspy)
    },

    scrollspy: function() {
        this.setState({'fixed': window.pageYOffset > this.origTop});
    },

    render: function() {
        var blocks = globals.blocks.getAll();
        var toolbar = (
            <div className={'layout-toolbar navbar navbar-default'}>
              <div className="container-fluid">
                <div className="navbar-left">
                    {Object.keys(blocks).map(b => <BlockAddButton key={b} blocktype={b} blockprops={blocks[b]} /> )}
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
                    <div className="layout-toolbar navbar navbar-default"></div>
                </div>
            );
        } else {
            return toolbar;
        }
    },

});


var Col = React.createClass({
    contextTypes: LAYOUT_CONTEXT,

    renderBlock: function(blockId, k) {
        var pos = this.props.pos.concat([k]);
        if (typeof blockId == 'string') {
            var block = this.context.blocks[blockId];
            return <Block value={block} key={k} pos={pos} />;
        } else {
            var row = blockId;
            return <Row value={row} key={k} pos={pos} />;
        }
    },

    render: function() {
        var classes = {};
        classes[this.props.className] = true;
        if (_.isEqual(this.props.pos, this.context.dst_pos)) {
            classes['drop-' + this.context.dst_quad] = true;
        }
        var blocks = this.props.value.blocks;
        return (
            <div className={cx(classes)} onDragOver={this.dragOver}>
                {blocks.map((blockId, k) => this.renderBlock(blockId, k))}
            </div>
        );
    },

    dragOver: function(e) { this.context.dragOver(e, this); },
});


var Row = React.createClass({
    contextTypes: LAYOUT_CONTEXT,
    render: function() {
        var classes = {
            row: true
        };
        if (_.isEqual(this.props.pos, this.context.dst_pos)) {
            classes['drop-' + this.context.dst_quad] = true;
        }
        var cols = this.props.value.cols;
        var col_class;
        switch (cols.length) {
            case 2: col_class = 'col-md-6'; break;
            case 3: col_class = 'col-md-4'; break;
            case 4: col_class = 'col-md-3'; break;
            default: col_class = 'col-md-12'; break;
        }
        return (
            <div className={cx(classes)} onDragOver={this.dragOver}>
                {cols.map((col, j) => <Col value={col} className={col.className || col_class} key={j} pos={this.props.pos.concat([j])} />)}
            </div>
        );
    },

    dragOver: function(e) { this.context.dragOver(e, this); },
});


var Layout = module.exports.Layout = React.createClass({

    getDefaultProps: function() {
        return {
            'editable': false,
            'pos': []
        };
    },

    getInitialState: function() {
        return this.stateFromProps(this.props);
    },

    stateFromProps: function(props) {
        var value = props.value;
        if (value.toJS !== undefined) value = value.toJS();

        var blockMap = {};
        var nextBlockNum = 2;
        value.blocks.map(function(block) {
            var block_id = block['@id'];
            blockMap[block_id] = block;
            var blockNum = parseInt(block_id.replace(/\D/g, ''));
            if (blockNum >= nextBlockNum) nextBlockNum = blockNum + 1;
        });
        value = _.extend({}, value, {blocks: blockMap});

        return {
            'nextBlockNum': nextBlockNum,
            'value': value,
            'src_pos': null,
            'dst_pos': null,
            'dst_quad': null,
        };
    },

    componentWillReceiveProps: function(nextProps) {
        this.setState(this.stateFromProps(nextProps));
    },

    childContextTypes: LAYOUT_CONTEXT,
    getChildContext: function() {
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
            blocks: this.state.value.blocks
        };
    },

    render: function() {
        var classes = {
            layout: true,
            editable: this.props.editable,
        };
        if (_.isEqual(this.state.dst_pos, [])) {
            classes['drop-' + this.state.dst_quad] = true;
        }
        return (
            <div className={cx(classes)} onDragOver={this.dragOver} onDrop={this.drop}>
                {this.props.editable ? <LayoutToolbar /> : ''}
                {this.state.value.rows.map((row, i) => <Row value={row} key={i} pos={[i]} />)}
                <canvas id="drag-marker" height="1" width="1"></canvas>
            </div>
        );
    },

    dragStart: function(e, block, pos) {
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
        this.setState({src_pos: pos});
    },

    _isBlockDragEvent: function(e) {
        var types = e.dataTransfer.types;
        if (types.indexOf && types.indexOf('application/x-encoded-block') != -1) {
            return true;
        } else if (types.contains && types.contains('application/x-encoded-block')) {
            return true;
        }   
        e.preventDefault();
    },

    drop: function(e) {
        if (this._isBlockDragEvent(e)) {
            e.preventDefault();            
        } else {
            return;
        }
    },

    _traverse: function(pos) {
        var layout = this.state.value;
        var path = [{type: 'layout', obj: layout}];
        var target = path[path.length - 1];
        var target_idx = 0;
        for (var i = 0; i < pos.length; i++) {
            target_idx = pos[i];
            if (target.type == 'layout') {
                path.push({type: 'row', obj: target.obj.rows[target_idx]});
            } else if (target.type == 'row') {
                path.push({type: 'col', obj: target.obj.cols[target_idx]});
            } else if (target.type == 'col') {
                var obj = target.obj.blocks[target_idx];
                if (typeof obj == 'string') {
                    path.push({type: 'block', obj: obj});
                } else {
                    path.push({type: 'row', obj: obj});
                }
            }
            target = path[path.length - 1];
        }
        return {
            path: path,
            target: target,
            container: path[path.length - 2],
            target_idx: target_idx,
        };
    },

    dragEnd: function(e) {
        var dst_pos = this.state.dst_pos;
        if (dst_pos === undefined || dst_pos === null) {
            return;
        } else {
            e.preventDefault();
        }
        var src_pos = this.state.src_pos;
        if (!_.isEqual(src_pos, dst_pos)) {
            var block;
            if (src_pos) {
                // cut block from current position
                var src = this._traverse(src_pos);
                block = src.container.obj.blocks.splice(src.target_idx, 1, 'CUT')[0];
            } else {
                block = this.dragged_block;
                if (typeof block == 'object') {
                    // new block; give it an id and store it
                    block['@id'] = '#block' + this.state.nextBlockNum;
                    this.state.nextBlockNum += 1;
                    this.state.value.blocks[block['@id']] = block;
                }
                block = block['@id'];
            }

            // add to new position
            var new_col = {blocks: [block]};
            var new_row = {cols: [new_col]};
            var quad = this.state.dst_quad;
            var dest = this._traverse(dst_pos);
            var row;
            if (dest.target.type == 'block') {
                if (quad == 'top') { // add block above in same col
                    dest.container.obj.blocks.splice(dest.target_idx, 0, block);
                } else if (quad == 'bottom') { // add block below in same col
                    dest.container.obj.blocks.splice(dest.target_idx + 1, 0, block);
                } else if (quad == 'left') { // split block into a new row
                    row = {cols: [new_col, {blocks: [dest.container.obj.blocks[dest.target_idx]]}]};
                    dest.container.obj.blocks.splice(dest.target_idx, 1, row);
                } else if (quad == 'right') { // split block into a new row
                    row = {cols: [{blocks: [dest.container.obj.blocks[dest.target_idx]]}, new_col]};
                    dest.container.obj.blocks.splice(dest.target_idx, 1, row);
                }
            } else if (dest.target.type == 'col') {
                if (quad == 'top') { // add block at top of col
                    dest.target.obj.blocks.splice(0, 0, block);
                } else if (quad == 'bottom') { // add block at bottom of col
                    dest.target.obj.blocks.push(block);
                } else if (quad == 'left') { // add col to left
                    dest.container.obj.cols.splice(dest.target_idx, 0, new_col);
                } else if (quad == 'right') { // add col to right
                    dest.container.obj.cols.splice(dest.target_idx + 1, 0, new_col);
                }
            } else if (dest.target.type == 'row') {
                var container = dest.container.obj.rows || dest.container.obj.blocks;
                if (quad == 'top') { // add new row above
                    container.splice(dest.target_idx, 0, new_row);
                } else if (quad == 'bottom') { // add new row below
                    container.splice(dest.target_idx + 1, 0, new_row);
                } else if (quad == 'left') { // add col at left of row
                    dest.target.obj.cols.splice(0, 0, new_col);
                } else if (quad == 'right') { // add col at right of row
                    dest.target.obj.cols.push(new_col);
                }
            } else if (dest.target.type == 'layout') {
                dest.target.obj.rows.push(new_row);
            }
        }

        this.cleanup();
        this.state.dst_pos = this.state.dst_quad = this.state.src_pos = null;

        // make sure we re-render and notify form of new value
        this.setState(this.state);
        this.onChange(this.state.value);
    },

    dragOver: function(e, target) {
        if (this._isBlockDragEvent(e)) {
            e.preventDefault();            
        } else {
            return;
        }
        e.stopPropagation();

        if (typeof target == 'string') return;
        target = target || this;
        var target_node = target.getDOMNode();
        if (!target_node.childNodes.length) return;
        var target_offset = offset(target_node);
        var x = e.pageX - target_offset.left;
        var y = e.pageY - target_offset.top;
        var h = target_node.clientHeight;
        var w = target_node.clientWidth;
        var sw_ne = h * x / w;
        var nw_se = h * (1 - x / w);
        var quad;
        if (y >= sw_ne && y >= nw_se) {
            quad = 'bottom';
        } else if (y >= sw_ne && y < nw_se) {
            quad = 'left';
        } else if (y < sw_ne && y >= nw_se) {
            quad = 'right';
        } else {
            quad = 'top';
        }

        var pos = target.props.pos;
        if (pos.length === 0) {
            if (this.state.value.rows.length === 0) {
                quad = 'bottom'; // first block in layout; always show indicator on bottom
            } else {
                return;
            }
        }

        if (this.state.dst_quad != quad || !_.isEqual(this.state.dst_pos, pos)) {
            console.log(pos + ' ' + quad);
        }
        this.setState({
            dst_pos: pos,
            dst_quad: quad
        });
    },

    change: function(value) {
        this.state.value.blocks[value['@id']] = value;
        this.setState(this.state);
        this.onChange(this.state.value);
    },

    remove: function(block, pos) {
        delete this.state.value.blocks[block['@id']];
        var dest = this._traverse(pos);
        dest.container.obj.blocks.splice(dest.target_idx, 1);
        this.cleanup();
        this.setState(this.state);
        this.onChange(this.state.value);
    },

    onChange: function() {
        var value = this.state.value;
        var blockList = Object.keys(value.blocks).map(function(blockId) {
            return value.blocks[blockId];
        });
        value = _.extend({}, value, {blocks: blockList});
        this.props.onChange(value);
    },

    _filter: function(objs) {
        return objs.filter(function(obj) {
            if (obj == 'CUT') {  // block
                return false;
            } else if (obj.blocks !== undefined) {  // col
                delete obj.droptarget;
                obj.blocks = this._filter(obj.blocks);
                if (obj.blocks.length == 1 && obj.blocks[0].cols !== undefined && obj.blocks[0].cols.length == 1) {
                    // flatten nested row & col
                    obj.blocks = obj.blocks[0].cols[0].blocks;
                }
                return obj.blocks.length;
            } else if (obj.cols !== undefined) {
                obj.cols = this._filter(obj.cols);
                return obj.cols.length;
            } else {
                return true;
            }
        }.bind(this));
    },

    cleanup: function() {
        // remove empty rows and cols
        this.state.value.rows = this._filter(this.state.value.rows);
    },

    mapBlocks: function(func) {
        Object.keys(this.state.value.blocks).map(function(block_id) {
            func.call(this, this.state.value.blocks[block_id]);
        }.bind(this));
    }

});
