#!/usr/bin/env python

import sys
import glob
import re
import copy
import os
from os.path import join as pjoin
import json
from optparse import OptionParser

try:
    from json_schema_validator.schema import Schema
    from json_schema_validator.validator import Validator
except ImportError:
    print "Cannot load json_schema_validator. Try using the node evaluator."

def read_json(filename):
    with open(filename) as f:
        return json.loads(f.read())

def get_casemap(directory):
    schemas = glob.glob(pjoin(directory, "*.jsonschema"))
    casemap = {}
    for schema in schemas:
        name = re.match('.*?/([^/]+)\.jsonschema', schema).group(1)
        cases = glob.glob(pjoin(directory, name+"*.json"))
        casemap[schema] = cases
    return casemap

def get_manual_casemap(directory):
    manuals = glob.glob(pjoin(directory, "*.cases.txt"))
    casemap = {}
    for manual in manuals:
        with open(manual) as f:
            for line in f.readlines():
                if line.startswith("#"): continue
                k, v = [pjoin(directory, x) for x in line.strip().split()]
                globbed = glob.glob(v)
                if len(globbed):
                    if k not in casemap:
                        casemap[k] = []
                    casemap[k].extend(globbed)
    return casemap

def merge_casemaps(m1, m2):
    m3 = copy.deepcopy(m1)
    for k, vs in m2.iteritems():
        if k not in m3:
            m3[k] = []
        m3[k].extend(vs)
    return m3

def run_testcases_python(casemap):
    for schemafile, casefiles in casemap.iteritems():
        print "SCHEMA:", schemafile
        sj = read_json(schemafile)
        print sj
        schema = Schema(sj)
        for casefile in casefiles:
            print "CASE:", casefile
            cj = read_json(casefile)
            print cj
            assert Validator.validate(schema, cj)

def find_refs(js, acc=None):
    if not acc:
        acc = set()
    if type(js) == dict:
        if u'$ref' in js:
            jsr = js[u'$ref']
            if jsr[-1] != u"#": jsr = jsr + u'#'
            if jsr != u"#" and u'/schema#' and u'/hyper-schema#' not in jsr:
                acc.add(jsr)
        for val in js.itervalues():
            acc.update(find_refs(val, acc))
    return acc

def visit(ref, refs_to_ids, visited, out):
    if ref not in visited:
        visited.add(ref)
        for i in refs_to_ids.iterkeys():
            if ref in refs_to_ids[i]:
                visit(i, refs_to_ids, visited, out)
        out.append(ref)

def run_topo(refs_to_ids):
    visited = set()
    out = []
    for ref, ids in refs_to_ids.iteritems():
        if not len(ids):
            visit(ref, refs_to_ids, visited, out)
    #print "ALL", refs_to_ids.keys()
    #print "VISITED", visited
    #print "OUT", out
    return out

def toposort_refs(schemafiles):
    # for some reason hyper-schema is problematic.
    all_schemas = [x for x in schemafiles if 'schema.jsonschema' not in x]
    id_to_filename = {}
    refs_to_ids = {}
    for schemafile in all_schemas:
        print "PROCESSING", schemafile
        sj = read_json(schemafile)
        sji = sj['id']
        if (sji[-1] != "#"): sji = sji + "#"
        id_to_filename[sji] = schemafile
        id_to_refs = find_refs(sj)
        for ref in id_to_refs:
            if ref not in refs_to_ids:
                refs_to_ids[ref] = set()
            refs_to_ids[ref].add(sji)
    for i in id_to_filename.iterkeys():
        if i not in refs_to_ids:
            refs_to_ids[i] = set()
    sorted_ids = run_topo(refs_to_ids)
    return (id_to_filename[i] for i in sorted_ids)

def run_testcases_node(casemap):
    all_schemas = ' '.join(toposort_refs(casemap.iterkeys()))
    for schemafile, casefiles in casemap.iteritems():
        print "SCHEMA:", schemafile
        for casefile in casefiles:
            print "CASE:", casefile
            cmd = './runjsv.js %s %s %s' % (all_schemas, schemafile, casefile)
            assert os.system(cmd) == 0

def main(directory, use_node):
    auto_casemap = get_casemap(directory)
    manual_casemap = get_manual_casemap(directory)
    casemap = merge_casemaps(auto_casemap, manual_casemap)
    if use_node:
        run_testcases_node(casemap)
    else:
        run_testcases_python(casemap)

def parse_args():
    parser = OptionParser()
    parser.add_option("-d", "--directory", dest="directory", default="./testcases",
                      help="read test cases from DIRECTORY", metavar="DIRECTORY")
    parser.add_option("-n", "--node", dest="node", default=True, action="store_true",
                      help="use node.js validator")
    return parser.parse_args()

if __name__ == "__main__":
    options, args = parse_args()
    main(options.directory, options.node)
