#!/usr/bin/env node

var JSV = require("../JSV").JSV;
var fs = require('fs');

var schema_file = process.argv[2];
var json_file = process.argv[3];

console.log("Loading "+schema_file+" "+json_file);

var schema_contents = fs.readFileSync(schema_file, 'utf8'); 
var schema = JSON.parse(schema_contents); 

var json_contents = fs.readFileSync(json_file, 'utf8'); 
var json = JSON.parse(json_contents); 

var env = JSV.createEnvironment();
var report = env.validate(schema, json);

if (report.errors.length === 0) {
    //JSON is valid against the schema
    console.log("PASS");
} else {
    console.log("FAIL:");
    report.errors.forEach(function(error) {
	console.log(error);
    });
}

process.exit(report.errors.length);