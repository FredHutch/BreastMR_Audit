USE [BCRP_Caisis]
GO

SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO

BEGIN

SET NOCOUNT ON;

DECLARE @Query      NVARCHAR(MAX)
DECLARE @ErrorStop INT
DECLARE @ErrorSourceDatabase int
DECLARE @ErrorDestinationDatabase int


--Known Cancer - 1,2,3,4,18,14,15,16,17
--Screening - 8,9,10
--Further Problem Solving - 5,6,13
--Response to Neo - 12
--Short Interval follow up - 7
--Implant present - 11--only if it is the only thing else goes with Other



--group the category now

IF OBJECT_ID('dbo.tempMRIIndications2', 'U') IS NOT NULL 
  DROP TABLE dbo.tempMRIIndications2; 

Create table tempMRIIndications2
(
PtMRN varchar(50), 
IpAccNum varchar(50),
ProcedureDate DateTime,
Indication varchar(100),
MRIID int,
No1 varchar(150), 
No2 varchar(150),
No3 varchar(150),
No4 varchar(150),
No5 varchar(150),
No6 varchar(150),
No7 varchar(150),
No8 varchar(150),
No9 varchar(150),
No10 varchar(150),
No11 varchar(150),
No12 varchar(150),
No13 varchar(150),
No14 varchar(150),
No15 varchar(150),
No16 varchar(150),
No17 varchar(150),
No18 varchar(150),
KnownCancer int,
Screening int,
FurtherProblemSolving int,
ResponsetoNeo int, 
ShortIntervalFollowUp int,
ImplantPresent int,
OtherComments varchar(max),
Final varchar(Max)
)


SET @Query = N'Insert into tempMRIIndications2 (PtMRN, IpAccNum, ProcedureDate)
SELECT      distinct  dbo.Patients.PtMRN, dbo.BreastImagingProc.IpAccNum, dbo.BreastImagingProc.ProcedureDate
FROM            dbo.BreastImagingProc INNER JOIN
                         dbo.Patients ON dbo.BreastImagingProc.PatientID = dbo.Patients.PatientId INNER JOIN
                         dbo.BreastMRI ON dbo.BreastImagingProc.IpID = dbo.BreastMRI.IpID INNER JOIN
                         dbo.BreastMRIIndications ON dbo.BreastMRI.MRIID = dbo.BreastMRIIndications.MRIID
ORDER BY dbo.Patients.PtMRN'

EXEC sp_executesql @Query

UPDATE       tempMRIIndications2
SET                No1 = '1'
FROM            tempMRIIndications2 INNER JOIN
                         vMRIIndications ON tempMRIIndications2.PtMRN = vMRIIndications.PtMRN AND tempMRIIndications2.IpAccNum = vMRIIndications.IpAccNum AND 
                         tempMRIIndications2.ProcedureDate = vMRIIndications.ProcedureDate
WHERE        (vMRIIndications.Indication = '1')

UPDATE       tempMRIIndications2
SET                No2 = '1'
FROM            tempMRIIndications2 INNER JOIN
                         vMRIIndications ON tempMRIIndications2.PtMRN = vMRIIndications.PtMRN AND tempMRIIndications2.IpAccNum = vMRIIndications.IpAccNum AND 
                         tempMRIIndications2.ProcedureDate = vMRIIndications.ProcedureDate
WHERE        (vMRIIndications.Indication = '2')


UPDATE       tempMRIIndications2
SET                No3 = '1'
FROM            tempMRIIndications2 INNER JOIN
                         vMRIIndications ON tempMRIIndications2.PtMRN = vMRIIndications.PtMRN AND tempMRIIndications2.IpAccNum = vMRIIndications.IpAccNum AND 
                         tempMRIIndications2.ProcedureDate = vMRIIndications.ProcedureDate
WHERE        (vMRIIndications.Indication = '3')

UPDATE       tempMRIIndications2
SET                No4 = '1'
FROM            tempMRIIndications2 INNER JOIN
                         vMRIIndications ON tempMRIIndications2.PtMRN = vMRIIndications.PtMRN AND tempMRIIndications2.IpAccNum = vMRIIndications.IpAccNum AND 
                         tempMRIIndications2.ProcedureDate = vMRIIndications.ProcedureDate
WHERE        (vMRIIndications.Indication = '4')


UPDATE       tempMRIIndications2
SET                No5 = '1'
FROM            tempMRIIndications2 INNER JOIN
                         vMRIIndications ON tempMRIIndications2.PtMRN = vMRIIndications.PtMRN AND tempMRIIndications2.IpAccNum = vMRIIndications.IpAccNum AND 
                         tempMRIIndications2.ProcedureDate = vMRIIndications.ProcedureDate
WHERE        (vMRIIndications.Indication = '5')


UPDATE       tempMRIIndications2
SET                No6 = '1'
FROM            tempMRIIndications2 INNER JOIN
                         vMRIIndications ON tempMRIIndications2.PtMRN = vMRIIndications.PtMRN AND tempMRIIndications2.IpAccNum = vMRIIndications.IpAccNum AND 
                         tempMRIIndications2.ProcedureDate = vMRIIndications.ProcedureDate
WHERE        (vMRIIndications.Indication = '6')


UPDATE       tempMRIIndications2
SET                No7 = '1'
FROM            tempMRIIndications2 INNER JOIN
                         vMRIIndications ON tempMRIIndications2.PtMRN = vMRIIndications.PtMRN AND tempMRIIndications2.IpAccNum = vMRIIndications.IpAccNum AND 
                         tempMRIIndications2.ProcedureDate = vMRIIndications.ProcedureDate
WHERE        (vMRIIndications.Indication = '7')


UPDATE       tempMRIIndications2
SET                No8 = '1'
FROM            tempMRIIndications2 INNER JOIN
                         vMRIIndications ON tempMRIIndications2.PtMRN = vMRIIndications.PtMRN AND tempMRIIndications2.IpAccNum = vMRIIndications.IpAccNum AND 
                         tempMRIIndications2.ProcedureDate = vMRIIndications.ProcedureDate
WHERE        (vMRIIndications.Indication = '8')



UPDATE       tempMRIIndications2
SET                No9 = '1'
FROM            tempMRIIndications2 INNER JOIN
                         vMRIIndications ON tempMRIIndications2.PtMRN = vMRIIndications.PtMRN AND tempMRIIndications2.IpAccNum = vMRIIndications.IpAccNum AND 
                         tempMRIIndications2.ProcedureDate = vMRIIndications.ProcedureDate
WHERE        (vMRIIndications.Indication = '9')



UPDATE       tempMRIIndications2
SET                No10 = '1'
FROM            tempMRIIndications2 INNER JOIN
                         vMRIIndications ON tempMRIIndications2.PtMRN = vMRIIndications.PtMRN AND tempMRIIndications2.IpAccNum = vMRIIndications.IpAccNum AND 
                         tempMRIIndications2.ProcedureDate = vMRIIndications.ProcedureDate
WHERE        (vMRIIndications.Indication = '10')



UPDATE       tempMRIIndications2
SET                No11 = '1'
FROM            tempMRIIndications2 INNER JOIN
                         vMRIIndications ON tempMRIIndications2.PtMRN = vMRIIndications.PtMRN AND tempMRIIndications2.IpAccNum = vMRIIndications.IpAccNum AND 
                         tempMRIIndications2.ProcedureDate = vMRIIndications.ProcedureDate
WHERE        (vMRIIndications.Indication = '11')



UPDATE       tempMRIIndications2
SET                No12 = '1'
FROM            tempMRIIndications2 INNER JOIN
                         vMRIIndications ON tempMRIIndications2.PtMRN = vMRIIndications.PtMRN AND tempMRIIndications2.IpAccNum = vMRIIndications.IpAccNum AND 
                         tempMRIIndications2.ProcedureDate = vMRIIndications.ProcedureDate
WHERE        (vMRIIndications.Indication = '12')



UPDATE       tempMRIIndications2
SET                No13 = '1'
FROM            tempMRIIndications2 INNER JOIN
                         vMRIIndications ON tempMRIIndications2.PtMRN = vMRIIndications.PtMRN AND tempMRIIndications2.IpAccNum = vMRIIndications.IpAccNum AND 
                         tempMRIIndications2.ProcedureDate = vMRIIndications.ProcedureDate
WHERE        (vMRIIndications.Indication = '13')


UPDATE       tempMRIIndications2
SET                No14 = '1'
FROM            tempMRIIndications2 INNER JOIN
                         vMRIIndications ON tempMRIIndications2.PtMRN = vMRIIndications.PtMRN AND tempMRIIndications2.IpAccNum = vMRIIndications.IpAccNum AND 
                         tempMRIIndications2.ProcedureDate = vMRIIndications.ProcedureDate
WHERE        (vMRIIndications.Indication = '14')


UPDATE       tempMRIIndications2
SET                No15 = '1'
FROM            tempMRIIndications2 INNER JOIN
                         vMRIIndications ON tempMRIIndications2.PtMRN = vMRIIndications.PtMRN AND tempMRIIndications2.IpAccNum = vMRIIndications.IpAccNum AND 
                         tempMRIIndications2.ProcedureDate = vMRIIndications.ProcedureDate
WHERE        (vMRIIndications.Indication = '15')



UPDATE       tempMRIIndications2
SET                No16 = '1'
FROM            tempMRIIndications2 INNER JOIN
                         vMRIIndications ON tempMRIIndications2.PtMRN = vMRIIndications.PtMRN AND tempMRIIndications2.IpAccNum = vMRIIndications.IpAccNum AND 
                         tempMRIIndications2.ProcedureDate = vMRIIndications.ProcedureDate
WHERE        (vMRIIndications.Indication = '16')



UPDATE       tempMRIIndications2
SET                No17 = '1'
FROM            tempMRIIndications2 INNER JOIN
                         vMRIIndications ON tempMRIIndications2.PtMRN = vMRIIndications.PtMRN AND tempMRIIndications2.IpAccNum = vMRIIndications.IpAccNum AND 
                         tempMRIIndications2.ProcedureDate = vMRIIndications.ProcedureDate
WHERE        (vMRIIndications.Indication = '17')



UPDATE       tempMRIIndications2
SET                No18 = '1'
FROM            tempMRIIndications2 INNER JOIN
                         vMRIIndications ON tempMRIIndications2.PtMRN = vMRIIndications.PtMRN AND tempMRIIndications2.IpAccNum = vMRIIndications.IpAccNum AND 
                         tempMRIIndications2.ProcedureDate = vMRIIndications.ProcedureDate
WHERE        (vMRIIndications.Indication = '18')


UPDATE       tempMRIIndications2
SET                KnownCancer = '1'
Where 
Not(No1 is null)
OR Not(No2 is null)
OR Not(No3 is null)
OR Not(No4 is null)
OR Not(No14 is null)
OR Not(No15 is null)
OR Not(No16 is null)
OR Not(No17 is null)
OR Not(No18 is null)

UPDATE       tempMRIIndications2
SET                Screening = '1'
Where 
Not(No8 is null)
OR Not(No9 is null)
OR Not(No10 is null)

UPDATE       tempMRIIndications2
SET                FurtherProblemSolving = '1'
Where 
Not(No5 is null)
OR Not(No6 is null)
OR Not(No13 is null)


UPDATE       tempMRIIndications2
SET             ResponsetoNeo = '1'
Where 
Not(No12 is null)


UPDATE       tempMRIIndications2
SET     ShortIntervalFollowUp = '1'
Where 
Not(No7 is null)

UPDATE       tempMRIIndications2
SET                ImplantPresent = '1'
Where 
Not(No11 is null)



UPDATE       tempMRIIndications2
SET                No1 = 'Known Bca eval ext disease'
Where 
Not(No1 is null)


UPDATE       tempMRIIndications2
SET                No2 = 'Prior to excis Bx/lump'
Where 
Not(No2 is null)

UPDATE       tempMRIIndications2
SET                No3 = 'Post Bx/lump neg marg'
Where 
Not(No3 is null)


UPDATE       tempMRIIndications2
SET                No4 = 'Pos marg eval resid disease'
Where 
Not(No4 is null)

UPDATE       tempMRIIndications2
SET                No5 = 'Add''l eval mammo lesion'
Where 
Not(No5 is null)

UPDATE       tempMRIIndications2
SET                No6 = 'Add''l eval palp lesion'
Where 
Not(No6 is null)

UPDATE       tempMRIIndications2
SET                No7 = 'Short-interv f/u MRI'
Where 
Not(No7 is null)

UPDATE       tempMRIIndications2
SET                No8 = 'Screening: tx pers Hx'
Where 
Not(No8 is null)


UPDATE       tempMRIIndications2
SET                No9 = 'Screening: genetic/family Hx'
Where 
Not(No9 is null)

UPDATE       tempMRIIndications2
SET                No10 = 'Screening: other'
Where 
Not(No10 is null)


UPDATE       tempMRIIndications2
SET                No11 = 'Implant present'
Where 
Not(No11 is null)


UPDATE       tempMRIIndications2
SET                No12 = 'Response to neoadj'
Where 
Not(No12 is null)


UPDATE       tempMRIIndications2
SET                No13 = 'Other'
Where 
Not(No13 is null)


UPDATE       tempMRIIndications2
SET                No14 = 'DCIS'
Where 
Not(No14 is null)


UPDATE       tempMRIIndications2
SET                No15 = 'IDC'
Where 
Not(No15 is null)


UPDATE       tempMRIIndications2
SET                No16 = 'ILC'
Where 
Not(No16 is null)


UPDATE       tempMRIIndications2
SET                No17 = 'Other invasive'
Where 
Not(No17 is null)


UPDATE       tempMRIIndications2
SET                No18 = 'Mal axil adnop, unk 1'
Where 
Not(No18 is null)

UPDATE       tempMRIIndications2
SET                FINAL = ' '



UPDATE       tempMRIIndications2
SET                FINAL = 'Known Cancer|'
Where 
Not(KnownCancer is null)

UPDATE       tempMRIIndications2
SET                FINAL = FINAL + '|Screening|'
Where 
Not(Screening  is null)

UPDATE       tempMRIIndications2
SET                FINAL = FINAL + '|Further Problem Solving|'
Where 
Not(FurtherProblemSolving   is null)

UPDATE       tempMRIIndications2
SET                FINAL = FINAL + '|Response to Neo|'
Where 
Not(ResponsetoNeo   is null)

UPDATE       tempMRIIndications2
SET                FINAL = FINAL + '|Short Interval FollowUp|'
Where 
Not(ShortIntervalFollowUp   is null)

UPDATE       tempMRIIndications2
SET                FINAL = FINAL + '|Implant Present|'
Where 
Not(ImplantPresent   is null)

UPDATE       tempMRIIndications2
SET                FINAL = Replace(Final,'Implant Present','')
Where (ImplantPresent ='1') and ((KnownCancer = '1') OR (Screening = '1') OR (FurtherProblemSolving = '1') OR (ResponsetoNeo = '1') OR  (ShortIntervalFollowUp = '1'))


UPDATE       tempMRIIndications2
SET                FINAL = Replace(Final, '||',', ')
Where NOT(FINAL is null)

UPDATE       tempMRIIndications2
SET                FINAL = Replace(Final,'|','')
Where (FINAL like '|%')

UPDATE       tempMRIIndications2
SET                FINAL = Replace(Final,'|','')
Where (FINAL like '%|')


UPDATE       tempMRIIndications2
SET                FINAL = Replace(Final,',','')
Where (FINAL like ',%')

UPDATE       tempMRIIndications2
SET                FINAL = Replace(Final,',','')
Where (FINAL like '%,')

UPDATE       tempMRIIndications2
SET                FINAL = LTRIM(RTRIM((Final)))
Where NOT(FINAL is null)





UPDATE       tempMRIIndications2
SET                MRIID = vMRIIndications.MRIID
FROM            tempMRIIndications2 INNER JOIN
                         vMRIIndications ON tempMRIIndications2.PtMRN = vMRIIndications.PtMRN AND tempMRIIndications2.IpAccNum = vMRIIndications.IpAccNum AND 
                         tempMRIIndications2.ProcedureDate = vMRIIndications.ProcedureDate


UPDATE       tempMRIIndications2
SET                OtherComments = BreastMRI.OtherIndications
FROM            tempMRIIndications2 INNER JOIN
                         BreastMRI ON tempMRIIndications2.MRIID = BreastMRI.MRIID 



Select * from tempMRIIndications2

END



