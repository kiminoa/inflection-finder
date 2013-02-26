#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import getopt
import logging
import unicodecsv
import jsondoa
import itertools
from collections import defaultdict

"""
An early step in any decipherment process: Is the language inflected?
"walked" and "walking" are inflections of "walk", as is "dogs" of "dog".
Won't catch irregular inflections like tener 'to have' inflected as tiene '(s)he has' and tengo 'i have' in Spanish, but is an organized step in approaching an undeciphered writing system
"""

# Phase I - kiminoa@gmail.com

def is_subset(member, member_of):
    """
    Checks if list (member) is a subset of list (member_of)
    """
    LOG.debug(u"is_subset: is %s a subset of %s?", member, member_of)
    setm = frozenset(member)
    setmo = frozenset(member_of)
    compare_sets = setm & setmo
    if compare_sets == setm:
        LOG.debug(u"is_subset: %s is a subset of %s", member, member_of)
        return True
    else:
        return False

def add_candidate_to_file(root, inflections):
    """
    outputs to an interim file: each line is a key-value pair [ { 'root' : ['inflection', 'candidates'] } ]
    """
    root = root.encode('utf-8')
    candidate_entry = [ {root : inflections } ]
    LOG.debug(u"add_candidate_to_file: %s", candidate_entry)
    
    candidate_entry = { root : inflections }
    JSON_DOA.append(candidate_entry) # accumulate interim data to store in JSON file

def process_inflections():
    """
    inputs a file with roots and inflection candidates, then determines which inflection 
    candidates recur and are worth investigating
    
    See also "Kober's Triplets", Alice Kober's early manual work on Linear B which used a 
    similar methodology and was instrumental in the decipherment of Linear B.

    Phase I: Identify inflection candidates based on frequency of occurrence
    Phase II: Identify membership overlap between inflection candidates
    """
    # get the key-value pairs we stashed in JSON in process_clusters
    inflections = defaultdict(list) # allows append even with a new key
    candidates = JSON_DOA.retrieve()
    
    for k, v in candidates.iteritems():
        LOG.debug(u"process_inflections: key from JSON: %s", k)
        # each line contains a key-value pair [ {'root': ['list', 'of', 'inflection', 'candidates'] } ]
        for inflection in v:
            # process through the value list and build our reverse key-value dictionary
            # each inflection candidate will act as a key and the roots as its list of values
            LOG.debug(u"process_inflections: inflection from JSON: %s", inflection)
            inflections[inflection].append(k) # add root to candidate inflection
	
    print "\n\nInterim: Inflection Candidates"
    # remove candidates with only one instance, and report what remains
    for i in inflections.keys():
        # special case: one instance
        if len(inflections[i]) == 1:
            # if the inflection occurs only once, we can assume it's noise and throw it 
            # out until added data in a future run corroborates it
            LOG.debug(u"process_inflections: nixing %s with only 1 instance in %s.", i, inflections[i])
            del inflections[i]
            continue
        print u"\n%s is an inflection candidate with members: " % i,
        for x in inflections[i]:
            print u"%s" % x,
         
    print "\n\nInflection Family Candidates\n"   
    # group candidates into sensical inflection candidate families
    inflection_families = {}
    
    for x in inflections.keys():
        # Find all other inflection candidates for which this one's members is a subset
        for y in inflections.keys():
            if x == y: continue
            if len(inflections[x]) < len (inflections[y]):
        	    smaller = inflections[x]
        	    larger = inflections[y]
            else:
                smaller = inflections[y]
                larger = inflections[x]
            
            if is_subset(smaller, larger):
                LOG.debug(u"process_inflections: candidate family found via %s", str(smaller))
                smaller = frozenset(smaller)
                if smaller not in inflection_families:
                    inflection_families[smaller] = []
                if x not in inflection_families[smaller]:
                    inflection_families[smaller].append(x)
                    LOG.debug(u"process_inflections: %s added to inflection family for %s", x, str(smaller))
                if y not in inflection_families[smaller]:
                    inflection_families[smaller].append(y)
                    LOG.debug(u"process_inflections: %s added to inflection family for %s", y, str(smaller))
            
    for i in inflection_families.keys():
    	print "[%s] is a candidate inflection family via" % ", ".join(inflection_families[i]),
    	for y in list(i):
    		print y,
    	print "\n"          

def get_clusters(raw_file):
    """
    [unimplemented] inputs a file of unique morphemes, outputs clusters of potential inflections
    
    Phase I: let OpenRefine do the heavy lifting and create the file of clusters (process_clusters) from raw data
    Phase II: use Python libraries to do the clustering (get_clusters)
    """
    pass
	
def is_substring(substring, cluster):
    """
    inputs a substring to find, returns True only if found for all data in cluster
    """
    is_found = True
    for data in cluster:
        LOG.debug("is_substring: Searching %s for substring %s...", data, substring)
        is_found = is_found and substring in data
    return is_found
	
def longest_substring(cluster):
    """
    inputs a list of potential inflections, returns the longest common substring shared by all
    """
    substring = ''
    # use cluster[0] to find the longest substring in all cluster elements [1] - [n]
    # needs to be start- and end-agnostic as the longest substring could be anywhere
    # start at index 0 in this cluster and move through to len for outside loop
    for x in xrange(len(cluster[0])):
        # then create short to long substrings starting from the outer loop's index point
        for y in xrange(x, len(cluster[0])-x+1):
            candidate = cluster[0][x:y]
            LOG.debug("longest_substring: Trying %s...", candidate)
            if is_substring(candidate, cluster) and len(candidate) > len(substring):
                substring = candidate
                LOG.debug("longest_substring: A substring match has been found: %s", substring)
    logging.info("Longest substring is %s.", substring)
    return substring
	
def get_inflections(substring, cluster):
    """
    inputs the longest common substring for a cluster and returns the list of what *isn't* common in the cluster
    """
    # Need a fix for Russian Cyrillic; this is where it starts having issues (plus double-byte issues in longest_substring)
    sublen = len(substring)
    inflections = []
    for i in cluster:
        LOG.debug("get_inflections: Processing %s", i)
        startdel = i.find(substring)
        inflection = i.replace(i[startdel:startdel+sublen], '')
        # Special case: if one of the elements in the cluster *is* the longest common substring
        if inflection == '':
            inflection = "self"
        LOG.debug("get_inflections: String %s after cutting %s: %s", i, substring, inflection)
        inflections.append(inflection.encode('utf-8')) # utf-8 friendly
    return inflections

def inflection_clusters(*args):
    """
    inputs a list of potential inflections, outputs a list of potential cases
    
    For example, if we receive the list (ko-no-so, ko-no-si-jo, ko-no-si-ja, ko-no-so-de), we will receive in response (o, i-jo, i-ja, o-de) as ko-no-s is ubiquitous. 
    How do we handle edge cases where the common ground is a complete set, i.e. (ko-no-so, ko-no-so-de)? should have a way to return root + -de instead of just -de
    """
    common_substring = longest_substring(*args)
    inflection_candidates = get_inflections(common_substring, *args)
	
    LOG.debug("Inflection candidates:\n%s", inflection_candidates)
	
    # Add common string as element 1 of list (treat as key) + inflections as element 2 of list
    add_candidate_to_file(common_substring, inflection_candidates)

def process_clusters(cluster_file):
    """
    inputs a file with a list of potential inflections in a cluster on each line, processes one line at a time
    """
    cfile = open(cluster_file)
    cluster_list = []
    for line in unicodecsv.reader(cfile, encoding="utf-8"):
        for i in line:
            LOG.debug(u"process_clusters: From CSV: %s", i)
            cluster_list.append(i.strip())
        inflection_clusters(cluster_list) # discover inflection candidates for each morpheme list
        del cluster_list[:] # reinitialize for next cluster
    cfile.close()
    
    JSON_DOA.store() # save interim data to JSON

def usage():
    print "inflection_finder.py -f <csv-file> -l <loglevel:INFO|DEBUG|etc.>"
    print "inflection_finder.py --file=<csv_file> --loglevel=DEBUG|INFO|WARNING|ERROR|CRITICAL"

if __name__ == "__main__":
    """
    process cmd line args, provide usage, and execute program
    """
    # Defaults
    loglevel = "ERROR"
    clustered_file = "None"
    candidate_file = "candidate_inflections"
    global JSON_DOA
    JSON_DOA = jsondoa.JSONDOA(candidate_file) # JSON DOA for stashing interim data
    
    # Grab command line arguments
    opts, misc = getopt.getopt(sys.argv[1:], "hf:l:", ["help","file=","loglevel="])
       
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit(0)
        elif opt in ("-f", "--file"):
            clustered_file = arg
        elif opt in ("-l", "--loglevel"):
            loglevel = arg
        else:
            print "Unrecognized option."
            usage()
            sys.exit(2)

    if clustered_file == "None":
        sys.exit("File not specified.  Use -f or --file to specify; see inflection_finder.py -h.")
            
    # Set up logging
    global LOG
    LOG = logging.getLogger(__name__)
    loglvl = getattr(logging, loglevel.upper()) # convert text log level to numeric
    LOG.setLevel(loglvl) # set log level
    handler = logging.StreamHandler()
    LOG.addHandler(handler)
        
    # Let's do it.
    print "\nFiles with candidate clustered morphemes should be CSV (utf-8 is Ok)."				
    process_clusters(clustered_file)
    process_inflections()