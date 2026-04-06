#!/bin/bash

function test() {
    echo Testing $1
    curl http://localhost:5000/address/$1
    echo
    curl http://localhost:5000/weather/$1
    echo
    curl http://localhost:5000/range/$1
    echo
    echo
}

site1="google.com"
site2="walmart.com"
site3="amazon.com"

test $site1
test $site2
test $site3
test $site1