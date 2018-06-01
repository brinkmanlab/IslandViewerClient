#!/usr/bin/env python3

import requests
import re
import os
import sys
import time
from requests_toolbelt.multipart.encoder import MultipartEncoder
from optparse import OptionParser

# Get options from the command line
parser = OptionParser()
parser.add_option("--accession", dest="accession", action="store", type="string", help="Accession is the RefSeq accession for the desired reference genome used in the contig reordering step (mandatory for draft genomes)", metavar="ACCESSION")
parser.add_option("--token", dest="token", action="store", type="string", help="Your authentication token for the API. This is found under'JOBS' > 'HTTP API Token' when you login at www.pathogenomics.sfu.ca/islandviewer and is valid for 30 days before having to be refreshed.", metavar="TOKEN")
parser.add_option("--gbk", dest="gbk", action="store", type="string", help="Provide a name for the reordered genbank file containing genomic islands predicted by IslandViewer (output file).", metavar="GENBANK")
parser.add_option("--seq","--sequence", dest="sequence", action="store", type="string", help="Provide a name for the sequence file (genbank format) used as input.", metavar="SEQUENCE")
parser.add_option("--tab", dest="tab", action="store", type="string", help="Provide a name for the tab-delimited file that summarizes predicted genomic islands (output file).", metavar="TAB")

(options, args) = parser.parse_args()

if options.accession == None:
    parser.error("Missing argument for --accession ")    
if options.token == None:
    parser.error("Missing argument for --token ")       
if options.gbk == None:
    parser.error("Missing argument for --gbk ")    
if options.sequence == None:
    parser.error("Missing argument for --sequence ") 
if options.tab == None:
    parser.error("Missing argument for --tab ") 


if not os.path.isfile(options.sequence):
    sys.stderr.write("Could not find file '"+options.sequence+"'\n")
    sys.exit()
    
host = "http://www.pathogenomics.sfu.ca/islandviewer"


multipart_data = MultipartEncoder(
    fields={ "format_type": "GENBANK",
             'ref_accnum': options.accession,
             'genome_file': ('filename', open(options.sequence, 'rb'), 'text/plain')}
)
headers={'Content-Type': multipart_data.content_type,'x-authtoken': options.token}
  
# submit this genome to IslandViewer
response = requests.post(host+"/rest/submit/", headers=headers, data=multipart_data)
   
if not response.ok:
    response.raise_for_status()
    sys.exit()
   
decoded = response.json()
  
if decoded['status']==200:
    job_token=decoded['token']
else:
    sys.stderr.write("Error submitting genome to IslandViewer"+"\n")
    sys.exit()
    

headers={'Content-Type': "text/plain",'x-authtoken': options.token} 

# Next check job status
job_status="" 
while job_status !='Complete':
    response = requests.post(host+"/rest/job/"+job_token+"/", headers=headers)
    decoded = response.json()
    job_status=decoded['status']
    time.sleep(30)
     
# Download the Genbank including genomic island predictions, and the reordered concatenated contigs
request_status=""
while request_status !=200:
    response = requests.get(host+"/rest/job/"+job_token+"/download/genbank/", headers=headers, stream=True)   
    request_status=response.status_code
    local_filename=options.gbk
    with open(local_filename, 'wb') as f:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk: 
                f.write(chunk)
    f.close()

# Download the table summarizing genomic island predictions
request_status=""
while request_status !=200:
    response = requests.get(host+"/rest/job/"+job_token+"/download/tab/", headers=headers, stream=True)   
    request_status=response.status_code
    local_filename=options.tab
    with open(local_filename, 'wb') as f:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk: 
                f.write(chunk)
    f.close()