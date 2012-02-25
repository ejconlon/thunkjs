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

def run_testcases_node(casemap):
    for schemafile, casefiles in casemap.iteritems():
        print "SCHEMA:", schemafile
        for casefile in casefiles:
            print "CASE:", casefile
            assert os.system('./runjsv.js %s %s' % (schemafile, casefile)) == 0

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
