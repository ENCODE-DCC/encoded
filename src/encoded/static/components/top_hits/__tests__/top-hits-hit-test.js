import Adapter from '@wojtekmaj/enzyme-adapter-react-17';
import Enzyme, { mount } from 'enzyme';
import Hit, {
    maybeTrimByWord,
    maybeConvertArrayToString,
    uniqueAndDefinedValues,
    maybeGetUniqueFieldsFromArray,
} from '../hits/base';
import BiosampleHit from '../hits/biosample';
import DonorHit from '../hits/donor';
import FileHit from '../hits/file';
import ExperimentHit from '../hits/experiment';
import {
    Text,
    Accession,
    Authors,
    Description,
    Target,
    Title,
    Organism,
    Other,
} from '../hits/parts';
import hitFactory from '../hits';


// Temporary use of adapter until Enzyme is compatible with React 17.
Enzyme.configure({ adapter: new Adapter() });

describe('Hit formatting', () => {
    describe('maybeTrimByWord', () => {
        test('only trim if longer than maxWords', () => {
            let value = 'a short description';
            expect(maybeTrimByWord(value)).toEqual(value);
            expect(maybeTrimByWord(value, 3)).toEqual(value);
            value = 'a very long description that should be cut short';
            expect(maybeTrimByWord(value)).toEqual(value);
            expect(maybeTrimByWord(value, 4)).toEqual('a very long description...');
        });
    });
    describe('maybeConvertArrayToString', () => {
        test('converts array to string with commas', () => {
            const value = ['an', 'array', 'that', 'should', 'be', 'joined'];
            expect(maybeConvertArrayToString(value)).toEqual(
                'an, array, that, should, be, joined'
            );
        });
        test('returns value otherwise', () => {
            const value = 'already a string';
            expect(maybeConvertArrayToString(value)).toEqual(value);
        });
    });
    describe('uniqueAndDefinedValues', () => {
        test('only returns unique and defined values from array', () => {
            const values = ['a', undefined, 'a', 'b', ''];
            expect(uniqueAndDefinedValues(values)).toEqual(
                [
                    'a',
                    'b',
                ]
            );
        });
    });
    describe('maybeGetUniqueFieldsFromArray', () => {
        test('get value or unique values from array', () => {
            const value = { target: 'a' };
            const otherValue = { target: 'b' };
            const values = [value, value, otherValue];
            expect(maybeGetUniqueFieldsFromArray(value, 'target')).toEqual('a');
            expect(maybeGetUniqueFieldsFromArray(values, 'target')).toEqual(['a', 'b']);
        });
    });
    describe('Text component', () => {
        test('renders span with value and classname', () => {
            const text = mount(
                <Text
                    className="my-formatting-class"
                    value="some string value"
                />
            );
            expect(text.find('span')).toHaveLength(1);
            expect(
                text.find('span').props().className
            ).toEqual('my-formatting-class');
            expect(
                text.find('span').text()
            ).toEqual('some string value');
        });
        test('Accession renders expected classname', () => {
            const accession = mount(
                <Accession
                    value="some string value"
                />
            );
            expect(
                accession.find('span').props().className
            ).toEqual('item-accession');
        });
        test('Authors renders expected classname', () => {
            const authors = mount(
                <Authors
                    value="some string value"
                />
            );
            expect(
                authors.find('span').props().className
            ).toEqual('item-authors');
        });
        test('Description renders expected classname', () => {
            const description = mount(
                <Description
                    value="some string value"
                />
            );
            expect(
                description.find('span').props().className
            ).toEqual('item-description');
        });
        test('Title renders expected classname', () => {
            const title = mount(
                <Title
                    value="some string value"
                />
            );
            expect(
                title.find('span').props().className
            ).toEqual('item-title');
        });
        test('Target renders expected classname', () => {
            const target = mount(
                <Target
                    value="some string value"
                />
            );
            expect(
                target.find('span').props().className
            ).toEqual('item-target');
        });
        test('Organism renders expected classname', () => {
            const organism = mount(
                <Organism
                    value="some string value"
                />
            );
            expect(
                organism.find('span').props().className
            ).toEqual('item-organism');
        });
        test('Other renders expected classname', () => {
            const other = mount(
                <Other
                    value="some string value"
                />
            );
            expect(
                other.find('span').props().className
            ).toEqual('item-other');
        });
    });
    describe('Hit class', () => {
        let hit;
        let missingValueHit;
        let hitWithArrayValue;
        beforeAll(() => {
            hit = new Hit(
                {
                    '@type': ['SomeSubType', 'SomeType'],
                    assay_title: 'my assay title',
                    biosample_ontology: {
                        term_name: 'a549',
                    },
                    annotation_type: 'imputation',
                    target: {
                        label: 'target label',
                    },
                    accession: 'abc123',
                    summary: 'something and somehow',
                    method: 'deletion',
                    lot_id: '123',
                    authors: 'xyz',
                }
            );
            missingValueHit = new Hit(
                {
                    '@type': ['SomeSubType', 'SomeType'],
                    '@id': 'abc123',
                    description: 'something and somehow',
                    annotation_type: 'imputation',
                    method: 'deletion',
                    lot_id: '123',
                    authors: 'xyz',
                }
            );
            hitWithArrayValue = new Hit(
                {
                    '@type': ['SomeSubType', 'SomeType'],
                    accession: 'abc123',
                    term_name: ['a thing', 'another thing'],
                    target: {
                        label: 'target label',
                    },
                    description: 'something and somehow',
                    annotation_type: 'imputation',
                    method: 'deletion',
                    lot_id: '123',
                    authors: 'xyz',
                }
            );
        });
        test('maybeGetBiosampleOntologyFromArray', () => {
            expect(hit.maybeGetBiosampleOntologyFromArray()).toEqual('a549');
            let hitWithBiosample = new Hit(
                {
                    '@type': ['something'],
                    '@id': 'abc123',
                    biosample_ontology: {
                        term_name: 'a thing',
                    },
                }
            );
            expect(hitWithBiosample.maybeGetBiosampleOntologyFromArray()).toEqual('a thing');
            hitWithBiosample = new Hit(
                {
                    '@type': ['something'],
                    '@id': 'abc123',
                    biosample_ontology: [
                        {
                            term_name: 'a thing',
                        },
                        {
                            term_name: 'another thing',
                        },
                        {
                            term_name: 'a thing',
                        },
                    ],
                }
            );
            expect(hitWithBiosample.maybeGetBiosampleOntologyFromArray()).toEqual(
                [
                    'a thing',
                    'another thing',
                ]
            );
            const hitWithNoTermName = new Hit(
                {
                    '@type': ['something'],
                    '@id': 'abc123',
                    biosample_ontology: {},
                }
            );
            expect(hitWithNoTermName.maybeGetBiosampleOntologyFromArray()).toEqual(undefined);
        });
        test('maybeGetOrganismFromArray', () => {
            let hitWithOrganism = new Hit(
                {
                    '@type': ['something'],
                    '@id': 'abc123',
                    organism: [
                        {
                            scientific_name: 'a thing',
                        },
                        {
                            scientific_name: 'another thing',
                        },
                        {
                            scientific_name: 'a thing',
                        },
                    ],
                }
            );
            expect(hitWithOrganism.maybeGetOrganismFromArray()).toEqual(
                [
                    'a thing',
                    'another thing',
                ]
            );
            hitWithOrganism = new Hit(
                {
                    '@type': ['something'],
                    '@id': 'abc123',
                    organism: {
                        scientific_name: 'a thing',
                    },
                }
            );
            expect(hitWithOrganism.maybeGetOrganismFromArray()).toEqual('a thing');
            const hitWithNoTermName = new Hit(
                {
                    '@type': ['something'],
                    '@id': 'abc12n3',
                    organism: {},
                }
            );
            expect(hitWithNoTermName.maybeGetOrganismFromArray()).toEqual(undefined);
        });
        test('getOrganismFromReplicatees', () => {
            const hitWithOrganism = new Hit(
                {
                    '@type': ['something'],
                    '@id': 'abc123',
                    replicates: [
                        {
                            library: {
                                biosample: {
                                    organism: {
                                        scientific_name: 'mus mus',
                                    },
                                },
                            },
                        },
                        {
                            library: {
                                biosample: {
                                    organism: {
                                        scientific_name: 'mus mus',
                                    },
                                },
                            },
                        },
                        {
                            library: {
                                biosample: {
                                    organism: {
                                        scientific_name: 'hom sap',
                                    },
                                },
                            },
                        },
                        {
                            missingKey: 'xyz',
                        },
                    ],
                }
            );
            expect(hitWithOrganism.getOrganismFromReplicates()).toEqual(
                [
                    'mus mus',
                    'hom sap',
                ]
            );
        });
        test('getLabelsFromTargets', () => {
            expect(hit.getLabelsFromTargets()).toEqual([]);
            const hitWithTargets = new Hit(
                {
                    '@type': ['something'],
                    '@id': 'abc12n3',
                    targets: [
                        {
                            label: 'abc',
                        },
                        {
                            label: 'xyz',
                        },
                        {
                            missingKey: 'zzz',
                        },
                    ],
                }
            );
            expect(hitWithTargets.getLabelsFromTargets()).toEqual(
                [
                    'abc',
                    'xyz',
                ]
            );
        });
        test('formatTitle', () => {
            expect(hit.formatTitle()).toEqual('my assay title');
        });
        test('formatAnnotationType', () => {
            expect(hit.formatAnnotationType()).toEqual('imputation');
        });
        test('formatBiosample', () => {
            expect(hit.formatBiosample()).toEqual('a549');
        });
        test('formatTarget', () => {
            expect(hit.formatTarget()).toEqual('target label');
            const hitWithTargets = new Hit(
                {
                    '@type': ['something'],
                    '@id': 'abc12n3',
                    targets: [
                        {
                            label: 'abc',
                        },
                        {
                            label: 'xyz',
                        },
                        {
                            missingKey: 'zzz',
                        },
                    ],
                }
            );
            expect(hitWithTargets.formatTarget()).toEqual(
                [
                    'abc',
                    'xyz',
                ]
            );
        });
        test('formatOrganism', () => {
            const hitWithOrganism = new Hit(
                {
                    '@type': ['something'],
                    '@id': 'abc123',
                    organism: {
                        scientific_name: 'a thing',
                    },
                }
            );
            expect(hitWithOrganism.formatOrganism()).toEqual('a thing');
        });
        test('formatName', () => {
            expect(hit.formatName()).toEqual('abc123');
        });
        test('formatDescription', () => {
            expect(hit.formatDescription()).toEqual('something and somehow');
        });
        test('formatDescriptionWithOrganism', () => {
            const hitWithOrganismAndDescription = new Hit(
                {
                    '@type': ['something'],
                    '@id': 'abc123',
                    organism: {
                        scientific_name: 'a thing',
                    },
                    description: 'something and somehow',
                }
            );
            expect(
                hitWithOrganismAndDescription.formatDescriptionWithOrganism()
            ).toEqual('a thing something and somehow');
        });
        test('formatLotId', () => {
            expect(hit.formatLotId()).toEqual('123');
        });
        test('formatAuthors', () => {
            expect(hit.formatAuthors()).toEqual('xyz');
        });
        test('formatDetails', () => {
            expect(hit.formatDetails()).toEqual('deletion');
        });
        test('getValues', () => {
            expect(hit.getValues()).toEqual(
                [
                    ['name', 'abc123'],
                    ['annotationType', 'imputation'],
                    ['title', 'my assay title'],
                    ['biosample', 'a549'],
                    ['target', 'target label'],
                    ['details', 'deletion'],
                    ['lotId', '123'],
                    ['authors', 'xyz'],
                    ['description', 'something and somehow'],
                ]
            );
            expect(missingValueHit.getValues()).toEqual(
                [
                    ['name', 'abc123'],
                    ['annotationType', 'imputation'],
                    ['title', undefined],
                    ['biosample', undefined],
                    ['target', undefined],
                    ['details', 'deletion'],
                    ['lotId', '123'],
                    ['authors', 'xyz'],
                    ['description', 'something and somehow'],
                ]
            );
            const biosampleHit = new BiosampleHit(
                {
                    '@type': ['SomeSubType', 'SomeType'],
                    biosample_ontology: {
                        term_name: 'a549',
                    },
                    annotation_type: 'imputation',
                    target: {
                        label: 'target label',
                    },
                    accession: 'abc123',
                    summary: 'something and somehow',
                    lot_id: '123',
                    authors: 'xyz',
                }
            );
            expect(biosampleHit.getValues()).toEqual(
                [
                    ['name', 'abc123'],
                    ['description', 'something and somehow'],
                ]
            );
            const fileHit = new FileHit(
                {
                    '@type': ['SomeSubType', 'SomeType'],
                    assay_title: 'my assay title',
                    biosample_ontology: {
                        term_name: 'a549',
                    },
                    target: {
                        label: 'target label',
                    },
                    organism: {
                        scientific_name: 'mus mus',
                    },
                    accession: 'abc123',
                    summary: 'something and somehow',
                    method: 'deletion',
                    file_type: 'bam',
                    output_type: 'fold change over control',
                }
            );
            expect(fileHit.makeFileDescription()).toEqual(
                'bam fold change over control'
            );
            expect(fileHit.getValues()).toEqual(
                [
                    ['name', 'abc123'],
                    ['title', 'my assay title'],
                    ['biosample', 'a549'],
                    ['target', 'target label'],
                    ['details', 'deletion'],
                    ['organism', 'mus mus'],
                    ['description', 'bam fold change over control'],
                ]
            );
            const donorHit = new DonorHit(
                {
                    '@type': ['SomeSubType', 'SomeType'],
                    assay_title: 'my assay title',
                    strain_name: 'W1118',
                    genotype: 'y[1] w[_]; P{y[+t7.7] w[+mC]=trem-GFP.FPTB}attP40',
                    organism: {
                        scientific_name: 'Drosophila melanogaster',
                    },
                    accession: 'abc123',
                }
            );
            expect(donorHit.makeDonorDescription()).toEqual(
                'W1118 y[1] w[_]; P{y[+t7.7] w[+mC]=trem-GFP.FPTB}attP40'
            );
            expect(donorHit.getValues()).toEqual(
                [
                    ['name', 'abc123'],
                    [
                        'description',
                        'Drosophila melanogaster W1118 y[1] w[_]; P{y[+t7.7] w[+mC]=trem-GFP.FPTB}attP40',
                    ],
                ]
            );
            const donorHitMissingStrainAndGenotype = new DonorHit(
                {
                    '@type': ['SomeSubType', 'SomeType'],
                    assay_title: 'my assay title',
                    organism: {
                        scientific_name: 'Drosophila melanogaster',
                    },
                    accession: 'abc123',
                }
            );
            expect(
                donorHitMissingStrainAndGenotype.makeDonorDescription()
            ).toEqual('');
            expect(
                donorHitMissingStrainAndGenotype.getConvertedAndFilteredValues()
            ).toEqual(
                [
                    ['name', 'abc123'],
                    ['description', 'Drosophila melanogaster'],
                ]
            );
            const experimentHit = new ExperimentHit(
                {
                    '@type': ['SomeSubType', 'SomeType'],
                    assay_title: 'my assay title',
                    biosample_ontology: {
                        term_name: 'a549',
                    },
                    organism: {
                        scientific_name: 'mus mus',
                    },
                    annotation_type: 'imputation',
                    target: {
                        label: 'target label',
                    },
                    accession: 'abc123',
                    summary: 'something and somehow',
                    method: 'deletion',
                    lot_id: '123',
                    authors: 'xyz',
                }
            );
            expect(experimentHit.getValues()).toEqual(
                [
                    ['name', 'abc123'],
                    ['title', 'my assay title'],
                    ['target', 'target label'],
                    ['details', 'deletion'],
                    ['description', 'mus mus something and somehow'],
                ]
            );
        });
        test('getConvertedAndFilteredValues', () => {
            expect(missingValueHit.getConvertedAndFilteredValues()).toEqual(
                [
                    ['name', 'abc123'],
                    ['annotationType', 'imputation'],
                    ['details', 'deletion'],
                    ['lotId', '123'],
                    ['authors', 'xyz'],
                    ['description', 'something and somehow'],
                ]
            );
            expect(hitWithArrayValue.getConvertedAndFilteredValues()).toEqual(
                [
                    ['name', 'abc123'],
                    ['annotationType', 'imputation'],
                    ['title', 'a thing, another thing'],
                    ['target', 'target label'],
                    ['details', 'deletion'],
                    ['lotId', '123'],
                    ['authors', 'xyz'],
                    ['description', 'something and somehow'],
                ]
            );
        });
        test('asString', () => {
            const actualValue = mount(
                <>
                    {hit.asString()}
                </>
            );
            const expectedValue = [
                <Accession value="abc123" />,
                <Title value="imputation" />,
                <Title value="my assay title" />,
                <Other value="a549" />,
                <Target value="target label" />,
                <Other value="deletion" />,
                <Other value="123" />,
                <Authors value="xyz" />,
                <Description value="something and somehow" />,
            ];
            expect(
                actualValue.containsAllMatchingElements(expectedValue)
            ).toBe(true);
        });
    });
    describe('hitFactory', () => {
        test('hitFactory returns correct Hit based on @type', () => {
            let item = {
                '@type': [
                    'Experiment',
                    'Dataset',
                    'Item',
                ],
            };
            let hit = hitFactory(item);
            expect(hit.constructor.name).toEqual('ExperimentHit');
            item = {
                '@type': [
                    'File',
                    'Item',
                ],
            };
            hit = hitFactory(item);
            expect(hit.constructor.name).toEqual('FileHit');
            item = {
                '@type': [
                    'Biosample',
                    'Item',
                ],
            };
            hit = hitFactory(item);
            expect(hit.constructor.name).toEqual('BiosampleHit');
            item = {
                '@type': [
                    'FlyDonor',
                    'Donor',
                    'Item',
                ],
            };
            hit = hitFactory(item);
            expect(hit.constructor.name).toEqual('DonorHit');
            item = {
                '@type': [
                    'Dataset',
                    'Item',
                ],
            };
            // Otherwise return default Hit type.
            hit = hitFactory(item);
            expect(hit.constructor.name).toEqual('Hit');
            item = {
                '@type': [
                    'AntibodyLot',
                    'Item',
                ],
            };
            hit = hitFactory(item);
            expect(hit.constructor.name).toEqual('Hit');
        });
    });
});
