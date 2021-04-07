#!/bin/bash

if [ $# -eq 0 ]
  then
    echo "No arguments supplied"
    exit
fi

export MPJ_HOME=/Users/ivanjuren/Library/mpj-v0_44
javac -version
java -version

echo 'Compiling...'
javac -cp $MPJ_HOME/lib/mpj.jar DrunkPhilosophers/src/main/java/hr/fer/zemris/Philosopher.java -d DrunkPhilosophers/build/classes/java/main
echo 'Compiled!'
cd DrunkPhilosophers/build/classes/java/main || echo "FAILED!!!"
echo 'running ...'
$MPJ_HOME/bin/mpjrun.sh -np $1 hr.fer.zemris.Philosopher
