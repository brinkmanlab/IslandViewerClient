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
parser.add_option("-a", "--accession", dest="accession", action="store", type="string", help="Accession is the RefSeq accession for the desired reference genome used in the contig reordering step (mandatory for draft genomes)", metavar="ACCESSION")
parser.add_option("-t", "--token", dest="token", action="store", type="string", help="Your authentication token for the API. This is found under'JOBS' > 'HTTP API Token' when you login at www.pathogenomics.sfu.ca/islandviewer and is valid for 30 days before having to be refreshed.", metavar="TOKEN")
parser.add_option("-g", "--genbank", dest="genbank", action="store", type="string", help="Name of the genbank file used for input to IslandViewer.", metavar="GENBANK")
parser.add_option("-i", "--indir", dest="indir", action="store", type="string", help="The directory containing the genbank file used for input.", metavar="INDIR")
parser.add_option("-o", "--outdir", dest="outdir", action="store", type="string", help="The directory to output IslandViewer results to.", metavar="OUTDIR")

(options, args) = parser.parse_args()

if options.accession == None:
    parser.error("Missing argument for --accession ")    
if options.indir == None:
    parser.error("Missing argument for --indir ") 
if options.outdir == None:
    parser.error("Missing argument for --outdir ") 
if options.token == None:
    parser.error("Missing argument for --token ")       
if options.genbank == None:
    parser.error("Missing argument for --genbank ")    

if not os.path.isdir(options.indir):
    sys.stderr.write("Could not find input directory: "+options.indir+"\n")
    sys.exit()

if not os.path.isdir(options.outdir):
    sys.stderr.write("Could not find output directory: "+options.outdir+"\n")
    sys.exit()

if not os.path.isfile(options.indir+"/"+options.genbank):
    sys.stderr.write("Could not find file '"+options.genbank+"' in input directory '"+ options.indir + "'\n")
    sys.exit()
    
host = "http://www.pathogenomics.sfu.ca/islandviewer"




multipart_data = MultipartEncoder(
    fields={ "format_type": "GENBANK",
             'ref_accnum': options.accession,
             'genome_file': ('filename', open(options.indir+"/"+options.genbank, 'rb'), 'text/plain')}
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
    
# Strip extension from the genbank file name
samplename=re.sub("\.\w+$","",options.genbank)

headers={'Content-Type': "text/plain",'x-authtoken': options.token} 

# Next check job status
job_status="" 
while job_status !='Complete':
    response = requests.post(host+"/rest/job/"+job_token+"/", headers=headers)
    decoded = response.json()
    job_status=decoded['status']
    time.sleep(30)
    print(job_status+"\n")
     
# Download the Genbank including genomic island predictions, and the reordered concatenated contigs
request_status=""
while request_status !=200:
    response = requests.get(host+"/rest/job/"+job_token+"/download/genbank/", headers=headers, stream=True)
   
    request_status=response.status_code
    local_filename=options.outdir+"/"+samplename+"_islandviewer.gbk"
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
    local_filename=options.outdir+"/"+samplename+"_islandviewer.tbl"
    with open(local_filename, 'wb') as f:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk: 
                f.write(chunk)
    f.close()
