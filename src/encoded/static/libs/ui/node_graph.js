const circlePlus = '\u2295';
const circleMinus = '\u2296';

const slowAnimation = 400;
const fastAnimation = 0;

const mobileLimit = 400;

const triCell = [
    { cx: 2, cy: 2, rx: 12, ry: 9 },
    { cx: 2, cy: 2, rx: 6.5, ry: 6 },
    { cx: -5, cy: 10, rx: 12, ry: 9 },
    { cx: -5, cy: 10, rx: 6.5, ry: 5 },
    { cx: 10, cy: 10, rx: 12, ry: 9 },
    { cx: 10, cy: 10, rx: 6.5, ry: 5 },
];

const doubleEllipse = [
    { cx: 6, cy: 6, rx: 12, ry: 12 },
    { cx: 8, cy: 3, rx: 6, ry: 6 },
];

// Standardizes node names
export const nodeKeyName = (name) => name.replace(/\s/g, '').replace(/[\W_]+/g, '').toLowerCase();

export const mapTermToNode = (term) => term;

// Shortened node graph labels
const nodeLabel = (name) => name.replaceAll('activated', 'ϟ')
    .replaceAll('stimulated', '☆')
    .replaceAll('alpha', 'α')
    .replaceAll('beta', 'β')
    .replaceAll('delta', 'δ')
    .replaceAll('gamma', 'γ')
    .replaceAll('-positive,', '+')
    .replaceAll('-negative,', '-')
    .replaceAll('-positive', '+')
    .replaceAll('-negative', '-');

// Map node name to color name
const colorCode = (node) => {
    if (node.data.name.indexOf('T') > -1) {
        return 'tcell';
    }
    if (node.data.name.indexOf('B') > -1) {
        return 'bcell';
    }
    if (node.data.name.indexOf('natural killer') > -1) {
        return 'nkcell';
    }
    return null;
};

// Creates a curved (diagonal) path from parent to the child nodes
function diagonal(d, s) {
    const path = `M${d.x},${d.y}C${d.x},${(d.y + s.y) / 2} ${s.x},${(d.y + s.y) / 2} ${s.x},${s.y}`;
    return path;
}

export const drawTree = (d3, targetDiv, data, fullWidth, fullHeight, margin, selectedNodes, setSelectedNodes, searchMapping, treeName) => {
    const isDesktop = fullWidth > mobileLimit;
    let textWrapWidth = 80;

    if (isDesktop) {
        textWrapWidth = 115;
    }

    if (treeName === 'immune') {
        textWrapWidth = 50;
    }

    let ellipseSettings;
    if (treeName === 'sescc') {
        ellipseSettings = triCell;
    } else if (treeName === 'immune') {
        ellipseSettings = doubleEllipse;
    }

    const width = fullWidth - margin.left - margin.right;
    const height = fullHeight - margin.top - margin.bottom;

    d3.select(targetDiv).select('svg').remove();

    let internalSelectedNodes = selectedNodes;

    const svg = d3.select(targetDiv).append('svg')
        .attr('width', fullWidth)
        .attr('height', fullHeight)
        .attr('viewBox', `0 0 ${fullWidth} ${fullHeight}`)
        .append('g')
        .attr('transform', `translate(${margin.left},${margin.top})`);

    const treemap = d3.tree().size([width, height]);
    const root = d3.hierarchy(data, (d) => d.children);

    // Tree is vertical, centered along x-axis
    root.x0 = width / 2;
    root.y0 = 100;

    function wrap(text, textWidth) {
        text.each(function textWrap() {
            text = d3.select(this);
            const words = text.text().split(/\s+/);
            let line = [];
            let lineNumber = 0;
            const lineHeight = 1.1;
            const y = text.attr('y');
            const dy = parseFloat(text.attr('dy'));
            let newDy = '';
            let tspan = text.text(null).append('tspan').attr('x', 0).attr('y', y);
            tspan = text.append('tspan').attr('x', 0).attr('y', y);
            words.forEach((word) => {
                line.push(word);
                tspan.text(line.join(' '));
                if (tspan.node().getComputedTextLength() > textWidth && (line.length > 1)) {
                    line.pop();
                    tspan.text(line.join(' '));
                    line = [word];
                    tspan = text.append('tspan').attr('x', 0).attr('y', y);
                    newDy = `${(lineNumber += 1) * lineHeight + dy}em`;
                    tspan.attr('dy', newDy);
                    tspan.text(word);
                }
            });
        });
    }

    function update(source, animationDuration) {
        function click(event, d) {
            if (d.children) {
                d._children = d.children;
                d.children = null;
            } else {
                d.children = d._children;
                d._children = null;
            }
            update(d, slowAnimation);
        }

        const treeData = treemap(root);
        const nodes = treeData.descendants();
        const links = treeData.descendants().slice(1);
        const nodeDepth = nodes.map((n) => n.depth);
        const maxNodeDepth = Math.max(...nodeDepth);

        nodes.forEach((d) => {
            d.id = nodeKeyName(d.data.name);
            if (d.depth === 0) {
                d.y = d.depth * 100;
            } else {
                d.y = (d.depth * height) / maxNodeDepth;
            }
        });

        const node = svg.selectAll('g.node')
            .data(nodes, (d) => d.id);

        const nodeEnter = node.enter().append('g')
            .attr('class', (d) => `node ${d.data.class ? d.data.class : ''} ${nodeKeyName(d.data.name)}`)
            .attr('transform', `translate(${source.x0},${source.y0})`)
            .on('click', (e, d) => {
                setSelectedNodes(d.data.name);
                const clickedName = nodeKeyName(d.data.name);
                const activeBool = d3.select(`.js-cell-${nodeKeyName(d.data.name)}`).classed('active-cell');
                if (document.querySelectorAll('.active-cell').length === 0) {
                    internalSelectedNodes = [];
                }
                if (activeBool) {
                    d3.selectAll(`.js-cell-${nodeKeyName(d.data.name)}`).classed('active-cell', false);
                    internalSelectedNodes = internalSelectedNodes.filter((s) => s !== clickedName);
                } else {
                    d3.selectAll(`.js-cell-${nodeKeyName(d.data.name)}`).classed('active-cell', true);
                    internalSelectedNodes = [...internalSelectedNodes, clickedName];
                }
                e.stopPropagation();
            });

        const nodeGroup = nodeEnter.append('g')
            .attr('class', (d) => `js-cell-${nodeKeyName(d.data.name)} js-cell ${internalSelectedNodes.indexOf(nodeKeyName(d.data.name)) > -1 ? 'active-cell' : ''} ${d._children ? 'parent-cell' : ''} ${(searchMapping && searchMapping.includes(mapTermToNode(d.data.name))) ? 'clickable' : !(searchMapping) ? 'clickable' : 'unclickable'}`)
            .on('mouseover', (e, d) => {
                // add hover styles on node
                d3.select(`.js-cell-${nodeKeyName(d.data.name)}`).selectAll('ellipse').style('transform', 'scale(1.2)');
                // highlight corresponding matrix row
                d3.select(`.${d.data.name.replace(/\s/g, '_').toLowerCase()}`).selectAll('th').attr('class', d.data.class);
            })
            .on('mouseout', (e, d) => {
                // remove hover styles from node
                d3.select(`.js-cell-${nodeKeyName(d.data.name)}`).selectAll('ellipse').style('transform', 'scale(1)');
                // remove highlight from corresponding matrix row
                d3.select(`.${d.data.name.replace(/\s/g, '_').toLowerCase()}`).selectAll('th').attr('class', '');
            });

        ellipseSettings.forEach((ellipseSetting, idx) => {
            nodeGroup.append('ellipse')
                .attr('cx', ellipseSetting.cx)
                .attr('cy', ellipseSetting.cy)
                .attr('rx', ellipseSetting.rx)
                .attr('ry', ellipseSetting.ry)
                .style('stroke', ellipseSetting.stroke)
                .style('stroke-width', 1)
                .attr('class', (d) => (d.data.class ? `${d.data.class} ellipse${idx}` : colorCode(d) ? `${colorCode(d)} ellipse${idx}` : `default ellipse${idx}`));
        });

        if (targetDiv.indexOf('thumbnail') === -1) {
            nodeEnter.append('text')
                .attr('dy', '.35em')
                .attr('y', 30)
                .style('text-anchor', 'middle')
                .text((d) => nodeLabel(d.data.name))
                .attr('class', (d) => `node-text ${(searchMapping && searchMapping.includes(d.data.name)) ? 'clickable' : !(searchMapping) ? 'clickable' : 'unclickable'}`);

            nodeEnter.selectAll('text')
                .call(wrap, textWrapWidth);

            nodeEnter.selectAll('.node-text')
                .attr('transform', (d) => {
                    const textNode = d3.select(`g.node.${nodeKeyName(d.data.name)} text.node-text`);
                    if (d.children && textNode && textNode.node()) {
                        const textNodeHeight = textNode.node().getBBox().height;
                        const newOffset = -50 - textNodeHeight;
                        return `translate(0, ${newOffset})`;
                    }
                    if (d.data.name === 'inflammatory macrophage') {
                        return 'translate(0,-70)';
                    }
                    return 'translate(0,0)';
                });

            nodeEnter.append('text')
                .attr('class', (d) => `node-expander-collapser clicker-${nodeKeyName(d.data.name)}`)
                .text((d) => (d._children ? circlePlus : d.children ? circleMinus : ''))
                .attr('y', '-10px')
                .attr('x', '-10px')
                .style('font-size', '28px')
                .on('click', function clickFunction(e, d) {
                    const thisText = d3.select(this).text();
                    if (thisText === circlePlus) {
                        d3.select(this).text(circleMinus);
                    } else if (thisText === circleMinus) {
                        d3.select(this).text(circlePlus);
                    }
                    click(e, d);
                    e.stopPropagation();
                });
        }

        const nodeUpdate = nodeEnter.merge(node);

        nodeUpdate.transition()
            .duration(animationDuration)
            .attr('transform', (d) => `translate(${d.x},${d.y})`);

        nodeUpdate.select('g.js-cell')
            .attr('class', (d) => `js-cell-${nodeKeyName(d.data.name)} js-cell ${internalSelectedNodes.indexOf(nodeKeyName(d.data.name)) > -1 ? 'active-cell' : ''} ${d._children ? 'parent-cell' : ''} ${(searchMapping && searchMapping.includes(mapTermToNode(d.data.name))) ? 'clickable' : !(searchMapping) ? 'clickable' : 'unclickable'}`);

        const nodeExit = node.exit().transition()
            .duration(animationDuration)
            .attr('transform', `translate(${source.x},${source.y})`)
            .remove();

        nodeExit.select('text')
            .style('fill-opacity', 1e-6);

        const link = svg.selectAll('path.link')
            .data(links, (d) => d.id);

        const linkEnter = link.enter().insert('path', 'g')
            .attr('class', (d) => `link ${d.data.linkClass ? d.data.linkClass : ''}`)
            .attr('d', () => {
                const o = {
                    x: source.x0,
                    y: source.y0,
                };
                return diagonal(o, o);
            });

        const linkUpdate = linkEnter.merge(link);

        linkUpdate.transition()
            .duration(animationDuration)
            .attr('d', (d) => diagonal(d, d.parent));

        link.exit().transition()
            .duration(animationDuration)
            .attr('d', () => {
                const o = {
                    x: source.x,
                    y: source.y,
                };
                return diagonal(o, o);
            })
            .remove();

        nodes.forEach((d) => {
            d.x0 = d.x;
            d.y0 = d.y;
        });
    }

    update(root, fastAnimation);
};


export const drawThumbnail = (d3, targetDiv, data, fullWidth, fullHeight, margin, selectedNodes, setSelectedNodes, searchMapping, treeName) => {
    const thumbnailMargin = { top: 40, right: 20, bottom: 40, left: 20 };
    drawTree(d3, targetDiv, data, 300, 500, thumbnailMargin, selectedNodes, setSelectedNodes, searchMapping, treeName);
};
