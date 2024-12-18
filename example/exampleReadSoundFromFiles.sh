#! /bin/bash

if [ "$#" != 3 ] ; then echo "Usage: $1 <list-of-wav-files-in-16kHz.txt> <model.onnx>" ; exit ; fi

INPUTLIST=$1
MODEL=$2

python exampleReadSoundFromFiles.py ${INPUTLIST} ${MODEL}
