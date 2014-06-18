/** @jsx React.DOM */
'use strict';
var React = require('react');
var ReactForms = require('react-forms');
var form = require('./form');
var FetchedData = require('./fetched').FetchedData;
var FallbackBlockEdit = require('./blocks/fallback').FallbackBlockEdit;
var globals = require('./globals');

var cx = React.addons.classSet;
var merge = require('react/lib/merge');
var ModalTrigger = require('react-bootstrap/ModalTrigger');
var Modal = require('react-bootstrap/Modal');

var LAYOUT_CONTEXT = {
    dragStart: React.PropTypes.func,
    dragOver: React.PropTypes.func,
    dragEnd: React.PropTypes.func,
    change: React.PropTypes.func,
    remove: React.PropTypes.func,
    editable: React.PropTypes.bool
}


var BlockEditModal = React.createClass({

    getInitialState: function() {
        return {value: this.props.value};
    },

    render: function() {
        var blocktype = globals.blocks.lookup(this.props.value);
        var BlockEdit = blocktype.edit || FallbackBlockEdit;
        return this.transferPropsTo(
            <Modal title={'Edit ' + blocktype.label}>
                <div className="modal-body">
                    <BlockEdit schema={blocktype.schema} value={this.state.value} onChange={this.onChange} />
                </div>
                <div className="modal-footer">
                    <button className="btn btn-default" onClick={this.props.onRequestHide}>Cancel</button>
                    <button className="btn btn-primary" onClick={this.save}>Save</button>
                </div>
            </Modal>
        );
    },

    onChange: function(value) {
        this.setState({value: value});
    },

    save: function() {
        this.props.onChange(this.state.value);
        this.props.onRequestHide();
    }

});


var Block = module.exports.Block = React.createClass({

    contextTypes: LAYOUT_CONTEXT,

    getInitialState: function() {
        return {hover: false};
    },

    renderToolbar: function() {
        var modal = <BlockEditModal value={this.props.value} onChange={this.onChange} />;
        return (
            <div className="block-toolbar">
                <ModalTrigger ref="edit_trigger" modal={modal}>
                    <a className="edit"><i className="icon-edit"></i></a>
                </ModalTrigger>
                {' '}
                <a className="remove" onClick={this.remove}><i className="icon-trash"></i></a>
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
            dragging: block.dragging,
            hover: this.state.hover
        };
        if (block.droptarget) {
            classes['drop-' + block.droptarget] = true;
        }
        return (
            <div className={cx(classes)} data-pos={this.props.pos}
                 draggable={this.context.editable}
                 onDragStart={this.dragStart}
                 onDragOver={this.dragOver}
                 onDragEnd={this.context.dragEnd}
                 onMouseEnter={this.mouseEnter}
                 onMouseLeave={this.mouseLeave}>
                {this.context.editable ? this.renderToolbar() : ''}
                <BlockView value={block} onChange={this.onChange} />
            </div>
        );
    },

    componentDidMount: function() {
        if (this.props.value === undefined) { this.refs.edit_trigger.show(); }
    },
    componentDidUpdate: function() {
        if (this.props.value === undefined) { this.refs.edit_trigger.show(); }
    },

    mouseEnter: function() {
        this.setState({hover: true});
    },

    mouseLeave: function() {
        this.setState({hover: false});
    },

    dragStart: function(e) {
        this.context.dragStart(e, this.props.value, this.props.pos);
    },

    dragOver: function(e) {
        this.context.dragOver(e, this);
    },

    onChange: function(value) {
        this.context.change(this.props.pos, value);
    },

    remove: function() {
        this.context.remove(this.props.value, this.props.pos);
    }
});


var BlockAddButton = React.createClass({
    contextTypes: LAYOUT_CONTEXT,

    render: function() {
        var classes = 'icon-large ' + this.props.blockprops.icon;
        return (
            <span>
                <button className="btn btn-primary navbar-btn btn-sm"
                        onClick={this.click}
                        draggable="true" onDragStart={this.dragStart} onDragEnd={this.context.dragEnd}
                        title={this.props.blockprops.label}><span className={classes}></span></button>
                {' '}
            </span>
        );
    },

    click: function() { return false; },

    dragStart: function(e) {
        var block = {
            '@type': [this.props.key, 'block']
        };
        if (this.props.blockprops.initial !== undefined) {
            block = merge(block, this.props.blockprops.initial);
        }
        this.context.dragStart(e, block);
    }
})


// "sticky" toolbar for editing layout
var LayoutToolbar = React.createClass({

    getInitialState: function() {
        return {fixed: false}
    },

    componentDidMount: function() {
        var $ = require('jquery');
        this.origTop = $(this.getDOMNode()).offset().top;
        window.addEventListener('scroll', this.scrollspy);
    },

    componentWillUnmount: function() {
        window.removeEventListener('scroll', this.scrollspy);
    },

    scrollspy: function() {
        this.setState({'fixed': window.pageYOffset > this.origTop});
    },

    render: function() {
        var blocks = globals.blocks.getAll();
        return (
            <div className={'layout-toolbar navbar navbar-default' + (this.state.fixed ? ' navbar-fixed-top' : '')}>
              <div className="container">
                {Object.keys(blocks).map(b => <BlockAddButton key={b} blockprops={blocks[b]} /> )}
              </div>
            </div>
        );
    },

});


var Layout = module.exports.Layout = React.createClass({

    getDefaultProps: function() {
        return {
            'editable': false
        };
    },

    getInitialState: function() {
        var nextBlockNum = 2;
        Object.keys(this.props.value.blocks).map(function(block_id) {
            var blockNum = parseInt(block_id.replace(/\D/g, ''));
            if (blockNum >= nextBlockNum) nextBlockNum = blockNum + 1;
        });
        return {
            'nextBlockNum': nextBlockNum,
            'value': this.props.value
        };
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
        };
    },

    componentWillReceiveProps: function(nextProps) {
        this.setState({value: nextProps.value});
    },

    componentDidMount: function() {
        this.$ = require('jquery');
        this.$('<i id="drag-marker"></i>').appendTo(this.getDOMNode());
    },

    renderBlock: function(blockId, pos) {
        var block = this.state.value.blocks[blockId];
        return <Block value={block} key={block['@id']} pos={pos} />;
    },

    renderCol: function(col, col_class, i, j) {
        var classes = {}
        if (col.className !== undefined) {
            classes[col.className] = true;
        } else {
            classes[col_class] = true;
        }
        if (col.droptarget !== undefined) {
            classes['drop-' + col.droptarget] = true;
        }
        return (
            <div className={cx(classes)}>
                {col.blocks.map((blockId, k) => this.renderBlock(blockId, [i,j,k]))}
            </div>
        );
    },

    renderRow: function(row, i) {
        var classes = {
            row: true
        };
        if (row.droptarget) {
            classes['drop-' + row.droptarget] = true;
        }
        var col_class;
        switch (row.cols.length) {
            case 2: col_class = 'col-md-6'; break;
            case 3: col_class = 'col-md-4'; break;
            case 4: col_class = 'col-md-3'; break;
            default: col_class = 'col-md-12'; break;
        }        
        return (
            <div className={cx(classes)}>
                {row.cols.map((col, j) => this.renderCol(col, col_class, i, j))}
            </div>
        )
    },

    render: function() {
        var classes = cx({
            layout: true,
            editable: this.props.editable,
        });
        return (
            <div className={classes} onDrop={this.drop}>
                {this.props.editable ? <LayoutToolbar /> : ''}
                {this.state.value.rows.map((row, i) => this.renderRow(row, i))}
            </div>
        );
    },

    dragStart: function(e, block, pos) {
        e.dataTransfer.effectAllowed = 'move';
        e.dataTransfer.setData('text/plain', JSON.stringify(block, null, 4));
        e.dataTransfer.setData('application/json', JSON.stringify(block));
        e.dataTransfer.setDragImage(document.getElementById('drag-marker'), 15, 15);

        this.dragged_block = block;
        this.src_pos = pos;
        block.dragging = true;
        this.setState(this.state);
    },

    drop: function(e) {
        e.preventDefault();
    },

    dragEnd: function(e) {
        e.preventDefault();
        if (this.src_pos != this.dst_pos) {
            if (this.src_pos) {
                // cut block from current position
                var block = this.state.value.rows[this.src_pos[0]].cols[this.src_pos[1]].blocks.splice(this.src_pos[2], 1, 'CUT');
            } else {
                var block = this.dragged_block;
                if (typeof block == 'object') {
                    // new block; give it an id and store it
                    block['@id'] = '#block' + this.state.nextBlockNum;
                    this.state.nextBlockNum += 1;
                    this.state.value.blocks[block['@id']] = block;
                }
                block = block['@id'];
            }

            // add to new position
            var dst_row = this.state.value.rows[this.dst_pos[0]];
            var dst_col = dst_row.cols[this.dst_pos[1]];
            if (this.quad == 'top') {
                // add above drop target in same col
                dst_col.blocks.splice(this.dst_pos[2], 0, block);
            } else if (this.quad == 'bottom') {
                // add below drop target in same col
                dst_col.blocks.splice(this.dst_pos[2] + 1, 0, block);
            } else if (this.quad == 'left') {
                // add in new col before drop target's col
                dst_row.cols.splice(this.dst_pos[1], 0, {blocks: [block]});
            } else if (this.quad == 'right') {
                // add in new col after drop target's col
                dst_row.cols.splice(this.dst_pos[1] + 1, 0, {blocks: [block]});
            }
        }

        this.cleanup();

        // make sure we re-render and notify form of new value
        this.setState(this.state);
        this.props.onChange(this.state.value);
    },

    dragOver: function(e, block) {
        e.preventDefault();
        var $target = this.$(block.getDOMNode());
        if (!$target.length) return;
        var x = e.pageX - $target.offset().left;
        var y = e.pageY - $target.offset().top;
        var h = $target.height();
        var w = $target.width();
        var sw_ne = h * x / w;
        var nw_se = h * (1 - x / w);
        if (y >= sw_ne && y >= nw_se) {
            var quad = 'bottom';
        } else if (y >= sw_ne && y < nw_se) {
            var quad = 'left';
        } else if (y < sw_ne && y >= nw_se) {
            var quad = 'right';
        } else {
            var quad = 'top';
        }
        this.quad = quad;
        var dst_block_id = block.props.value['@id'];
        var dst_pos = this.dst_pos = block.props.pos;
        var pos = dst_pos + ' ' + quad;
        if (pos != this.oldpos) {
            this.oldpos = pos;
            console.log(pos);
            this.state.value.rows.map(function(row, i) {
                row.cols.map(function(col, j) {
                    if ((quad == 'left' || quad == 'right') && i == dst_pos[0] && j == dst_pos[1]) {
                        dst_block_id = null;
                        col.droptarget = quad;
                    } else {
                        delete col.droptarget;
                    }
                });
            });
            this.mapBlocks(function(block) {
                if (block['@id'] == dst_block_id) {
                    block.droptarget = quad;
                } else {
                    delete block.droptarget;
                }
            });
            this.setState(this.state);
        }
    },

    change: function(pos, value) {
        // update the block at a particular position
        this.state.value.rows[pos[0]].cols[pos[1]].blocks[pos[2]] = value;
        this.setState(this.state);
        this.props.onChange(this.state.value);
    },

    remove: function(block, pos) {
        delete this.state.value.blocks[block['@id']];
        this.state.value.rows[pos[0]].cols[pos[1]].blocks.splice(pos[2], 1);
        this.cleanup();
        this.setState(this.state);
        this.props.onChange(this.state.value);
    },

    cleanup: function() {
        // remove empty rows and cols
        this.state.value.rows = this.state.value.rows.filter(function(row) {
            row.cols = row.cols.filter(function(col) {
                delete col.droptarget;
                col.blocks = col.blocks.filter(function(block_id) {
                    return (block_id != 'CUT');
                });
                return col.blocks.length;
            });
            return row.cols.length;
        });

        // remove temporary drag styles
        this.mapBlocks(function(block) {
            delete block.droptarget;
            delete block.dragging;
        });
    },

    mapBlocks: function(func) {
        Object.keys(this.state.value.blocks).map(function(block_id) {
            func.call(this, this.state.value.blocks[block_id]);
        }.bind(this));
    }

});
