import datetime
import json
import os
import glob
import shutil
import tarfile
import urllib.request
import zipfile


def default_asset_prefix(platform):
    if platform == "windows":
        return "opengoal-windows"
    elif platform == "linux":
        return "opengoal-linux"
    elif platform == "macos-intel":
        return "opengoal-macos-intel"
    elif platform == "macos-arm":
        return "opengoal-macos-arm"
    else:
        return "opengoal-unknown"


def get_args(platform):
    return {
        "outputDir": os.getenv("outputDir"),
        "versionName": os.getenv("versionName"),
        "toolingRepo": os.getenv("toolingRepo"),
        "toolingReleaseAssetPrefix": os.getenv(
            "toolingReleaseAssetPrefix", default_asset_prefix(platform)
        ),
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


def create_output_dir(args, dir_name):
    if os.path.exists(os.path.join(args["outputDir"], dir_name)):
        print(
            "Expected output directory already exists, clearing it - {}".format(
                os.path.join(args["outputDir"], dir_name)
            )
        )
        os.rmdir(os.path.join(args["outputDir"], dir_name))

    os.makedirs(os.path.join(args["outputDir"], dir_name), exist_ok=True)


def download_release(args, out_folder, is_zip=True):
    toolingRepo = args["toolingRepo"]
    tooling_version = args["toolingVersion"]
    if tooling_version == "latest":
        # Get the latest release
        with urllib.request.urlopen(
            f"https://api.github.com/repos/{toolingRepo}/releases/latest"
        ) as response:
            data = json.loads(response.read().decode())
            tooling_version = data["tag_name"]
    if is_zip:
        releaseAssetUrl = f"https://github.com/{toolingRepo}/releases/download/{tooling_version}/{args['toolingReleaseAssetPrefix']}-{tooling_version}.zip"
        urllib.request.urlretrieve(
            releaseAssetUrl, os.path.join(args["outputDir"], out_folder, "release.zip")
        )
        # Extract it
        with zipfile.ZipFile(
            os.path.join(args["outputDir"], out_folder, "release.zip"), "r"
        ) as zip_ref:
            zip_ref.extractall(os.path.join(args["outputDir"], out_folder))
        os.remove(os.path.join(args["outputDir"], out_folder, "release.zip"))
    else:
        releaseAssetUrl = f"https://github.com/{toolingRepo}/releases/download/{tooling_version}/{args['toolingReleaseAssetPrefix']}-{tooling_version}.tar.gz"
        urllib.request.urlretrieve(
            releaseAssetUrl,
            os.path.join(args["outputDir"], out_folder, "release.tar.gz"),
        )
        # Extract it
        with tarfile.open(
            os.path.join(args["outputDir"], out_folder, "release.tar.gz")
        ) as tar_ball:
            tar_ball.extractall(os.path.join(args["outputDir"], out_folder))
        os.remove(os.path.join(args["outputDir"], out_folder, "release.tar.gz"))


def override_binaries_and_assets(args, out_folder, executable_extensions=True):
    extractor_binary = "extractor.exe" if executable_extensions else "extractor"
    goalc_binary = "goalc.exe" if executable_extensions else "goalc"
    gk_binary = "gk.exe" if executable_extensions else "gk"

    if args["toolingBinaryDir"] != "":
        # User is specifying the binaries themselves, let's make sure they exist
        dir = args["toolingBinaryDir"]
        if (
            not os.path.exists(os.path.join(dir, extractor_binary))
            or not os.path.exists(os.path.join(dir, goalc_binary))
            or not os.path.exists(os.path.join(dir, gk_binary))
        ):
            print("Tooling binaries not found, expecting extractor, goalc, and gk")
            exit(1)

        # Binaries are all there, let's replace 'em
        if args["copyEntireBinaryDir"] != "" and (
            args["copyEntireBinaryDir"] == "true" or args["copyEntireBinaryDir"]
        ):
            # user has some DLLs or something, copy entire binary dir
            shutil.copytree(
                dir, os.path.join(args["outputDir"], out_folder), dirs_exist_ok=True
            )
        else:
            # copy the 3 key binaries
            shutil.copyfile(
                os.path.join(dir, extractor_binary),
                os.path.join(args["outputDir"], out_folder, extractor_binary),
            )
            shutil.copyfile(
                os.path.join(dir, goalc_binary),
                os.path.join(args["outputDir"], out_folder, goalc_binary),
            )
            shutil.copyfile(
                os.path.join(dir, gk_binary),
                os.path.join(args["outputDir"], out_folder, gk_binary),
            )
        # permissions
        if out_folder != "windows":
            os.chmod(os.path.join(args["outputDir"], out_folder, extractor_binary), 0o775)
            os.chmod(os.path.join(args["outputDir"], out_folder, goalc_binary), 0o775)
            os.chmod(os.path.join(args["outputDir"], out_folder, gk_binary), 0o775)

    # Copy-in Mod Assets
    customAssetsDir = args["customAssetsDir"]
    if os.path.exists(customAssetsDir):
        shutil.copytree(
            customAssetsDir,
            os.path.join(args["outputDir"], out_folder, "data", "custom_assets"),
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
        os.path.join(args["outputDir"], out_folder, "data", "goal_src"),
        dirs_exist_ok=True,
    )

    if args["gameAssetsDir"] != "":
        gameAssetsDir = args["gameAssetsDir"]
        if not os.path.exists(gameAssetsDir):
            print("Game assets directory not found at {}!".format(gameAssetsDir))
            exit(1)
        shutil.copytree(
            gameAssetsDir,
            os.path.join(args["outputDir"], out_folder, "data", "game", "assets"),
            dirs_exist_ok=True,
        )

    decompilerConfigDir = args["decompilerConfigDir"]
    if os.path.exists(decompilerConfigDir):
        shutil.copytree(
            decompilerConfigDir,
            os.path.join(args["outputDir"], out_folder, "data", "decompiler", "config"),
            dirs_exist_ok=True,
        )
    else:
        print(
            "Decompiler config directory not found at {}, skipping.".format(
                decompilerConfigDir
            )
        )


def patch_mod_timestamp_and_version_info(args, out_folder):
    try:
        mod_settings_files = glob.glob(f"{args['outputDir']}/{out_folder}/data/goal_src/**/mod-settings.gc", recursive=True)
        for settings_file_path in mod_settings_files:
            file = open(settings_file_path, "r")
            file_data = file.read()
            file.close()
            # Check if the placeholder string is present in the file
            if "%MODVERSIONPLACEHOLDER%" in file_data:
                # Replace the placeholder string with the version and date string
                version_str = (
                    args["versionName"]
                    + " "
                    + datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
                )
                file_data = file_data.replace("%MODVERSIONPLACEHOLDER%", version_str)
                # Write the updated content back to the mod-settings
                file = open(settings_file_path, "w")
                file.write(file_data)
                file.close()
                print(
                    f"String %MODVERSIONPLACEHOLDER% replaced with '{version_str}' in the file."
                )
            else:
                print(f"Couldn't find %MODVERSIONPLACEHOLDER% in the file.")
    except Exception as e:
        print(
            f"Something went wrong trying to replace placeholder text with mod version info:"
        )
        print(e)

def finalize_bundle(args, out_folder, is_zip=True):
    if is_zip:
        shutil.make_archive(
            f"{out_folder}-{args['versionName']}",
            "zip",
            os.path.join(args["outputDir"], out_folder),
        )
        os.makedirs(os.path.join(args["outputDir"], "dist"), exist_ok=True)
        shutil.move(
            f"{out_folder}-{args['versionName']}.zip",
            os.path.join(
                args["outputDir"], "dist", f"{out_folder}-{args['versionName']}.zip"
            ),
        )
    else:
        shutil.make_archive(
            f"{out_folder}-{args['versionName']}",
            "gztar",
            os.path.join(args["outputDir"], out_folder),
        )
        os.makedirs(os.path.join(args["outputDir"], "dist"), exist_ok=True)
        shutil.move(
            f"{out_folder}-{args['versionName']}.tar.gz",
            os.path.join(
                args["outputDir"], "dist", f"{out_folder}-{args['versionName']}.tar.gz"
            ),
        )
    # Cleanup
    shutil.rmtree(os.path.join(args["outputDir"], out_folder))
