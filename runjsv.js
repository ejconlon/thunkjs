#!/usr/bin/env node

var JSV = require("../JSV").JSV;
var fs = require('fs');

var jsons = []
for (var i = 2; i < process.argv.length; ++i) {
    var filename = process.argv[i];
    var contents = fs.readFileSync(filename, 'utf8'); 
    var json = JSON.parse(contents);
    jsons.push(json);
}
    
var env = JSV.createEnvironment();
for (var j = 0; j < jsons.length - 1; ++j) {
    var schema = jsons[j];
    if (schema.id) {
	console.log("Registering "+schema.id);
	env.createSchema(schema, true, schema.id);
    } else {
	console.log("Registering <anon>");
	env.createSchema(schema, true);
    }
}

console.log("CHECKING "+process.argv[process.argv.length - 1]+" AGAINST "+
	    process.argv[process.argv.length - 2]);
var report = env.validate(jsons[jsons.length - 1], jsons[jsons.length - 2]);

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