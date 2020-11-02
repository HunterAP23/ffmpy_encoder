import os
import ffmpy
import shlex
import time
import shutil
from pymediainfo import MediaInfo

class EK_Logger:
    def __init__(self, log_file):
        self.my_log = log_file

    def print_both(self, phrase):
        print(str(phrase))
        self.my_log.write(str(phrase))


# Returns False if file is not a video.
# Returns True if file is a video.
def check_file(filename, my_log):
    file_info = MediaInfo.parse(filename)
    for track in file_info.tracks:
        if track.track_type == "Video":
            my_log.print_both("File is confirmed as video. Adding to file list.")
            tmp_name = filename.split(".")
            exported_name = tmp_name[0] + "_CRF14_HEVC.mp4"
            my_log.print_both("exported_name is " + str(exported_name))
            return (True, exported_name)
    my_log.print_both("Skipping non-video file " + str(filename))
    return (False, None)


def get_codec(filename):
    file_info = MediaInfo.parse(filename)
    for track in file_info.tracks:
        if track.track_type == "Video":
            return track.format


def main(args):
    overall_time_start = time.time()
    file_list = []
    log_file = None
    if os.path.isfile("Master.log"):
        log_file = open("Master.log", "a")
    else:
        log_file = open("Master.log", "w")
    my_log = EK_Logger(log_file)

    if not os.path.exists("source"):
        os.makedirs("source")

    if not os.path.exists("output"):
        os.makedirs("output")

    search_path = ""

    for root, directories, filenames in os.walk(os.getcwd()):
        for filename in filenames:
            root_file = os.path.join(os.getcwd(), filename)
            if os.path.exists(root_file) and os.path.isfile(root_file):
                my_log.print_both(os.path.join(root, filename))
                my_log.print_both("Checking if file '" + str(filename) + "' is a video file.")

                file_check = check_file(filename, my_log)
                if file_check[0] is False:
                    my_log.print_both("-" * 80 + "\n")
                    continue
                else:
                    file_list.append([filename, file_check[1], root])
                    my_log.print_both("-" * 80)

    for vid in file_list:
        my_log.print_both("Removing and apostrophees and quotes from file names.")
        while "'" in vid[0]:
            new_filename = vid[0].replace("'", "")
            os.rename(vid[0], new_filename)
            vid[0] = vid[0].replace("'", "")
        while '"' in vid[0]:
            new_filename = vid[0].replace('"', '')
            os.rename(vid[0], new_filename)
            vid[0] = vid[0].replace('"', '')

        while "'" in vid[1]:
            new_filename = vid[1].replace("'", "")
            os.rename(vid[1], new_filename)
            vid[1] = vid[1].replace("'", "")
        while '"' in vid[1]:
            new_filename = vid[1].replace('"', '')
            os.rename(vid[1], new_filename)
            vid[1] = vid[1].replace('"', '')

        my_log.print_both("Filename is now " + str(vid[0]))

        log_name = str(vid[1]).replace("_COMP.mp4", ".log")
        env_path = str(vid[2]) + "\\" + str(log_name)

        my_log.print_both("vid[0]: {0}".format(vid[0]))
        my_log.print_both("vid[1]: {0}".format(vid[1]))
        my_log.print_both("vid[2]: {0}".format(vid[2]))

        my_log.print_both("log_name: {0}".format(log_name))
        my_log.print_both("env_path: {0}".format(env_path))

        inp = input("Wait...")

        if ("FFREPORT" in os.environ):
            del os.environ["FFREPORT"]
        os.environ["FFREPORT"] = str("file=" + str(repr(env_path)))
        # my_log.print_both(os.environ["FFREPORT"])

        file_codec = get_codec(vid[0])

        my_log.print_both("Source file codec is {0}.".format(file_codec))
        # Beginning of the encoding commands
        encoder_commands = []

        tmp_commands = "-hide_banner -report -threads 0 -probesize 5000000 -analyzeduration 50000000 -hwaccel auto "
        if file_codec == "HEVC":
            tmp_commands += "-c:v hevc_cuvid "
        elif file_codec == "AVC":
            tmp_commands += "-c:v h264_cuvid "
        elif file_codec == "VP9":
            tmp_commands += "-c:v vp9_cuvid "
        tmp_commands += "-i " + repr(vid[0]) + " -c:v libx265 -preset medium -threads 0 -crf 14 -c:a copy -max_muxing_queue_size 2048 -f mp4 "

        my_log.print_both(tmp_commands)
        inp = input("Wait...")

        tmp_commands = shlex.split(tmp_commands)
        for i in range(0, len(tmp_commands), 1):
            encoder_commands.append(tmp_commands[i])

        ffmpeg_run = ffmpy.FFmpeg(
            executable=r"D:\Downloads\CompTools\Media\ffmpeg\bin\ffmpeg.exe",
            outputs={
                str(vid[1]): encoder_commands
            }
        )

        my_log.print_both("ffmpeg_run.cmd: \n")
        my_log.print_both(str(ffmpeg_run.cmd) + "\n")
        inp = input("Wait...")

        encoding_time_start = time.time()
        ffmpeg_run.run()
        encoding_time_end = time.time()

        inp = input("Wait...")

        my_log.print_both("Encoding time for " + str(vid[0]) + " was " + str(encoding_time_end - encoding_time_start) + " seconds.\n")
        my_log.print_both("Moving files.")
        my_log.print_both("Moving " + str(vid[0]) + " to " + str(vid[2]) + "\\" + "source" + "\\" + str(vid[0]))
        shutil.move(vid[0], str(vid[2]) + "\\" + "source" + "\\" + str(vid[0]))
        my_log.print_both("Moving " + str(vid[1]) + " to " + str(vid[2]) + "\\" + "output" + "\\" + str(vid[1]))
        shutil.move(vid[1], str(vid[2]) + "\\" + "output" + "\\" + str(vid[1]))
        my_log.print_both("Moving " + str(log_name) + " to " + str(vid[2]) + "\\" + "output" + "\\" + str(log_name))
        shutil.move(log_name, str(vid[2]) + "\\" + "output" + "\\" + str(log_name))
        my_log.print_both("-" * 80 + "\n")
        inp = input("Wait...")

    overall_time_end = time.time()
    my_log.print_both("Overall time for the program was " + str(overall_time_end - overall_time_start) + " seconds.")
    my_log.close()
