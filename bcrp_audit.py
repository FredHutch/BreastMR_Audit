# -*- coding: utf-8 -*-
"""
Created on Tue Oct 11 09:19:29 2016

@author: esilgard


query BCRP imaging and find overall assessment (BIRADS) per scan for the year
query labkey NLP output tables for verified pathology outcomes within a year
"""

import pyodbc, json, sys
from datetime import datetime
import pandas.io.sql as psql
import xlsxwriter
config = json.load(open(sys.argv[1],'r'))
overall_label = {None:0, 'Benign':1, 'High Risk':2, 'Malignant':3}
###############################################################################        
def get_path():
    
    ## labkey/NLP connection string details
    path_conn = pyodbc.connect("DRIVER=" + config["database"]["LabKey"]["driver"] + \
    ";SERVER=" + config["database"]["LabKey"]["server"] + ";DATABASE=" + \
    config["database"]["LabKey"]["db_name"] + ";Trusted_Connection=yes") 

    # getclassifiedDiseaseGroup (to determine dz group)
    reports = psql.read_sql("select distinct ReportNo, \
        nlp.fieldResult.IterationId, Value from nlp.FieldResult \
        inner join nlp.Report on nlp.Report.reportId = nlp.fieldResult.ReportId \
        where Field = 'ClassifiedDiseaseGroup' AND JobRunId in (" + \
            ','.join(config["database"]["LabKey"]["job_run"]) + ")" + \
        " order by nlp.fieldResult.IterationId"
        , path_conn)

    # get updated path site (to determine dz location)
    # this is to filter out breast primaries occurring in other anatomical locations 
    # this is a per laterality field; there could potentially be breast site 
    # on one laterality and non on the other
    site_reports = psql.read_sql("select distinct ReportNo, \
        nlp.fieldResult.IterationId, Value from nlp.FieldResult \
        inner join nlp.Report on nlp.Report.reportId = nlp.fieldResult.ReportId \
        where Field = 'PathSite' AND JobRunId in (" + \
            ','.join(config["database"]["LabKey"]["job_run"]) + ")" + \
        " order by nlp.fieldResult.IterationId"
        , path_conn)
        
    st_accs = {}
    breast_sites = set([x.split(';')[0].strip() for x in open(config["input"]["path_sites_file"],"r").readlines()])
    
    # most recent update count should be the same for both lateralities
    # if one laterality is breast site and the other is not, the breast site
    # should overwrite/add back into the dictionary if it was removed
    for i,r in site_reports.iterrows():
        if breast_sites.intersection(set([y.strip() for y in r.Value.split(';')])):
            if r.ReportNo not in st_accs:
                st_accs[r.ReportNo] = r.IterationId
        # it's not breast and it's in the dictionary
        elif r.ReportNo in st_accs:
            del st_accs[r.ReportNo]

    #print len(st_accs),'breast site reports in this year'
    
    # then limit to only breast cancer cases
    accs = {}
    for i,r in reports.iterrows():
        # must be breast pathology AND breast site
        if r.Value == 'breast' and st_accs.get(r.ReportNo):
            if r.ReportNo not in accs:
                accs[r.ReportNo] = r.IterationId
        elif r.ReportNo in accs:
            del accs[r.ReportNo]
    #print len(accs),'breast cancer related reports in this year'

    def read_sql(field_name):
        val_d = {}
        rows = psql.read_sql("select distinct MRN, ReportNo, Value, TargetTable, \
            max(nlp.fieldResult.IterationId) from nlp.FieldResult \
            inner join nlp.Report on nlp.Report.reportId = nlp.fieldResult.ReportId \
            WHERE Field = '" + field_name + "' AND ReportNo in ('" + \
            "','".join(accs) + "') group by MRN, Value, ReportNo, TargetTable ",path_conn)
        # note! we're including table name to differentiate between lateralities
        # but only take the most recently modified values for each table&field
        for i,r in rows.iterrows():    
            val_d[r.MRN] = val_d.get(r.MRN,{})
            # take the most severe finding per report (there may be one for each laterality)   
            if 'etastatic' in r.Value: r.Value = "Malignant"            
            if r.ReportNo in val_d[r.MRN] and (r.Value in ["Malignant","Benign","High Risk"]):
                if overall_label[val_d[r.MRN][r.ReportNo]] > overall_label[r.Value]:
                   r.Value = val_d[r.MRN][r.ReportNo]            
            val_d[r.MRN][r.ReportNo] = r.Value
        
        return val_d
   
    dx = read_sql("OverallFinding")

    #print len(dx),'total dx'
    dt = read_sql("PathCollectedDate")
    #print len(dt),'total collected date'
    path_timeline = {}

    for mrn in scan_timeline:  
        path_timeline[mrn] = {}  
        # all patients with a scan will have a path timeline dict-it just may be empty
        #if mrn in dt: print mrn, ' in dt'
        for accession, date in dt.get(mrn, {}).items():
            #if mrn == 'U2514137': print accession, date
            path_date = datetime.strptime(date.split('T')[0], '%Y-%m-%d')
            #print mrn, date, accession, dx[mrn][accession]
            # in the case of two (or more) accessions on the same day, take the worst
            if date in path_timeline[mrn]:
                #print 'TWO PATHOLOGIES'
                path_timeline[mrn][path_date]['overall_category'] = \
                max(path_timeline[mrn][path_date]['overall_category'],
                    overall_label.get(dx[mrn][accession]))
            else:
                path_timeline[mrn][path_date] = {}           
            
            if mrn in dx and accession in dx[mrn]:                 
                path_timeline[mrn][path_date]['overall_category'] = overall_label.get(dx[mrn][accession])  
            else:
                print ('no finding found ' + mrn + ' ' + str(dt[mrn]))
   
    return path_timeline
###############################################################################
def get_scans():    
    '''
    query BCRP for all MR scans, BIRADS, and indications in the parameter time period
    '''
    timeline = {}
    BCRP_d = {}  
    screenings = set([])
    indication_d = {}
    ## trumping order for BIRADS assessment
    trump_ord = ['',None,'1','2','6','0','3','4','5']

    #print 'querying BCRP for MRIs from', config["input"]["min_date"],'to', config["input"]["max_date"]
    
    bcrp_conn = pyodbc.connect("DRIVER=" + config["database"]["BCRP"]["driver"] + \
        ";SERVER=" + config["database"]["BCRP"]["server"] + ";DATABASE=" + \
        config["database"]["BCRP"]["db_name"] + ";Trusted_Connection=yes")
      
    scan_rows = psql.read_sql("select distinct [PatientId],[PtMRN],[ProcedureDate], \
        [AssessmentNumber],[AssessmentCategoryLeft],[AssessmentCategoryRight], \
        [ProcedureLaterality],[AssessmentCategoryLesion],[LesionLaterality], \
        [LesionRecommendation], [Indications] FROM [BCRP_Caisis].[dbo].[vEmilyAssessmentIndications] \
        WHERE ProcedureDate >='" + config["input"]["min_date"] + "' AND proceduredate < '" +\
        config["input"]["max_date"] + "' AND PtMRN like 'U%'", bcrp_conn)
    #print len(scan_rows),'total scans'


    for i,r in scan_rows.iterrows():
        # check for conflicting indications (ignore if NULL)
        PtMRN = r.PtMRN.upper().strip()
        AssessmentNumber = r.AssessmentNumber.strip()
        if r.AssessmentNumber in indication_d and \
            indication_d[AssessmentNumber] != r.Indications:
            print ('WARNING: multiple indications '+ str(AssessmentNumber) + \
            ' ' + str(indication_d[AssessmentNumber]) + ' ' + str(r.Indications))
            
        elif r.Indications == 'Screening': 
            screenings.add((PtMRN,r.ProcedureDate))
        
        # reformat lesion indication field to compare to Right and Left Assessments
        if r.AssessmentCategoryLesion: 
            r.AssessmentCategoryLesion = r.AssessmentCategoryLesion.split('=')[0]
        
        # get "max" birads from trumping order
        birads = trump_ord[max(trump_ord.index(r.AssessmentCategoryLeft), \
            trump_ord.index(r.AssessmentCategoryRight),
            trump_ord.index(r.AssessmentCategoryLesion))]
        # collapse empty string and NULL instances
        if birads == '': 
            birads = None
        
        if r.AssessmentNumber in BCRP_d:
            ## if there's already an assessment,overwrite w/ "max" BIRADS (by trumping order)
            new_max_birads = trump_ord[max(trump_ord.index(birads),
                trump_ord.index(BCRP_d[AssessmentNumber]))]
            BCRP_d[AssessmentNumber] = new_max_birads   

            ## if there's an assessment for the same day with a different acc_num
        elif PtMRN in timeline and r.ProcedureDate in timeline[PtMRN]:
            new_max_birads = trump_ord[max(trump_ord.index(birads),
                trump_ord.index(timeline[PtMRN][r.ProcedureDate]))]
            timeline[PtMRN][r.ProcedureDate] = new_max_birads
        else:        
            BCRP_d[AssessmentNumber] = birads
            timeline[PtMRN] = timeline.get(PtMRN,{})
            timeline[PtMRN][r.ProcedureDate] = birads
        #if not BCRP_d[acc_num]: print 'Warning, no BIRADS',mrn, date, 'no birads' 
    print ('total screenings ' + str(len(screenings)))
    print (str(len(BCRP_d)) + ' ' + str(len(screenings)))
    return BCRP_d, screenings, timeline

###############################################################################
def compile_timelines(path_timeline, scan_timeline, screenings):
    from copy import deepcopy
    workbook = xlsxwriter.Workbook(config['output']['audit_spreadsheet'])  
    ws_counts = workbook.add_worksheet('OutcomesCounts')
    ws_cases = workbook.add_worksheet('TP&FN')

    table_format_bold = workbook.add_format({'bold': 1,'border': 2, 'align': 'center',
        'valign': 'vcenter'})
    table_format = workbook.add_format({'border': 2,'align': 'center',
        'valign': 'vcenter'})
    table_format_color = workbook.add_format({'bold': 1,'border': 2, 'align': 'center',
        'valign': 'vcenter','fg_color': '#39b6b9'})
    
    ws_cases.write_row('A1', ['MRN','MR Date','Label'], table_format_color)
    
    conf_matrix = {'0':dict.fromkeys([1,2,3,None],0),'1':dict.fromkeys([1,2,3,None],0),
        '2':dict.fromkeys([1,2,3,None],0),'3':dict.fromkeys([1,2,3,None],0),
        '4':dict.fromkeys([1,2,3,None],0),'5':dict.fromkeys([1,2,3,None],0),
        '6':dict.fromkeys([1,2,3,None],0), None:dict.fromkeys([1,2,3,None],0)}
    screen_conf_matrix = deepcopy(conf_matrix)
    tp_fn_count = 2
    print (str(len(scan_timeline)) + ' patients')
    
    for patient, timeline in scan_timeline.items():
        combined_scan_line = {}
        scan_index = 1
        for t in sorted(timeline.items(), key=lambda x: x[0]):
            combined_scan_line['Scan'+str(scan_index)] = t
            scan_index +=1
        
        ## iterate through all path for findings after scan, order events
        combined_line = {}     
        for primary_index in range(1,len(combined_scan_line)+1):
            string_scan_key = 'Scan'+str(primary_index)
            next_string_scan_key = 'Scan'+str(primary_index + 1)
            path_ordinal = 97
            combined_line[string_scan_key] = combined_scan_line[string_scan_key] 
            for path_date in sorted(path_timeline[patient]):
                ## only consider path AFTER (or on the day of) the scan in question
                if path_date >= combined_line[string_scan_key][0]:
                    ## restrict to path that is BEFORE the next scan
                    if next_string_scan_key in combined_scan_line:
                        ## if there are further scans, make sure the path is between this oneand the next
                        if path_date < combined_scan_line[next_string_scan_key][0]:                                
                            combined_line['Path'+str(primary_index)+chr(path_ordinal)] = (path_date, path_timeline[patient][path_date]['overall_category'])
                            path_ordinal += 1                                
                    ## there are no further scans; record this path
                    else:                           
                        combined_line['Path'+str(primary_index)+chr(path_ordinal)] = (path_date, path_timeline[patient][path_date]['overall_category'])
                        path_ordinal += 1
                            
                   
        ## tally up results by BIRADS for audit                      
        for scan_event in sorted([e[-1] for e in combined_line.keys() if 'Scan' in e]):
            finding = None
            #malignancy = None
            for path_event in sorted([p for k,p in combined_line.items() if 'Path'+scan_event in k]):
                finding = max(finding,path_event[1])                
            conf_matrix[combined_line['Scan'+scan_event][1]][finding] += 1
            #print patient, combined_line['Scan'+scan_event]
            if (patient, combined_line['Scan'+scan_event][0]) in screenings:
                screen_conf_matrix[combined_line['Scan'+scan_event][1]][finding] += 1
                if combined_line['Scan'+scan_event][1] in ('4', '5') and finding is None:
                    print (patient + ',' + str(combined_line))
                if finding == 3: 
                    if combined_line['Scan'+scan_event][1] in ['1','2','3']:
                        case = 'FN'
                    else:
                        case = 'TP'                   
                    ws_cases.write_row('A'+str(tp_fn_count),[patient,str(combined_line['Scan'+scan_event][0]),case],table_format)
                    tp_fn_count = tp_fn_count + 1
                    #print 'tp,fn count',tp_fn_count, case
            elif combined_line['Scan'+scan_event][1] in ['1','2','3']:
                print ('Diagnostic\t' + patient + '\t' + str(combined_line['Scan'+scan_event][0]) + '\t' + str(combined_line['Scan'+scan_event][1]) + '\t' + str(finding))


    def write_audit_counts():

        def write_table(col1,row1,title,cnf_mat):    
            '''
            write in initial tables/confusion matrices for total scans, 
            screens, and diagnostic scans
            '''
            ws_counts.write_row(col1 + str(row1),[title,'None','Benign','High Risk','Malignant','Totals'],table_format_color)       
            ws_counts.write_column(col1 + str(row1+1),['None','0','1',' 2','3','4','5','6'],table_format_color)
            
            mr_row = row1 + 1
            for key in sorted(cnf_mat):
                ws_counts.write_row(chr(ord(col1)+1)+str(mr_row),[v for k,v in sorted(cnf_mat[key].items())],table_format)
                ws_counts.write_formula(chr(ord(col1)+5) + str(mr_row),\
                    '=SUM(' + chr(ord(col1)+1) + str(mr_row) + ':'+ chr(ord(col1)+4) + str(mr_row)+')',table_format_color)
                mr_row += 1
            ws_counts.write_formula(chr(ord(col1)+5) + str(mr_row), \
                '=SUM(' + chr(ord(col1)+5) + str(row1+1) + ':' + chr(ord(col1)+5) + str(mr_row-1)+')',table_format_color)

        ws_counts.write_row('A1',['Preliminary 2016 MR Audit'],table_format_bold)  
        write_table('A',3, 'All MRIs',conf_matrix)
        write_table('H',3, 'Screenings',screen_conf_matrix)
        dx_conf_matrix = {}
        for brd in conf_matrix:            
            dx_conf_matrix[brd] = {}
            for find in conf_matrix[brd]: 
                dx_conf_matrix[brd][find] = conf_matrix[brd][find] - screen_conf_matrix[brd][find]
        #for k,v in  dx_conf_matrix.items():
        #    print k,v
        write_table('H',15, 'Diagnostic',dx_conf_matrix)
        
        percent_fmt = workbook.add_format({'num_format': '0.00%'})
        # insert formulas for audit counts
        ws_counts.write_column('A15',['Screening Audit','From: ' + \
            config['input']['min_date'] + '  Up to: ' + config['input']['max_date'], \
            '','1. Total Screening cases','2. Total Screening cases given 0, 3, 4 or 5',\
            'Category 0','Category 3','Category 4','Category 5','' ,'', \
            'True Positives (TP) (malignant 0,3,4&5)','FP1 (0,3,4&5 minus TP)',\
            'FP2 (4,5&lost to FU)','FP3 (4,5 not inc lost to FU)',\
            'PPV1 (0,3,4,5 -> malignancy)','PPV2 (4,5 -> malignancy )',\
            'PPV3 (4,5 -> malignancy; not inc lost to FU)','',\
            'Cancer Detection Rate (per 1,000 cases)','','Sensitivity','Specificity'])
    
        ws_counts.write_column('B36',['TP/(TP+FN)','TN/(TN + FP (inc no path))'])
        
        ws_counts.write_formula('C18','=M12');ws_counts.write_column('D18',['M12'])
        ws_counts.write_formula('C19','=SUM(M5,M8:M10)');ws_counts.write_column('D19',['SUM(M5,M8:M10)'])
        ws_counts.write_formula('C20','=M5');ws_counts.write_column('D20',['M5'])
        ws_counts.write_formula('C21','=M8');ws_counts.write_column('D21',['M8'])
        ws_counts.write_formula('C22','=M9');ws_counts.write_column('D22',['M9'])
        ws_counts.write_formula('C23','=M10');ws_counts.write_column('D23',['M10'])
        
        ws_counts.write_formula('C26','=SUM(L5,L8:L10)');ws_counts.write_column('D26',['SUM(L5,L8:L10)'])
        ws_counts.write_formula('C27','=SUM(M8:M10,M5) - C26');ws_counts.write_column('D27',['SUM(M8:M10,M5) - C26'])
        ws_counts.write_formula('C28','=SUM(I9:K10)');ws_counts.write_column('D28',['SUM(I9:K10)'])
        ws_counts.write_formula('C29','=SUM(J9:K10)');ws_counts.write_column('D29',['SUM(J9:K10)'])
        ws_counts.write_formula('C30','=SUM(L5,L8:L10)/SUM(M5,M8:M10)',percent_fmt);ws_counts.write_column('D30',['SUM(L5,L8:L10)/SUM(M5,M8:M10)'])
        ws_counts.write_formula('C31','=SUM(L9:L10)/SUM(M9:M10)',percent_fmt);ws_counts.write_column('D31',['SUM(L9:L10)/SUM(M9:M10)'])
        ws_counts.write_formula('C32','=C26/SUM(J9:L10)',percent_fmt);ws_counts.write_column('D32',['C26/SUM(J9:L10)'])
        ws_counts.write_formula('C34','=(C26/M12) *1000');ws_counts.write_column('D34',['(C26/M12) *1000'])
        ws_counts.write_formula('C36','=SUM(L9:L10)/SUM(L1:L11)',percent_fmt);ws_counts.write_column('D36',['SUM(L9:L10)/SUM(L1:L11)'])
        ws_counts.write_formula('C37','=SUM(I6:K7)/SUM(I5:K11)',percent_fmt);ws_counts.write_column('D37',['SUM(I6:K7)/SUM(I5:K11)'])
        
        
    write_audit_counts()
    workbook.close()
    print ('done')



BCRP_d, screenings, scan_timeline = get_scans()
path_timeline = get_path()

compile_timelines(path_timeline, scan_timeline, screenings)

#print '\nBIRADS\tCOUNTS'
#for v in sorted(set(BCRP_d.values())):      
 #   print v,'\t',BCRP_d.values().count(v)
    
