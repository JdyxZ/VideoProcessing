# Imports
import os
import time
import asyncio
from Utils import Utils
from SimpleEncoder import SimpleEncoder

# Define your root!
root = "/home/haylo/Documents/University/SCAV/Video/S3/"


class S3:

    def __init__(self, video_name, screen_width, screen_height):
        self.video_name = video_name
        self.screen_width = screen_width
        self.screen_height = screen_height

    def exercise1(self):
        # Create the video_fragment (if not already created)
        video_fragment = self.video_name[0:self.video_name.find(".")] + "_fragment.mkv"
        if not os.path.isfile(video_fragment):
            success = Utils.create_video_fragment(self.video_name, video_fragment, 60)
            if not success:
                return

        # Some setting vars
        repeat = False
        success = True
        approach = 3  # 1 = Sequential, 2 = Threaded, 3 = Asynchronous
        channels = Utils.get_stream_value(video_fragment, "a", None, "channels").splitlines(False)

        # Video frame count
        num_frames = Utils.get_num_frames(video_fragment)

        # Let's create a dictionary of videos to encode
        videos = \
            {
                "VP8": "Exercise1_vp8.mkv",
                "VP9": "Exercise1_vp9.mkv",
                "h265": "Exercise1_h265.mkv",
                "AV1": "Exercise1_av1.mkv",
            }

        # Only repeat if desired
        if repeat:

            # VP8 command
            vp8_command = "ffmpeg -i '" + video_fragment + "' -an -c:v libvpx" \
                          " -crf 4 -b:v 10M -cpu-used 0 -row-mt 1" \
                          " -y '" + videos["VP8"] + "' -loglevel error -progress pipe:1"

            # VP9 command
            vp9_command = "ffmpeg -i '" + video_fragment + "' -an -c:v libvpx-vp9" \
                          " -crf 35 -b:v 0 -cpu-used 0 -row-mt 1" \
                          " -y '" + videos["VP9"] + "' -loglevel error -progress pipe:1"

            # h265 command
            # Some reference: https://unix.stackexchange.com/questions/229390/bash-ffmpeg-libx265-prevent-output
            h265_command = "ffmpeg -i '" + video_fragment + "' -an -c:v libx265 -x265-params log-level=error" \
                           " -crf 30 -b:v 0 -preset slower" \
                           " -y '" + videos["h265"] + "' -loglevel error -progress pipe:1"

            # AV1 command
            av1_command = "ffmpeg -i '" + video_fragment + "' -an -c:v libsvtav1" \
                          " -crf 45 -preset 3" \
                          " -y '" + videos["AV1"] + "' -loglevel error -progress pipe:1"

            # Create a dictionary of commands
            commands = \
                {
                    "VP8": [vp8_command, num_frames],
                    "VP9": [vp9_command, num_frames],
                    "h265": [h265_command, num_frames],
                    "AV1": [av1_command, num_frames],
                }

            # Transcode
            print("Transcoding video fragment\n")

            # Choose the approach to the problem
            if approach == 1:
                # Sequential approach: Do nothing special
                start = time.time()
                for command_key, [command, num_frames] in commands.items():
                    print(command_key)
                    success &= Utils.sequential_call(command, num_frames, True)
                end = time.time()
                print("Elapsed time: " + str(end - start) + "s\n")
            if approach == 2:
                # Threaded process (By default): Use threads to boost performance
                success = Utils.threaded_call(commands, True)
            else:
                # Asynchronous process: Use asynchronous waiting to boost performance
                success = asyncio.run(Utils.asynchronous_call(commands, True))

            # Check transcoding success
            if not success:
                return

        # Burn bit rate
        print("Burning bit rates into videos\n")
        success = Utils.burn_bit_rate(videos, False)
        if not success:
            return

        # Stack videos into a single videos
        print("Stacking videos into a single video\n")
        stack_command = "ffmpeg -i '" + videos["VP8"] + "' -i '" + videos["VP9"] + "' -i '" + \
                        videos["h265"] + "' -i '" + videos["AV1"] + "' -i 'BBB_fragment.mkv'" + \
                        " -acodec copy -filter_complex \"" \
                        "[0:v]drawtext=font='Ubuntu':fontsize=60:fontcolor=white:text='VP8':" \
                        "x=(w/2):y=(h-text_h-50):box=1:boxcolor=black:boxborderw=20[vp8];" \
                        "[1:v]drawtext=font='Ubuntu':fontsize=60:fontcolor=white:text='VP9':" \
                        "x=(w/2):y=(h-text_h-50):box=1:boxcolor=black:boxborderw=20[vp9];" \
                        "[2:v]drawtext=font='Ubuntu':fontsize=60:fontcolor=white:text='h265':" \
                        "x=(w/2):y=(h-text_h-50):box=1:boxcolor=black:boxborderw=20[h265];" \
                        "[3:v]drawtext=font='Ubuntu':fontsize=60:fontcolor=white:text='AV1':" \
                        "x=(w/2):y=(h-text_h-50):box=1:boxcolor=black:boxborderw=20[av1];" \
                        "[vp8][vp9][h265][av1]xstack=inputs=4:layout=0_0|0_h0|w0_0|w0_h0:fill=black[output_video]" \
                        "\" -map '[output_video]':0 " + \
                        " ".join \
                        (
                            # Map all audio tracks to their related channel
                            ["-map 4:a:" + str(position) for position, _ in enumerate(channels)]
                        ) + \
                        " -y 'S3_Exercise1.mkv' -loglevel error -progress pipe:1"

        # Process stack command
        success = Utils.sequential_call(stack_command, num_frames)
        if success:
            for _, video_name in videos.items():
                os.remove(video_name)
        else:
            return

        # Play the video
        asyncio.run(Utils.play("S3_Exercise1.mkv", self.screen_width / 2, self.screen_height / 2))

    @staticmethod
    def exercise2():
        app = SimpleEncoder()
        app.mainloop()


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
    Seminar3 = S3(video_name, int(screen_resolution[0]), int(screen_resolution[1]))

    # Choose an exercise
    while True:
        choice = input("Enter the number of the exercise (S to stop): ")
        if choice == "1":
            Seminar3.exercise1()
        elif choice == "2":
            Seminar3.exercise2()
        elif choice == "s" or choice == "S":
            break
        else:
            print("Enter a right expression\n")