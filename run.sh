#!/bin/sh

python ipchrome.py \
    --allowed_languages "pol" \
    --allowed_broadcast_areas "c/PL" \
    --banned_endings ".us" ".be" ".nl" \
    --forced_endings ".pl" \
    --merge false \
    --fetch false \
    --timeout 1 \
    --verbose