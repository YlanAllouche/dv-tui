#!/bin/bash
# Generate dynamic task data for testing refresh
# Simulates changing data by including a timestamp

TIMESTAMP=$(date +%s)
COUNT=$(( (TIMESTAMP % 5) + 3 ))  # Varies between 3-7 items

echo "["
echo "  {"
echo "    \"type\": \"work\","
echo "    \"status\": \"active\","
echo "    \"summary\": \"Task generated at $TIMESTAMP\","
echo "    \"priority\": \"high\""
echo "  },"
echo "  {"
echo "    \"type\": \"work\","
echo "    \"status\": \"pending\","
echo "    \"summary\": \"Review PR #$TIMESTAMP\","
echo "    \"priority\": \"medium\""
echo "  }"

# Add 1-3 more items based on timestamp
for i in $(seq 1 $((COUNT - 2))); do
  echo "  ,"
  echo "  {"
  echo "    \"type\": \"study\","
  echo "    \"status\": \"pending\","
  echo "    \"summary\": \"Learn topic #$i at $TIMESTAMP\","
  echo "    \"priority\": \"low\""
  echo "  }"
done

echo "]"
