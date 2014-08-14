module.exports = {
    "@id": "/software/30ca86a0-1c09-11e4-8c21-0800200c9a66/",
    "name": "haploreg",
    "title": "HaploReg",
    "description": "Explores annotations of the noncoding genome at variants on haplotype blocks, such as candidate regulatory SNPs at disease-associated loci. Under Set Options tab, set Browse ENCODE button to \"on\" and select an LD threshold and reference population. Under Build Query Tab, enter a SNP (rsXXXXX), a set of SNPs, a genomic region, or select a GWAS from the drop down menu. HaploReg returns SNPs in LD with query SNPs, their frequency in 4 populations from 1000 Genomes Phase1, and also tells you what evidence ENCODE has found for regulatory protein binding (mouse over to see the protein names), chromatin structure (mouse over to see the cell types with DNase hypersensitivity), the chromatin state of the region (the chromatin state can predict an enhancer or promoter), and putative transcription factor binding motifs that are altered by the variant. Clicking on the SNP name hyperlink reveals further details, including cell type metadata and the mechanism of disruption/creation of TF binding regulatory motifs (showing the PWM matched and its alignment to the local sequence context). SNPs are also intersected with cross-species conserved elements, chromatin states from the Roadmap Epigenomics Consortium, and lead eQTLs from the GTEx Project browser.",
    "software_type": ["database", "variant annotation"],
    "purpose": ["community resource"],
    "source_url": "http://www.broadinstitute.org/mammals/haploreg/haploreg.php",
    "references": [],
    "status": "released",
    "uuid": "30ca86a0-1c09-11e4-8c21-0800200c9a66",
    "@type": [
        "software",
        "item"
    ]
};
