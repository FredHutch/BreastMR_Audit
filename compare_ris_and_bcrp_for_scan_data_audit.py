# -*- coding: utf-8 -*-
"""
Created on Mon May 08 14:35:14 2017

@author: esilgard

compare RIS (billing output) in excel spreadsheed to breast MRI data
manually entered into BCRP database and email mismatched records 
for data audit/QA
"""
import pyodbc
import pandas
import pandas.io.sql as psql
import win32com.client
import os

# input variables needed for RIS and BCRP comparison and notification
RIS_SHEET = <excel spreadsheet with RIS billing data from MR scans>
MIN_DATE = <minimum search date>
MAX_DATE = <maxmum search date>
EMAIL_RECIPIENTS = <email address>

dir_path = os.path.dirname(os.path.realpath(__file__))

def get_ris():
    '''
    read in RIS report (from global RIS SHEET variable)
    for time period (based on global MIN_DATE and MAX_DATE variables),
    restrict by ExamCode to MRIs (no biopsies)
    return pandas dataframe of patient id, scan id, and scan date
    '''
    ris_df = pandas.read_excel(RIS_SHEET)
    ris_df = ris_df[ris_df.ExamCode != 'MMRIBX']
    
    # clean up data frame by stripping whitespace,
    # converting datetime to date, and removing unnecessary columns
    ris_df['Accession'] = ris_df['Accession'].map(lambda x: str(x))
    ris_df['CompletedDTTM'] = ris_df['CompletedDTTM'].dt.date
    del ris_df['ExamCode']
    del ris_df['LastName']
    del ris_df['FirstName']
    del ris_df['ExamDesc']
    
    return ris_df


def get_bcrp():    
    ''' 
    query BCRP_Caisis database for all records between MIN_DATE and MAX_DATE
    return dataframe of patient MRNS, scan assessions, and scan dates
    '''
    conn = pyodbc.connect('DRIVER={SQL Server};SERVER=CRANE;\
        DATABASE=BCRP_Caisis;Trusted_Connection=yes')
    query_string = "select distinct PtMRN as MedicalRecord, ProcedureDate as \
        CompletedDTTM, AssessmentNumber as Accession\
        FROM vEmilyAssessment WHERE  ProcedureDate >'" + MIN_DATE + "' \
        AND proceduredate < '" + MAX_DATE + "' AND ptmrn like 'U%'"
    bcrp_df = psql.read_sql(query_string, conn)
    conn.close()
    
    # clean up data frame by matching column headers
    bcrp_df['CompletedDTTM'] = bcrp_df['CompletedDTTM'].dt.date
    bcrp_df['MedicalRecord'] = bcrp_df['MedicalRecord'].map(lambda x: x.strip().upper())
    bcrp_df['Accession'] = bcrp_df['Accession'].map(lambda x: x.strip())
    
    return bcrp_df


def get_diff(ris_df, bcrp_df):
    '''
    clean dataframes so they can be compared through joins
    return dataframe of mismatched scans and total number of matched scans
    '''
    merged = ris_df.merge(bcrp_df,  how='outer', indicator= 'Comparison')
    matched = ris_df.merge(bcrp_df, how='inner', indicator= 'Comparison')
    # create copy of dataframe with unique values from both sources
    mismatched_df = merged[merged.Comparison != 'both'].copy(deep=True )
    mismatched_df.index.name = 'Index'
    
    #replace comparison category labels using dictionary
    mismatched_df['Comparison'].replace({'left_only': 'IN RIS',
        'right_only':' IN BCRP'}, inplace=True)

    return mismatched_df, len(matched)


def email_mismatched_spreadsheet(mismatched_df, match_num):
    '''
    write dataframe of mismatched records to excel to local directory and
    send email with excel spreadsheet of mismatched scans attched
    '''
    # write excel spreadsheet to local directory
    writer = pandas.ExcelWriter('mismatched_scans_output.xlsx')
    mismatched_df.to_excel(writer,'RIS vs BCRP')
    writer.save()
    # create email for notification
    olMailItem = 0x0
    obj = win32com.client.Dispatch("Outlook.Application")
    newMail = obj.CreateItem(olMailItem)
    newMail.Subject = "RIS/BCRP MRI comparison for " + MIN_DATE + " to " + \
        MAX_DATE
    newMail.Body = "This is an automatically generated email detailing the " + \
        "BCRP/RIS comparison of MRIs between " + MIN_DATE + " and " + \
        MAX_DATE + ": \n" + str(match_num) + " matched scans and " + \
        str(len(mismatched_df)) + " mismatched scans (attached)"
    newMail.To = EMAIL_RECIPIENTS    
    newMail.Attachments.Add(dir_path + os.path.sep + 'mismatched_scans_output.xlsx')
    #newMail.Send()

##############################################################################

ris_df = get_ris()    
bcrp_df = get_bcrp()
mismatched_df, match_num = get_diff(ris_df, bcrp_df)
email_mismatched_spreadsheet(mismatched_df, match_num)



