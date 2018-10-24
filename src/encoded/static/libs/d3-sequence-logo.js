/**
 * File: sequence_logo.js
 * Author: Sam Lichtenberg (splichte@gmail.com)
 *
 * This file implements sequence logo generation for
 * bounded sequences in d3.
 *
 * See `https://en.wikipedia.org/wiki/Sequence_logo`
 * for more information.
 *
 * Usage (see `index.html` for example):
 *  (1) define sequence number and length bounds
 *  (2) define sequence data
 *  (3) call entry_point with (1) and (2).
 */

var d3 = require('d3');

/**
 * For each index, get the transform needed so that things line up
 * correctly. This is an artifact of the font->svg path conversion
 * used (letter paths are not even width, even in monospace fonts).
 *
 * @param {number} i - letter index. Range: [0,4)
 * @returns {number[]} baseTransform - the (x,y) transform that will
 *  be applied to all letters.
 */
function getLetterBaseTransform(i) {
  const baseTransform = [];
  baseTransform[0] = -132.09;
  baseTransform[1] = -20.32;

  if (i === 3) { // letter T
    baseTransform[0] += 3;
    baseTransform[1] -= 0.0;
  } else if (i === 1) { // letter A
    baseTransform[0] += 1;
    baseTransform[1] -= 0.5;
  }

  return baseTransform;
}

/**
 * The letters G,A,C,T are encoded as constant SVG path strings
 * which undergo 'transform' operations when exposed to the data.
 *
 * @param {number} i - letter index. Range: [0,4)
 * @returns {string} SVG path corresponding to i.
 */
function getLetterPath(i) {
  const letterA = 'M142.59,54.29l-5,15.27h-6.48L147.55,21h7.56l16.56,48.53H165l-5.18-15.27Zm15.91-4.9-4.75-14c-1.08-3.17-1.8-6-2.52-8.86h-.14c-.72,2.88-1.51,5.83-2.45,8.78l-4.75,14Z';

  const letterG = 'M171.68,67.39a45.22,45.22,0,0,1-14.91,2.66c-7.34,0-13.39-1.87-18.15-6.41-4.18-4-6.77-10.51-6.77-18.07.07-14.47,10-25.06,26.28-25.06a30,30,0,0,1,12.1,2.23l-1.51,5.11A25.15,25.15,0,0,0,158,25.77c-11.81,0-19.51,7.34-19.51,19.51s7.42,19.59,18.72,19.59c4.1,0,6.91-.58,8.35-1.3V49.1h-9.86v-5h16Z';

  const letterT = 'M144,26.35H129.19V21h35.93v5.33H150.29v43.2H144Z';

  const letterC = 'M168.65,68c-2.3,1.15-6.91,2.3-12.82,2.3-13.68,0-24-8.64-24-24.55,0-15.19,10.3-25.49,25.35-25.49,6,0,9.86,1.3,11.52,2.16l-1.51,5.11a22.82,22.82,0,0,0-9.79-2c-11.38,0-18.94,7.27-18.94,20,0,11.88,6.84,19.51,18.65,19.51a25.08,25.08,0,0,0,10.23-2Z';

  if (i === 0) {
    return letterG;
  } else if (i === 1) {
    return letterA;
  } else if (i === 2) {
    return letterC;
  } else if (i === 3) {
    return letterT;
  }
  return null;
}

/**
 * @param {string[]} s - sequence data. An array of equal-length strings.
 * @param {number} i - letter index. Range: [0,4)
 * @returns {number[]} counts of each letter.
 */
function getLetterCnts(s, i) {
  const dict = { G: 0,
    A: 0,
    C: 0,
    T: 0 };

  s.forEach((d) => {
    dict[d[i]] += 1;
  });

  const out = Object.keys(dict).map(key => dict[key]);
  return out;
}

/**
 * @param {string[]} s - sequence data. An array of equal-length strings.
 * @param {number} i - letter index. Range: [0,4)
 * @returns {number[][]} counts of each letter.
 */
function offsets(s, i) {
  const cnts = getLetterCnts(s, i);
  const offs = [];

  let ctr = 0;

  // add on the index so we can use it.
  // determine heights of rects
  cnts.forEach((d, j) => {
    const nextCtr = ctr + d;
    // -(nextCtr-ctr) is for sorting
    offs.push([ctr, nextCtr, (nextCtr - ctr), j]);
    ctr = nextCtr;
  });


  // sort by heights of produced rects
  offs.sort((a, b) => (b[2] - a[2]));

  // re-arrange data structure based on sort
  const outOffsets = [];
  ctr = 0;
  offs.forEach((d) => {
    const diff = d[2];
    outOffsets.push([ctr, ctr + diff, d[3]]);
    ctr += diff;
  });

  return outOffsets;
}

/**
 * @param {Object} path - SVG path object.
 * @param {number[]} d - contains information about offsets.
 * @param {Object} yscale - d3 scale object.
 * @param {number} colWidth - width of each column (each nucleotide pos)
 * @returns {string} transform string to be applied to the SVG path object.
 */
function calcPathTransform(path, d, yscale, colWidth) {
  const pathBBox = path.getBBox();

  /**
   * calculate scale factor based on height
   * of bounding "rectangle" (imagine a stacked bar chart)
   */
  const rectHeight = yscale(d[1] - d[0]);
  const rectWidth = colWidth;

  const scaleY = rectHeight / pathBBox.height;
  const scaleX = rectWidth / pathBBox.width;

  // transform to origin so scaling behaves as desired
  const originX = pathBBox.x;
  const originY = pathBBox.y;

  /**
   * base transform required by font->path conversion
   * (see getLetterBaseTransform comment)
   */
  const baseTransforms = getLetterBaseTransform(d[2]);
  const baseTransformX = baseTransforms[0];
  const baseTransformY = baseTransforms[1];

  // apply scale in reverse to post-scale transforms
  const postTY = (yscale(d[0]) / scaleY) + (baseTransformY / scaleY);
  const postTX = baseTransformX / scaleX;

  // pre-scale transforms
  const preTX = -originX * (scaleX - 1);
  const preTY = -originY * (scaleY - 1);

  const out = `translate(${preTX},${preTY}) scale(${scaleX},${scaleY}) translate(${postTX},${postTY})`;

  return out;
}

/**
 * Checks that sequence data obeys bounds, and that each
 * sequence has the same length.
 *
 * Possible change is to create more informative error msg.
 *
 * @param {string[]} data - sequenceData
 * @param {number[]} seqLenBounds - lower/upper bounds for
 *  number of bases in a sequence.
 * @param {number[]} seqNumBounds - lower/upper bounds for
 *  number of sequences.
 * @returns {boolean} true/false - does the data conform?
 */
function isValidData(data, seqLenBounds, seqNumBounds) {
  const n = data.length;

  if (n > seqNumBounds[1] || n < seqNumBounds[0]) {
    return false;
  }
  const m0 = d3.min(data, d => d.length);
  const m1 = d3.max(data, d => d.length);

  if (m0 !== m1) {
    return false;
  }
  // m == m0 == m1
  const m = m0;

  if (m > seqLenBounds[1] || m < seqLenBounds[0]) {
    return false;
  }
  return true;
}

/**
 * Yields nucleotide base string corresponding to given int.
 *
 * @param {number} i
 * @returns {string}
 */

function intToLetter(i) {
  if (i === 0) {
    return 'G';
  } else if (i === 1) {
    return 'A';
  } else if (i === 2) {
    return 'C';
  } else if (i === 3) {
    return 'T';
  }
  return null;
}

/**
 * Standard, from MDN.
 * Returns a random integer between min (inclusive) and max
 * (inclusive)
 *
 * @param {number} min
 * @param {number} max
 * @returns {number}
 */
function getRandomInt(min, max) {
  return Math.floor(Math.random() * ((max - min) + 1)) + min;
}


/**
 * Generate random sequences by sampling from DiscreteUniform(0,4).
 *
 * A different approach could be to favor some bases more
 * than others at different positions by modeling the
 * distribution P(base | position) as a categorical that
 * has its parameters sampled from a Dirichlet.
 *
 * @param {number[]} seqLenBounds
 * @param {number[]} seqNumBounds
 * @returns {string[]} seqData
 */
function getRandomData(seqLenBounds, seqNumBounds) {
  const seqLen = getRandomInt(seqLenBounds[0], seqLenBounds[1]);
  const seqNum = getRandomInt(seqNumBounds[0], seqNumBounds[1]);

  const seqData = [];

  for (let i = 0; i < seqNum; i += 1) {
    const thisSeq = [];
    for (let j = 0; j < seqLen; j += 1) {
      // upper bound is inclusive (getRandomInt)
      const newLetter = intToLetter(getRandomInt(0, 3));
      thisSeq.push(newLetter);
    }
    seqData.push(thisSeq.join(''));
  }

  return seqData;
}

/**
 * Entry point for all functionality.
 *
 * @param {string[]} sequenceData
 * @param {number[]} seqLenBounds
 * @param {number[]} seqNumBounds
 */
function entryPoint(sequenceData, seqLenBounds, seqNumBounds, LogoSelector) {
  const isValid = isValidData(sequenceData, seqLenBounds, seqNumBounds);

  if (!isValid) {
    return;
  }

  // number of sequences
  const n = sequenceData.length;

  // number of nucleotides per sequence
  const m = d3.max(sequenceData, d => d.length);

  // range of letter bounds at each nucleotide index position
  const yz = d3.range(m).map(i => offsets(sequenceData, i));

  /**
   * Next, we set local values that govern visual appearance.
   *
   * We define width/height here, rather than in the HTML,
   * so one can easily switch the code to modify svg size
   * based on the data if desired.
   */

  // width including endpoint markers
  const svgFullWidth = 550;

  // width of just the base letters + x-axis labels
  const svgLetterWidth = 500;

  const endpointWidth = (svgFullWidth - svgLetterWidth) / 2;

  // height including x-axis labels and endpoint markers
  const svgFullHeight = 250;

  // height of just the base letters
  const svgLetterHeight = 150;

  const colors = d3.scaleOrdinal(d3.schemeCategory10);

  // map: sequence length -> innerSVG
  const xscale = d3.scaleLinear().domain([0, m])
    .range([endpointWidth, svgLetterWidth + endpointWidth]);

  // get one unit of width from d3 scale (convenience)
  const colWidth = (xscale(1) - xscale(0));

  // map: number of sequences -> svg letter height
  const yscale = d3.scaleLinear().domain([0, n]).range([0, svgLetterHeight]);

  const svg = d3.select(LogoSelector)
    .append('svg')
    .attr('width', svgFullWidth)
    .attr('height', svgFullHeight)
    .attr('viewBox','0 0 '+svgFullWidth+' '+svgFullHeight)
    .attr('preserveAspectRation','xMidYMid meet');

  const endptFontSize = 32;

  const endptTY = (svgFullHeight + svgLetterHeight) / 2;

  // Attach left endpoint to SVG
  svg.append('text')
    .text('5\'')
    .style('text-anchor', 'begin')
    .style('font-size', endptFontSize)
    .attr('transform', `translate(0,${endptTY})`);

  // Attach right endpoint to SVG
  svg.append('text')
    .text('3\'')
    .style('text-anchor', 'end')
    .style('font-size', endptFontSize)
    .attr('transform', `translate(${svgFullWidth},${endptTY})`);


  /**
   * Our groups are organized by columns--
   * each column gets an SVG group.
   *
   * The column is used to neatly handle all x-offsets and labels.
   */
  const group = svg.selectAll('group')
    .data(yz)
    .enter()
    .append('g')
    .attr('class', 'column')
    .attr('transform', (d, i) => `translate(${xscale(i)},0)`);

  /**
   * Attach the number labels to the x-axis.
   *
   * A possible modification is to make xLabelFontSize
   * data-dependent. As written its position will change
   * with the column width (# of nucleotides), so
   * visually it will look fine, but it may be
   * desirable to alter font size as well.
   */
  const xLabelFontSize = 20;
  const xLabelTX = (colWidth / 2) + (xLabelFontSize / 3);
  const xLabelTY = svgLetterHeight + 10;

  group.append('text')
    .text((d, i) => `${i + 1}`)
    .style('font-size', xLabelFontSize)
    .style('text-anchor', 'end')
    .attr('transform', `translate(${xLabelTX}, ${xLabelTY}) rotate(270)`);

  /*
   * For each column (group):
   *  Add the letter (represented as an SVG path, see above)
   *  if the calculated height is nonzero (the filter condition).
   *
   * In other words, if that base appeared at this position
   * in at least one sequence.
   *
   * notes:
   *  Filter is used here to avoid attaching paths with 0 size
   *  to the DOM. This filtering could optionally be performed
   *  earlier, when we build yz.
   */
  group.selectAll('path')
    .data(d => d)
    .enter()
    .filter(d => (d[1] - d[0] > 0))
    .append('path')
    .attr('d', d => getLetterPath(d[2]))
    .style('fill', d => colors(d[2]))
    .attr('transform', function (d) { return calcPathTransform(this, d, yscale, colWidth); });
}

/**
 * Get random sequence data, then call entry point.
 *
 * @param {number[]} seqLenBounds
 * @param {number[]} seqNumBounds
 */
function refreshSVG(seqLenBounds, seqNumBounds) {
  const sequenceData = getRandomData(seqLenBounds, seqNumBounds);

  // clear SVG if it exists
  const svg = d3.select('svg');

  if (svg) {
    svg.remove();
  }

  entryPoint(sequenceData, seqLenBounds, seqNumBounds);
}

module.exports.entryPoint = entryPoint;
