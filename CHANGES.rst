Changes
=======
This is the commit starting the regulome-master branch, rebased off v72.
This is a long running feature branch for RegulomeDB.  This will be kept
up to date with origin/dev.


72.0 (released)
-----------------
1. ENCD-4103 Fix tests broken by SNO-41 (#2317)
2. ENCD-4098 Update to snovault 1.0.11 (#2314)
3. ENCD-4072 Remove es master from deployment (#2302)
4. ENCD-4086 Analysis-Step schema (#2305)
5. ENCD-4048 rep-num-in-pub-n-exp (#2311)
6. ENCD-4093 Fix initial region indexing failure (#2308)
7. ENCD-3728 Fix build error (#2306)
8. ENCD-4020 Allowing specification of Sets as controls (#2296)
9. ENCD-4055 removed-some-styling-on-raw-data (#2277)
10. ENCD-4057 properly-format-data-on-biosample-page (#2276)
11. ENCD-4088 Remove extra code added in ENCD-3306 (#2310)
12. ENCD-4040 vis index replicate conditional (#2294)
13. ENCD-3718 return-404-when-file-not-found (#2278)
14. ENCD-4073 Revert accidental blocked dataset status expansion (#2291)
15. ENCD-4077 Fix deploy volume size type (#2304)
16. ENCD-3776 move-to-standard-status (#2295)
17. ENCD-4078 Remove unused statuses (#2293)
18. ENCD-4058 expanding-matrix-creates-unaligned-header (#2280)
19. ENCD-4085 Add weiwei as a submitter (#2298)
20. ENCD-4081 Add Yunhai as a submitter in local test. (#2288)

71.0 (released)
-----------------
01. ENCD-4046 update to snovault 1.0.10, add CHANGES (#2275)
02. ENCD-3306-fix-line-in-table (#2271)
03. ENCD-4045 gdpr auth0 (#2274)
04. ENCD-3695-upgrade-to-boto3 (#2272)
05. ENCD-3883-add-pmi-data (#2263)
06. ENCD-3727 added hypen for long words (#2270)
07. Add zoldello (Phil) as an authorized submitter for the test environments. ENCD-4049
08. ENCD-4019 adding readname_details field to the file.json (#2260)
09. ENCD-4042 Update genetic mods for functional characterization experiments (#2262)
10. ENCD-3629 Refactor and redesign status displays. (#2246)
11. ENCD-4034 SVG tooltip and minor JS clean up (#2255)
12. ENCD-3911 Added a break above document box (#2256)
13. ENCD-3364  fixed text and link button misalignment (#2257)

70.0 (released)
-----------------
01. ENCD-4037 Update snovault 1.0.9 (#2258)
02. ENCD-4029 Update to snovault 1.0.8 (#2254)
03. ENCD-3889 supersedes refepi (#2247)
04. ENCD-3871-target-standard-status (#2252)
05. ENCD-4011 Fix wrong vars in buildout candidate config file (#2241)
06. ENCD-3867 Display proper replicate_type string (#2249)
07. ENCD-4015 adding an audit for read_count and test for it (#2242)
08. ENCD-4010 fixing a typo in the samtools flagstat quality metric (#2238)
09. ENCD-3995 Update file output_type (#2239)
10. ENCD-4016 adding community to users (#2243)
11. ENCD-3957 Add biosample accession to report columns (#2250)
12. ENCD-3970 Add encore badge (#2251)
13. ENCD-4008-fix-source-title (#2253)
14. ENCD-4007-nginx-proxy-header (#2244)
15. ENCD-3981 remove histone modification (#2240)
16. ENCD-3963 Remove antibody accession column (#2233)
17. ENCD-3974 Update biosample organoid (#2234)
18. ENCD-3641 fix navigate to file download URI (#2237)

69.0 (released)
-----------------
01. REG-9 Fix vis button for region search (#2210)
02. ENCD-3986 Update to snovault 1.0.7 (#2229)
03. ENCD-3950 Require date_submitted in submitted experiments (#2224)
04. ENCD-3923 Allow es to deploy separately from encoded
05. ENCD-3620 Update deploy options for region search
06. ENCD-3621 Refactor deploy script
07. ENCD-3980 Organize ini files and vars
08. ENCD-3216 Hide antibody characterizations via user access level (#2225)
09. ENCD-3726 adding platform to library (#2223)
10. ENCD-3959 Add int and bool to displayed QC types (#2212)
11. ENCD-3973 Redo how GM characterization documents get displayed (#2219)
12. ENCD-3979 Fix zc buildout for pypi update (#2221)
13. ENCD-3961 eslint AirBnB npm package updates (#2214)

68.0 (released)
-----------------
01. ENCD-3965 Update to snovault 1.0.6 (#2209)
02. ENCD-3934 fix plate location in library (#2208)
03. ENCD-3944 Add organ slim shims & update ontology.json (#2201)
04. ENCD-3934 Update to original 3934 commit (#2207)
05. ENCD-3739 rewriting chip control read depth audit (#2188)
06. ENCD-3775-started-to-in-progress (#2202)
07. ENCD-3451 Summary page (#2200)
08. ENCD-2992 Remove unused status (#2206)
09. ENCD-3960 Fix batch download lookup column test (#2205)
10. ENCD-3935 adding new biosample type "single cell" (#2193)
11. ENCD-3898 adding an audit flagging "tagging" GM without characterization (#2187)
12. ENCD-3886 Update deploy machine instance types (#2181)
13. ENCD-3863 Eliminate repeated values in report TSV (#2136)
14. ENCD-3938 Adding new Series type "AggregateSeries" (#2190)
15. ENCD-3934 adding "barcode_details" to library schema (#2197)
16. ENCD-3189 Traverse root using external_accession key from files (#2178)
17. ENCD-3645 & ENCD-3716 Strip white spaces from values (#2194)
18. ENCD-3716 Strip white spaces from values (#2194)
19. ENCD-3773-pipeline-status (#2189)
20. ENCD-3870-publication-status-mixin (#2191)
21. ENCD-3780-remove-ready-for-review (#2192)
22. ENCD-3772-remove-virtual (#2195)
23. ENCD-1 Add treatments amount, duration to metadata.tsv
24. ENCD-2845 Quick fix for biosamples with both the sexes
25. ENCD-3868 - Adding unit tests for batch_download helpers
26. ENCD-3823 & ENCD-3864 - Filter out restricted files and refactor batch_download
27. ENCD-3864 - Filter out restricted files and refactor batch_download

67.1 (released)
---------------
1. ENCD-3916 Fix for broken metadata queries (#2179)

67.0 (released)
-----------------
01. ENCD-3915 Remove chromedriver lock from Travis (#2174)
02. ENCD-3892 Update to snovault 1.0.5 (#2173)
03. ENCD-3809 Add run_types for pacbio and oxford nanopore (#2172)
04. ENCD-3839 Remove schemas for the deleted objects (#2167)
05. ENCD-3891 Fix file test for duplicates in derived_from (#2162)
06. ENCD-3908 Update indexer doc for march 2018 update
07. ENCD-3913 Update regionsearch MAX_CLAUSES request_timeout
08. ENCD-3900 Increase demo volume size
09. ENCD-3756 Remove scorefilter in dnase visuals
10. ENCD-3907 Adopting UCSC bigNarrowPeak type
11. ENCD-3260 Refactor visualization
12. ENCD-3602 Migrate indexers to region and secondary
13. ENCD-3894 Move NIH cert audit to experiment (#2166)
14. ENCD-3840 Add link to linkFrom linkTo schema properties (#2168)
15. ENCD-3899 Fix exp audit trigger on non-encode pipelines (#2170)
16. ENCD-3604 Update boost to include GM accessions (#2171)
17. ENCD-3848 Remove immortalize from cell line (#2164)
18. ENCD-3854 Fix report description column sort error (#2150)
19. ENCD-3893 Add NIH cert to biosample facets (#2165)
20. ENCD-3828 Update redacted alignments (#2163)
21. ENCD-3841 Add collapsing sections on schema pages (#2154)
22. ENCD-3880 Add Alembic documentation (#2152)
23. ENCD-3821 Show biosample characterization doc links (#2145)
24. ENCD-3882 Update DOI preferred resolver url (#2135)
25. ENCD-3879 Pin Alembic version (#2151)

66.0 (released)
---------------
01. ENCD-3878 Update to snovault version 1.0.4 (#2148)
02. ENCD-3834 Add Alembic framework for Postgres migrations (#2142)
03. ENCD-3869 Downgrade chromedriver version 2.33 (#2143)
04. ENCD-3827 Fix ES5 version in README (#2141)
05. ENCD-3698 Add Institutional certifications to biosample (#2140)
06. ENCD-1934 Format schema displays (#2115)
07. ENCD-3865 Update to snovault version 1.0.3 (#2139)
08. ENCD-3836 Small heap single machine (#2137)
09. ENCD-3819 Add biosample preservation method (#2122)
10. ENCD-3835 Fix inconsistent platforms audit HiSeq2K 2.5K (#2133)
11. ENCD-3341 Add new output_types to file json (#2132)
12. ENCD-3853 Remove UCSC logos (#2134)
13. ENCD-3757 Adjust histone broad peak read depth audit (#2125)
14. ENCD-3831 Add exp audit to flag standards violations (#2124)
15. ENCD-3766 Add submitter comments to certain js pages (#2123)
16. ENCD-3820 Biosample: PMI property (#2120)
17. ENCD-3798 Ontology Update Jan2018 (#2119)
18. ENCD-3816 Update selenium version to 3.8.1 (#2118)
19. ENCD-3803 Allow fastq_sig to accept 3 in SRR headers (#2113)
20. ENCD-3456 Stringify array and object items in a cell (#2111)
21. ENCD-3762 Add RegulomeDB internal_tag and badge (#2110)
22. ENCD-3421 Properly link home chart to matrix (#2108)
23. ENCD-2567 New report page column selector modal (#2105)

65.3 (released)
----------------
    * ENCD-3851 Add max clause es5 updates

65.2 (unreleased)
-----------------
    * Update to snovault 1.0.2 (#2128) -> ENCD-3845

65.1 (unreleased)
-----------------
    * ENCD-3813 Update to snovault 1.0.1 (#2116)

65.0 (unreleased)
-----------------
    1. ENCD-3815 Fix tests for facet aggregation set to 200 (#2109)
    2. ENCD-3795 Fix spelling in histone and idr qm jsons (#2104)
    3. ENCD-3810 Set facet aggregation to 200 in search (#2107)
    4. ENCD 3749 Update README for ES5 and dependency requirements (#2087)
    5. ENCD-3741 Search for objects based on associated grant number (#2103)
    6. ENCD-3792 Add histone_chip_quality_metric PIP-198 (#2101)
    7. Update to snovault v1.0.0 -> ENCD-3788
    8. ENCD-3745 Add platform to file and exp facets (#2088)
    9. ENCD-3765 Set max_result_window for annotations index (#2083)
    10. ENCD-2488 ES5 Update aka RM3910
    11. ENCD-3546 Create 'save and add' button to add forms (#2100)
    12. ENCD-3700 Remove unreplicated exp audit for genetic mod DNase (#2096)
    13. ENCD-3781 Resolve WGBS lambda audit error (#2095)
    14. ENCD 3759 Fix WGBS coverage audit (#2093)
    15. ENCD-3743 Fix read depth audits for DNase and ChIP (#2091)
    16. ENCD-3760 Remove the NTR assay audit (#2089)
    17. ENCD-3724 Adjust facet term display check (#2086)
    18. ENCD-3755 Remove schemas for RNAi and construct characterizations (#2085)
    19. ENCD-3737 Add M14 gencode annotations to file enums (#2084)
    20. ENCD-3708 Update publication states (#2077)
    21. ENCD-3699 Remove mixed run type audit from DNase (#2065)
    22. ENCD-3661 Update drawing file graphs and JS Tests (#2080)
    23. ENCD-3764 Fix message typo in Assay audit (#2081)
    24. ENCD-3473 Fix for unknown error in batch_download
    25. ENCD-3579 Fix for batch download error
    26. ENCD-3566 Fix JS FileInput add document (#2076)
    27. ENCD-3597 Use obj picker for user impersonation (#2068)
    28. ENCD-3721 Allow 'in vitro sample' to have biosample_term_name (#2067)
    29. ENCD-3734 file audit escalation (#2066)

0.1 (unreleased)
----------------
