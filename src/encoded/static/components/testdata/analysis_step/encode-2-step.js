module.exports = {
    "@id": "/analysis-steps/1b7bec83-dd21-4086-8673-2e08cf8f1c0f/",
    "@type": ["AnalysisStep", "Item"],
    "name": "encode-2-step",
    "major_version": 1,
    "title": "ENCODE 2 step",
    "analysis_step_types": [
        "filtering", 
        "file format conversion",
        "QA calculation",
        "signal generation",
        "peak calling"
    ],
    "input_file_types": ["bam", "fasta", "bed"],
    "output_file_types": ["bigWig", "narrowPeak"],
    "qa_stats_generated": ["NSC", "RSC", "SPOT"],
    "status": "released",
    "uuid": "1b7bec83-dd21-4086-8673-2e08cf8f1c0f"
};
