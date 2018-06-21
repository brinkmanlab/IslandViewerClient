#!/usr/bin/env python3

import requests
import re
import os
import sys
import time
import csv
import json
from operator import itemgetter
from Bio import SeqIO
from subprocess import call # subprocess preferred to using os.system()

from requests_toolbelt.multipart.encoder import MultipartEncoder
from optparse import OptionParser

# Get options from the command line
parser = OptionParser()
parser.add_option("--token", dest="token", action="store", type="string", help="Your authentication token for the API. This is found under'JOBS' > 'HTTP API Token' when you login at www.pathogenomics.sfu.ca/islandviewer and is valid for 30 days before having to be refreshed.", metavar="TOKEN")

(options, args) = parser.parse_args()


if options.token == None:
    parser.error("Missing argument for --token ")       
 
host = "http://pathogenomics.sfu.ca/islandviewer"
 
 
 # open file handle for choices
choices=open('choices.txt','w')

 # open properties file handle for messages_en.properties
properties=open('islandviewer_messages_en.properties','w')

properties.write("pipeline.title.IslandViewerClient=IslandViewer Genomic Island Prediction Pipeline\n")
properties.write("pipeline.h1.IslandViewerClient=IslandViewer Genomic Island Prediction\n\n")

properties.write("workflow.islandviewerclient.title=IslandViewer Genomic Island Prediction\n")
properties.write("workflow.islandviewerclient.description=IslandViewer is a computational tool that integrates four different genomic island prediction methods: IslandPick, IslandPath-DIMOB, SIGI-HMM, and Islander.\n\n")

properties.write("pipeline.parameters.modal-title.islandviewerclient=IslandViewer Pipeline Parameters\n")
properties.write("pipeline.parameters.islandviewerclient.islandviewerclient-accession=RefSeq Accession (Reference)\n")
properties.write("pipeline.parameters.islandviewerclient.islandviewerclient-token=Authentication Token\n")
properties.write("pipeline.parameters.islandviewerclient.read-merge-min-overlap=The minimum overlap of paired reads to merge.\n")
properties.write("pipeline.parameters.islandviewerclient.read-merge-max-overlap=The maximum overlap of paired reads to merge.\n")
properties.write("pipeline.parameters.islandviewerclient.assembly-kmers=Comma-separated k-mer values to use for assembly with SPAdes\n")
properties.write("pipeline.parameters.islandviewerclient.assembly-contig-min-length=Minimum contig length to keep from an assembly.\n")
properties.write("pipeline.parameters.islandviewerclient.assembly-contig-min-coverage-ratio=The minimum coverage ratio compared to the average coverage for a contig to be included.\n")
properties.write("pipeline.parameters.islandviewerclient.assembly-contig-min-repeat-coverage-ratio=The minimum coverage ratio compared to the average coverage for a contig to be considered a repeat.\n")
properties.write("pipeline.parameters.islandviewerclient.assembly-contig-min-length-coverage-calculation=The minimum length of a contig to be used for calculating the average coverage.\n")
properties.write("pipeline.parameters.islandviewerclient.annotation-similarity-e-value-cutoff=The e-value cutoff for annotation with Prokka.\n")


# Next get the name of the reference genome used

headers={'Content-Type': "text/plain",'x-authtoken': options.token} 
response = requests.post(host+"/rest/genomes/", headers=headers)
decoded = response.json()

tab=open('tab.txt','w')
for i in decoded:
    key=i['ref_accnum']
    value=i['name']
    tab.write(key+"\t"+value+"\n")
tab.close()

reader = csv.reader(open("tab.txt"), delimiter="\t")
for line in sorted(reader, key=itemgetter(1)):
    
    
    key=line[0]
    key=re.sub("\.\d+$","",key)
    value=line[1]
    print(key+"\t"+value)
    choices.write("<choice name=\""+key+"\" value=\""+line[0]+"\"/>\n")
    properties.write("pipeline.parameters.islandviewerclient.islandviewerclient-accession."+key+"="+value+"\n")


