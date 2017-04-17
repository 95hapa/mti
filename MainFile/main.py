#!/usr/bin/env python3
''' 
MainFile

Usage:
    main.py <reference> (<sample>|(--paired=<sampleA,sampleB>))...

TODO:
1. NCBI querying
2. Refactor and clean

Possible Improvements:
1. All I/O filenames declared here by user
2. Object-orientation

'''

import subprocess as sp
from docopt import docopt
import os.path
import paramiko


'''
0. User -> FASTA ('')
1. FASTA -> BWA => SAM ('twoReferences.sam')
2. SAM -> parser.py => CSV ('parsed_SAM_v4.csv')
3. CSV -> grammy.cpp => GRA ('result    s.gra')
4. GRA -> visualization => User
''' 

#paramiko.util.log_to_file('/temp/paramiko.log')



# Step 0: Get the user's input
options = docopt(__doc__, version='mti-vis 1.0')

# Split paired-end strings into two filenames
single = options['<sample>']
paired = [tuple(s.split(',')) for s in options['--paired']]
if any(not len(e) == 2 for e in paired):
    print('Error: paired samples must have exactly two files')
    raise SystemExit(0)

# Ensure everything ends with '.fasta' or '.fastq'
if any((not s.endswith('.fasta')       # ends with .fasta
        and (not s.endswith('.fastq'))) # ends with .fastq
        for s in single + [x for p in paired for x in p]):
    print('Error: Please only valid provide .fasta or .fastq files')
    raise SystemExit(0)

# Check if .fasta/fastq files exist.
if any(not os.path.isfile(s)
        for s in single + [x for p in paired for x in p]):
    print('Error: The provided .fasta/fastq files do not exist in /bwa-0.7.15 and /MainFile')
    raise SystemExit(0)

if (not os.path.isfile(options['<reference>'])):
    print('Error: reference file does not exist in /bwa-0.7.15 and /MainFile')
    raise SystemExit(0)

sp.call(["bwa", "index", options['<reference>']])

# Step 1 (single-end): Execute BWA
for read in single:
    nameBase = read[:-6]
    filenameBase = '../GRAMMy/' + nameBase
    filename = filenameBase + ".sam"  
    with open(filename, 'w') as f:
        sp.call(
            ["bwa", "mem", options['<reference>'], read], stdout=f)
    # Step 2: Execute parser
    sp.call(["python3", "parser.py", filename], cwd="../GRAMMy")
    # Step 3: Execute GRAMMy
    sp.call(["./grammy", filenameBase + '.csv'], cwd="../GRAMMy")

# Step 1 (paired-ends): Execute BWA
for reads in paired:
    nameBase = reads[0][:-6] + '_' + reads[1][:-6]
    filenameBase = '../GRAMMy/' + nameBase
    filename = filenameBase + ".sam"
    with open(filename, 'w') as f:
        sp.call(
            ["bwa", "mem", options['<reference>'], reads[0], reads[1]], stdout=f)
    # Step 2: Execute parser
    sp.call(["python3", "parser.py", filename], cwd="../GRAMMy")
    # Step 3: Execute GRAMMy
    sp.call(["./grammy", filenameBase + '.csv'], cwd="../GRAMMy")
    


gra_file_name = nameBase + '.gra'
gra_file_path = '../GRAMMy/' + gra_file_name

if(os.path.isfile(gra_file_path)):
    
    print("File found");
    # Open a transport
    host = "10.171.204.176"
    port = 22
    transport = paramiko.Transport((host,port))
    
    
    # Authorization
    username = "student"
    password = "student"
    transport.connect(username = username, password = password)
    
    print("Authorization successful");
    
    # GO
    sftp = paramiko.SFTPClient.from_transport(transport)

    
    # Upload
    localpath = gra_file_path
    filepath = "/home/student/mti-site/server/graFilesDownloads/" + gra_file_name
    sftp.put(localpath, filepath)
    print("Transfer successful");

    
    sftp.close()
    transport.close()
    
    
    
    
    
