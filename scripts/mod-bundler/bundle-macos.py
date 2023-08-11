import os
import shutil
import requests
import urllib.request
import zipfile
import tarfile

args = {
    "outputDir": os.getenv("outputDir"),
    "versionName": os.getenv("versionName"),
    "toolingVersion": os.getenv("toolingVersion"),
    "toolingBinaryDir": os.getenv("toolingBinaryDir"),
    "textureReplacementDir": os.getenv("textureReplacementDir"),
    "customLevelsDir": os.getenv("customLevelsDir"),
    "goalSourceDir": os.getenv("goalSourceDir"),
}

print(args)

# Create our output directory
if os.path.exists(os.path.join(args["outputDir"], "macos")):
    print(
        "Expected output directory already exists, clearing it - {}".format(
            os.path.join(args["outputDir"], "macos")
        )
    )
    os.rmdir(os.path.join(args["outputDir"], "macos"))

os.makedirs(os.path.join(args["outputDir"], "macos"), exist_ok=True)

# Download the Release
toolingVersion = args["toolingVersion"]
if toolingVersion == "latest":
    # Get the latest open-goal/jak-project release
    toolingVersion = requests.get(
        "https://api.github.com/repos/open-goal/jak-project/releases/latest"
    ).json()["tag_name"]
releaseAssetUrl = "https://github.com/open-goal/jak-project/releases/download/{}/opengoal-macos-intel-{}.tar.gz".format(
    toolingVersion, toolingVersion
)
urllib.request.urlretrieve(
    releaseAssetUrl, os.path.join(args["outputDir"], "macos", "release.tar.gz")
)

# Extract it
with tarfile.open(
    os.path.join(args["outputDir"], "macos", "release.tar.gz")
) as tar_ball:
    tar_ball.extractall(os.path.join(args["outputDir"], "macos"))
os.remove(os.path.join(args["outputDir"], "macos", "release.tar.gz"))


if args["toolingBinaryDir"] != "":
    # User is specifying the binaries themselves, let's make sure they exist
    dir = args["toolingBinaryDir"]
    if (
        not os.path.exists(os.path.join(dir, "extractor"))
        or not os.path.exists(os.path.join(dir, "goalc"))
        or not os.path.exists(os.path.join(dir, "gk"))
    ):
        print("Tooling binaries not found, expecting extractor, goalc, and gk")
        exit(1)
    # Binaries are all there, let's replace 'em
    shutil.copyfile(
        os.path.join(dir, "extractor"),
        os.path.join(args["outputDir"], "macos", "extractor"),
    )
    os.chmod(os.path.join(args["outputDir"], "macos", "extractor"), 0o775)
    shutil.copyfile(
        os.path.join(dir, "goalc"),
        os.path.join(args["outputDir"], "macos", "goalc"),
    )
    os.chmod(os.path.join(args["outputDir"], "macos", "goalc"), 0o775)
    shutil.copyfile(
        os.path.join(dir, "gk"), os.path.join(args["outputDir"], "macos", "gk")
    )
    os.chmod(os.path.join(args["outputDir"], "macos", "gk"), 0o775)

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
    os.path.join(args["outputDir"], "macos", "data", "goal_src"),
    dirs_exist_ok=True,
)

# Rezip it up and prepare it for upload
shutil.make_archive(
    "macos-intel-{}".format(args["versionName"]),
    "gztar",
    os.path.join(args["outputDir"], "macos"),
)
os.makedirs(os.path.join(args["outputDir"], "dist"), exist_ok=True)
shutil.move(
    "macos-intel-{}.tar.gz".format(args["versionName"]),
    os.path.join(
        args["outputDir"], "dist", "macos-intel-{}.tar.gz".format(args["versionName"])
    ),
)

# Cleanup
shutil.rmtree(os.path.join(args["outputDir"], "macos"))
