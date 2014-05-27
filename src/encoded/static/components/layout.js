/** @jsx React.DOM */
'use strict';
var React = require('react');
var ReactForms = require('react-forms');
var form = require('./form');
var FetchedData = require('./fetched').FetchedData;
var globals = require('./globals');


var Block = module.exports.Block = React.createClass({

    render: function() {
        var block = this.props.block;
        if (typeof block['@type'] == 'string') {
            block['@type'] = [block['@type'], 'block'];
        }
        var block_view = globals.block_views.lookup(block);
        if (this.props.editable) {
            var buttons = (
                <div className="block-toolbar">
                    <a className="remove" onClick={this.remove}><i className="icon-trash"></i></a>
                </div>
                )
        } else {
            var buttons = '';
        }
        return this.transferPropsTo(
            <div data-row={this.props.row} data-col={this.props.col}
                 onDragStart={this.dragStart}>
                {buttons}
                <block_view type={block['@type']} data={block.data} />
            </div>
        );
    },

    dragStart: function(e) {
        this.props.dragStart(e, this.props.block, this.props.row, this.props.col);
    },

    remove: function() {
        this.props.remove(this.props.row, this.props.col)
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
                       editable={this.props.editable}
                       block={block}
                       key={i}
                       row={this.props.i}
                       col={i}
                       draggable="true"
                       dragStart={this.props.dragStart}
                       onDragEnd={this.props.dragEnd}
                       remove={this.props.remove} />
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
        return (
            <div className={'layout-toolbar navbar navbar-default' + (this.state.fixed ? ' navbar-fixed-top' : '')}>
              <div className="container">
                <button className="btn btn-primary navbar-btn btn-xs"
                        draggable="true" onDragStart={this.dragStart} onDragEnd={this.props.dragEnd}
                        title="Rich text"><i className="icon-file-alt"></i></button>
              </div>
            </div>
        );
    },

    dragStart: function(e) {
        this.props.dragStart(e, {
            'data': {
                'body': '<p>This is a new block.</p>'
            },
            '@type': ['richtextblock', 'block']
        });
    }

});


var Layout = module.exports.Layout = React.createClass({

    getDefaultProps: function() {
        return {
            'editable': false
        }
    },

    getInitialState: function() {
        return {
            'value': this.props.value
        }
    },

    componentDidMount: function() {
        this.$ = require('jquery');
        this.$('<i id="drag-marker"></i>').appendTo(this.getDOMNode());
    },

    render: function() {
        var rows = this.state.value.rows.map(function(row, i) {
            if (this.props.editable) {
                return <Row blocks={row.blocks}
                            droptarget={row.droptarget}
                            i={i}
                            editable={true}
                            dragStart={this.dragStart}
                            dragEnd={this.dragEnd}
                            remove={this.remove} />;
            } else {
                return <Row blocks={row.blocks} editable={false} />;
            }
        }, this);
        var className = 'layout' + (this.props.editable ? ' editable' : '');
        return (
            <div className={className} onDragOver={this.dragOver}>
                {this.props.editable ? <LayoutToolbar dragStart={this.dragStart} dragEnd={this.dragEnd} /> : ''}
                {rows}
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
            this.state.value.rows.filter(function(row) {
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

    remove: function(row, col) {
        // remove block
        this.state.value.rows[row].blocks.splice(col, 1)[0];
        // cull empty rows
        this.state.value.rows.filter(function(row) {
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
