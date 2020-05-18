# -*- coding: utf-8 -*-
"""
@author: esilgard

compare MRI data from HIDRA (azRad) to breast MRI data
manually entered into BCRP database and email mismatched records 
for data audit/QA prior to clinical outcomes audit (involving pathology)
"""
import pyodbc
import pandas
import argparse
import pandas.io.sql as psql
import win32com.client
import json
import sys


def get_scan_data(config, source_name):
    specs = config["database"][source_name]
    '''
    query appropriate data source for all MR scans in the parameter time period
    '''
    conn = pyodbc.connect('DRIVER={};SERVER={};DATABASE={};Trusted_Connection=yes'.\
                   format(specs["driver"], specs["server"], specs["db_name"]))
   
    query_string = "select distinct {} as MRN, {} as ScanDate, {} as Accession FROM {} WHERE \
                    {} >= '{}' AND {} < '{}' {}".format(specs['mrn'], specs['date'], specs['acc'], 
                    specs['table'], specs['date'], config["input"]["min_date"], specs['date'],
                    config["input"]["max_date"], specs['extra_query'])
    df = psql.read_sql(query_string, conn)
    conn.close()    
    print ('{} found in {}'.format(len(df), specs['table']))
    # clean up data frame by matching column headers
    df["ScanDate"] = df["ScanDate"].dt.date
    df["MRN"] = df["MRN"].map(lambda x: x.strip().upper())
    df["Accession"] = df["Accession"].map(lambda x: x.strip())    
    return df


def get_diff(ris_df, bcrp_df):
    '''
    clean dataframes so they can be compared through joins
    return dataframe of mismatched scans and total number of matched scans
    '''
    merged = ris_df.merge(bcrp_df,  how="outer", indicator= "Comparison")
    matched = ris_df.merge(bcrp_df, how="inner", indicator= "Comparison")
    # create copy of dataframe with unique values from both sources
    mismatched_df = merged[merged.Comparison != "both"].copy(deep=True )
    mismatched_df.index.name = "Index"
    
    #replace comparison category labels using dictionary
    mismatched_df["Comparison"].replace({"left_only": "IN RIS","right_only":" IN BCRP"}, inplace=True)

    return mismatched_df, len(matched)


def output(mismatched_df):
    # write excel spreadsheet to local directory
    writer = pandas.ExcelWriter(config["output"]["diff_spreadsheet"])
    mismatched_df.to_excel(writer,"Radiology Feed vs BCRP")
    writer.save()

def email_mismatched_spreadsheet(mismatched_df, match_num):
    '''
    write dataframe of mismatched records to excel to local directory and
    send email with excel spreadsheet of mismatched scans attched
    '''
    # create email for notification
    olMailItem = 0x0
    obj = win32com.client.Dispatch("Outlook.Application")
    newMail = obj.CreateItem(olMailItem)
    newMail.Subject = "Radiology Feed/BCRP MRI comparison for " + \
        config["input"]["min_date"] + " to " + config["input"]["max_date"]
    newMail.Body = "This is an automatically generated email detailing the " + \
        "Radiology Feed/BCRP comparison of MRIs between " + config["input"]["min_date"] + \
        " and " + config["input"]["max_date"]  + ": \n" + str(match_num) + \
        " matched scans and " + str(len(mismatched_df)) + \
        " mismatched scans (attached)"
    newMail.To = config["output"]["email_recipients"]    
    newMail.Attachments.Add(config["output"]["diff_spreadsheet"])
    newMail.Send()


def getArgParser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=str, default='refs/config.json',
                        help='config file with input/output/database details')
    parser.add_argument('--email', type=str, default=None, 
                        help='optional email recipient')
    return parser.parse_args()


if __name__ == '__main__':
    args = getArgParser()
    config = json.load(open(args.config,'r'))
    rad_df = get_scan_data(config, "UW_Feed")    
    bcrp_df = get_scan_data(config, "BCRP")
    mismatched_df, match_num = get_diff(rad_df, bcrp_df)
    print ('number of mismatched records {}'.format(len(mismatched_df)))
    print ('number of matched records {}'.format(match_num))
    output(mismatched_df)
    if args.email:
        email_mismatched_spreadsheet(mismatched_df, match_num)