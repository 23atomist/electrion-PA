Pennsylvania Department of State
Electronic Data File Layout
Precinct Voter Registration


Date Extracted:		Dec 23, 2024
Record Count:		9,187
Requested Year:		2024
Requested Election:	Presidential


Please find the accompanying data file, prcvot.txt, containing precinct level voter registration statistics.  The file is an ASCII text, comma delimited file.  The file can also be easily imported into most PC database and spreadsheet applications.  The arrangement and types of fields in the files is given in the table below.

Party 1:	Democratic (DEM)
Party 2:	Republican (REP)
Party 3:	Green (GR)
Party 4:	Libertarian (LIB)
Party 5:	Other (OTH)
Party 6:	Empty

                                                     		Max
Field Name and Description                           		Length  	Data Type
Election Year (2024 for all records on CD)                	4  		Numeric
Election Type Code (G for all records on CD)              	1  		Character
County Code (01 through 67 see attached sheet)			2  		Numeric
Precinct Code                                             	7  		Numeric
Party 1 rank                                              	2  		Numeric
Party 1 abbreviation                                      	3  		Character
Registered Voters for party 1                             	7  		Numeric
Party 2 rank                                              	2  		Numeric
Party 2 abbreviation                                      	3  		Character
Registered Voters for party 2                             	7  		Numeric 
Party 3 rank                                              	2  		Numeric
Party 3 abbreviation                                      	3  		Character
Registered Voters for party 3                             	7  		Numeric
Party 4 rank                                              	2  		Numeric
Party 4 abbreviation                                      	3  		Character
Registered Voters for party 4                             	7  		Numeric
Party 5 rank                                              	2  		Numeric
Party 5 abbreviation                                      	3  		Character
Registered Voters for party 5                             	7  		Numeric
Party 6 rank                                              	2  		Numeric
Party 6 abbreviation                                      	3  		Character
Registered Voters for party 6                             	7  		Numeric
U.S. Congressional District                               	2  		Numeric
Pennsylvania State Senatorial District                    	2  		Numeric
Pennsylvania State House District                         	3  		Numeric
Municipality Type Code                                    	1  		Numeric
Municipality Name                                        	23  		Character
Municipality Breakdown Code 1                             	1  		Character
Municipality Breakdown Name 1                            	21  		Character
Municipality Breakdown Code 2                             	1  		Character
Municipality Breakdown Name 2                            	21  		Character
Bi-County Code (if municipality crosses county lines)    	2  		Numeric
MCD Code                                                  	3  		Numeric
FIPS Code                                                 	3  		Numeric
VTD code                                                  	4  		Numeric
Previous Precinct Code                                    	7  		Numeric
Previous U.S. Congressional District                      	2  		Numeric
Previous PA State Senatorial District                     	2  		Numeric
Previous PA State House District                          	3  		Numeric


County Code Table
-----------------
01 Adams
02 Allegheny
03 Armstrong
04 Beaver
05 Bedford
06 Berks
07 Blair
08 Bradford
09 Bucks
10 Butler
11 Cambria
12 Cameron
13 Carbon
14 Centre
15 Chester
16 Clarion
17 Clearfield
18 Clinton
19 Columbia
20 Crawford
21 Cumberland
22 Dauphin
23 Delaware
24 Elk
25 Erie
26 Fayette
27 Forest
28 Franklin
29 Fulton
30 Greene
31 Huntingdon
32 Indiana
33 Jefferson
34 Juniata
35 Lackawanna
36 Lancaster
37 Lawrence
38 Lebanon
39 Lehigh
40 Luzerne
41 Lycoming
42 McKean
43 Mercer
44 Mifflin
45 Monroe
46 Montgomery
47 Montour
48 Northampton
49 Northumberland
50 Perry
51 Philadelphia
52 Pike
53 Potter
54 Schuylkill
55 Snyder
56 Somerset
57 Sullivan
58 Susquehanna
59 Tioga
60 Union
61 Venango
62 Warren
63 Washington
64 Wayne
65 Westmoreland
66 Wyoming
67 York


Municipality Type Codes
-----------------------
2 City
4 Township
5 Town
6 Borough


Municipality Breakdown Codes (MUN ID)
---------------------------------------
D District
W Ward
P Precinct
X Other

