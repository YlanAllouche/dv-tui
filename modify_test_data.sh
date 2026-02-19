#!/bin/bash
# Script to modify test_data.json for testing file refresh
# This simulates external changes to the file

TIMESTAMP=$(date +%s)
RANDOM_STATUS=$((TIMESTAMP % 2))

if [ "$RANDOM_STATUS" -eq 0 ]; then
    STATUS="completed"
else
    STATUS="pending"
fi

cat > test_data.json <<EOF
[
  {
    "type": "work",
    "status": "$STATUS",
    "summary": "Modified at $TIMESTAMP",
    "priority": "high"
  },
  {
    "type": "work",
    "status": "pending",
    "summary": "Review PR #$TIMESTAMP",
    "priority": "medium"
  },
  {
    "type": "study",
    "status": "active",
    "summary": "Learn patterns #$TIMESTAMP",
    "priority": "low"
  }
]
EOF

echo "Modified test_data.json at $(date)"
