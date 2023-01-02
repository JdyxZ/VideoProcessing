# Import
import os
import subprocess

# Define your root!
root = "/home/haylo/Documents/University/SCAV/Video/P2/"


class Lab2:

    def __init__(self, video, file, width, height):
        self.video = video
        self.file = file
        self.width = width
        self.height = height

    def exercise1(self):

        # Write video info into a file
        command = "ffprobe -hide_banner " + self.video
        file_path = root + "output.txt"
        file = open(file_path, "w")
        subprocess.call(command.split(), stderr=file)

        # Read and parse the video file info
        file = open(file_path, "r")
        file_lines = file.readlines()
        audio_track = 1
        for line in file_lines:
            v_position = line.find("Video:")
            a_position = line.find("Audio:")

            # Video properties
            if v_position != -1:
                video_properties = line[v_position + 7:].split(",")
                print("\nVideo Info\n")
                print("Coded: ", video_properties[0])
                print("Color space: ", video_properties[1])
                print("Resolution: ", video_properties[2])
                print("Bitrate: ", video_properties[3])
                print("Framerate: ", video_properties[4])
            # Audio properties
            elif a_position != -1:
                print("\nAudio Track " + str(audio_track) + " Info\n")
                audio_properties = line[a_position + 7:].split(",")
                print("Coded: ", audio_properties[0])
                print("Sampling rate: ", audio_properties[1])
                print("Channels: ", audio_properties[2])
                print("Sample format: ", audio_properties[3])
                print("Bitrate: ", audio_properties[4])
                audio_track += 1

        # Delete the video info file
        os.remove(file_path)

    def exercise2(self):
        # Commands
        command1 = "ffmpeg -i " + self.video + " \
        -t 60 -c:v copy -an -y BBB_1min.mp4 \
        -t 60 -vn -c:a copy -ac 2 -map 0:1 -y BBB_1min.mp3 \
        -t 60 -acodec aac -ac 2 -ab 128k -map 0:2 -y BBB_1min.aac"

        command2 = "ffmpeg -i BBB_1min.mp4 -i BBB_1min.mp3 -i BBB_1min.aac" \
                   " -map 0:v:0 -map 1:a:0 -map 2:a:0 -codec copy -y " \
                   "exercise2_output.mp4"

        # Process
        subprocess.call(command1.split(), stderr=False)
        subprocess.call(command2.split(), stderr=False)

        # Delete temporary files
        os.remove(root + "BBB_1min.mp4")
        os.remove(root + "BBB_1min.mp3")
        os.remove(root + "BBB_1min.aac")

        # Notify success
        print("Process successfully completed\n")

    def exercise3(self):
        # Variables
        codec = self.file[self.file.find(".") + 1:]
        resolution = str(self.width) + ":" + str(self.height)
        command = "ffmpeg -i " + self.file + " -vf scale=" + resolution + \
                  " -y exercise3_output." + codec

        # Process
        subprocess.call(command.split(), stderr=False)

        # Notify success
        print("Process successfully completed\n")

    def exercise4(self):
        # Write audio codecs into a file
        command = "ffprobe -v error -select_streams a -show_entries " \
                  "stream=codec_name -of default=noprint_wrappers=1:nokey=1 " \
                  + self.video
        file_path = root + "output.txt"
        file = open(file_path, "w")
        subprocess.call(command.split(), stdout=file)

        # Read and parse the audio codecs file
        file = open(file_path, "r")
        file_codecs = file.read().splitlines()
        number_of_codecs = len(file_codecs)

        # Compatibility
        compatibility = \
        {
            "aac": ["DVB", "ISDB", "DTMB"],
            "ac3": ["DVB", "ATSC", "DTMB"],
            "mp3": ["DVB", "DTMB"],
            "dra": "DTMB",
            "mp2": "DTMB"
        }

        # Get compatibility
        try:
            unprocessed_bsc = \
                [compatibility[audio_codec] for audio_codec in file_codecs]
        except:
            print("No compatible broadcast standard")
            return

        # Place compatibility in a list
        processed_bsc = \
            [bs for c in unprocessed_bsc for bs in c]

        # Join and count values
        processed_compatibility = \
            {bs: processed_bsc.count(bs) for bs in processed_bsc}

        # Get compatible standards and place them in a list
        compatible_standards = []
        for broadcast_standard, count in processed_compatibility.items():
            if count == number_of_codecs:
                compatible_standards.append(broadcast_standard)

        # Output broadcast standard compatibility
        if(len(compatible_standards) == 0):
            print("No compatible broadcast standards")
        else:
            print \
            (
                "\n" +
                ", ".join(map(str, compatible_standards)) +
                " are compatible with " +
                " and ".join(map(str, file_codecs)) +
                " of the audio track(s) of " +
                self.video +
                "\n"
            )

        # Delete the audio codecs file
        os.remove(file_path)


def main():
    # Change working directory
    os.chdir(root)

    # Create your lab instance
    lab2 = Lab2("BBB.mp4", "Lenna.png", 1280, 720)

    # Choose an exercise
    while (True):
        choice = input("Enter the number of the exercise (S to stop): ")
        if choice == "1":
            lab2.exercise1()
        elif choice == "2":
            lab2.exercise2()
        elif choice == "3":
            lab2.exercise3()
        elif choice == "4":
            lab2.exercise4()
        elif choice == "s":
            break
        else:
            print("Enter a right expression\n")


# Execute main
main()
