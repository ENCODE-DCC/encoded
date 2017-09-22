import React from 'react';
import { mount } from 'enzyme';

// Import test component.
import { DbxrefListNew } from '../dbxref';


describe('Dbxref', () => {
    describe('Test UniProtKB', () => {
        let dbxLinks;

        beforeAll(() => {
            const wrapper = mount(
                <DbxrefListNew dbxrefs={['UniProtKB:1234', 'UniProtKB:5678']} />
            );

            dbxLinks = wrapper.find('a');
        });

        it('has the correct links', () => {
            expect(dbxLinks.length).toBe(2);
            expect(dbxLinks.at(0).prop('href')).toEqual('http://www.uniprot.org/uniprot/1234');
            expect(dbxLinks.at(1).prop('href')).toEqual('http://www.uniprot.org/uniprot/5678');
        });
    });

    describe('Test HGNC', () => {
        let dbxLinks;

        beforeAll(() => {
            const wrapper = mount(
                <DbxrefListNew
                    dbxrefs={['HGNC:hCGBP', 'HGNC:ZCGPC1']}
                    preprocessor={() => ({ altValue: 'CXXC1' })}
                />
            );

            dbxLinks = wrapper.find('a');
        });

        it('has the correct links', () => {
            expect(dbxLinks.length).toBe(2);
            expect(dbxLinks.at(0).prop('href')).toEqual('http://www.genecards.org/cgi-bin/carddisp.pl?gene=CXXC1');
            expect(dbxLinks.at(1).prop('href')).toEqual('http://www.genecards.org/cgi-bin/carddisp.pl?gene=CXXC1');
        });
    });

    describe('Test ENSEMBLE', () => {
        let dbxLinks;

        beforeAll(() => {
            const wrapper = mount(
                <DbxrefListNew dbxrefs={['ENSEMBL:ENSG00000101126', 'ENSEMBL:ENSG00000154832']} />
            );

            dbxLinks = wrapper.find('a');
        });

        it('has the correct links', () => {
            expect(dbxLinks.length).toBe(2);
            expect(dbxLinks.at(0).prop('href')).toEqual('http://www.ensembl.org/Homo_sapiens/Gene/Summary?g=ENSG00000101126');
            expect(dbxLinks.at(1).prop('href')).toEqual('http://www.ensembl.org/Homo_sapiens/Gene/Summary?g=ENSG00000154832');
        });
    });

    describe('Test GeneID', () => {
        let dbxLinks;

        beforeAll(() => {
            const wrapper = mount(
                <DbxrefListNew dbxrefs={['GeneID:23394', 'GeneID:10664']} />
            );

            dbxLinks = wrapper.find('a');
        });

        it('has the correct links', () => {
            expect(dbxLinks.length).toBe(2);
            expect(dbxLinks.at(0).prop('href')).toEqual('https://www.ncbi.nlm.nih.gov/gene/23394');
            expect(dbxLinks.at(1).prop('href')).toEqual('https://www.ncbi.nlm.nih.gov/gene/10664');
        });
    });

    describe('Test GEO', () => {
        let dbxLinks;

        beforeAll(() => {
            const wrapper = mount(
                <DbxrefListNew
                    dbxrefs={['GEO:GSM1002657', 'GEO:GPL9442', 'GEO:SAMN00003235']}
                    preprocessor={(dbxref) => {
                        // If the first four characters of the GEO value is "SAMN" then we need
                        // to use a different URL, and we select that URL with the fake prefix
                        // "GEOSAMN".
                        const value = dbxref.split(':');
                        if (value[1] && value[1].substr(0, 4) === 'SAMN') {
                            return { altPrefix: 'GEOSAMN' };
                        }
                        return {};
                    }}
                />
            );

            dbxLinks = wrapper.find('a');
        });

        it('has the correct links', () => {
            expect(dbxLinks.length).toBe(3);
            expect(dbxLinks.at(0).prop('href')).toEqual('https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSM1002657');
            expect(dbxLinks.at(1).prop('href')).toEqual('https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GPL9442');
            expect(dbxLinks.at(2).prop('href')).toEqual('https://www.ncbi.nlm.nih.gov/biosample/SAMN00003235');
        });
    });

    describe('Test IHEC', () => {
        let dbxLinks;

        beforeAll(() => {
            const wrapper = mount(
                <DbxrefListNew dbxrefs={['IHEC:IHECRE00000004.3', 'IHEC:IHECRE00000129.3']} />
            );

            dbxLinks = wrapper.find('a');
        });

        it('has the correct links', () => {
            expect(dbxLinks.length).toBe(2);
            expect(dbxLinks.at(0).prop('href')).toEqual('http://www.ebi.ac.uk/vg/epirr/view/IHECRE00000004.3');
            expect(dbxLinks.at(1).prop('href')).toEqual('http://www.ebi.ac.uk/vg/epirr/view/IHECRE00000129.3');
        });
    });

    describe('Test Cellosaurus', () => {
        let dbxLinks;

        beforeAll(() => {
            const wrapper = mount(
                <DbxrefListNew dbxrefs={['Cellosaurus:CVCL_0395', 'Cellosaurus:CVCL_5486']} />
            );

            dbxLinks = wrapper.find('a');
        });

        it('has the correct links', () => {
            expect(dbxLinks.length).toBe(2);
            expect(dbxLinks.at(0).prop('href')).toEqual('http://web.expasy.org/cellosaurus/CVCL_0395');
            expect(dbxLinks.at(1).prop('href')).toEqual('http://web.expasy.org/cellosaurus/CVCL_5486');
        });
    });

    describe('Test FlyBase for targets and fly donors', () => {
        let dbxLinksFlyDonor;
        let dbxLinksTarget;

        beforeAll(() => {
            const wrapperFlyDonor = mount(
                <DbxrefListNew
                    dbxrefs={['FlyBase:FBst0038626', 'FlyBase:FBst0000005']}
                    preprocessor={() => ({ altPrefix: 'FlyBaseStock' })}
                />
            );
            const wrapperTarget = mount(
                <DbxrefListNew dbxrefs={['FlyBase:CG43860', 'FlyBase:FBtr0332562']} />
            );

            dbxLinksFlyDonor = wrapperFlyDonor.find('a');
            dbxLinksTarget = wrapperTarget.find('a');
        });

        it('has the correct links for FlyBase', () => {
            expect(dbxLinksFlyDonor.length).toBe(2);
            expect(dbxLinksFlyDonor.at(0).prop('href')).toEqual('http://flybase.org/reports/FBst0038626.html');
            expect(dbxLinksFlyDonor.at(1).prop('href')).toEqual('http://flybase.org/reports/FBst0000005.html');
        });

        it('has the correct links for Targets', () => {
            expect(dbxLinksTarget.length).toBe(2);
            expect(dbxLinksTarget.at(0).prop('href')).toEqual('http://flybase.org/cgi-bin/quicksearch_solr.cgi?caller=quicksearch&tab=basic_tab&data_class=FBgn&species=Dmel&search_type=all&context=CG43860');
            expect(dbxLinksTarget.at(1).prop('href')).toEqual('http://flybase.org/cgi-bin/quicksearch_solr.cgi?caller=quicksearch&tab=basic_tab&data_class=FBgn&species=Dmel&search_type=all&context=FBtr0332562');
        });
    });

    describe('Test BDSC', () => {
        let dbxLinks;

        beforeAll(() => {
            const wrapper = mount(
                <DbxrefListNew dbxrefs={['BDSC:38626', 'BDSC:5']} />
            );

            dbxLinks = wrapper.find('a');
        });

        it('has the correct links', () => {
            expect(dbxLinks.length).toBe(2);
            expect(dbxLinks.at(0).prop('href')).toEqual('http://flystocks.bio.indiana.edu/Reports/38626');
            expect(dbxLinks.at(1).prop('href')).toEqual('http://flystocks.bio.indiana.edu/Reports/5');
        });
    });

    describe('Test WormBase for targets and worm donors', () => {
        let dbxLinksWormDonor;
        let dbxLinksTarget;

        beforeAll(() => {
            const wrapperWormDonor = mount(
                <DbxrefListNew
                    dbxrefs={['WormBase:RB884', 'WormBase:RB885']}
                    preprocessor={() => ({ altPrefix: 'WormBaseStock' })}
                />
            );
            const wrapperTarget = mount(
                <DbxrefListNew dbxrefs={['WormBase:WBGene00003222', 'WormBase:Y2H9A.1']} />
            );

            dbxLinksWormDonor = wrapperWormDonor.find('a');
            dbxLinksTarget = wrapperTarget.find('a');
        });

        it('has the correct links for FlyBase', () => {
            expect(dbxLinksWormDonor.length).toBe(2);
            expect(dbxLinksWormDonor.at(0).prop('href')).toEqual('http://www.wormbase.org/species/c_elegans/strain/RB884');
            expect(dbxLinksWormDonor.at(1).prop('href')).toEqual('http://www.wormbase.org/species/c_elegans/strain/RB885');
        });

        it('has the correct links for Targets', () => {
            expect(dbxLinksTarget.length).toBe(2);
            expect(dbxLinksTarget.at(0).prop('href')).toEqual('http://www.wormbase.org/species/c_elegans/gene/WBGene00003222');
            expect(dbxLinksTarget.at(1).prop('href')).toEqual('http://www.wormbase.org/species/c_elegans/gene/Y2H9A.1');
        });
    });
});
