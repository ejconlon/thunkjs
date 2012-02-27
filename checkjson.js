#!/usr/bin/env node

var fs = require('fs');

for (var i = 2; i < process.argv.length; ++i) {
    var filename = process.argv[i];
    var contents = fs.readFileSync(filename, 'utf8'); 
    var json = JSON.parse(contents);
}
