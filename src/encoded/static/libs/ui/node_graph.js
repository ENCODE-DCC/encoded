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

const iconFileMapping = {};

// Standardizes node names
export const nodeKeyName = (name) => {
    if (name === 'H1') {
        return 'h1node';
    } else if (name === 'brain (30/90/180 days organoid)') {
        return 'brain';
    } else if (name === 'nephron (21/35/49 days organoid)') {
        return 'nephron';
    } else if (name === 'brain (90/180 days organoid)') {
        return 'brain';
    }
    const newName = name.replace(/\s/g, '').replace(/[\W_]+/g, '').toLowerCase();
    return newName;
}

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
    return 'default';
};

const iconLookup = (name) => {
    let iconName = '/static/img/immune-cells/t_cell.svg';
    if (['basophil', 'eosinophil', 'neutrophil', 'erythrocytes', 'platelets', 'megakaryocyte'].includes(name)) {
        iconName = `/static/img/immune-cells/${name}.svg`;
    }
    if (name.includes('natural killer')) {
        iconName = '/static/img/immune-cells/nk_cell.svg';
    }
    if (name.includes('progenitor')) {
        iconName = '/static/img/immune-cells/progenitor_cell.svg';
    }
    if (name.includes('monocyte')) {
        iconName = '/static/img/immune-cells/monocyte.svg';
    }
    if (name.includes('macrophage')) {
        iconName = '/static/img/immune-cells/macrophage.svg';
    }
    if (name.includes('Hematopoietic')) {
        iconName = '/static/img/immune-cells/hematopoetic_cell.svg';
    }
    if (name.includes('dendritic')) {
        iconName = '/static/img/immune-cells/dendritic_cell.svg';
    }
    if (name.includes('B')) {
        iconName = '/static/img/immune-cells/b_cell.svg';
    }
    return iconName;
};

// Creates a curved (diagonal) path from parent to the child nodes
function diagonal(d, s) {
    const path = `M${d.x},${d.y}C${d.x},${(d.y + s.y) / 2} ${s.x},${(d.y + s.y) / 2} ${s.x},${s.y}`;
    return path;
}

export const drawTree = (d3, targetDiv, data, fullWidth, fullHeight, margin, selectedNodes, setSelectedNodes, searchMapping, treeName) => {
    const isDesktop = fullWidth > mobileLimit;
    let textWrapWidth = 50;

    if (isDesktop) {
        textWrapWidth = 115;
    }

    if (treeName === 'immune') {
        textWrapWidth = 50;
    }

    if (data.name === 'H9') {
        textWrapWidth = 50;
    }

    const width = fullWidth - margin.left - margin.right;
    const height = fullHeight - margin.top - margin.bottom;

    d3.select(targetDiv).select('svg').remove();

    let internalSelectedNodes = selectedNodes;

    const traverseTree = (d, activeBool) => {
        const children = d.children || d._children;
        if (children) {
            children.forEach((child) => {
                const clickedName = nodeKeyName(child.data.name);
                setSelectedNodes(child.data.name, activeBool);
                if (activeBool) {
                    d3.selectAll(`.js-cell-${nodeKeyName(child.data.name)}`).classed('active-cell', false);
                    internalSelectedNodes = internalSelectedNodes.filter((s) => s !== clickedName);
                } else {
                    d3.selectAll(`.js-cell-${nodeKeyName(child.data.name)}`).classed('active-cell', true);
                    internalSelectedNodes = [...internalSelectedNodes, clickedName];
                }
                traverseTree(child, activeBool);
            });
        }
    };

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

        // If "hide all" has been selected and no nodes are active, the internal selected nodes need to be cleared
        if (document.querySelectorAll('.active-cell').length === 0 && targetDiv.indexOf('thumbnail') === -1 && treeName === 'immune') {
            internalSelectedNodes = [];
        }
        // If "show all" has been selected and all nodes are active, the internal selected nodes need to be added
        if (document.querySelectorAll('.active-cell').length > 0 && internalSelectedNodes.length === 0 && targetDiv.indexOf('thumbnail') === -1 && treeName === 'immune') {
            internalSelectedNodes = selectedNodes;
        }

        const node = svg.selectAll('g.node')
            .data(nodes, (d) => d.id);

        const nodeEnter = node.enter().append('g')
            .attr('class', (d) => `node ${d.data.class ? d.data.class : ''} ${nodeKeyName(d.data.name)}`)
            .attr('transform', `translate(${source.x0},${source.y0})`)
            .on('click', (e, d) => {
                const clickedName = nodeKeyName(d.data.name);
                // 'activeBool' represents if a clicked node is currently selected or de-selected so that that state can be toggled (and its children changed to that toggle value if shift is not pressed)
                const activeBool = d3.select(`.js-cell-${nodeKeyName(d.data.name)}`).classed('active-cell');
                setSelectedNodes(d.data.name, activeBool);
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
                // If the shift key is pressed, children nodes are not selected/deselected on click
                // If the shift key is not pressed, the children nodes are traversed to be selected/deselected along with clicked node
                if (!e.shiftKey) {
                    traverseTree(d, activeBool);
                }
                e.stopPropagation();
            });

        const nodeGroup = nodeEnter.append('g')
            .attr('class', (d) => `js-cell-${nodeKeyName(d.data.name)} js-cell-${nodeKeyName(d.data.name)}-${(targetDiv.indexOf('thumbnail') > -1) ? 'thumbnail' : 'full'} js-cell ${colorCode(d)} ${internalSelectedNodes.indexOf(nodeKeyName(d.data.name)) > -1 ? 'active-cell' : ''} ${d._children ? 'parent-cell' : ''} ${(searchMapping && searchMapping.includes(mapTermToNode(d.data.name))) ? 'clickable' : !(searchMapping) ? 'clickable' : 'unclickable'}`)
            .on('mouseover', (e, d) => {
                // add hover styles on node
                d3.select(`.js-cell-${nodeKeyName(d.data.name)}`).selectAll('ellipse').style('transform', 'scale(1.2)');
                // highlight corresponding matrix row
                const rowSelector = `.${nodeKeyName(d.data.name)}`;
                if (d3.select(rowSelector)) {
                    d3.select().selectAll('th').attr('class', d.data.class);
                }
            })
            .on('mouseout', (e, d) => {
                // remove hover styles from node
                d3.select(`.js-cell-${nodeKeyName(d.data.name)}`).selectAll('ellipse').style('transform', 'scale(1)');
                // remove highlight from corresponding matrix row
                const rowSelector = `.${nodeKeyName(d.data.name)}`;
                if (d3.select(rowSelector)) {
                    d3.select(rowSelector).selectAll('th').attr('class', '');
                }
            });

        if (treeName === 'sescc') {
            nodes.forEach((d) => {
                if (d.data.name === 'PGP donor') {
                    d3.select('.pgpdonor').append('g')
                            .attr('class', 'icon-group')
                            .style('transform', 'translate(-13px, -5px) scale(0.06)')
                        .append('path')
                            .attr('d', 'M224,256c70.7,0,128-57.3,128-128S294.7,0,224,0S96,57.3,96,128S153.3,256,224,256z M134.4,288C85,297,0,348.2,0,422.4V464 c0,26.5,0,48,48,48h352c48,0,48-21.5,48-48v-41.6c0-74.2-92.8-125.4-134.4-134.4S183.8,279,134.4,288z')
                            .attr('fill', '#eaeaea')
                            .attr('stroke', 'black')
                            .attr('stroke-width', '15px');
                }
            });
            triCell.forEach((ellipseSetting, idx) => {
                nodeGroup.append('ellipse')
                    .attr('cx', ellipseSetting.cx)
                    .attr('cy', ellipseSetting.cy)
                    .attr('rx', ellipseSetting.rx)
                    .attr('ry', ellipseSetting.ry)
                    .style('stroke', ellipseSetting.stroke)
                    .style('stroke-width', 1)
                    .style('fill', (d) => d.data.selectedColor ? internalSelectedNodes.indexOf(nodeKeyName(d.data.name)) > -1 ? d.data.selectedColor : d.data.deselectedColor : 'unset')
                    .style('stroke', (d) => (d.data.selectedColor ? 'black' : 'unset'))
                    .attr('class', (d) => ((d.data.class && !(d.data.selectedColor))? `${d.data.class} ellipse${idx}` : colorCode(d) ? `${colorCode(d)} ellipse${idx}` : `default ellipse${idx}`));
            });
        } else {
            require('d3-fetch');
            nodes.forEach((d) => {
                const iconFile = iconLookup(d.data.name);
                if (iconFileMapping[iconFile]) {
                    iconFileMapping[iconFile].push(`.js-cell-${nodeKeyName(d.data.name)}-${(targetDiv.indexOf('thumbnail') > -1) ? 'thumbnail' : 'full'}`);
                } else {
                    iconFileMapping[iconFile] = [`.js-cell-${nodeKeyName(d.data.name)}-${(targetDiv.indexOf('thumbnail') > -1) ? 'thumbnail' : 'full'}`];
                }
            });
            Object.keys(iconFileMapping).forEach((iconFile) => {
                d3.xml(iconFile)
                    .then((svgXml) => {
                        let newSvg;
                        iconFileMapping[iconFile].forEach((n) => {
                            if (d3.select(n) && d3.select(n).node()) {
                                newSvg = svgXml.documentElement.cloneNode(true);
                                d3.select(n).node().append(newSvg);
                            }
                        });
                    });
            });
        }

        if (targetDiv.indexOf('thumbnail') === -1) {
            nodeEnter.append('text')
                .attr('dy', '.35em')
                .attr('y', 30)
                .style('text-anchor', 'middle')
                .style('stroke','white')
                .style('stroke-width','6px')
                .text((d) => nodeLabel(d.data.name))
                .attr('class', (d) => `node-text`);

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
                    let xOffset = 0;
                    if (d.data.name === 'lateral mesodermal cell') {
                        xOffset = -5;
                    }
                    if (d.data.name === 'mesothelial cell of epicardium') {
                        xOffset = 5;
                    }
                    const textNode = d3.select(`g.node.${nodeKeyName(d.data.name)} text.node-text`);
                    if (d.children && textNode && textNode.node()) {
                        const textNodeHeight = textNode.node().getBBox().height;
                        const newOffset = -50 - textNodeHeight;
                        return `translate(${xOffset}, ${newOffset})`;
                    }
                    if (d.data.name === 'inflammatory macrophage') {
                        return 'translate(0,-70)';
                    }
                    return `translate(${xOffset},0)`;
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
            .attr('class', (d) => `js-cell-${nodeKeyName(d.data.name)} js-cell-${nodeKeyName(d.data.name)}-${(targetDiv.indexOf('thumbnail') > -1) ? 'thumbnail' : 'full'} js-cell ${colorCode(d)} ${internalSelectedNodes.indexOf(nodeKeyName(d.data.name)) > -1 ? 'active-cell' : ''} ${d._children ? 'parent-cell' : ''} ${(searchMapping && searchMapping.includes(mapTermToNode(d.data.name))) ? 'clickable' : !(searchMapping) ? 'clickable' : 'unclickable'}`);

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
