#!/usr/bin/env bash

if [ -z "${STAT_FILE}" ] || [ -z "${SEARCH_STR}" ]
then
  echo Please provide STAT_FILE and SEARCH_STR envirnoment variables.
  exit 1
fi

truncated_size=$(grep -aob "${SEARCH_STR}" "${STAT_FILE}" | grep -Eo "^[0-9]+") && truncate -s $truncated_size "${STAT_FILE}"
