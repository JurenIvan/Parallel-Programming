#!/bin/bash
# export MPJ_HOME=/Users/ivanjuren/Library/mpj-v0_44
echo "javac version:"
javac -version
echo "java version :"
java -version

javac -cp $MPJ_HOME/lib/mpj.jar DrunkPhilosophers/src/main/java/hr/fer/zemris/Main.java -d DrunkPhilosophers/build/classes/java/main
echo 'compiled'
cd DrunkPhilosophers/build/classes/java/main
echo 'running'
$MPJ_HOME/bin/mpjrun.sh -np $1 hr.fer.zemris.Main
