#!/usr/bin/env python

import json
from json_schema_validator.schema import Schema
from json_schema_validator.validator import Validator

import glob
import re
from os.path import join as pjoin

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

def run_testcases(casemap):
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

def main(directory):
    casemap = get_casemap(directory)
    run_testcases(casemap)

if __name__ == "__main__":
    main('./testcases')
