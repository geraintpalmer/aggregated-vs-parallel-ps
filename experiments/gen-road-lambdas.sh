#!/bin/bash

DATASET=$1

names=( "highway-corso-unita-italia" "industrial-corso-agneli.json" "low-emissions-corso-san-maurizio" "residential-corso-unione-sovietica" )

echo '{"highway": ["45.01779", "7.66908"]}' > "/tmp/${names[0]}.json"
echo '{"industrial": ["45.02499", "7.63621"]}' > "/tmp/${names[1]}.json"
echo '{"low_emissions": ["45.07417", "7.69008"]}' > "/tmp/${names[2]}.json"
echo '{"residential": ["45.03448", "7.64825"]}' > "/tmp/${names[3]}.json"



for name in ${names[@]}; do
    echo Generating lambdas for $name
    python3 gen-real-lambdas.py $DATASET "/tmp/$name.json" "roads-lambdas/$name-lambdas.csv"
done


