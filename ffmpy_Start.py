#!/usr/bin/env python

import argparse as argp
import json
import multiprocessing as mp
import os

import ffmpy_Main as Main


def validate_file(args):
    config_file = None
    if args.Settings:
        file_path = os.path.join(os.getcwd(), args.Settings)
        if os.path.exists(file_path):
            config_file = open(file_path, "r")
        else:
            print("ERROR: Settings file '{}' does not exist.".format(file_path))
    else:
        file_path = os.path.join(os.getcwd(), "Settings.json")
        if os.path.exists(file_path):
            config_file = open(file_path, "r")
        else:
            print("ERROR: Settings file '{}' does not exist.".format(file_path))
    config = json.load(config_file)
    config_file.close()
    return config


def validate_threads(threads, type, config):
    if threads:
        if threads > mp.cpu_count():
            msg = "ERROR: User specified {0} threads which is more than the number the system supports ({1}), clamping the value to the available number of threads on this system."
            print(msg.format(threads, mp.cpu_count()))
            threads = mp.cpu_count()
    else:
        if type not in config:
            print("ERROR: '{0}' key does not exist in the configuration file. Manually asking user for input...".format(type))
            threads = mp.cpu_count()
        else:
            if "threads_{0}".format(type) not in config[type]:
                print("ERROR: 'threads_{0}' key does not exist in the '{0}' section of the configuration file. Going with default value of all threads ({1})".format(type, mp.cpu_count()))
                threads = mp.cpu_count()
            else:
                try:
                    threads_int = int(config[type]["threads_{0}".format(type)])
                    if threads_int > mp.cpu_count():
                        msg = "ERROR: Configuration file specified {0} {1} threads which is more than the number the system supports, clamping the value to the available number of threads on this system ({2})."
                        print(msg.format(threads, type, mp.cpu_count()))
                        threads = mp.cpu_count()
                    else:
                        threads = threads_int
                except ValueError:
                    print("ERROR: Value {0} for 'threads_{1}' key is not an integer. Defaulting to all CPU threads ({2}).".format(config[type]["threads_{0}".format(type)], type, mp.cpu_count()))
                    threads = mp.cpu_count()
    return threads


def check_if_exists(item):
    return os.path.exists(item)


def validate_directories(dirs, config):
    def len_check(dirs_list):
        if len(dirs_list) == 0:
            return True
        else:
            return False

    should_config = False
    if dirs:
        should_config = len_check(dirs)
        if not should_config:
            msg = "ERROR: User did not specify any directories. Attempting to use configuration file's settings..."
            print(msg)
            for dir in dirs:
                ex = check_if_exists(dir)
                if not ex:
                    dirs.remove(dir)
            should_config = len_check(dirs)

    if should_config:
        if "global" not in config:
            print("ERROR: 'global' key does not exist in the configuration file. Defaulting to current directory...")
            return [].append(os.getcwd())
        else:
            if "directories".format(type) not in config["global"]:
                msg = "ERROR: 'directories' key does not exist in the 'global' section of the configuration file. Defaulting to current directory..."
                print(msg)
                return [].append(os.getcwd())
            else:
                dirs = config["global"]["directories"]
                dirs_empty = len_check(dirs)
                if dirs_empty or (len(dirs) == 1 and dirs[0].lower() == "none"):
                    msg = "ERROR: Configuration file did not specify any directories. Defaulting to current directory..."
                    print(msg)
                    return [].append(os.getcwd())
                else:
                    for dir in dirs:
                        ex = check_if_exists(dir)
                        if not ex:
                            dirs.remove(dir)
                    if len(dirs) == 0:
                        msg = "ERROR: Configuration file did not specify any directories. Defaulting to current directory..."
                        print(msg)
                        return [].append(os.getcwd())
                    return dirs
            return dirs


def validate_cache(cache, config):
    should_config = False
    if cache is not None and cache != "":
        ex = check_if_exists(cache)
        if not ex:
            should_config = len_check(cache)
    else:
        if not should_config:
            msg = "ERROR: User did not specify a cache location. Attempting to use configuration file's settings..."
            print(msg)
            if check_if_exists(cache):
                should_config = True

    if should_config:
        if "global" not in config:
            print("ERROR: 'global' key does not exist in the configuration file. Defaulting to current directory...")
            return [].append(os.getcwd())
        else:
            if "directories".format(type) not in config["global"]:
                msg = "ERROR: 'directories' key does not exist in the 'global' section of the configuration file. Defaulting to current directory..."
                print(msg)
                return [].append(os.getcwd())
            else:
                dirs = config["global"]["directories"]
                dirs_empty = len_check(dirs)
                if dirs_empty or (len(dirs) == 1 and dirs[0].lower() == "none"):
                    msg = "ERROR: Configuration file did not specify any directories. Defaulting to current directory..."
                    print(msg)
                    return [].append(os.getcwd())
                else:
                    for dir in dirs:
                        ex = check_if_exists(dir)
                        if not ex:
                            dirs.remove(dir)
                    if len(dirs) == 0:
                        msg = "ERROR: Configuration file did not specify any directories. Defaulting to current directory..."
                        print(msg)
                        return [].append(os.getcwd())
                    return dirs
            return dirs


def parse_args():
    parser = argp.ArgumentParser(description="Intelligently run ffmpeg commands on video files within given directories.", formatter_class=argp.RawTextHelpFormatter, add_help=False)

    args_optional = parser.add_argument_group("Optional arguments")
    args_optional.add_argument("-s", "--settings", dest="Settings", default="Settings.json", required=False, help="Specify different JSON file for getting settings.\n")
    args_optional.add_argument("-o", "--output-pattern", dest="Output_Pattern", required=False, help="Specify the pattern to append to the name of output files.\n")
    args_optional.add_argument("-d", "--directories", dest="Directories", nargs="+", required=False, help="Specify the directories to look for input files.\n")

    cache_help = "Specify the directory to copy the source file to and encode the output file to before copying them to the current 'source' and 'output' folders.\n"
    args_optional.add_argument("-c", "--cache", dest="Cache", required=False, help=cache_help)

    args_decode = parser.add_argument_group("Decoder arguments")
    args_decode.add_argument("-td", "--threads-decode", dest="Threads_Decode", type=int, required=False, help="Specify number of threads to use for decoding the input files.\n")
    args_decode.add_argument("-hw", "--hwaccel", dest="HWAccel", required=False, help="Specify a hardware accleration method to use.\n")
    args_decode.add_argument("-dec", "--decode_codec", dest="Decode_Codec", required=False, help="Specify the codec to use for decoding the input video.\n")

    args_encode = parser.add_argument_group("Encoder arguments")
    args_encode.add_argument("-te", "--threads-encode", dest="Threads_Encode", type=int, required=False, help="Specify number of threads to use for encoding the output files.\n")
    args_encode.add_argument("-enc", "--encode_codec", dest="Encode_Codec", required=False, help="Specify the codec to use for encoding the output video.\n")

    args_misc = parser.add_argument_group("Miscellaneous arguments")
    args_misc.add_argument("--debug", dest="Debug", action="store_true", required=False, help="Print verbose statements.\n")
    args_misc.add_argument("-v", "--version", action="version", version="%(prog)s 2020-08-16")
    args_misc.add_argument("-h", "--help", action="help", default=argp.SUPPRESS, help="Show this help message and exit.\n")

    args = parser.parse_args()

    config = validate_file(args)

    args.Threads_Decode = validate_threads(args.Threads_Decode, "decode", config)
    args.Threads_Encode = validate_threads(args.Threads_Encode, "encode", config)
    args.Directories = validate_directories(args.Directories, config)

    # print("{}".format(args))
    for k, v in vars(args).items():
        print("{0}: {1}".format(k, v))

    inp = input("Wait...")

    return (config, args.Threads_Decode, args.Threads_Encode,)


def start():
    args = parse_args()
    Main.main(args)


if __name__ == "__main__":
    start()
