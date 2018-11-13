import React from 'react';
import PropTypes from 'prop-types';

const maxFilesBrowsed = 40; // Maximum number of files to browse
const domainName = 'https://www.encodeproject.org';
const dummyFiles = [
    {
        file_format: 'bigWig',
        output_type: 'minus strand signal of all reads',
        accession: 'ENCFF425LKJ',
        href: '/files/ENCFF425LKJ/@@download/ENCFF425LKJ.bigWig',
        dataset: '/files/ENCFF425LKJ/@@download/ENCFF425LKJ.bigWig',
    },
    {
        file_format: 'bigWig',
        output_type: 'plus strand signal of all reads',
        accession: 'ENCFF638QHN',
        href: '/files/ENCFF638QHN/@@download/ENCFF638QHN.bigWig',
        dataset: '/files/ENCFF638QHN/@@download/ENCFF638QHN.bigWig',
    },
    {
        file_format: 'bigWig',
        output_type: 'plus strand signal of unique reads',
        accession: 'ENCFF541XFO',
        href: '/files/ENCFF541XFO/@@download/ENCFF541XFO.bigWig',
        dataset: '/files/ENCFF541XFO/@@download/ENCFF541XFO.bigWig',
    },
    {
        file_format: 'bigBed',
        output_type: 'transcription start sites',
        accession: 'ENCFF517WSY',
        href: '/files/ENCFF517WSY/@@download/ENCFF517WSY.bigBed',
        dataset: '/files/ENCFF517WSY/@@download/ENCFF517WSY.bigBed',
    },
    {
        file_format: 'bigBed',
        output_type: 'peaks',
        accession: 'ENCFF026DAN',
        href: '/files/ENCFF026DAN/@@download/ENCFF026DAN.bigBed',
        dataset: '/files/ENCFF026DAN/@@download/ENCFF026DAN.bigBed',
    },
    {
        file_format: 'bigBed',
        output_type: 'peaks',
        accession: 'ENCFF847CBY',
        href: '/files/ENCFF847CBY/@@download/ENCFF847CBY.bigBed',
        dataset: '/files/ENCFF847CBY/@@download/ENCFF847CBY.bigBed',
    },
];

// Display information on page as JSON formatted data
export class Biodalliance extends React.Component {
    constructor(props, context) {
        super(props, context);

        this.state = {
            chr: +props.context.coordinates.split("chr")[1].split(":")[0],
            viewStart: +props.context.coordinates.split(":")[1].split("-")[0],
            viewEnd: +props.context.coordinates.split("-")[1],
        };

        console.log(this.state);

        // Bind `this` to non-React methods.
        this.locationChange = this.locationChange.bind(this);
        this.makeTrackLabel = this.makeTrackLabel.bind(this);
    };

    componentDidMount() {

        let cookieKey = 'GRCh37';
        let coordSystem = { speciesName: 'Homo sapiens', taxon: 9606, auth: 'GRCh', version: 37, ucscName: 'hg19' };
        let sources = [
            {
                name: 'Genome',
                desc: 'Human reference genome build GRCh37/hg19',
                twoBitURI: 'https://s3-us-west-1.amazonaws.com/encoded-build/browser/hg19/male.hg19.2bit',
                tier_type: 'sequence',
                provides_entrypoints: true,
                pinned: true,
            },
            {
                name: 'GENCODE',
                desc: 'Gene structures from GENCODE v19',
                bwgURI: 'https://s3-us-west-1.amazonaws.com/encoded-build/browser/hg19/gencode.v19.annotation.bb',
                stylesheet_uri: 'https://s3-us-west-1.amazonaws.com/encoded-build/browser/hg19/gencode_v19.xml',
                collapseSuperGroups: true,
                trixURI: 'https://s3-us-west-1.amazonaws.com/encoded-build/browser/hg19/gencode.v19.annotation.ix',
            },
            {
                name: 'SNPs',
                desc: 'dbSNP v141',
                jbURI: '/jbrest/snp141/hg19',
                jbQuery: 'type=HTMLFeatures',
                style: [{ style: { HEIGHT: 10 } }],
            },
            {
                name: 'Repeats',
                desc: 'Repeat annotation from RepeatMasker',
                bwgURI: 'https://s3-us-west-1.amazonaws.com/encoded-build/browser/hg19/repeats_hg19.bb',
                stylesheet_uri: 'https://s3-us-west-1.amazonaws.com/encoded-build/browser/hg19/bb-repeats_hg19.xml',
                forceReduction: -1,
            },
        ];

        this.browserFiles = [];
        let domain = `${window.location.protocol}//${window.location.hostname}`;
        if (domain.includes('localhost')) {
            domain = domainName;
        }

        // Extract only bigWig and bigBed files from the list:
        let files = dummyFiles;
        // let files = this.props.files.filter(file => file.file_format === 'bigWig' || file.file_format === 'bigBed');
        // files = files.filter(file => ['released', 'in progress', 'archived'].indexOf(file.status) > -1);
        files.forEach((file) => {
            const trackLabels = this.makeTrackLabel(file);
            if (file.file_format === 'bigWig') {
                this.browserFiles.push({
                    name: trackLabels.shortLabel,
                    desc: trackLabels.longLabel,
                    bwgURI: `${domain}${file.href}`,
                    style: [
                        {
                            type: 'default',
                            style: {
                                glyph: 'HISTOGRAM',
                                HEIGHT: 30,
                                BGCOLOR: 'rgb(166,71,71)',
                            },
                        },
                    ],
                });
            } else if (file.file_format === 'bigBed') {
                this.browserFiles.push({
                    name: trackLabels.shortLabel,
                    desc: trackLabels.longLabel,
                    bwgURI: `${domain}${file.href}`,
                    style: [
                        {
                            style: {
                                HEIGHT: 10,
                            },
                        },
                    ],
                });
            }
        });
        if (this.browserFiles.length) {
            sources = sources.concat(this.browserFiles);
        }

        console.log(files);

        require.ensure(['dalliance'], (require) => {
            const Dalliance = require('dalliance').browser;

            this.browser = new Dalliance({
                maxHeight: 2000,
                noPersist: false,
                noPersistView: false,
                noTrackAdder: true,
                maxWorkers: 4,
                noHelp: true,
                noExport: true,
                rulerLocation: 'none',
                chr: this.state.chr,
                viewStart: this.state.viewStart,
                viewEnd: this.state.viewEnd,
                cookieKey: cookieKey,
                coordSystem: coordSystem,
                sources: sources,
                noTitle: true,
                disablePoweredBy: true,
                maxViewWidth: Math.min((this.viewEnd - this.viewStart) * 10, 100000),
            });
            this.browser.addViewListener(this.locationChange);
        });
    }

    locationChange(chr, min, max) {
        const location = `chr${chr}:${min}-${max}`;
        if (location !== this.props.region) {
            if (this.props.currentRegion) {
                this.props.currentRegion(this.props.assembly, location);
                // console.log('locationChange %s %s', this.props.assembly, this.props.region);
            }
        }
    }

    makeTrackLabel(file) {
        const datasetAccession = file.dataset.split('/')[2];
        // Unreleased files are not in visBlob so get default labels
        const trackLabels = {
            shortLabel: file.accession,
            longLabel: `${file.status} ${file.output_type}`,
        };
        if (this.props.visBlobs === undefined || this.props.visBlobs === null) {
            console.log(trackLabels);
            return trackLabels;
        }
        console.log(this.props.visBlobs);
        Object.keys(this.props.visBlobs).forEach((blobKey) => {
            if (blobKey.startsWith(datasetAccession)) {
                const tracks = this.props.visBlobs[blobKey].tracks;
                const trackCount = tracks ? tracks.length : 0;
                for (let ix = 0; ix < trackCount; ix += 1) {
                    if (tracks[ix].name === file.accession) {
                        trackLabels.shortLabel = tracks[ix].shortLabel;
                        trackLabels.longLabel = tracks[ix].longLabel;
                        break;
                    }
                }
            }
        });
        return trackLabels;
    }

    render() {
        return (
            <div id="svgHolder" className="trackhub-element" />
        );
    }
}


//
//
// class GenomeBrowser extends React.Component {
//     constructor() {
//         super();
//
//         // Bind this to non-React methods.
//         this.locationChange = this.locationChange.bind(this);
//         this.makeTrackLabel = this.makeTrackLabel.bind(this);
//     }
//
//     componentDidMount() {
//         const { assembly, region, limitFiles } = this.props;
//         // console.log('DidMount ASSEMBLY: %s', assembly);
//
//         // Probably not worth a define in globals.js for visualizable types and statuses.
//         // Extract only bigWig and bigBed files from the list:
//         let files = this.props.files.filter(file => file.file_format === 'bigWig' || file.file_format === 'bigBed');
//         files = files.filter(file => ['released', 'in progress', 'archived'].indexOf(file.status) > -1);
//
//
//         // Make some fake file objects from "test" just to give the genome browser something to
//         // chew on if we're running locally.
//         // this.context.localInstance = false;
//         files = !this.context.localInstance ?
//             (limitFiles ? files.slice(0, maxFilesBrowsed - 1) : files)
//         : dummyFiles;
//
//         const browserCfg = rAssemblyToSources(assembly, region);
//
//         this.browserFiles = [];
//         let domain = `${window.location.protocol}//${window.location.hostname}`;
//         if (domain.includes('localhost')) {
//             domain = domainName;
//         }
//         files.forEach((file) => {
//             const trackLabels = this.makeTrackLabel(file);
//             if (file.file_format === 'bigWig') {
//                 this.browserFiles.push({
//                     name: trackLabels.shortLabel,
//                     desc: trackLabels.longLabel,
//                     bwgURI: `${domain}${file.href}`,
//                     style: [
//                         {
//                             type: 'default',
//                             style: {
//                                 glyph: 'HISTOGRAM',
//                                 HEIGHT: 30,
//                                 BGCOLOR: 'rgb(166,71,71)',
//                             },
//                         },
//                     ],
//                 });
//             } else if (file.file_format === 'bigBed') {
//                 this.browserFiles.push({
//                     name: trackLabels.shortLabel,
//                     desc: trackLabels.longLabel,
//                     bwgURI: `${domain}${file.href}`,
//                     style: [
//                         {
//                             style: {
//                                 HEIGHT: 10,
//                             },
//                         },
//                     ],
//                 });
//             }
//         });
//         if (this.browserFiles.length) {
//             browserCfg.sources = browserCfg.sources.concat(this.browserFiles);
//         }
//
//         require.ensure(['dalliance'], (require) => {
//             const Dalliance = require('dalliance').browser;
//
//             console.log(browserCfg);
//
//             let chr =
//
//             this.browser = new Dalliance({
//                 maxHeight: 2000,
//                 noPersist: false,
//                 noPersistView: false,
//                 noTrackAdder: true,
//                 maxWorkers: 4,
//                 noHelp: true,
//                 noExport: true,
//                 rulerLocation: 'none',
//                 chr: browserCfg.chr,
//                 viewStart: browserCfg.viewStart,
//                 viewEnd: browserCfg.viewEnd,
//                 cookieKey: browserCfg.cookieKey,
//                 coordSystem: browserCfg.coordSystem,
//                 sources: browserCfg.sources,
//                 noTitle: true,
//                 disablePoweredBy: true,
//                 maxViewWidth: Math.min((browserCfg.viewEnd - browserCfg.viewStart) * 10, 100000),
//             });
//             this.browser.addViewListener(this.locationChange);
//         });
//     }
//
//     componentDidUpdate() {
//         // Remove old tiers
//         if (this.browser && this.browserFiles && this.browserFiles.length) {
//             this.browserFiles.forEach((fileSource) => {
//                 this.browser.removeTier({
//                     name: fileSource.name,
//                     desc: fileSource.desc,
//                     bwgURI: fileSource.bwgURI,
//                 });
//             });
//         }
//
//         const files = !this.context.localInstance ? this.props.files.slice(0, maxFilesBrowsed - 1) : dummyFiles;
//         if (this.browser && files && files.length) {
//             let domain = `${window.location.protocol}//${window.location.hostname}`;
//             if (domain.includes('localhost')) {
//                 domain = domainName;
//             }
//             files.forEach((file) => {
//                 const trackLabels = this.makeTrackLabel(file);
//                 if (file.file_format === 'bigWig') {
//                     this.browser.addTier({
//                         name: trackLabels.shortLabel,
//                         desc: trackLabels.longLabel,
//                         bwgURI: `${domain}${file.href}`,
//                         style: [
//                             {
//                                 type: 'default',
//                                 style: {
//                                     glyph: 'HISTOGRAM',
//                                     HEIGHT: 30,
//                                     BGCOLOR: 'rgb(166,71,71)',
//                                 },
//                             },
//                         ],
//                     });
//                 } else if (file.file_format === 'bigBed') {
//                     this.browser.addTier({
//                         name: trackLabels.shortLabel,
//                         desc: trackLabels.longLabel,
//                         bwgURI: `${domain}${file.href}`,
//                         style: [
//                             {
//                                 style: {
//                                     HEIGHT: 10,
//                                 },
//                             },
//                         ],
//                     });
//                 }
//             });
//         }
//     }
//
//     locationChange(chr, min, max) {
//         console.log("changing location");
//         const location = `chr${chr}:${min}-${max}`;
//         if (location !== this.props.region) {
//             if (this.props.currentRegion) {
//                 this.props.currentRegion(this.props.assembly, location);
//                 // console.log('locationChange %s %s', this.props.assembly, this.props.region);
//             }
//         }
//     }
//
//     makeTrackLabel(file) {
//         const datasetAccession = file.dataset.split('/')[2];
//         // Unreleased files are not in visBlob so get default labels
//         const trackLabels = {
//             shortLabel: file.accession,
//             longLabel: `${file.status} ${file.output_type}`,
//         };
//         if (this.props.visBlobs === undefined || this.props.visBlobs === null) {
//             return trackLabels;
//         }
//         Object.keys(this.props.visBlobs).forEach((blobKey) => {
//             if (blobKey.startsWith(datasetAccession)) {
//                 const tracks = this.props.visBlobs[blobKey].tracks;
//                 const trackCount = tracks ? tracks.length : 0;
//                 for (let ix = 0; ix < trackCount; ix += 1) {
//                     if (tracks[ix].name === file.accession) {
//                         trackLabels.shortLabel = tracks[ix].shortLabel;
//                         trackLabels.longLabel = tracks[ix].longLabel;
//                         break;
//                     }
//                 }
//             }
//         });
//         return trackLabels;
//     }
//
//     render() {
//         return (
//             <div id="svgHolder" className="trackhub-element" />
//         );
//     }
// }
//
// Biodalliance.propTypes = {
//     files: PropTypes.array.isRequired, // Array of files to represent
//     assembly: PropTypes.string.isRequired, // Assembly to use with browser
//     region: PropTypes.string, // Region to use with browser
//     visBlobs: PropTypes.object, // This should contain one or more vis_blobs for dataset(s)
//     limitFiles: PropTypes.bool, // True to limit # files to maxFilesBrowsed
//     currentRegion: PropTypes.func,
// };
//
// Biodalliance.defaultProps = {
//     region: '',
//     visBlobs: undefined,
//     limitFiles: false,
//     currentRegion: undefined,
// };
//
// Biodalliance.contextTypes = {
//     location_href: PropTypes.string,
//     localInstance: PropTypes.bool,
// };

export default Biodalliance;
