const circlePlus = '\u2295';
const circleMinus = '\u2296';

const slowAnimation = 400;
const fastAnimation = 0;

const mobileLimit = 400;

let offset = -35;
let doubleOffset = -65;

const ellipseSettings = [
    { cx: 2, cy: 2, rx: 12, ry: 9 },
    { cx: 2, cy: 2, rx: 6.5, ry: 6 },
    { cx: -5, cy: 10, rx: 12, ry: 9 },
    { cx: -5, cy: 10, rx: 6.5, ry: 5 },
    { cx: 10, cy: 10, rx: 12, ry: 9 },
    { cx: 10, cy: 10, rx: 6.5, ry: 5 },
];

// Standardizes node names
const nodeKeyName = (name) => name.replace(/\s/g, '').toLowerCase();

// Creates a curved (diagonal) path from parent to the child nodes
function diagonal(d, s) {
    const path = `M${d.x},${d.y}C${d.x},${(d.y + s.y) / 2} ${s.x},${(d.y + s.y) / 2} ${s.x},${s.y}`;
    return path;
}

const drawTree = (d3, targetDiv, data, fullWidth, fullHeight, margin, selectedNodes, setSelectedNodes) => {
    const isDesktop = fullWidth > mobileLimit;
    let textWrapWidth = 80;
    let characterLimitForWrap = 15;
    margin.top = 50;
    margin.bottom = 80;
    margin.left = 3;
    margin.right = 3;

    if (isDesktop) {
        textWrapWidth = 115;
        characterLimitForWrap = 18;
        offset = -40;
        doubleOffset = -60;
    }

    const width = fullWidth - margin.left - margin.right;
    const height = fullHeight - margin.top - margin.bottom;

    d3.select(targetDiv).select('svg').remove();

    let internalSelectedNodes = selectedNodes;

    const svg = d3.select(targetDiv).append('svg')
        .attr('width', fullWidth)
        .attr('height', fullHeight)
        .attr('viewBox', `0 0 ${fullWidth} ${fullHeight}`)
        .attr('preserveAspectRatio', 'xMidYMin meet')
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
                if (tspan.node().getComputedTextLength() > textWidth) {
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
            .attr('class', (d) => `node ${d.data.class} ${d.data.name}`)
            .attr('transform', `translate(${source.x0},${source.y0})`)
            .on('click', (e, d) => {
                setSelectedNodes(d.data.name);
                const clickedName = nodeKeyName(d.data.name);
                if (internalSelectedNodes.indexOf(clickedName) > -1 && internalSelectedNodes.length > 1) {
                    internalSelectedNodes = internalSelectedNodes.filter((s) => s !== clickedName);
                } else if (internalSelectedNodes.indexOf(clickedName) > -1) {
                    internalSelectedNodes = [];
                } else {
                    internalSelectedNodes = [...internalSelectedNodes, clickedName];
                }
                const clickedCell = d3.select(`.js-cell-${nodeKeyName(d.data.name)}`);
                clickedCell.attr('class', `${internalSelectedNodes.indexOf(clickedName) > -1 ? 'active-cell' : ''} js-cell-${clickedName} js-cell ${d._children ? 'parent-cell' : ''}`);
                e.stopPropagation();
            });

        const nodeGroup = nodeEnter.append('g')
            .attr('class', (d) => `js-cell-${nodeKeyName(d.data.name)} js-cell ${internalSelectedNodes.indexOf(nodeKeyName(d.data.name)) > -1 ? 'active-cell' : ''} ${d._children ? 'parent-cell' : ''}`)
            .on('mouseover', (e, d) => {
                // add hover styles on node
                d3.select(`.js-cell-${nodeKeyName(d.data.name)}`).selectAll('ellipse').style('transform', 'scale(1.2)');
                d3.select(`.js-cell-${nodeKeyName(d.data.name)}`).selectAll('ellipse').attr('class', `hover-class ${d.data.class ? d.data.class : 'default'}`);
                // highlight corresponding matrix row
                d3.select(`.${d.data.name.replace(/\s/g, '_').toLowerCase()}`).selectAll('th').attr('class', d.data.class);
            })
            .on('mouseout', (e, d) => {
                // remove hover styles from node
                d3.select(`.js-cell-${nodeKeyName(d.data.name)}`).selectAll('ellipse').style('transform', 'scale(1)');
                d3.select(`.js-cell-${nodeKeyName(d.data.name)}`).selectAll('ellipse').attr('class', (d.data.class ? d.data.class : 'default'));
                // remove highlight from corresponding matrix row
                d3.select(`.${d.data.name.replace(/\s/g, '_').toLowerCase()}`).selectAll('th').attr('class', '');
            });

        ellipseSettings.forEach((ellipseSetting) => {
            nodeGroup.append('ellipse')
                .attr('cx', ellipseSetting.cx)
                .attr('cy', ellipseSetting.cy)
                .attr('rx', ellipseSetting.rx)
                .attr('ry', ellipseSetting.ry)
                .style('stroke', ellipseSetting.stroke)
                .style('stroke-width', 1)
                .attr('class', (d) => (d.data.class ? d.data.class : 'default'));
        });

        nodeEnter.append('text')
            .attr('dy', '.35em')
            .attr('y', (d) => ((d.children && (d.data.name.length < characterLimitForWrap || d.data.name.split(' ').length === 1)) ? offset : d.children ? doubleOffset : 30))
            .style('text-anchor', 'middle')
            .text((d) => d.data.name)
            .attr('class', 'node-text');

        nodeEnter.selectAll('text')
            .call(wrap, textWrapWidth);

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

        const nodeUpdate = nodeEnter.merge(node);

        nodeUpdate.transition()
            .duration(animationDuration)
            .attr('transform', (d) => `translate(${d.x},${d.y})`);

        nodeUpdate.select('g.js-cell')
            .attr('class', (d) => `js-cell-${nodeKeyName(d.data.name)} js-cell ${internalSelectedNodes.indexOf(nodeKeyName(d.data.name)) > -1 ? 'active-cell' : ''} ${d._children ? 'parent-cell' : ''}`);

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

export default drawTree;