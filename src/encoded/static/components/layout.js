/** @jsx React.DOM */
'use strict';
var React = require('react');
var ReactForms = require('react-forms');
var form = require('./form');
var FetchedData = require('./fetched').FetchedData;
var FallbackBlockEdit = require('./blocks/fallback').FallbackBlockEdit;
var globals = require('./globals');

var ModalTrigger = require('react-bootstrap/ModalTrigger');
var Modal = require('react-bootstrap/Modal');

var LAYOUT_CONTEXT = {
    dragStart: React.PropTypes.func,
    dragEnd: React.PropTypes.func,
    change: React.PropTypes.func,
    remove: React.PropTypes.func,
    editable: React.PropTypes.bool
}


var BlockEditModal = React.createClass({

    getInitialState: function() {
        return {value: this.props.block.data};
    },

    render: function() {
        var blocktype = globals.blocks.lookup(this.props.block);
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

    renderToolbar: function() {
        var modal = <BlockEditModal block={this.props.block} onChange={this.onChange} />;
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
        var block = this.props.block;
        if (typeof block['@type'] == 'string') {
            block['@type'] = [block['@type'], 'block'];
        }
        var BlockView = globals.blocks.lookup(block).view;
        return this.transferPropsTo(
            <div data-row={this.props.row} data-col={this.props.col}
                 draggable={this.context.editable}
                 onDragStart={this.dragStart}
                 onDragEnd={this.context.dragEnd}>
                {this.context.editable ? this.renderToolbar() : ''}
                {block.data !== undefined ?
                    <BlockView type={block['@type']} value={block.data}
                               editable={this.context.editable} onChange={this.onChange} /> : ''}
            </div>
        );
    },

    componentDidMount: function() {
        if (this.props.block.data === undefined) { this.refs.edit_trigger.show(); }
    },
    componentDidUpdate: function() {
        if (this.props.block.data === undefined) { this.refs.edit_trigger.show(); }
    },

    dragStart: function(e) {
        this.context.dragStart(e, this.props.block, this.props.row, this.props.col);
    },

    onChange: function(value) {
        this.context.change(this.props.row, this.props.col, value);
    },

    remove: function() {
        this.context.remove(this.props.row, this.props.col);
    }
});


var Row = module.exports.Row = React.createClass({
    render: function() {
        var col_class;
        switch (this.props.blocks.length) {
            case 2: col_class = 'col-md-6'; break;
            case 3: col_class = 'col-md-4'; break;
            case 4: col_class = 'col-md-3'; break;
            default: col_class = 'col-md-12'; break;
        }
        var blocks = this.props.blocks.map(function(block, i) {
            if (block.className) {
                var classes = block.className + ' block';
            } else {
                var classes = col_class + ' block';
            }
            if (block.dragging) {
                classes += ' dragging';
            } else if (block.droptarget) {
                classes += ' drop-' + block.droptarget;
            }
            return (
                <Block className={classes}
                       block={block}
                       key={i}
                       row={this.props.i}
                       col={i} />
            );
        }, this);
        var classes = 'row';
        if (this.props.droptarget) {
            classes += ' drop-' + this.props.droptarget;
        }
        return this.transferPropsTo(
            <div className={classes}>
                {blocks}
            </div>
        );
    }
});


var BlockAddButton = React.createClass({
    contextTypes: LAYOUT_CONTEXT,

    render: function() {
        var classes = 'icon-large ' + this.props.blockprops.icon;
        return (
            <button className="btn btn-primary navbar-btn btn-sm"
                    onClick={this.click}
                    draggable="true" onDragStart={this.dragStart} onDragEnd={this.context.dragEnd}
                    title={this.props.blockprops.label}><span className={classes}></span></button>
        );
    },

    click: function() { return false; },

    dragStart: function(e) {
        var block = {
            '@type': [this.props.key, 'block']
        };
        if (this.props.blockprops.initial !== undefined) {
            block.data = this.props.blockprops.initial;
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
        return {
            'value': this.props.value
        };
    },

    childContextTypes: LAYOUT_CONTEXT,
    getChildContext: function() {
        return {
            dragStart: this.dragStart,
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

    render: function() {
        var className = 'layout' + (this.props.editable ? ' editable' : '');
        return (
            <div className={className} onDragOver={this.dragOver}>
                {this.props.editable ? <LayoutToolbar /> : ''}
                {this.state.value.rows.map((row, i) => <Row blocks={row.blocks} droptarget={row.droptarget} i={i} />)}
            </div>
        );
    },

    dragStart: function(e, block, row, col) {
        e.dataTransfer.effectAllowed = 'move';
        e.dataTransfer.setData('text/plain', JSON.stringify(block, null, 4));
        e.dataTransfer.setData('application/json', JSON.stringify(block));
        e.dataTransfer.setDragImage(document.getElementById('drag-marker'), 15, 15);

        this.dragged_block = block;
        this.src_row = row;
        this.src_col = col;
        block.dragging = true;
        this.setState(this.state);
    },

    dragEnd: function(e) {
        if ((this.src_col != this.dst_col || this.src_row != this.dst_row) || (this.quad == 'top' || this.quad == 'bottom')) {
            if (this.src_row !== undefined) {
                // remove block from current position
                var block = this.state.value.rows[this.src_row].blocks.splice(this.src_col, 1)[0];                
            } else {
                // new block
                var block = this.dragged_block;
            }
            if (this.quad == 'top') {
                // add to new row above drop target
                this.state.value.rows.splice(this.dst_row, 0, {blocks: [block]});
            } else if (this.quad == 'bottom') {
                // add to new row below drop target
                this.state.value.rows.splice(this.dst_row + 1, 0, {blocks: [block]});
            } else if (this.quad == 'left') {
                // compensate for removed block
                var dst_col = (this.src_row == this.dst_row && this.src_col && this.src_col < this.dst_col) ? (this.dst_col - 1) : this.dst_col;
                // add before drop target
                this.state.value.rows[this.dst_row].blocks.splice(dst_col, 0, block);
            } else if (this.quad == 'right') {
                // compensate for removed block
                var dst_col = (this.src_row == this.dst_row && this.src_col && this.src_col < this.dst_col) ? this.dst_col : this.dst_col + 1;
                // add after drop target
                this.state.value.rows[this.dst_row].blocks.splice(dst_col, 0, block);
            }
            // cull empty rows
            this.state.value.rows = this.state.value.rows.filter(function(row) {
                return row.blocks.length;
            });
        }

        // clean up drag/drop styles
        this.state.value.rows.map(function(row) {
            delete row.droptarget;
        });
        this.mapBlocks(function(block) {
            delete block.dragging;
            delete block.droptarget;
        });

        // make sure we re-render and notify form of new value
        this.setState(this.state);
        this.props.onChange(this.state.value);
    },

    dragOver: function(e) {
        e.preventDefault();
        var $target = this.$(e.target).closest('.block');
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
        var row = this.dst_row = $target.data('row');
        var col = this.dst_col = $target.data('col');
        var pos = row + ' ' + col + ' ' + quad;
        if (pos != this.oldpos) {
            this.oldpos = pos;
            //console.log(pos);
            this.state.value.rows.map(function(obj, i) {
                if (i == row) {
                    obj.droptarget = quad;
                } else {
                    delete obj.droptarget;
                }
            });
            this.mapBlocks(function(block, i, j) {
                if (i == row && j == col) {
                    block.droptarget = quad;
                } else {
                    delete block.droptarget;
                }
            });
            this.setState(this.state);
        }
    },

    change: function(row, col, value) {
        this.state.value.rows[row].blocks[col].data = value;
        this.setState(this.state);
        this.props.onChange(this.state.value);
    },

    remove: function(row, col) {
        // remove block
        this.state.value.rows[row].blocks.splice(col, 1)[0];
        // cull empty rows
        this.state.value.rows = this.state.value.rows.filter(function(row) {
            return row.blocks.length;
        });
        // refresh
        this.setState(this.state);
        this.props.onChange(this.state.value);
    },

    mapBlocks: function(func) {
        this.state.value.rows.map(function(row, i) {
            row.blocks.map(function(block, j) {
                func.call(this, block, i, j);
            }.bind(this));
        }.bind(this));
    }

});
