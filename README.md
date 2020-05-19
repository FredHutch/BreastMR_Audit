# BreastMR_Audit
Scripts to conduct breast MR audit using RIS, BCRP, and extracted pathology elements
(to be run in batches quarterly...ish)
====================================================================================

Steps:


1.	This program **compare_ris_and_bcrp_for_scan_data_audit.py** takes a single argument; the path to the json config file, which contains all other necessary input and output variables. Compare the RIS (MR billing output) for a given period to the manually entered data in BCRP for the same time
   - match against patient identifier, scan identifier, and scan date for all MRI's
   - email discordancies to appropriate clinical staff for QA


2. Update indications for scans in BCRP
   - run SQL script (from bchin) **BCRPIndications.sql** to update assessment view used for the audit with clinical indications (e.g. screening versus known cancer)


3. Check for missing or conflicting BIRADS or indications
   - run script to check view for missing assessemnts (BIRADS) or clinical indications
   - email discordancies to appropriate clinical staff for QA


4. Look for new pathology reports in HIDRA for any/all MR patients from *previous* year
     - look for pathology reports within 1 year of breast MR
     - pull out batch tsv files for data extraction


5. Batch path through NLP engine and assign for review
   - run tsv file of reports through nlp engine, assign appropriate reviewers and parameters
   - review pathology reports and approve/edit feilds (manual, offline process)


6. Write to pathology table in BCRP
   - write approved pathology elements from nlp output table to pathology data table in BCRP


7. Run audit script
   - compare scan assessments to pathology outcomes within one year
   - produce audit report (with confusion matrix) as well as PPV values
   - email to appropriate clinical staff

