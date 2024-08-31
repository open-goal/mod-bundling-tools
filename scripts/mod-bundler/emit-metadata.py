# Simple script to emit a metadata.json file with the relevant mod information
# Values are passed in as environment variables
from datetime import datetime
import json
import os


def split_comma_sep_val(str):
    if "," not in str:
        return [str]
    return str.split(",")


# Fail if the user hasn't changed anything
if (
    os.getenv("NAME") == "NAME"
    or os.getenv("DESCRIPTION") == "DESCRIPTION"
    or os.getenv("AUTHORS") == "authorName1,authorName2"
):
    print(
        "Mod metadata is just copy-pasted from the example and not actually setup, do that!"
    )
    exit(1)

metadata = {
    "schemaVersion": os.getenv("SCHEMA_VERSION"),
    "version": os.getenv("VERSION").removeprefix("v"),
    "name": os.getenv("NAME"),
    "description": os.getenv("DESCRIPTION"),
    "supportedGames": split_comma_sep_val(os.getenv("SUPPORTED_GAMES")),
    "authors": split_comma_sep_val(os.getenv("AUTHORS")),
    "tags": split_comma_sep_val(os.getenv("TAGS")),
    "publishedDate": datetime.now().isoformat(),
}
if os.getenv("WEBSITE_URL") != "":
    metadata["websiteUrl"] = os.getenv("WEBSITE_URL")

# Fail if the user hasn't changed anything
if metadata["websiteUrl"] == "https://www.example.com/this/is/optional" or metadata["websiteUrl"] == "https://www.example.com/please/change/me":
    print(
        "Mod metadata is just copy-pasted from the example and not actually setup, do that!"
    )
    exit(1)

with open("{}/metadata.json".format(os.getenv("OUT_DIR")), "w", encoding="utf-8") as f:
    print(
        "Writing the following metadata: {}".format(
            json.dumps(metadata, indent=2, ensure_ascii=False)
        )
    )
    f.write(json.dumps(metadata, indent=2, ensure_ascii=False))
