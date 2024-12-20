#! /bin/bash

if [ "$#" == 0 ] ; then echo "usage: $0 <INDIR> (directory with all .wav files that should be converted to 16kHz sampling rate/"; exit; fi

INDIR=$1
OUTDIR="${INDIR}_sr16000"
mkdir -p $OUTDIR


# now resample to 16000 all (and only) wav files that are named DAVOICE_*.wav   
for FILE in `find $INDIR -type f -iname "*.wav"` 
do
   OUTFILE=${FILE/$INDIR/$OUTDIR}
   echo "sox ${FILE} -r 16000 ${OUTFILE}"
   sox ${FILE} -r 16000 ${OUTFILE}
done
