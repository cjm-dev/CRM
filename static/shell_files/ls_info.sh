#!/bin/bash

#result=$(/bin/ls \
#		| /usr/bin/awk -F: '{print "\"file_name \": \""$1"\"," }	'\
#		)

n=0
result=$(
for i in $(/bin/ls); do
  if [ "$n" -eq 4 ]
  then
    break
  fi

  echo -n "\"filename_$n\": \" $i\", ";
 
  ((n+=1))
done|sed 's/, $//');
echo "{" $result "}"
