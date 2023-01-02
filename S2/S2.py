# Import
import os
import time
import asyncio
from Utils import Utils


# Define your root!
root = "/home/haylo/Documents/University/SCAV/Video/S2/"


class S2:

    def __init__(self, video_name, screen_width, screen_height):
        self.video_name = video_name
        self.screen_width = screen_width
        self.screen_height = screen_height

    def exercise1(self):
        # Get video duration and frame count
        duration = int(float(Utils.get_stream_value(self.video_name, "v", 0, "duration")))
        num_frames = Utils.get_num_frames(self.video_name)

        # Ask the user for an input
        while True:
            seconds = input("Enter the second you want to cut the video at: ")

            # Try to parse input to integer
            try:
                int_seconds = int(seconds)
            except ValueError:
                print("Error: The input seconds you entered cannot be converted to integer\n")
                continue
            except:
                print("Error: The input you entered is invalid\n")
                continue

            # Check whether the input is in range
            if 0 < int_seconds < duration:
                break
            else:
                print("Error: The input you entered is not inside the video duration limits")

        # Commands
        ffmpeg_command = "ffmpeg -i '" + self.video_name + "' -t " + str(seconds) + " -acodec copy -vcodec copy" \
                         " -y 'S2_exercise1.mkv' " \
                         "-loglevel error -progress pipe:1"

        # Cut the input video
        print("Cutting video")
        success = Utils.sequential_call(ffmpeg_command, num_frames)

        # Play the output video
        if success:
            asyncio.run(Utils.play("S2_exercise1.mkv", self.screen_width / 2, self.screen_height / 2))

    def exercise2(self):
        # References
        # https://hhsprings.bitbucket.io/docs/programming/examples/ffmpeg/video_data_visualization/histogram.html
        # https://ffmpeg.org/ffmpeg-filters.html#Filtergraph-description
        # http://underpop.online.fr/f/ffmpeg/help/

        # Create the cut video (if not already created)
        if not os.path.isfile("S2_exercise1.mkv"):
            self.exercise1()

        # Set some vars
        histogram_width = int(360/1920 * self.screen_width)
        video_width = self.screen_width - histogram_width
        pixel_format = Utils.get_stream_value(self.video_name, "v", 0, "pix_fmt")
        num_frames = Utils.get_num_frames("S2_exercise1.mkv")

        # Commands: Create a video with the yuv histogram attached on the right hand side and display it
        ffmpeg_command = "ffmpeg -i 'S2_exercise1.mkv' -c:a copy -filter_complex " \
                         "split=2[original_video][video_to_histogram];" \
                         "[video_to_histogram]format=" + \
                         pixel_format + \
                         ",histogram=display_mode=stack,scale=" + \
                         str(histogram_width) + ":" + str(self.screen_height) + ",setsar=1[yuv_histogram];" \
                         "[original_video]scale=" + str(video_width) + ":" + str(self.screen_height) + \
                         ":flags=lanczos,setsar=1[scaled_video];"\
                         "[scaled_video]pad=" + str(self.screen_width) + ":" + str(self.screen_height) + \
                         "[full_range_video];" \
                         "[full_range_video][yuv_histogram]overlay=x=" + str(video_width) + ":y=0" \
                         " -y 'S2_exercise2.mkv'" \
                         " -loglevel error -progress pipe:1"

        # Create the original video with the yuv histogram attached to its right side
        print("Building YUV histogram and attaching it")
        success = Utils.sequential_call(ffmpeg_command, num_frames)

        # Play the video
        if success:
            asyncio.run(Utils.play("S2_exercise2.mkv", self.screen_width/2, self.screen_height/2))

    def exercise3(self):
        # Some setting vars
        repeat = True
        success = True
        approach = 2  # 1 = Sequential, 2 = Threaded, 3 = Asynchronous

        # Video frame count
        num_frames = Utils.get_num_frames(self.video_name)

        # Create a dictionary of resolutions
        resolutions = \
        {
            "120p": "160x120",
            "240p": "360x240",
            "480p": "640x480",
            "720p": "1280x720",
        }

        # Create a dictionary of key_name/[command,command_frames] to process
        commands = dict()

        # Only repeat if desired
        if repeat:
            # Iterate through values of resolutions
            for resolution_key, resolution_value in resolutions.items():
                # Use lanzcos for down-sampling
                # https://write.corbpie.com/a-guide-to-upscaling-or-downscaling-video-with-ffmpeg/

                resolution_values = resolution_value.split("x")
                ffmpeg_command = "ffmpeg -i '" + self.video_name + "' -c:a copy -vf scale=" \
                                 + resolution_values[0] + ":" + resolution_values[1] + \
                                 " -sws_flags lanczos -y" + \
                                 " 'S2_exercise3_" + resolution_values[1] + "p.mkv'" + \
                                 " -loglevel error -progress pipe:1"
                commands[resolution_key] = [ffmpeg_command, num_frames]

            # Choose the approach to the problem
            print("Scaling resolutions")
            if approach == 1:
                # Sequential approach: Do nothing special
                start = time.time()
                for _, command in commands.items():
                    success &= Utils.sequential_call(command)
                end = time.time()
                print("Elapsed time: " + str(end - start) + "s\n")
            if approach == 2:
                # Threaded process (By default): Use threads to boost performance
                success = Utils.threaded_call(commands)
            else:
                # Asynchronous process: Use asynchronous waiting to boost performance
                success = asyncio.run(Utils.asynchronous_call(commands))

        # Choose a video to play
        if success:
            while True:
                # Print menu
                index = 1
                for resolution_key in resolutions.keys():
                    print(index, ". ", resolution_key)
                    index += 1

                # Input
                choice = input("Choose the resolution you want to play (E to exit): ")

                # Make a choice
                if choice.isnumeric() and 0 < int(choice) <= index:
                    resolution_key = list(resolutions)[int(choice) - 1]
                    asyncio.run(Utils.play("S2_exercise3_" + resolution_key + ".mkv"))
                    continue
                if choice == "e" or choice == "E":
                    break
                else:
                    print("Enter a right expression\n")

            print("\n")

    def exercise4(self):
        # Get number of channels and bit rates of each audio track of the video
        channels = Utils.get_stream_value(self.video_name, "a", None, "channels").splitlines(False)
        bit_rates = list(map(lambda bit_rate: str(int(int(bit_rate) / 1000)) + "k",
                             Utils.get_stream_value(self.video_name, "a", None, "bit_rate").splitlines(False)))

        # Video frame count
        num_frames = Utils.get_num_frames(self.video_name)

        # Commands: Convert stereo tracks to mono tracks and vice versa
        # Best way to do this it to apply -ac filter, since amerge, join and pan only maps audio channels:
        # https://trac.ffmpeg.org/wiki/AudioChannelManipulation
        # Preserve bit rate:
        # https://superuser.com/questions/217356/merge-two-audio-channels-stereo-into-one-mono-on-gsm6-10-using-ffmpeg

        ffmpeg_command_S2M = "ffmpeg -i '" + self.video_name + "' -hide_banner -c:v copy " + \
                             " ".join \
                             (
                                # Locate non-stereo tracks and set copy option
                                ["-c:a:" + str(position) + " copy"
                                 for position, channel in enumerate(channels) if channel != '2']
                             ) + \
                             " " + \
                             " ".join\
                             (
                                 # Locate stereo tracks and build options
                                 ["-ac:a:" + str(position) + " 1 -b:a:" + str(position) + " " + bit_rates[position]
                                  for position, channel in enumerate(channels) if channel == '2']
                             ) + \
                             " -map 0:v:0 " + \
                             " ".join \
                             (
                                 # Map all audio tracks to their related channel
                                 ["-map 0:a:" + str(position)
                                  for position, _ in enumerate(channels)]
                             ) + \
                             " -y 'S2_exercise4_mono.mkv' " \
                             "-loglevel error -progress pipe:1"

        ffmpeg_command_M2S = "ffmpeg -i '" + self.video_name + "' -hide_banner -c:v copy " + \
                             " ".join \
                             (
                                # Locate non-stereo tracks and set copy option
                                ["-c:a:" + str(position) + " copy"
                                 for position, channel in enumerate(channels) if channel != '2']
                             ) + \
                             " " + \
                             " ".join\
                             (
                                 # Locate mono tracks and build options
                                 ["-ac:a:" + str(position) + " 2 -b:a:" + str(position) + " " + bit_rates[position]
                                  for position, channel in enumerate(channels) if channel == '2']
                             ) + \
                             " -map 0:v:0 " + \
                             " ".join \
                             (
                                 # Map all audio tracks to their related channel
                                 ["-map 0:a:" + str(position)
                                  for position, _ in enumerate(channels)]
                             ) + \
                             " -y 'S2_exercise4_stereo.mkv' " \
                             "-loglevel error -progress pipe:1"

        # Convert stereo tracks to mono and reconvert the mono tracks to stereo again
        print("Converting to Mono")
        success = Utils.sequential_call(ffmpeg_command_S2M, num_frames)
        print("Reconverting to Stereo")
        success &= Utils.sequential_call(ffmpeg_command_M2S, num_frames)

        # Choose a video to play
        if success:
            while True:
                # Print menu
                print("\n1. Mono")
                print("2. Stereo")

                # Input
                choice = input("Choose the file you want to play (E to exit): ")

                # Make a choice
                if choice.isnumeric() and 0 < int(choice) <= 2:
                    if int(choice) == 1:
                        asyncio.run(Utils.play("S2_exercise4_mono.mkv"))
                    else:
                        asyncio.run(Utils.play("S2_exercise4_stereo.mkv"))
                    continue
                if choice == "e" or choice == "E":
                    break
                else:
                    print("Enter a right expression\n")

            print("\n")


# Main
if __name__ == "__main__":
    # Check the given path is right and contains the BBB video
    assert os.path.exists(root), "Invalid root"

    # Change working directory
    os.chdir(root)

    # Set the video we are going to work with and check that it exists in the current working directory
    video_name = "BBB.mp4"
    assert os.path.isfile(root + video_name), video_name + " video not found"

    # Get screen resolution
    screen_resolution = Utils.get_screen_resolution()

    # Create your lab instance
    Seminar2 = S2(video_name, int(screen_resolution[0]), int(screen_resolution[1]))

    # Choose an exercise
    while True:
        choice = input("Enter the number of the exercise (S to stop): ")
        if choice == "1":
            Seminar2.exercise1()
        elif choice == "2":
            Seminar2.exercise2()
        elif choice == "3":
            Seminar2.exercise3()
        elif choice == "4":
            Seminar2.exercise4()
        elif choice == "s" or choice == "S":
            break
        else:
            print("Enter a right expression\n")
