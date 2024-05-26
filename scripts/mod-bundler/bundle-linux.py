import os
import shutil
import requests
import urllib.request
import zipfile
import tarfile

args = {
    "outputDir": os.getenv("outputDir"),
    "versionName": os.getenv("versionName"),
    "toolingRepo": os.getenv("toolingRepo"),
    "toolingVersion": os.getenv("toolingVersion"),
    "toolingBinaryDir": os.getenv("toolingBinaryDir"),
    "copyEntireBinaryDir": os.getenv("copyEntireBinaryDir"),
    "textureReplacementDir": os.getenv("textureReplacementDir"),
    "customLevelsDir": os.getenv("customLevelsDir"),
    "customAssetsDir": os.getenv("customAssetsDir"),
    "goalSourceDir": os.getenv("goalSourceDir"),
    "gameAssetsDir": os.getenv("gameAssetsDir"),
    "decompilerConfigDir": os.getenv("decompilerConfigDir"),
}

print(args)

# Create our output directory
if os.path.exists(os.path.join(args["outputDir"], "linux")):
    print(
        "Expected output directory already exists, clearing it - {}".format(
            os.path.join(args["outputDir"], "linux")
        )
    )
    os.rmdir(os.path.join(args["outputDir"], "linux"))

os.makedirs(os.path.join(args["outputDir"], "linux"), exist_ok=True)

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
    releaseAssetUrl = f"https://github.com/{toolingRepo}/releases/download/{toolingVersion}/opengoal-linux-{toolingVersion}.tar.gz"
    urllib.request.urlretrieve(
        releaseAssetUrl, os.path.join(args["outputDir"], "linux", "release.tar.gz")
    )

    # Extract it
    with tarfile.open(
        os.path.join(args["outputDir"], "linux", "release.tar.gz")
    ) as tar_ball:
        tar_ball.extractall(os.path.join(args["outputDir"], "linux"))
    os.remove(os.path.join(args["outputDir"], "linux", "release.tar.gz"))

else: # args["toolingBinaryDir"] != "":
    # User has tooling binaries commited to repo
    dir = args["toolingBinaryDir"]

    # Verify all binaries are present
    if (
        not os.path.exists(os.path.join(dir, "extractor"))
        or not os.path.exists(os.path.join(dir, "goalc"))
        or not os.path.exists(os.path.join(dir, "gk"))
    ):
        print("Tooling binaries not found, expecting extractor, goalc, and gk")
        exit(1)

    # Binaries are all there, let's replace 'em

    if args["copyEntireBinaryDir"] != "" and (args["copyEntireBinaryDir"] == "true" or args["copyEntireBinaryDir"]):
      # user has some DLLs or something, copy entire binary dir
      shutil.copytree(
        dir,
        os.path.join(args["outputDir"], "linux"),
        dirs_exist_ok=True
      )
    else:
      # copy the 3 key binaries
      shutil.copyfile(
          os.path.join(dir, "extractor"),
          os.path.join(args["outputDir"], "linux", "extractor"),
      )
      shutil.copyfile(
          os.path.join(dir, "goalc"),
          os.path.join(args["outputDir"], "linux", "goalc"),
      )
      shutil.copyfile(
          os.path.join(dir, "gk"), os.path.join(args["outputDir"], "linux", "gk")
      )
    
    # permissions
    os.chmod(os.path.join(args["outputDir"], "linux", "extractor"), 0o775)
    os.chmod(os.path.join(args["outputDir"], "linux", "goalc"), 0o775)
    os.chmod(os.path.join(args["outputDir"], "linux", "gk"), 0o775)

# Copy-in Mod Assets
textureReplacementDir = args["textureReplacementDir"]
if os.path.exists(textureReplacementDir):
    shutil.copytree(
        textureReplacementDir,
        os.path.join(args["outputDir"], "linux", "data", "texture_replacements"),
        dirs_exist_ok=True,
    )

# Old structure
customLevelsDir = args["customLevelsDir"]
if os.path.exists(customLevelsDir):
    shutil.copytree(
        customLevelsDir,
        os.path.join(args["outputDir"], "linux", "data", "custom_levels"),
        dirs_exist_ok=True,
    )

# New structure
customAssetsDir = args["customAssetsDir"]
if os.path.exists(customAssetsDir):
    shutil.copytree(
        customAssetsDir,
        os.path.join(args["outputDir"], "linux", "data", "custom_assets"),
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
    os.path.join(args["outputDir"], "linux", "data", "goal_src"),
    dirs_exist_ok=True,
)

decompilerConfigDir = args["decompilerConfigDir"]
if os.path.exists(decompilerConfigDir):
    shutil.copytree(
        decompilerConfigDir,
        os.path.join(args["outputDir"], "linux", "data", "decompiler", "config"),
        dirs_exist_ok=True,
    )
else:
    print("Decompiler config directory not found at {}, skipping.".format(decompilerConfigDir))

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
      os.path.join(args["outputDir"], "linux", "data", "game", "assets"),
      dirs_exist_ok=True,
  )

# Rezip it up and prepare it for upload
shutil.make_archive(
    "linux-{}".format(args["versionName"]),
    "gztar",
    os.path.join(args["outputDir"], "linux"),
)
os.makedirs(os.path.join(args["outputDir"], "dist"), exist_ok=True)
shutil.move(
    "linux-{}.tar.gz".format(args["versionName"]),
    os.path.join(
        args["outputDir"], "dist", "linux-{}.tar.gz".format(args["versionName"])
    ),
)

# Cleanup
shutil.rmtree(os.path.join(args["outputDir"], "linux"))
