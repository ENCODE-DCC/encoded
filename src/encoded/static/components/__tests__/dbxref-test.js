import Adapter from '@wojtekmaj/enzyme-adapter-react-17';
import Enzyme, { mount } from 'enzyme';

// Import test component.
import { DbxrefList } from '../dbxref';

// Temporary use of adapter until Enzyme is compatible with React 17.
Enzyme.configure({ adapter: new Adapter() });

describe('Test individual dbxref types', () => {
    describe('Test UniProtKB', () => {
        let dbxLinks;

        beforeAll(() => {
            const context = { '@type': ['Treatment'] };
            const wrapper = mount(
                <DbxrefList context={context} dbxrefs={['UniProtKB:1234', 'UniProtKB:5678']} />
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
            const context = { '@type': ['Target'], genes: [{ symbol: 'CXXC1' }] };
            const wrapper = mount(
                <DbxrefList
                    dbxrefs={['HGNC:hCGBP', 'HGNC:ZCGPC1']}
                    context={context}
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
            const context = { '@type': ['Target'] };
            const wrapper = mount(
                <DbxrefList context={context} dbxrefs={['ENSEMBL:ENSG00000101126', 'ENSEMBL:ENSG00000154832']} />
            );

            dbxLinks = wrapper.find('a');
        });

        it('has the correct links', () => {
            expect(dbxLinks.length).toBe(2);
            expect(dbxLinks.at(0).prop('href')).toEqual('http://www.ensembl.org/Homo_sapiens/Gene/Summary?g=ENSG00000101126');
            expect(dbxLinks.at(1).prop('href')).toEqual('http://www.ensembl.org/Homo_sapiens/Gene/Summary?g=ENSG00000154832');
        });
    });

    describe('Test mouse ENSEMBLE', () => {
        let dbxLinks;

        beforeAll(() => {
            const context = { '@type': ['Gene'], organism: { scientific_name: 'Mus musculus' } };
            const wrapper = mount(
                <DbxrefList context={context} dbxrefs={['ENSEMBL:ENSMUSG00000005698', 'ENSEMBL:ENSMUSG00000017167']} />
            );

            dbxLinks = wrapper.find('a');
        });

        it('has the correct links', () => {
            expect(dbxLinks.length).toBe(2);
            expect(dbxLinks.at(0).prop('href')).toEqual('http://www.ensembl.org/Mus_musculus/Gene/Summary?g=ENSMUSG00000005698');
            expect(dbxLinks.at(1).prop('href')).toEqual('http://www.ensembl.org/Mus_musculus/Gene/Summary?g=ENSMUSG00000017167');
        });
    });

    describe('Test GeneID', () => {
        let dbxLinks;

        beforeAll(() => {
            const context = { '@type': ['Target'] };
            const wrapper = mount(
                <DbxrefList context={context} dbxrefs={['GeneID:23394', 'GeneID:10664']} />
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
            const context = { '@type': 'UcscBrowserComposite' };
            const wrapper = mount(
                <DbxrefList context={context} dbxrefs={['GEO:GSM1002657', 'GEO:GPL9442', 'GEO:SAMN00003235']} />
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
            const context = { '@type': 'ReferenceEpigenome' };
            const wrapper = mount(
                <DbxrefList context={context} dbxrefs={['IHEC:IHECRE00000004.3', 'IHEC:IHECRE00000129.3']} />
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
            const context = { '@type': 'Biosample' };
            const wrapper = mount(
                <DbxrefList context={context} dbxrefs={['Cellosaurus:CVCL_0395', 'Cellosaurus:CVCL_5486']} />
            );

            dbxLinks = wrapper.find('a');
        });

        it('has the correct links', () => {
            expect(dbxLinks.length).toBe(2);
            expect(dbxLinks.at(0).prop('href')).toEqual('https://web.expasy.org/cellosaurus/CVCL_0395');
            expect(dbxLinks.at(1).prop('href')).toEqual('https://web.expasy.org/cellosaurus/CVCL_5486');
        });
    });

    describe('Test FlyBase for targets and fly donors', () => {
        let dbxLinksFlyDonor;
        let dbxLinksTarget;

        beforeAll(() => {
            const contextFly = { '@type': ['FlyDonor'] };
            const contextTarget = { '@type': ['Target'] };
            const wrapperFlyDonor = mount(
                <DbxrefList
                    context={contextFly}
                    dbxrefs={['FlyBase:FBst0038626', 'FlyBase:FBst0000005']}
                />
            );
            const wrapperTarget = mount(
                <DbxrefList
                    context={contextTarget}
                    dbxrefs={['FlyBase:CG43860', 'FlyBase:FBtr0332562']}
                />
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
            const flybaseSearchUrl = 'http://flybase.org/search/symbol/';

            expect(dbxLinksTarget.at(0).prop('href')).toEqual(`${flybaseSearchUrl}CG43860`);
            expect(dbxLinksTarget.at(1).prop('href')).toEqual(`${flybaseSearchUrl}FBtr0332562`);
        });
    });

    describe('Test BDSC', () => {
        let dbxLinks;

        beforeAll(() => {
            const context = { '@type': 'Biosample' };
            const wrapper = mount(
                <DbxrefList context={context} dbxrefs={['BDSC:38626', 'BDSC:5']} />
            );

            dbxLinks = wrapper.find('a');
        });

        it('has the correct links', () => {
            expect(dbxLinks.length).toBe(2);
            expect(dbxLinks.at(0).prop('href')).toEqual('http://flystocks.bio.indiana.edu/stocks/38626');
            expect(dbxLinks.at(1).prop('href')).toEqual('http://flystocks.bio.indiana.edu/stocks/5');
        });
    });

    describe('Test WormBase for targets and worm donors', () => {
        let dbxLinksWormDonor;
        let dbxLinksTarget;

        beforeAll(() => {
            const contextWorm = { '@type': ['WormDonor'] };
            const contextTarget = { '@type': ['Target'] };
            const wrapperWormDonor = mount(
                <DbxrefList
                    context={contextWorm}
                    dbxrefs={['WormBase:RB884', 'WormBase:RB885']}
                />
            );
            const wrapperTarget = mount(
                <DbxrefList
                    context={contextTarget}
                    dbxrefs={['WormBase:WBGene00003222', 'WormBase:Y2H9A.1']}
                />
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

    describe('Test CGC', () => {
        let dbxLinks;

        beforeAll(() => {
            const context = { '@type': 'WormDonor' };
            const wrapper = mount(
                <DbxrefList context={context} dbxrefs={['CGC:RB884', 'CGC:N5']} />
            );

            dbxLinks = wrapper.find('a');
        });

        it('has the correct links', () => {
            expect(dbxLinks.length).toBe(2);
            expect(dbxLinks.at(0).prop('href')).toEqual('https://cgc.umn.edu/strain/RB884');
            expect(dbxLinks.at(1).prop('href')).toEqual('https://cgc.umn.edu/strain/N5');
        });
    });

    describe('Test DSSC', () => {
        let dbxLinks;

        beforeAll(() => {
            const context = { '@type': 'FlyDonor' };
            const wrapper = mount(
                <DbxrefList context={context} dbxrefs={['DSSC:15181-2171.01', 'DSSC:14012-0141.05']} />
            );

            dbxLinks = wrapper.find('a');
        });

        it('has the correct links', () => {
            expect(dbxLinks.length).toBe(2);
            expect(dbxLinks.at(0).prop('href')).toEqual('https://stockcenter.ucsd.edu/index.php?action=view&q=15181-2171.01&table=Species&submit=Search');
            expect(dbxLinks.at(1).prop('href')).toEqual('https://stockcenter.ucsd.edu/index.php?action=view&q=14012-0141.05&table=Species&submit=Search');
        });
    });

    describe('Test MGI.D', () => {
        let dbxLinks;

        beforeAll(() => {
            const context = { '@type': 'MouseDonor' };
            const wrapper = mount(
                <DbxrefList context={context} dbxrefs={['MGI.D:RIII', 'MGI.D:NOD']} />
            );

            dbxLinks = wrapper.find('a');
        });

        it('has the correct links', () => {
            expect(dbxLinks.length).toBe(2);
            expect(dbxLinks.at(0).prop('href')).toEqual('http://www.informatics.jax.org/inbred_strains/mouse/docs/RIII.shtml');
            expect(dbxLinks.at(1).prop('href')).toEqual('http://www.informatics.jax.org/inbred_strains/mouse/docs/NOD.shtml');
        });
    });

    describe('Test RBPImage', () => {
        let dbxLinks;

        beforeAll(() => {
            const context = {
                '@type': ['Experiment'],
                biosample_ontology: {
                    classification: 'cell line',
                    term_id: 'EFO:0001187',
                    term_name: 'HepG2',
                },
            };
            const wrapper = mount(
                <DbxrefList
                    dbxrefs={['RBPImage:DNAJC2', 'RBPImage:SRSF9']}
                    context={context}
                />
            );

            dbxLinks = wrapper.find('a');
        });

        it('has the correct links', () => {
            expect(dbxLinks.length).toBe(2);
            expect(dbxLinks.at(0).prop('href')).toEqual('http://rnabiology.ircm.qc.ca/RBPImage/gene.php?cells=HepG2&targets=DNAJC2');
            expect(dbxLinks.at(1).prop('href')).toEqual('http://rnabiology.ircm.qc.ca/RBPImage/gene.php?cells=HepG2&targets=SRSF9');
        });
    });

    describe('Test JAX', () => {
        let dbxLinks;

        beforeAll(() => {
            const context = { '@type': ['MouseDonor'] };
            const wrapper = mount(
                <DbxrefList context={context} dbxrefs={['JAX:002448', 'JAX:000646']} />
            );

            dbxLinks = wrapper.find('a');
        });

        it('has the correct links', () => {
            expect(dbxLinks.length).toBe(2);
            expect(dbxLinks.at(0).prop('href')).toEqual('https://www.jax.org/strain/002448');
            expect(dbxLinks.at(1).prop('href')).toEqual('https://www.jax.org/strain/000646');
        });
    });

    describe('Test NBRP', () => {
        let dbxLinks;

        beforeAll(() => {
            const context = { '@type': ['MouseDonor'] };
            const wrapper = mount(
                <DbxrefList context={context} dbxrefs={['NBRP:233', 'NBRP:292']} />
            );

            dbxLinks = wrapper.find('a');
        });

        it('has the correct links', () => {
            expect(dbxLinks.length).toBe(2);
            expect(dbxLinks.at(0).prop('href')).toEqual('https://shigen.nig.ac.jp/c.elegans/mutants/DetailsSearch?lang=english&seq=233');
            expect(dbxLinks.at(1).prop('href')).toEqual('https://shigen.nig.ac.jp/c.elegans/mutants/DetailsSearch?lang=english&seq=292');
        });
    });

    describe('Test UCSC-ENCODE-mm9', () => {
        let dbxLinks;

        beforeAll(() => {
            const context = { '@type': ['Experiment'] };
            const wrapper = mount(
                <DbxrefList context={context} dbxrefs={['UCSC-ENCODE-mm9:wgEncodeEM002001', 'UCSC-ENCODE-mm9:wgEncodeEM002004']} />
            );

            dbxLinks = wrapper.find('a');
        });

        it('has the correct links', () => {
            expect(dbxLinks.length).toBe(2);
            expect(dbxLinks.at(0).prop('href')).toEqual('http://genome.ucsc.edu/cgi-bin/hgTracks?tsCurTab=advancedTab&tsGroup=Any&tsType=Any&hgt_mdbVar1=dccAccession&hgt_tSearch=search&hgt_tsDelRow=&hgt_tsAddRow=&hgt_tsPage=&tsSimple=&tsName=&tsDescr=&db=mm9&hgt_mdbVal1=wgEncodeEM002001');
            expect(dbxLinks.at(1).prop('href')).toEqual('http://genome.ucsc.edu/cgi-bin/hgTracks?tsCurTab=advancedTab&tsGroup=Any&tsType=Any&hgt_mdbVar1=dccAccession&hgt_tSearch=search&hgt_tsDelRow=&hgt_tsAddRow=&hgt_tsPage=&tsSimple=&tsName=&tsDescr=&db=mm9&hgt_mdbVal1=wgEncodeEM002004');
        });
    });

    describe('Test UCSC-ENCODE-hg19', () => {
        let dbxLinks;

        beforeAll(() => {
            const context = { '@type': ['Experiment'] };
            const wrapper = mount(
                <DbxrefList context={context} dbxrefs={['UCSC-ENCODE-hg19:wgEncodeEH003317', 'UCSC-ENCODE-hg19:wgEncodeEH002546']} />
            );

            dbxLinks = wrapper.find('a');
        });

        it('has the correct links', () => {
            expect(dbxLinks.length).toBe(2);
            expect(dbxLinks.at(0).prop('href')).toEqual('http://genome.ucsc.edu/cgi-bin/hgTracks?tsCurTab=advancedTab&tsGroup=Any&tsType=Any&hgt_mdbVar1=dccAccession&hgt_tSearch=search&hgt_tsDelRow=&hgt_tsAddRow=&hgt_tsPage=&tsSimple=&tsName=&tsDescr=&db=hg19&hgt_mdbVal1=wgEncodeEH003317');
            expect(dbxLinks.at(1).prop('href')).toEqual('http://genome.ucsc.edu/cgi-bin/hgTracks?tsCurTab=advancedTab&tsGroup=Any&tsType=Any&hgt_mdbVar1=dccAccession&hgt_tSearch=search&hgt_tsDelRow=&hgt_tsAddRow=&hgt_tsPage=&tsSimple=&tsName=&tsDescr=&db=hg19&hgt_mdbVal1=wgEncodeEH002546');
        });
    });

    describe('Test UCSC-ENCODE-cv', () => {
        let dbxLinks;

        beforeAll(() => {
            const context = { '@type': ['Experiment'] };
            const wrapper = mount(
                <DbxrefList context={context} dbxrefs={['UCSC-ENCODE-cv:IgG-Yale', 'UCSC-ENCODE-cv:Illumina_GA2e']} />
            );

            dbxLinks = wrapper.find('a');
        });

        it('has the correct links', () => {
            expect(dbxLinks.length).toBe(2);
            expect(dbxLinks.at(0).prop('href')).toEqual('http://genome.cse.ucsc.edu/cgi-bin/hgEncodeVocab?ra=encode%2Fcv.ra&term=%22IgG-Yale%22');
            expect(dbxLinks.at(1).prop('href')).toEqual('http://genome.cse.ucsc.edu/cgi-bin/hgEncodeVocab?ra=encode%2Fcv.ra&term=%22Illumina_GA2e%22');
        });
    });

    describe('Test UCSC-GB-mm9', () => {
        let dbxLinks;

        beforeAll(() => {
            const context = { '@type': ['Experiment'] };
            const wrapper = mount(
                <DbxrefList context={context} dbxrefs={['UCSC-GB-mm9:wgEncodeSydhHist', 'UCSC-GB-mm9:wgEncodePsuRnaSeq']} />
            );

            dbxLinks = wrapper.find('a');
        });

        it('has the correct links', () => {
            expect(dbxLinks.length).toBe(2);
            expect(dbxLinks.at(0).prop('href')).toEqual('http://genome.cse.ucsc.edu/cgi-bin/hgTrackUi?db=mm9&g=wgEncodeSydhHist');
            expect(dbxLinks.at(1).prop('href')).toEqual('http://genome.cse.ucsc.edu/cgi-bin/hgTrackUi?db=mm9&g=wgEncodePsuRnaSeq');
        });
    });

    describe('Test 4DN', () => {
        let dbxLinks;

        beforeAll(() => {
            const context = { '@type': ['Experiment'] };
            const wrapper = mount(
                <DbxrefList context={context} dbxrefs={['4DN:4DNESUCQ2Q6H', '4DN:4DNESA84SNKC']} />
            );

            dbxLinks = wrapper.find('a');
        });

        it('has the correct links', () => {
            expect(dbxLinks.length).toBe(2);
            expect(dbxLinks.at(0).prop('href')).toEqual('https://data.4dnucleome.org/experiment-set-replicates/4DNESUCQ2Q6H');
            expect(dbxLinks.at(1).prop('href')).toEqual('https://data.4dnucleome.org/experiment-set-replicates/4DNESA84SNKC');
        });
    });

    describe('Test UCSC-GB-hg19', () => {
        const context = { '@type': ['Experiment'] };
        let dbxLinks;

        beforeAll(() => {
            const wrapper = mount(
                <DbxrefList context={context} dbxrefs={['UCSC-GB-hg19:wgEncodeUwAffyExonArray', 'UCSC-GB-hg19:wgEncodeUmassDekker5C']} />
            );

            dbxLinks = wrapper.find('a');
        });

        it('has the correct links', () => {
            expect(dbxLinks.length).toBe(2);
            expect(dbxLinks.at(0).prop('href')).toEqual('http://genome.cse.ucsc.edu/cgi-bin/hgTrackUi?db=hg19&g=wgEncodeUwAffyExonArray');
            expect(dbxLinks.at(1).prop('href')).toEqual('http://genome.cse.ucsc.edu/cgi-bin/hgTrackUi?db=hg19&g=wgEncodeUmassDekker5C');
        });
    });

    describe('Test PMID', () => {
        let dbxLinks;

        beforeAll(() => {
            const context = { '@type': ['Publication'] };
            const wrapper = mount(
                <DbxrefList context={context} dbxrefs={['PMID:22064851', 'PMID:19966280']} />
            );

            dbxLinks = wrapper.find('a');
        });

        it('has the correct links', () => {
            expect(dbxLinks.length).toBe(2);
            expect(dbxLinks.at(0).prop('href')).toEqual('https://www.ncbi.nlm.nih.gov/pubmed/?term=22064851');
            expect(dbxLinks.at(1).prop('href')).toEqual('https://www.ncbi.nlm.nih.gov/pubmed/?term=19966280');
        });
    });

    describe('Test PMCID', () => {
        let dbxLinks;

        beforeAll(() => {
            const context = { '@type': ['Publication'] };
            const wrapper = mount(
                <DbxrefList context={context} dbxrefs={['PMCID:PMC3530905', 'PMCID:PMC2832824']} />
            );

            dbxLinks = wrapper.find('a');
        });

        it('has the correct links', () => {
            expect(dbxLinks.length).toBe(2);
            expect(dbxLinks.at(0).prop('href')).toEqual('https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3530905');
            expect(dbxLinks.at(1).prop('href')).toEqual('https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2832824');
        });
    });

    describe('Test doi', () => {
        let dbxLinks;

        beforeAll(() => {
            const context = { '@type': ['Publication'] };
            const wrapper = mount(
                <DbxrefList context={context} dbxrefs={['doi:10.1038/nphys1170', 'doi:10.1006/geno.1998.5693']} />
            );

            dbxLinks = wrapper.find('a');
        });

        it('has the correct links', () => {
            expect(dbxLinks.length).toBe(2);
            expect(dbxLinks.at(0).prop('href')).toEqual('https://doi.org/doi:10.1038%2Fnphys1170');
            expect(dbxLinks.at(1).prop('href')).toEqual('https://doi.org/doi:10.1006%2Fgeno.1998.5693');
        });
    });

    describe('Test AR', () => {
        let dbxLinks;

        beforeAll(() => {
            const context = { '@type': ['AntibodyLot'] };
            const wrapper = mount(
                <DbxrefList context={context} dbxrefs={['AR:AB_2615158', 'AR:AB_2614941']} />
            );

            dbxLinks = wrapper.find('a');
        });

        it('has the correct links', () => {
            expect(dbxLinks.length).toBe(2);
            expect(dbxLinks.at(0).prop('href')).toEqual('http://antibodyregistry.org/search.php?q=AB_2615158');
            expect(dbxLinks.at(1).prop('href')).toEqual('http://antibodyregistry.org/search.php?q=AB_2614941');
        });
    });

    describe('Test NIH', () => {
        let dbxLinks;

        beforeAll(() => {
            const context = { '@type': ['HumanDonor'] };
            const wrapper = mount(
                <DbxrefList context={context} dbxrefs={['NIH:NIHhESC-10-0062', 'NIH:NIHhESC-10-0063']} />
            );

            dbxLinks = wrapper.find('a');
        });

        it('has the correct links', () => {
            expect(dbxLinks.length).toBe(2);
            expect(dbxLinks.at(0).prop('href')).toEqual('https://search.usa.gov/search?utf8=%E2%9C%93&affiliate=grants.nih.gov&query=NIHhESC-10-0062');
            expect(dbxLinks.at(1).prop('href')).toEqual('https://search.usa.gov/search?utf8=%E2%9C%93&affiliate=grants.nih.gov&query=NIHhESC-10-0063');
        });
    });

    describe('Test TRiP', () => {
        let dbxLinks;

        beforeAll(() => {
            const context = { '@type': ['FlyDonor'] };
            const wrapper = mount(
                <DbxrefList context={context} dbxrefs={['TRiP:HMC04792', 'TRiP:HMC04793']} />
            );

            dbxLinks = wrapper.find('a');
        });

        it('has the correct links', () => {
            expect(dbxLinks.length).toBe(2);
            expect(dbxLinks.at(0).prop('href')).toEqual('http://www.flyrnai.org/cgi-bin/DRSC_gene_lookup.pl?gname=HMC04792');
            expect(dbxLinks.at(1).prop('href')).toEqual('http://www.flyrnai.org/cgi-bin/DRSC_gene_lookup.pl?gname=HMC04793');
        });
    });

    describe('Test DGGR', () => {
        let dbxLinks;

        beforeAll(() => {
            const context = { '@type': ['FlyDonor'] };
            const wrapper = mount(
                <DbxrefList context={context} dbxrefs={['DGGR:109027', 'DGGR:101084']} />
            );

            dbxLinks = wrapper.find('a');
        });

        it('has the correct links', () => {
            expect(dbxLinks.length).toBe(2);
            expect(dbxLinks.at(0).prop('href')).toEqual('https://kyotofly.kit.jp/cgi-bin/stocks/search_res_det.cgi?DB_NUM=1&DG_NUM=109027');
            expect(dbxLinks.at(1).prop('href')).toEqual('https://kyotofly.kit.jp/cgi-bin/stocks/search_res_det.cgi?DB_NUM=1&DG_NUM=101084');
        });
    });

    describe('Test no matching dbxref prefix', () => {
        let dbxLinks;
        let dbxSpans;

        beforeAll(() => {
            const context = { '@type': ['HumanDonor'] };
            const wrapper = mount(
                <DbxrefList context={context} dbxrefs={['OK:NOT-REAL']} />
            );

            dbxLinks = wrapper.find('a');
            dbxSpans = wrapper.find('span');
        });

        it('has the correct span contents', () => {
            expect(dbxLinks.length).toBe(0);
            expect(dbxSpans.length).toBe(1);
            expect(dbxSpans.at(0).text()).toEqual('OK:NOT-REAL');
        });
    });

    describe('Test DepMap', () => {
        let dbxLinks;

        beforeAll(() => {
            const context = { '@type': 'BiosampleType' };
            const wrapper = mount(
                <DbxrefList context={context} dbxrefs={['DepMap:ACH-000551', 'DepMap:ACH-000552']} />
            );

            dbxLinks = wrapper.find('a');
        });

        it('has the correct links', () => {
            expect(dbxLinks.length).toBe(2);
            expect(dbxLinks.at(0).prop('href')).toEqual('https://depmap.org/portal/cell_line/ACH-000551');
            expect(dbxLinks.at(1).prop('href')).toEqual('https://depmap.org/portal/cell_line/ACH-000552');
        });
    });

    describe('Test FactorBook', () => {
        let dbxLinks;

        beforeAll(() => {
            const context = { '@type': ['Experiment'] };
            const wrapper = mount(
                <DbxrefList context={context} dbxrefs={['FactorBook:ENCSR343RJH', 'FactorBook:ENCSR614HHL']} />
            );

            dbxLinks = wrapper.find('a');
        });

        it('has the correct links', () => {
            expect(dbxLinks.length).toBe(2);
            expect(dbxLinks.at(0).prop('href')).toEqual('https://factorbook.org/experiment/ENCSR343RJH');
            expect(dbxLinks.at(1).prop('href')).toEqual('https://factorbook.org/experiment/ENCSR614HHL');
        });
    });

    describe('Test GeneCards', () => {
        let dbxLinks;

        beforeAll(() => {
            const context = { '@type': ['Gene'] };
            const wrapper = mount(
                <DbxrefList context={context} dbxrefs={['GeneCards:ATF3', 'GeneCards:MXD1']} />
            );

            dbxLinks = wrapper.find('a');
        });

        it('has the correct links', () => {
            expect(dbxLinks.length).toBe(2);
            expect(dbxLinks.at(0).prop('href')).toEqual('http://www.genecards.org/cgi-bin/carddisp.pl?gene=ATF3');
            expect(dbxLinks.at(1).prop('href')).toEqual('http://www.genecards.org/cgi-bin/carddisp.pl?gene=MXD1');
        });
    });

    describe('Test VISTA', () => {
        let dbxLinks;

        beforeAll(() => {
            const context = { '@type': ['TransgenicEnhancerExperiment'] };
            const wrapper = mount(
                <DbxrefList context={context} dbxrefs={['VISTA:hs10', 'VISTA:mm1694']} />
            );

            dbxLinks = wrapper.find('a');
        });

        it('has the correct links', () => {
            expect(dbxLinks.length).toBe(2);
            expect(dbxLinks.at(0).prop('href')).toEqual('https://enhancer.lbl.gov/cgi-bin/imagedb3.pl?form=presentation&show=1&experiment_id=10&organism_id=1');
            expect(dbxLinks.at(1).prop('href')).toEqual('https://enhancer.lbl.gov/cgi-bin/imagedb3.pl?form=presentation&show=1&experiment_id=1694&organism_id=2');
        });
    });

    describe('Test Factorbook for targets', () => {
        let dbxLinksHumanTarget;
        let dbxLinksMouseTarget;

        beforeAll(() => {
            const contextHumanTarget = { '@type': ['Target'], organism: { scientific_name: 'Homo sapiens' } };
            const contextMouseTarget = { '@type': ['Target'], organism: { scientific_name: 'Mus musculus' } };
            const wrapperHumanTarget = mount(
                <DbxrefList
                    context={contextHumanTarget}
                    dbxrefs={['FactorBook:CTCF', 'FactorBook:SOX12']}
                />
            );
            const wrapperMouseTarget = mount(
                <DbxrefList
                    context={contextMouseTarget}
                    dbxrefs={['FactorBook:CTCF', 'FactorBook:TBP']}
                />
            );

            dbxLinksHumanTarget = wrapperHumanTarget.find('a');
            dbxLinksMouseTarget = wrapperMouseTarget.find('a');
        });

        it('has the correct links for Human targets', () => {
            expect(dbxLinksHumanTarget.length).toBe(2);
            expect(dbxLinksHumanTarget.at(0).prop('href')).toEqual('https://factorbook.org/tf/human/CTCF/function');
            expect(dbxLinksHumanTarget.at(1).prop('href')).toEqual('https://factorbook.org/tf/human/SOX12/function');
        });

        it('has the correct links for Mouse targets', () => {
            expect(dbxLinksMouseTarget.length).toBe(2);
            expect(dbxLinksMouseTarget.at(0).prop('href')).toEqual('https://factorbook.org/tf/mouse/Ctcf/function');
            expect(dbxLinksMouseTarget.at(1).prop('href')).toEqual('https://factorbook.org/tf/mouse/Tbp/function');
        });
    });

    describe('Test SCREEN-GRCh38', () => {
        let dbxLinks;

        beforeAll(() => {
            const context = { '@type': ['Experiment'] };
            const wrapper = mount(
                <DbxrefList context={context} dbxrefs={['SCREEN-GRCh38:T-cell_donor_ENCDO685OXD', 'SCREEN-GRCh38:iPS_DF_4.7_male_newborn']} />
            );
            dbxLinks = wrapper.find('a');
        });

        it('has the correct links for Human experiments', () => {
            expect(dbxLinks.length).toBe(2);
            expect(dbxLinks.at(0).prop('href')).toEqual('https://screen.encodeproject.org/search?q=T-cell_donor_ENCDO685OXD&assembly=GRCh38');
            expect(dbxLinks.at(1).prop('href')).toEqual('https://screen.encodeproject.org/search?q=iPS_DF_4.7_male_newborn&assembly=GRCh38');
        });
    });

    describe('Test SCREEN-mm10', () => {
        let dbxLinks;

        beforeAll(() => {
            const context = { '@type': ['Experiment'] };
            const wrapper = mount(
                <DbxrefList context={context} dbxrefs={['SCREEN-mm10:C3H_C2C12', 'SCREEN-mm10:CD-1_c-Kit-negative_CD71-positive_TER-119-positive_erythroid_progenitor_cells_male_embryo_14.5_days']} />
            );
            dbxLinks = wrapper.find('a');
        });

        it('has the correct links for Mouse experiments', () => {
            expect(dbxLinks.length).toBe(2);
            expect(dbxLinks.at(0).prop('href')).toEqual('https://screen.encodeproject.org/search?q=C3H_C2C12&assembly=mm10');
            expect(dbxLinks.at(1).prop('href')).toEqual('https://screen.encodeproject.org/search?q=CD-1_c-Kit-negative_CD71-positive_TER-119-positive_erythroid_progenitor_cells_male_embryo_14.5_days&assembly=mm10');
        });
    });
});
