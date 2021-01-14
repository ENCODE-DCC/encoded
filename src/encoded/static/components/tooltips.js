export let tooltips = {
    //for patient page dominant tumor
    "ACD-RCC": "Acquired cystic disease-associated renal cell carcinoma",
    "AML": "Angiomyolipoma",
    "ChRCC": "Chromophobe renal cell carcinoma",
    "ccPRCC": "Clear cell papillary renal cell carcinoma",
    "ccRCC": "Clear cell renal cell carcinoma",
    "CDC": "Collecting duct carcinoma",
    "CN": "Cystic nephroma",
    "FH RCC": "Hereditary leiomyomatosis and RCC-associated RCC",
    "MA": "Metanephric adenoma",
    "MiT TRCC": "MiT family translocation renal cell carcinoma",
    "MTSCC": "Mucinous tubular and spindle cell carcinoma",
    "MCRN": "Multilocular cystic renal neoplasm of low malignant potential",
    "RON": "Oncocytic renal neoplasm, not further classified",
    "RO": "Oncocytoma",
    "Other": "Other",
    "PRCC": "Papillary renal cell carcinoma",
    "RCC, NOS": "Renal cell carcinoma, not further classified",
    "RMC": "Renal medullary carcinoma",
    "SDH RCC": "SDH deficient renal cell carcinoma",
    "TC RCC": "Tubulocystic renal cell carcinoma",
    "Unclassified RCC": "Unclassified RCC",

    //for patient page other facets
    "Tumor Laterality": "Laterality of the tumor is recorded when available in the pathology report.",
    "Tumor Size Range": "Greatest dimension range of tumor was recorded in cm.",

    //other page facets
    "Tumor Focality": "Single or multiple foci of tumors in that specimen is recorded when available.",
    "Sarcomatoid Change": "Presence of sarcomatoid dedifferentiation when reported",
    "Tumor Necrosis": "Presence of tumor necrosis (this is available only after 2012).",
    "Tumor Grade": " Highest Fuhrman or ISUP grade seen in tumor, 1-4. Benign tumors and ChRCC are recorded as not applicable. Tumors for which grade was not reported in pathology are considered not available. Some of the cases have been reviewed centrally, and the centrally reviewed grade has been depicted in KCE for these cases.",
    "Margin Status": "Tumor transected at the surgical margins are considered positive/involved.",
    "Lymphvascular invasion(LVI)": "Lymphovascular invasion in non-muscle containing vessels.",
    "6th edition": "TNM Stage composite stage based on 6th edition rules.",
    "7th edition": "TNM Stage composite stage based on 7th edition rules.",
    "8th edition": "TNM Stage composite stage based on 7th edition rules.",

    //patient page facets
    "Metastatic Site": "This is recorded either from pathology report using natural language search or from clinical and radiotherapy notes. These may not be all inclusive.",
    "Metastasis Histology Proven": "Record of metastatic RCC in pathology reports and nephrectomy specimens are considered histologically proven.",
    "Medication Duration": "The duration (in months) of the following prescribed Cancer and Support drugs (courtesy Dr. Bowman) are recorded.",
    "Radiation Treatment Status": "Patients with RCC that received radiotherapy (any technique including SBRT and Stereotactic radiotherapy) at UTSW. The date, dose, fraction, and site of RT are extracted. The patient may receive RT to multiple sites. Brain RT data were partly manually extracted.",

    // Patient Demographics
    "Sex": "Identifies the sex of the patient as recorded in the patient’s EMR.",
    "Ethnicity": "Persons of Spanish or Hispanic origin as recorded in the patient’s EMR. Patients that declined or their records were not found are recorded as unknown.",
    "Race": "The primary race of the person (American Indian, Asian, Black, Hawaiian Pacific, White, Others) as recorded in the patient’s EMR.",
    "Age at Diagnosis": "The age of the patient in years at diagnosis of renal tumor.",
    "Last Follow Up Date": "Patient's most recent visit date as recorded in EMR.",
    "Vital Status": "Patient's status (Alive or deceased) as recorded in EMR or in Tumor Registry.",
    "Dominant Tumor": "The patient's dominant tumor based on current data availability ( stage, histology and size)",

    // Surgery
    "Hospital Location": "The location procedure was conducted For patients with surgery at an outside institution, the surgery hospital location is recorded as “Outside”.",
    "Surgery Treatment Summary": "The surgery treatment status. For patients that did not undergo surgery, their status is recorded as “No” (management at UTSW for active surveillance or metastasis without surgical treatment).",
    "Procedure": "The surgical procedure conducted as recorded in the EMR.",
    "Nephrectomy Details": "The Nephrectomy type, and the method (Nephrectomy approach and nephrectomy robotic assist) of nephrectomy for patients that underwent surgery.",

    // Pathology Report
    "Laterality": "Laterality of the tumor is recorded when available in the pathology report.",
    "Size": "The greatest dimension of the tumor was recorded in cm.",
    "Focality": "Single or multiple foci of tumors in that specimen is recorded when available.",
    "Sarcomatoid": "The presence of sarcomatoid dedifferentiation when reported. The percentage is reported if available.",
    "Necrosis": "The presence of tumor necrosis (this is available only after 2012).",
    "Grade": "highest Fuhrman or ISUP grade seen in tumor, 1-4. ChRCC are recorded as “Not applicable”. Tumors for which grade was not reported in pathology are considered “Not available”.",
    "Margins": "Tumor transected at the surgical margins are considered positive.",
    "LVI": "Lymphovascular invasion in non-muscle containing vessels.",
    "Perinephric Infiltration": "Tumor extension into perinephric tissues, identified microscopically.",
    "Renal Vein Involvement": "Tumor extension into major renal veins, identified microscopically.",
    "Ipsilateral Adrenal Gland Involvement": "Tumor extension into adrenal gland, identified microscopically. Contiguous or not (this was reported only after 2010 and were derived based on gross description in prior pathology reports. If not stated in old reports, it was assumed to be continuous).",
    "Pelvicaliceal Involvement": "Tumor extension into pelvicalyceal, identified microscopically (this will be part of staging 2018 onwards and is may not be mentioned in the prior pathology reports).",
    "AJCC TNM Stage": "Included both the pathology and clinical stage. The edition used is noted at the time of report.",

    // Follow up Data
    "Diagnosis Date: The earliest date of diagnosis of renal tumor (irrespective of the laterality and focality). It is the earliest date of any of the following": "documented renal carcinoma in patient’s electronic medical records (EMR) in clinical notes, or date of nephrectomy or date of metastasis or initiation of treatment for (medication or radiation). If physicians stated that in retrospect the patient had cancer earlier, earlier date is used. Ambiguous terms in the notes are not used for diagnosis (likely, cannot be ruled out, suggests, worrisome, possible, potentially malignant). When treatment is received as first course before definite diagnosis, treatment date was used as date of diagnosis. For nephrectomies with benign tumors, date of nephrectomy as considered date of diagnosis. Date of diagnosis/resection of contralateral tumor in an outside institution is not always available but when available was considered as date of diagnosis. When only the year is available, the 1st of July for that year, if only month is available, 1st of that month is considered as date of diagnosis.",
    "Surgery Date": "The date (yyyy-mm-dd) of nephrectomy, RCC metastasectomy, biopsy and/or radioablation are recorded for patients that underwent surgery at UTSW . Data are extracted from CPT codes and when not available from pathology reports. For patients with prior nephrectomy at an outside institution, the data are extracted whenever available from pathology reports. If only the month and year are available, the date was rounded to 01 for that month. If only the year is available, the date is rounded to July first of that year. If no dates were available, it is recorded as “not available”.",

    // Other:
    "Radiation Treatment": "Patients with RCC that received radiotherapy (any technique including SBRT and Stereotactic radiotherapy) at UTSW. The date, dose, fraction, and site of RT are extracted. The patient may receive RT to multiple sites. Brain RT data were partly manually extracted.",
    "Medication": "The duration (in days) of the prescribed cancer drugs as recorded in EMR.",
    "Supportive medication": "The duration (in days) of the prescribed supportive drugs as recorded in EMR.",

    // Summary definitions :
    "Metastasis Status": "Patients that had histologic proven metastasis either at the time of nephrectomy or subsequently (FNA, core biopsy or metastasectomy), or patients started on systemic cancer drug, or received radiotherapy in non-renal site (including thrombus) or stated to have metastasis in the clinical notes are categorized as “Yes”.",

    "Metastasis Site": "This is recorded either from pathology report using natural language search or from clinical and radiotherapy notes. These may not be all-inclusive.",
    "Histology Proven": "Record of metastatic RCC in pathology reports and nephrectomy specimens are considered histologically proven.",
    "Biometric Parameters and Basic Blood Workup ": "Biometric parameters (Blood Pressure (BP_Systolic and BP_Diastolic) and Body Mass Index (BMI)) and laboratory values (serum albumin, creatinine, corrected calcium, hemoglobin, lactate dehydrogenase (LDH), neutrophils, platelets, sodium and WBC count) recorded in the patient's EMR within 30 days prior to first nephrectomy. If there are multiple entries of the same parameter within 30 days, the closest to surgery are displayed.",
    "Medical Imaging": "Types of medical imaging (CT abdomen and pelvis (with or without contrast), MRI abdomen (with or without contrast), and PET done within 90 days prior to Nephrectomy. If there are multiple entries of the same imaging modality within 90 days, only the closest to Nephrectomy is displayed.",
    "Germline Mutation": "Mutation of clinical significance or a variant of uncertain clinical significance in any of the genes from 76 cancer genes tested at the UTSW Genetics lab for these patients when available.",
    // bioexperiment, biodataset, bioreference, bioproject :
    "Biological replicate": "Replication on two distinct biosamples on which the same experimental protocol was performed. For example, on different growths, two different knockdowns, etc.",
    "Technical replicate": "Two replicates from the same biosample, treated identically for each replicate (e.g. same growth, same knockdown).",
    "Genome assembly": "Genome assembly that files were mapped to.",
    "Reference type": "The category that best describes the reference set.",
    "spike-in": "Designed to bind to a DNA molecule with a matching sequence, known as a control probe.",
    "Isogenic": "Biological replication. Two replicates from biosamples derived from the same human donor or model organism strain. These biosamples have been treated separately (i.e. two growths, two separate knockdowns, or two different excisions).",
    "Anisogenic": "Biological replication. Two replicates from similar tissue biosamples derived from different human donors or model organism strains.",
    "Sequencing replication": "A library can be run through a sequencer multiple times. Each one of these runs could be considered a sequencing replicate of the experiment, especially if the sequencing run is treated differently, e.g. paired- versus single-ended.",

    //facets for specimen:
    "Specimen Class": "The class of the biospecimen when it was taken.",
    "Specimen Type": "The final product after sample processing. It is the subtype of specimen/derivative (paired with Specimen Class).",
    "Specimen Lineage": "Parent vs derived sample. New is parent sample. Derived is the sample derived from another sample.Aliquot is an aliquot of a sample.",
    "Specimen Pathological Type": "Normal sample is Non-Malignant. Tumor sample is Malignant, which can be primary or metastatic.",
    "Specimen Activity Status": "Whether this sample is still available. Active is for available samples. Closed is for unavailable samples. Disabled is for revoked samples."
    
};

