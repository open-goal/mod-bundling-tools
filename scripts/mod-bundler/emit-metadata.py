# Simple script to emit a metadata.json file with the relevant mod information
# Values are passed in as environment variables
from datetime import datetime
import json
import os

def split_comma_sep_val(str):
    if "," not in str:
        return [str]
    return str.split(",")

metadata = {
    "schemaVersion": os.getenv("SCHEMA_VERSION"),
    "version": os.getenv("VERSION"),
    "name": os.getenv("NAME"),
    "description": os.getenv("DESCRIPTION"),
    "authors": split_comma_sep_val(os.getenv("AUTHORS")),
    "tags": split_comma_sep_val(os.getenv("TAGS")),
    "publishedDate": datetime.now().isoformat()
}
if os.getenv("WEBSITE_URL") != "":
    metadata["websiteUrl"] = os.getenv("WEBSITE_URL")

with open("%s/metadata.json".format(os.getenv("OUT_DIR")), "w", encoding="utf-8") as f:
    f.write(json.dumps(metadata, indent=2, ensure_ascii=False))
