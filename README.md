# Huawei Health Activity Retriever
This script retrieves activity data from Huawei/Honor smart watches wirelessly, and converts them into a `.tcx` format.

This will enable you to upload activities from your device to services such as Strava within a single click.

**This script only supports Android devices.**

## Setup
#### Root your phone
Your phone must be rooted to enable access to Huawei's Health app data.

#### Host an FTP server on your phone
Setup an FTP server, such as  [FTPDroid](https://play.google.com/store/apps/details?id=berserker.android.apps.ftpdroid), on your phone.

Ensure that the FTP application has super user access, so that it can access the activity data.

**You will also need to mount the root folder `/`, this is typically not the default for android FTP apps.**


## Run
Example
```
python ExportFiles.py -h host -u user -p pass
```

By default, the script will only pull down new activities which it has not yet seen. To override this behaviour, and retrieve all activities stored on the watch use the flag `-f` or `--fresh`.

You can also specify the output directory for the converted files via the `-o` or `--output-dir` argument.

####
####
## Troubleshooting
#### My latest activity is not being identified
Check that your watch has synced with your Android device since you completed your activity.
#### I want to re-run the tool on activities that have already been processed
This script will only transfer and convert files which have not been processed in previous runs.

You can either run the script with the `-f` flag set, or manually clear files from the `./tmp` directory.

## Disclaimer
This has only been tested on an Honor Magic smart watch.

## Credit
This script heavily relies on https://github.com/aricooperdavis/Huawei-TCX-Converter.

An unmodified version of this script has been embedded in this project, full credit goes to the contributors of Huawei-TCX-Converter.