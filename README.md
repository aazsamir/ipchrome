# ipchrome

A simple python script, to fetch channels and streams from [https://iptv-org.github.io/](https://iptv-org.github.io/), filter them for given criteria, validate connection and save as M3U8 file to be used in any IPTV player.

# Usage

```bash
python ipchrome.py \
    --allowed_languages "pol" \
    --allowed_broadcast_areas "c/PL" \
    --banned_endings ".us" ".be" ".nl" \
    --forced_endings ".pl" \
    --timeout 3 \
    --verbose
```

This will streams that are:

-   with `pol` language
-   from `c/PL` broadcast area
-   not ending with `.us`, `.be`, `.nl`
-   all that ends with `.pl`
-   with connection timeout of 3 seconds
