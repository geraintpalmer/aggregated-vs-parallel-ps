#!/bin/bash - 
#===============================================================================
#
#          FILE: exec_PDSCH_PUSCH.sh
# 
#         USAGE: ./exec_PDSCH_PUSCH.sh 
# 
#   DESCRIPTION: 
# 
#       OPTIONS: ---
#  REQUIREMENTS: ---
#          BUGS: ---
#         NOTES: ---
#        AUTHOR: YOUR NAME (), 
#  ORGANIZATION: 
#       CREATED: 20/12/24 13:46
#      REVISION:  ---
#===============================================================================

set -o nounset                              # Treat unset variables as an error

min_SNRIn=0
max_SNRIn=20
MCS='256QAM'
NFrames=40
SCS=60 # kHz
NSizeGrid=138 # [RBs] with mu=2 this corresponds to 100MHz (half the available BW in Italy)



######################
## PDSCH simulation ##
######################

logPDSCH='/tmp/pdsch.log'
outPDSCH='pdsch-result.json'
echo "" > $outPDSCH

# Exec PDSCH sweep
cd NewRadioPDSCHThroughputExample
~/Documentos/Matlab_R2023a/bin/matlab -nodisplay\
    -logfile $logPDSCH -nosplash -nodesktop\
    -r "issuePDSCH($min_SNRIn,$max_SNRIn,$NSizeGrid,$SCS,'$MCS',$NFrames); quit;"


# Get the obtained throughputs
pdsch_th="";
for th in `grep "Throughput(Mb" $logPDSCH | cut -d= -f2`; do
    pdsch_th="$pdsch_th, $th";
done

# Get the obtained SNRs
pdsch_snr=""
for snr in `grep -oe "[0-9]\+dB" $logPDSCH | cut -dd -f1`; do
    pdsch_snr="$pdsch_snr, $snr"
done


pdsch_max_reps=""
for max_rep in `grep repetitions $logPDSCH | cut -d: -f2`; do
    pdsch_max_reps="$pdsch_max_reps, $max_rep"
done

echo throughputs: $pdsch_th
echo SNRs: $pdsch_snr
echo max_reps: $pdsch_max_reps

# Create the PDSCH JSON with the results
pdsch_json="{"
pdsch_json=$pdsch_json"\"snrs\": ["`echo $pdsch_snr | cut -d, -f2-`"],"
pdsch_json=$pdsch_json"\"max_reps\": ["`echo $pdsch_max_reps | cut -d, -f2-`"],"
pdsch_json=$pdsch_json"\"throughput\": ["`echo $pdsch_th | cut -d, -f2-`"],"
pdsch_json=$pdsch_json"\"NFrames\": $NFrames,"
pdsch_json=$pdsch_json"\"MCS\": \"$MCS\","
pdsch_json=$pdsch_json"\"SCS\": $SCS,"
pdsch_json=$pdsch_json"\"NSizeGrid\": $NSizeGrid"
pdsch_json="$pdsch_json}"
echo $pdsch_json >> ../$outPDSCH




######################
## PUSCH simulation ##
######################

logPUSCH='/tmp/pusch.log'
outPUSCH='pusch-result.json'
echo "" > $outPUSCH

# Exec PUSCH sweep
cd ../NewRadioPUSCHThroughputExample
~/Documentos/Matlab_R2023a/bin/matlab -nodisplay\
    -logfile $logPUSCH -nosplash -nodesktop\
    -r "issuePUSCH($min_SNRIn,$max_SNRIn,$NSizeGrid,$SCS,'$MCS',$NFrames); quit;"


# Get the obtained throughputs
pusch_th="";
for th in `grep "Throughput(Mb" $logPUSCH | cut -d= -f2`; do
    pusch_th="$pusch_th, $th";
done

# Get the obtained SNRs
pusch_snr=""
for snr in `grep -oe "[0-9]\+dB" $logPUSCH | cut -dd -f1`; do
    pusch_snr="$pusch_snr, $snr"
done


pusch_max_reps=""
for max_rep in `grep repetitions $logPUSCH | cut -d: -f2`; do
    pusch_max_reps="$pusch_max_reps, $max_rep"
done

echo throughputs: $pusch_th
echo SNRs: $pusch_snr
echo max_reps: $pusch_max_reps

# Create the PUSCH JSON with the results
pusch_json="{"
pusch_json=$pusch_json"\"snrs\": ["`echo $pusch_snr | cut -d, -f2-`"],"
pusch_json=$pusch_json"\"max_reps\": ["`echo $pusch_max_reps | cut -d, -f2-`"],"
pusch_json=$pusch_json"\"throughput\": ["`echo $pusch_th | cut -d, -f2-`"],"
pusch_json=$pusch_json"\"NFrames\": $NFrames,"
pusch_json=$pusch_json"\"MCS\": \"$MCS\","
pusch_json=$pusch_json"\"SCS\": $SCS,"
pusch_json=$pusch_json"\"NSizeGrid\": $NSizeGrid"
pusch_json="$pusch_json}"
echo $pusch_json >> ../$outPUSCH
