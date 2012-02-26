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
    if (!schema.id) {
	console.log("ERROR: need id in "+process.argv[2+j])
	process.exit(1);
    } else if (!schema["$schema"]) {
	console.log("ERROR: need $schema in "+process.argv[2+j])
	process.exit(1);
    } else {
	console.log("Registering "+schema.id);
	env.createSchema(schema, undefined, schema.id);
    }
}

var target_name = process.argv[process.argv.length - 1];
var target_instance = jsons[jsons.length - 1];
var target_id = target_instance["$schema"];
if (!target_id) {
    console.log("ERROR: need $schema in "+target_name);
    process.exit(1);
}

console.log("CHECKING "+target_name+" AGAINST "+target_id);

var target_schema = env.findSchema(target_id);
var report = target_schema.validate(target_instance);

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