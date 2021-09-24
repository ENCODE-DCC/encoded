import { svgIcon } from '../svg-icons';

const animationDuration = 300;
const textWrapWidth = 120;

const emptyCheckbox = '\u25EF';
const filledCheckbox = '\u2B24';

// const emptyCheckbox = '\u2295';
// const filledCheckbox = '\u2295';

// const emptyCheckbox = '&#xf058;';
// const filledCheckbox = '&#xf05d;';

// const emptyCheckbox = '○';
// const filledCheckbox = '●';

const ellipseSettings = [
    { cx: 2, cy: 2, rx: 12, ry: 9, stroke: 'black', 'stroke-width': 1 },
    { cx: 2, cy: 2, rx: 6.5, ry: 6, stroke: 'black', 'stroke-width': 1 },
    { cx: -5, cy: 10, rx: 12, ry: 9, stroke: 'black', 'stroke-width': 1 },
    { cx: -5, cy: 10, rx: 6.5, ry: 5, stroke: 'black', 'stroke-width': 1 },
    { cx: 10, cy: 10, rx: 12, ry: 9, stroke: 'black', 'stroke-width': 1 },
    { cx: 10, cy: 10, rx: 6.5, ry: 5, stroke: 'black', 'stroke-width': 1 },
];

// Collapse node and its children
function collapse(d) {
    if (d.children) {
        d._children = d.children;
        d._children.forEach(collapse);
        d.children = null;
    }
}

function textClick(e, d) {
    console.log(d.data.name);
    console.log(e);
    e.stopPropagation();
}

// Creates a curved (diagonal) path from parent to the child nodes
function diagonal(d, s) {
    const path = `M${d.x},${d.y}C${d.x},${(d.y + s.y) / 2} ${s.x},${(d.y + s.y) / 2} ${s.x},${s.y}`;
    return path;
}

const drawTree = (d3, targetDiv, treeData, fullWidth, fullHeight, margin, selectedNodes) => {
    // Set the dimensions and margins of the diagram
    const width = fullWidth - margin.left - margin.right;
    const height = fullHeight - margin.top - margin.bottom;

    // append the svg object to the body of the page
    // appends a 'group' element to 'svg'
    // moves the 'group' element to the top left margin
    const svg = d3.select(targetDiv).append('svg')
        .attr('width', fullWidth)
        .attr('height', fullHeight)
        .attr('viewBox', `0 0 ${fullWidth} ${fullHeight}`)
        .attr('preserveAspectRatio', 'xMidYMin meet')
        .append('g')
        .attr('transform', `translate(${margin.left},${margin.top})`);

    let i = 0;

    // declares a tree layout and assigns the size
    const treemap = d3.tree().size([width, height]);

    // Assigns parent, children, height, depth
    const root = d3.hierarchy(treeData, (d) => d.children);
    root.x0 = width / 2;
    root.y0 = 100;

    function wrap(text, textWidth) {
        text.each(function() {
            text = d3.select(this);
            const words = text.text().split(/\s+/).reverse();
            let word = '';
            console.log(text.text());
            let line = [];
            console.log(emptyCheckbox);
            console.log(filledCheckbox);
            if (selectedNodes.indexOf(text.text()) > -1) {
                line = [emptyCheckbox];
            } else {
                line = [filledCheckbox];
            }
            let lineNumber = 0;
            const lineHeight = 1.1;
            const y = text.attr('y');
            const dy = parseFloat(text.attr('dy'));

            // append checkbox
            let tspan = text.text(null).append('tspan').attr('x', 0).attr('y', y);
            // tspan.attr('class', 'layer-bubble');
            // tspan.attr('dy', '-1em');
            // tspan.text(emptyCheckbox);
            //
            // // loop through words appending tspans
            // tspan = text.append('tspan').attr('x', 0).attr('y', y);
            while (word = words.pop()) {
                line.push(word);
                tspan.text(line.join(' '));
                if (tspan.node().getComputedTextLength() > textWidth) {
                    line.pop();
                    tspan.text(line.join(' '));
                    line = [word];
                    tspan = text.append('tspan').attr('x', 0).attr('y', y);
                    tspan.attr('dy', `${(lineNumber += 1) * lineHeight + dy}em`).text(word);
                }
            }
        });
    }

    // Collapse after the second level
    // root.children.forEach(collapse);
    update(root);

    function update(source) {
        // Assigns the x and y position for the nodes
        const treeData = treemap(root);

        // Compute the new tree layout.
        const nodes = treeData.descendants();
        const links = treeData.descendants().slice(1);
        const nodeDepth = nodes.map((n) => n.depth);
        const maxNodeDepth = Math.max(...nodeDepth);

        // Normalize for fixed-depth.
        nodes.forEach(function(d) {
            // d.y = d.depth * 100;
            if (d.depth === 0) {
                d.y = d.depth * 100;
            } else {
                d.y = d.depth * height / maxNodeDepth;
            }
        });

        const node = svg.selectAll('g.node')
            .data(nodes, function(d) {return d.id || (d.id = (i += 1)); });

        // Enter any new modes at the parent's previous position.
        const nodeEnter = node.enter().append('g')
            .attr('class', (d) => `node ${d.data.class ? d.data.class : ''}`)
            .attr('transform', function(d) {
                return "translate(" + source.x0 + "," + source.y0 + ")";
            })
            .on('click', click);

        const nodeGroup = nodeEnter.append('g')
            .attr('class', (d) => (d._children ? 'js-cell parent-cell' : 'js-cell'))
            .on('mouseover', function() {
                d3.select(this).selectAll('ellipse').style('transform', 'scale(1.2)');
                d3.select(this).selectAll('ellipse').attr('class', 'hover-class');
            })
            .on('mouseout', function() {
                d3.select(this).selectAll('ellipse').style('transform', 'scale(1)');
                d3.select(this).selectAll('ellipse').attr('class', '');
            });

        ellipseSettings.forEach((ellipseSetting) => {
            nodeGroup.append('ellipse')
                .attr('cx', ellipseSetting.cx)
                .attr('cy', ellipseSetting.cy)
                .attr('rx', ellipseSetting.rx)
                .attr('ry', ellipseSetting.ry)
                .style('stroke', ellipseSetting.stroke)
                .style('stroke-width', 1)
                .attr('class', () => 'js-cell');
        });

        // adds the text to the node
        nodeEnter.append('text')
            .attr('dy', '.35em')
            .attr('y', (d) => ((d.children && (d.data.name.length < 16 || d.data.name.split(' ').length === 1)) ? -20 : d.children ? -40 : 30))
            .style('text-anchor', 'middle')
            .text((d) => d.data.name)
            .on('click', textClick);

        nodeEnter.selectAll('text')
            .call(wrap, textWrapWidth);

        // adds the text to the node
        // nodeEnter.append('circle')
        //     .attr('class', 'node')
        //     .attr('r', 1e-6)
        //     .style('fill', 'red');

        // UPDATE
        const nodeUpdate = nodeEnter.merge(node);

        // Transition to the proper position for the node
        nodeUpdate.transition()
            .duration(animationDuration)
            .attr('transform', function(d) {
                return "translate(" + d.x + "," + d.y + ")";
             });

        // Update the node attributes and style
        // nodeUpdate.select('circle.node')
        //     .attr('r', 10);

        // Update the node attributes and style
        nodeUpdate.select('g.js-cell')
            .attr('class', (d) => (d._children ? 'js-cell parent-cell' : 'js-cell'));


        // Remove any exiting nodes
        const nodeExit = node.exit().transition()
            .duration(animationDuration)
            .attr("transform", function(d) {
                return "translate(" + source.x + "," + source.y + ")";
            })
            .remove();

        nodeExit.select('text')
            .style('fill-opacity', 1e-6);

        const link = svg.selectAll('path.link')
            .data(links, function(d) { return d.id; });

        // Enter any new links at the parent's previous position.
        const linkEnter = link.enter().insert('path', "g")
            .attr('class', 'link')
            .attr('d', function(d){
                const o = {x: source.x0, y: source.y0}
                return diagonal(o, o)
            });

        const linkUpdate = linkEnter.merge(link);

        linkUpdate.transition()
            .duration(animationDuration)
            .attr('d', function(d){ return diagonal(d, d.parent) });

        const linkExit = link.exit().transition()
            .duration(animationDuration)
            .attr('d', function(d) {
                const o = {x: source.x, y: source.y}
                return diagonal(o, o)
            })
            .remove();

        nodes.forEach((d) => {
            d.x0 = d.x;
            d.y0 = d.y;
        });

        function click(event, d) {
            if (d.children) {
                d._children = d.children;
                d.children = null;
            } else {
                d.children = d._children;
                d._children = null;
            }
            update(d);
        }
    }
};

export default drawTree;
