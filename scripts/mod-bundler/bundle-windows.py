import os
import shutil
import requests
import urllib.request
import zipfile
import datetime

args = {
    "outputDir": os.getenv("outputDir"),
    "versionName": os.getenv("versionName"),
    "toolingRepo": os.getenv("toolingRepo"),
    "toolingVersion": os.getenv("toolingVersion"),
    "toolingBinaryDir": os.getenv("toolingBinaryDir"),
    "copyEntireBinaryDir": os.getenv("copyEntireBinaryDir"),
    "textureReplacementDir": os.getenv("textureReplacementDir"),
    "customLevelsDir": os.getenv("customLevelsDir"),
    "goalSourceDir": os.getenv("goalSourceDir"),
    "gameAssetsDir": os.getenv("gameAssetsDir"),
    "decompilerConfigDir": os.getenv("decompilerConfigDir"),
}

print(args)

# Create our output directory
if os.path.exists(os.path.join(args["outputDir"], "windows")):
    print(
        "Expected output directory already exists, clearing it - {}".format(
            os.path.join(args["outputDir"], "windows")
        )
    )
    os.rmdir(os.path.join(args["outputDir"], "windows"))

os.makedirs(os.path.join(args["outputDir"], "windows"), exist_ok=True)

# Locate tooling binaries
if args["toolingBinaryDir"] is None or args["toolingBinaryDir"] == "":
   # User doesn't have tooling binaries committed to repo, so download release
    toolingRepo = args["toolingRepo"]
    toolingVersion = args["toolingVersion"]
    if toolingVersion == "latest":
        # Get the latest release
        toolingVersion = requests.get(
            f"https://api.github.com/repos/{toolingRepo}/releases/latest"
        ).json()["tag_name"]
    releaseAssetUrl = f"https://github.com/{toolingRepo}/releases/download/{toolingVersion}/opengoal-windows-{toolingVersion}.zip"
    urllib.request.urlretrieve(
        releaseAssetUrl, os.path.join(args["outputDir"], "windows", "release.zip")
    )

    # Extract it
    with zipfile.ZipFile(
        os.path.join(args["outputDir"], "windows", "release.zip"), "r"
    ) as zip_ref:
        zip_ref.extractall(os.path.join(args["outputDir"], "windows"))
    os.remove(os.path.join(args["outputDir"], "windows", "release.zip"))

else: # args["toolingBinaryDir"] != "":
    # User has tooling binaries commited to repo
    dir = args["toolingBinaryDir"]

    # Verify all binaries are present
    if (
        not os.path.exists(os.path.join(dir, "extractor.exe"))
        or not os.path.exists(os.path.join(dir, "goalc.exe"))
        or not os.path.exists(os.path.join(dir, "gk.exe"))
    ):
        print(
            "Tooling binaries not found, expecting extractor.exe, goalc.exe, and gk.exe"
        )
        exit(1)

    # Binaries are all there, let's replace 'em

    if args["copyEntireBinaryDir"] != "" and (args["copyEntireBinaryDir"] == "true" or args["copyEntireBinaryDir"]):
      # user has some DLLs or something, copy entire binary dir
      shutil.copytree(
        dir,
        os.path.join(args["outputDir"], "windows"),
        dirs_exist_ok=True
      )
    else:
      # copy the 3 key binaries
      shutil.copyfile(
          os.path.join(dir, "extractor.exe"),
          os.path.join(args["outputDir"], "windows", "extractor.exe"),
      )
      shutil.copyfile(
          os.path.join(dir, "goalc.exe"),
          os.path.join(args["outputDir"], "windows", "goalc.exe"),
      )
      shutil.copyfile(
          os.path.join(dir, "gk.exe"),
          os.path.join(args["outputDir"], "windows", "gk.exe")
      )

# Copy-in Mod Assets
textureReplacementDir = args["textureReplacementDir"]
if os.path.exists(textureReplacementDir):
    shutil.copytree(
        textureReplacementDir,
        os.path.join(args["outputDir"], "windows", "data", "texture_replacements"),
        dirs_exist_ok=True,
    )

customLevelsDir = args["customLevelsDir"]
if os.path.exists(customLevelsDir):
    shutil.copytree(
        customLevelsDir,
        os.path.join(args["outputDir"], "windows", "data", "custom_levels"),
        dirs_exist_ok=True,
    )

goalSourceDir = args["goalSourceDir"]
if not os.path.exists(goalSourceDir):
    print(
        "Goal source directory not found at {}, not much of a mod without that!".format(
            goalSourceDir
        )
    )
    exit(1)
shutil.copytree(
    goalSourceDir,
    os.path.join(args["outputDir"], "windows", "data", "goal_src"),
    dirs_exist_ok=True,
)

if args["gameAssetsDir"] != "":
  gameAssetsDir = args["gameAssetsDir"]
  if not os.path.exists(gameAssetsDir):
      print(
          "Game assets directory not found at {}!".format(
              gameAssetsDir
          )
      )
      exit(1)
  shutil.copytree(
      gameAssetsDir,
      os.path.join(args["outputDir"], "windows", "data", "game", "assets"),
      dirs_exist_ok=True,
  )

decompilerConfigDir = args["decompilerConfigDir"]
if os.path.exists(decompilerConfigDir):
    shutil.copytree(
        decompilerConfigDir,
        os.path.join(args["outputDir"], "windows", "data", "decompiler", "config"),
        dirs_exist_ok=True,
    )
else:
    print("Decompiler config directory not found at {}, skipping.".format(decompilerConfigDir))

# Replace placeholder text with mod version and timestamp
try:
  path = os.path.join(args["outputDir"], "windows", "data", "goal_src", "jak1", "engine", "mods", "mod-settings.gc")
  file = open(path, "r")
  file_data = file.read()
  file.close()

  # Check if the placeholder string is present in the file
  if "%MODVERSIONPLACEHOLDER%" in file_data:
    # Replace the placeholder string with the version and date string
    version_str = args["versionName"] + " " + datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    file_data = file_data.replace("%MODVERSIONPLACEHOLDER%", version_str)

    # Write the updated content back to the mod-settings
    file = open(path, "w")
    file.write(file_data)
    file.close()
    print(f"String %MODVERSIONPLACEHOLDER% replaced with '{version_str}' in the file.")
  else:
    print(f"Couldn't find %MODVERSIONPLACEHOLDER% in the file.")
except Exception as e:
  print(f"Something went wrong trying to replace placeholder text with mod version info:")
  print(e)

# Rezip it up and prepare it for upload
shutil.make_archive(
    "windows-{}".format(args["versionName"]),
    "zip",
    os.path.join(args["outputDir"], "windows"),
)
os.makedirs(os.path.join(args["outputDir"], "dist"), exist_ok=True)
shutil.move(
    "windows-{}.zip".format(args["versionName"]),
    os.path.join(
        args["outputDir"], "dist", "windows-{}.zip".format(args["versionName"])
    ),
)

# Cleanup
shutil.rmtree(os.path.join(args["outputDir"], "windows"))
