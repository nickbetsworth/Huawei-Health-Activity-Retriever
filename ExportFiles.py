import argparse
import ftplib
import subprocess
import re
import datetime
import sys

from pathlib import Path

TCX_CONVERTER_PATH = f'{sys.path[0]}/third-party/Huawei-TCX-Converter.py'
TEMP_DIR = f'{sys.path[0]}/tmp'
DEFAULT_OUTPUT_DIR = './output'


def _init_arg_parse():
    parser = argparse.ArgumentParser(description='Retrieves and processes activity data from Huawei Health.', conflict_handler='resolve')
    ftp_group = parser.add_argument_group('FTP Arguments')
    ftp_group.add_argument('-h', '--host', help='Hostname/IP address of FTP server', required=True)
    ftp_group.add_argument('-u', '--user', help='FTP user - leave empty for anonymous authentication', default='')
    ftp_group.add_argument('-p', '--password', help='FTP password - leave empty for anonymous authentication', default='')

    parser.add_argument('-o', '--output-dir', help=f'Output folder for processed activities. Defaults to {DEFAULT_OUTPUT_DIR}', default=DEFAULT_OUTPUT_DIR)
    parser.add_argument('-f', '--fresh', help='Clears all existing data and pulls all available data fresh from the device', action='store_true')

    return parser


def transfer_files(server, username, password):
    """
    Transfers unseen files from the server to local storage
    """

    try:
        ftp = ftplib.FTP(server)
    except ConnectionError:
        exit('Unable to communicate with ftp server')

    try:
        ftp.login(username, password)
    except ftplib.error_perm:
        exit('Unable to connect to FTP server with the given credentials')

    try:
        ftp.cwd('data/data/com.huawei.health')
    except ftplib.error_perm:
        exit('Unable to locate Huawei health directory in /data/data/com.huawei.health')

    try:
        ftp.cwd('files')
    except ftplib.error_perm:
        exit('Unable to locate Huawei files directory')

    # Create the tmp directory if it does not exist
    Path(TEMP_DIR).mkdir(exist_ok=True)

    # Get a list of existing files which have been processed in previous runs
    existing_files = [x.name for x in Path(TEMP_DIR).iterdir() if x.is_file()]

    # Get a list of all new HiTrack files which contain activity data
    new_files = list(filter(lambda f: f.startswith('HiTrack_') and f not in existing_files, ftp.nlst()))

    # Transfer the files to your local machine
    for file in new_files:
        with open(f'{TEMP_DIR}/{file}', 'wb') as fp:
            ftp.retrbinary(f'RETR {file}', fp.write)

    ftp.close()

    return new_files


def process_file(file, output_dir):
    """
    Runs the specified HiTrack file through the Huawei-TCX-Converter
    """

    p = subprocess.Popen(f'python {TCX_CONVERTER_PATH} -f {TEMP_DIR}/{file} --output_dir {output_dir}')
    p.wait()


def rename_file(file, output_dir):
    """
    Renames a .tcx file from the default 'HiTrack_xxxx' format into a more readable format:
     {Start datetime} to {End datetime}
    """

    # Extract the start and end timestamps
    search = re.search('^HiTrack_([0-9]{13})([0-9]{13})', file)
    datetime_from = timestamp_to_datetime(int(search.group(1)))
    datetime_to = timestamp_to_datetime(int(search.group(2)))

    p = Path(f'{output_dir}/{file}.tcx')
    p.replace(Path(p.parent, f'{datetime_from} to {datetime_to}{p.suffix}'))


def timestamp_to_datetime(micro_timestamp):
    date_str = datetime.datetime.fromtimestamp(micro_timestamp / 1000).replace(microsecond=0).isoformat()
    return date_str.replace(':', '_')


def clear_tmp():
    [f.unlink() for f in Path(TEMP_DIR).glob('HiTrack_*') if f.is_file()]


def main():
    parser = _init_arg_parse()
    args = parser.parse_args()

    # If the user wants to do a fresh run, clear tmp directory
    if args.fresh:
        clear_tmp()

    files = transfer_files(args.host, args.user, args.password)

    if files:
        print('Found', len(files), 'new activies', files)
    else:
        print('No new activities found')

    for file in files:
        process_file(file, args.output_dir)
        rename_file(file, args.output_dir)


if __name__ == '__main__':
    main()
