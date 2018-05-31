#!/usr/bin/env python3

import requests
import sys
import time
from requests_toolbelt.multipart.encoder import MultipartEncoder
from optparse import OptionParser

# Get options from the command line
parser = OptionParser()
parser.add_option("-r", "--reference", dest="reference", action="store", type="string", help="For draft genomes, the accession number of the desired reference genome for contig reordering", metavar="ACCESSION")
parser.add_option("-t", "--token", dest="token", action="store", type="string", help="Your authentication token for the API", metavar="TOKEN")
parser.add_option("-s", "--sample", dest="sample", action="store", type="string", help="The sample/genome name", metavar="SAMPLE")
parser.add_option("-i", "--indir", dest="indir", action="store", type="string", help="The directory containing the input genbank file", metavar="INDIR")
parser.add_option("-o", "--outdir", dest="outdir", action="store", type="string", help="The directory to output IslandViewer results to", metavar="OUTDIR")

(options, args) = parser.parse_args()

if options.reference == None:
    parser.error("Missing argument for --reference ")    
if options.indir == None:
    parser.error("Missing argument for --indir ") 
if options.outdir == None:
    parser.error("Missing argument for --outdir ") 
if options.token == None:
    parser.error("Missing argument for --token ")       
if options.sample == None:
    parser.error("Missing argument for --sample ")    
    
host = "http://www.pathogenomics.sfu.ca/islandviewer"



multipart_data = MultipartEncoder(
    fields={ "format_type": "GENBANK",
             'ref_accnum': options.reference,
             'genome_file': ('filename', open(options.indir+"/"+options.sample+"-genome.gbk", 'rb'), 'text/plain')}
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
    sys.exit()
    print >> sys.stderr, "Error submitting genome to IslandViewer"


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
    local_filename=options.outdir+"/"+options.sample+"_islandviewer.gbk"
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
    local_filename=options.outdir+"/"+options.sample+"_islandviewer.tbl"
    with open(local_filename, 'wb') as f:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk: 
                f.write(chunk)
    f.close()
