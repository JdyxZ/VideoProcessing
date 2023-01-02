# Imports
import os
import asyncio
import shlex
import subprocess
import sys
import time
import shutil
from Utils import Utils
from threading import Thread

# References
# https://www.youtube.com/watch?v=jT4JzpE_psY
# https://www.youtube.com/watch?v=s40dUDJFw2o
# https://hlsbook.net/segmenting-video-with-ffmpeg/
# http://hlsbook.net/segmenting-video-with-ffmpeg-part-2/
# https://hlsbook.net/playing-hls-video-in-the-browser/
# https://hlsbook.net/playing-hls-video-in-the-browser-part-2/
# https://videojs.com/getting-started
# https://hlsbook.net/how-to-add-subtitles-to-a-live-hls-stream/
# http://hlsbook.net/sample-chapter/
# https://hlsbook.net/how-to-start-playing-a-video-at-a-specific-point-in-time/
# https://hlsbook.net/adaptive-streaming-with-hls/
# https://hlsbook.net/creating-a-master-playlist-with-ffmpeg/
# https://developer.apple.com/documentation/http_live_streaming/http_live_streaming_hls_authoring_specification_for_apple_devices
# https://hlsbook.net/how-to-encrypt-hls-video-with-ffmpeg/
# https://hlsbook.net/adding-session-data-to-a-playlist/
# https://hlsbook.net/validating-hls-video-streams/
# https://hlsbook.net/generating-hls-playlists-with-bento4/
# http://hlsbook.net/wp-content/examples/mse.html
# http://trac.ffmpeg.org/wiki/Creating%20multiple%20outputs
# https://github.com/video-dev/hls.js/blob/master/docs/API.md#getting-started
# https://www.youtube.com/watch?v=TQ_BX1Su0qc
# https://stackoverflow.com/questions/70460979/how-do-i-create-an-hls-master-playlist-with-ffmpeg
# https://www.bogotobogo.com/VideoStreaming/ffmpeg_http_live_streaming_hls.php
# https://ottverse.com/hls-http-live-streaming-how-does-it-work/
# https://ottverse.com/hls-packaging-using-ffmpeg-live-vod/
# https://www.codeinsideout.com/blog/pi/stream-ffmpeg-hls-dash/
# https://cloudinary.com/blog/http_live_streaming_hls_a_practical_guide
# https://developer.apple.com/forums/thread/712994
# https://superuser.com/questions/1670150/how-to-install-bento4-tools-on-ubuntu
# https://phoenixnap.com/kb/linux-add-to-path
# https://stackoverflow.com/questions/48428647/how-to-use-cmake-to-install
# https://www.bento4.com/developers/dash/
# https://ottverse.com/bento4-mp4dash-for-mpeg-dash-packaging/
# http://trac.ffmpeg.org/wiki/Creating%20multiple%20outputs
# https://streaminglearningcenter.com/blogs/open-and-closed-gops-all-you-need-to-know.html
# https://forums.developer.nvidia.com/t/h264-hevc-passing-private-pointers-through-enocders/46147/10
# https://en.wikipedia.org/wiki/Comparison_of_video_container_formats
# https://ahelpme.com/software/drm/mpeg-dash-and-clearkey-cenc-drm-encryption-with-nginx-bento4-and-dashjs-under-centos-8/
# https://reference.dashif.org/dash.js/latest/samples/drm/clearkey.html
# https://ahelpme.com/linux/centos-stream-9/how-to-install-linux-nginx-mysql-mariadb-php-fpm-lemp-stack-on-centos-stream-9/
# https://www.youtube.com/watch?v=HO6oU5oT6uU
# https://www.linuxquestions.org/questions/linux-desktop-74/ffmpeg-fails-cannot-open-display-0-0-error-1-a-4175613512/
# https://trac.ffmpeg.org/wiki/Capture/Webcam
# https://github.com/SoloSynth1/nginx-hls-server
# https://www.youtube.com/watch?v=3fyB70A5rwU
# https://forums.developer.nvidia.com/t/how-to-use-ffmpeg-overlay-cuda-filter-to-create-sbs-video/147495
# https://trac.ffmpeg.org/wiki/Capture/ALSA
# https://askubuntu.com/questions/611580/how-to-check-the-password-entered-is-a-valid-password-for-this-user
# https://stackoverflow.com/questions/12517451/automatically-creating-directories-with-file-output
# https://github.com/Dash-Industry-Forum/dash.js/issues/2385

# Define your workspace!
work_root = "/home/haylo/Documents/University/SCAV/Video/P3/"

# Resources root
# I have created a softlink between the shared memory and the server resources dir because the server dir
# is protected and requires admin permission. Otherwise, shm_root will be the root of the server resources dir
shm_root = "/dev/shm/"

# Global variables
stop_animation = False


class Lab3:

    def __init__(self, video_name, screen_width, screen_height):
        self.video_name = video_name
        self.screen_width = screen_width
        self.screen_height = screen_height

    def exercise1(self):

        # Create a dictionary of resolution parameters (use parameters according to Apple guidelines for HEVC)
        resolutions = \
            {
                # resolution_key : [ video_height, video_width, video_bit_rate, var_stream_map additional options]
                "1080p": ["1920", "1080", "4500k", "default=yes"],
                "720p": ["1280", "720", "2400k", ""],
                "360p": ["640", "360", "145k", ""]
            }

        # Get/set some vars
        num_frames = Utils.get_num_frames(self.video_name)
        num_videos = str(len(resolutions))
        repeat = True

        # HLS pipeline
        if repeat:

            # Remove previous HLS playlist
            if os.path.isdir('hls'):
                shutil.rmtree('hls')

            # Build HLS playlist command
            hls_command = 'ffmpeg -hwaccel cuda -hwaccel_output_format cuda -i "' + self.video_name + '" -filter_complex "' \
                          '[0:v]split=' + num_videos + \
                          ''.join\
                              (
                                  [
                                      '[v' + str(position) + ']'
                                      for position, _ in enumerate(resolutions.items())
                                  ]
                              ) + ';' + \
                          ';'.join \
                             (
                                 [
                                     '[v' + str(position) + ']scale_npp=w=' + width + ':h=' + height +
                                     ':interp_algo=lanczos[' + res_key + '_video]'
                                     for position, [res_key, [width, height, _, _]] in enumerate(resolutions.items())]
                             ) + '" ' + \
                          ' '.join \
                            (
                                 [
                                     '-map [' + res_key + '_video] -c:v:' +
                                     str(position) + ' hevc_nvenc -b:v:' + str(position) + ' ' + bit_rate + ' ' +
                                     '-preset p6 -sc_threshold 0 -g 48 -keyint_min 48 -level 4.0 -b_ref_mode disabled'
                                     for position, [res_key, [_, _, bit_rate, _]] in enumerate(resolutions.items())
                                 ]
                            ) + ' ' + \
                          '-map a:0 -c:a copy '\
                          '-sn ' \
                          '-f hls ' \
                          '-hls_allow_cache 1 ' \
                          '-hls_time 6 ' \
                          '-hls_playlist_type vod ' \
                          '-hls_segment_type mpegts ' \
                          '-master_pl_name tmp_master.m3u8 ' \
                          '-hls_segment_filename hls/stream_%v/segment%d.ts ' \
                          '-var_stream_map "' + \
                          ' '.join \
                             (
                                 [
                                     'v:' + str(position) + ',name:' + res_key + ',agroup:japanese_128k' +
                                     (',default:yes' if res_key == list(resolutions.keys())[0] else '')
                                     for position, res_key in enumerate(resolutions.keys())
                                 ]
                             ) + ' ' \
                         'a:0,name:audio,agroup:japanese_128k,language:ja,default:yes" ' \
                         'hls/stream_%v/playlist.m3u8 ' \
                         '-loglevel error -progress pipe:1'

            # Process the HLS command
            print("\nHLS playlist process")
            success = Utils.sequential_call(hls_command, num_frames)

            # Check last process result
            if not success:
                return

            # Create a directory to store the subtitles
            os.mkdir('hls/stream_subtitles')

            # Build subtitles playlist command
            subtitles_command = 'ffmpeg -itsoffset 1.5 -i "' + self.video_name + '" -map s:0 -c:s webvtt ' \
                                '-f stream_segment ' \
                                '-segment_list_flags cache ' \
                                '-segment_list hls/stream_subtitles/playlist.m3u8 ' \
                                '-segment_list_size 0 ' \
                                '-segment_format webvtt ' \
                                '-break_non_keyframes 1 ' \
                                'hls/stream_subtitles/segment%d.vtt ' \
                                '-loglevel error -progress pipe:1'

            # Process the HLS command
            print("Subtitles playlist process")
            success = Utils.sequential_call(subtitles_command, num_frames)

            # Check last process result
            if not success:
                return

            # Configure master
            print("Configuring master...")

            # Open the old master playlist to iterate through lines
            old_master = open("hls/tmp_master.m3u8", "r")

            # Open a new master playlist to change and add some parameters from the old master info
            new_master = open("hls/master.m3u8", "w")

            # Read old lines
            file_lines = old_master.readlines()
            for line in file_lines:

                # Look for streams that we want to modify
                audio_stream = line.find('#EXT-X-MEDIA:TYPE=AUDIO')
                video_stream = line.find('#EXT-X-STREAM-INF')

                if audio_stream != -1:
                    group_index = line.find('GROUP-ID')
                    name_index = line.find('NAME')

                    if group_index != -1:
                        start = group_index + len('GROUP-ID="')
                        end = line.find('"', start)
                        line = line[0:start] + 'japanese_128k' + line[end:]
                    else:
                        line += ',GROUP-ID="japanese_128k"'

                    if name_index != -1:
                        start = line.find('NAME') + len('NAME="')
                        end = line.find('"', start)
                        line = line[0:start] + 'Japanese' + line[end:]
                    else:
                        line += ',NAME="Japanese"'

                    subtitle_line = '#EXT-X-MEDIA:TYPE=SUBTITLES,' \
                                    'GROUP-ID="japanese_subtitles",' \
                                    'NAME="Japanese",' \
                                    'DEFAULT=YES,' \
                                    'AUTOSELECT=YES,' \
                                    'LANGUAGE="ja",' \
                                    'URI="stream_subtitles/playlist.m3u8"'

                    # Build the final line
                    line = '\n' + line + '\n' + subtitle_line + '\n\n'

                if video_stream != -1:
                    audio_index = line.find('AUDIO')
                    start = audio_index + len('AUDIO="')
                    end = line.find('"', start)
                    line = line[0:start] + 'japanese_128k' + line[end:-1]
                    line += ',SUBTITLES="japanese_subtitles"' + '\n'

                # Write the line to the new master
                new_master.write(line)

            # Close files
            old_master.close()
            new_master.close()

            # Remove the old master
            os.remove('hls/tmp_master.m3u8')

        # Play the video (Warning!: To play the video with subs use VLC player or similar)
        asyncio.run(Utils.play("hls/master.m3u8", self.screen_width / 2, self.screen_height / 2))

    def exercise2(self):
        # ClearKey DRM encryption:
        # I use this model of encryption to avoid setting up a real DRM License Sever

        # Create a dictionary of resolution parameters (use parameters according to Apple guidelines)
        resolutions = \
            {
                # resolution_key : [ video_height, video_width, video_bit_rate]
                "1080p": ["1920", "1080", "4500k"],
                "720p": ["1280", "720", "2400k"],
                "360p": ["640", "360", "145k"]
            }

        # Get/set some vars
        num_frames = Utils.get_num_frames(self.video_name)
        num_videos = str(len(resolutions))
        repeat = True

        # MPEG-DASH pipeline
        if repeat:

            # Remove previous dash playlist
            if os.path.isdir(shm_root + 'dash'):
                shutil.rmtree(shm_root + 'dash')

            # Encoding: Encode input video with codec x265 in the GPU
            encoding_command = 'ffmpeg -hwaccel cuda -hwaccel_output_format cuda -i "' + self.video_name + '" -filter_complex "' \
                               '[0:v]split=' + num_videos + \
                               ''.join(['[v' + str(position) + ']' for position, _ in
                                        enumerate(resolutions.items())]) + ';' + \
                               ';'.join \
                                   (
                                       [
                                           '[v' + str(position) + ']scale_npp=w=' + width + ':h=' + height +
                                           ':interp_algo=lanczos[' + res_key + '_video]'
                                           for position, [res_key, [width, height, _]] in enumerate(resolutions.items())
                                       ]
                                   ) + '" ' + \
                               ' '.join \
                                   (
                                       [
                                           '-map [' + res_key + '_video] -c:v hevc_nvenc -b:v: ' + bit_rate + ' ' +
                                           '-preset p6 -sc_threshold 0 -g 48 ' +
                                           '-keyint_min 48 -level 4.0 -b_ref_mode disabled ' +
                                           '-an -sn -y Lab3_exercise2_' + res_key + '.mp4'
                                           for position, [res_key, [_, _, bit_rate]] in enumerate(resolutions.items())
                                       ]
                                   ) + ' ' \
                               '-loglevel error -progress pipe:1'

            # Extract audio
            audio_command = 'ffmpeg -i "' + self.video_name + '" -vn -acodec copy -sn ' \
                                                              '-y "Lab3_exercise2_audio.mp4" -loglevel error'

            # Extract subtitles
            subtitles_command = 'ffmpeg -i "' + self.video_name + '" -vn -an -scodec webvtt ' \
                                                                  '-y "Lab3_exercise2_subs.vtt" -loglevel error'

            # Fragmentation: Break up the videos and the audio into segments of a predefined length
            fragmentation_commands = dict()

            # Video
            for res_key in resolutions.keys():
                command = 'mp4fragment ' \
                          '--fragment-duration 6000 ' \
                          '--sequence-number-start 0 ' \
                          '--verbosity 0 ' \
                          '"Lab3_exercise2_' + res_key + '.mp4" "Lab3_exercise2_' + res_key + '_frag.mp4"'

                fragmentation_commands['Fragment ' + res_key] = [command, 0]

            # Audio
            command = 'mp4fragment ' \
                      '--fragment-duration 6000 ' \
                      '--sequence-number-start 0 ' \
                      '--verbosity 0 ' \
                      '"Lab3_exercise2_audio.mp4" "Lab3_exercise2_audio_frag.mp4"'

            fragmentation_commands['Fragment audio'] = [command, 0]

            # Encryption (ClearKey DRM): Generate the encryption keys with OpenSLL
            key_id, key = Utils.generate_keys('encryption_key_id.key', 'encryption_key.key', shm_root)

            # Dashing: Encrypt and dash video fragments into a MPD playlist
            # Warning: Subprocess throws an error if we use mp4dash binary (in the Ubuntu shell I have achieved to use it)
            # instead of the python file. So I have placed the route of my python file
            dash_command = '/usr/local/bin/utils/mp4-dash.py ' \
                            '--output-dir=' + shm_root + 'dash ' \
                            '--force ' \
                            '--mpd-name=master.mpd ' \
                            '--use-segment-timeline ' \
                            '--always-output-lang ' \
                            '--clearkey ' \
                            '--encryption-key=' + key_id + ':' + key + ':random ' + \
                            ' '.join \
                                (
                                    [
                                        '[type=video]Lab3_exercise2_' + res_key + '_frag.mp4'
                                        for res_key in resolutions.keys()
                                    ]
                                ) + ' ' \
                            '[type=audio,+language=jap,+language_name=Japanese,+label=japanese_128k]Lab3_exercise2_audio_frag.mp4 ' \
                            '[+format=webvtt,+language=esp,+label=Castellano]Lab3_exercise2_subs.vtt'

            # Process
            print("\nEncoding")
            success = Utils.sequential_call(encoding_command, num_frames)
            if not success:
                return
            print("Extracting audio and subtitles")
            success = Utils.sequential_call(audio_command, animation=False)
            success &= Utils.sequential_call(subtitles_command, animation=False)
            if not success:
                return
            print("Fragmentation")
            success = Utils.threaded_call(fragmentation_commands, animation=False)
            if not success:
                return
            print("Encryption & Dashing")
            success = Utils.sequential_call(dash_command, animation=False)
            if not success:
                return

            # Remove files
            for res_key in resolutions.keys():
                os.remove('Lab3_exercise2_' + res_key + '.mp4')
                os.remove('Lab3_exercise2_' + res_key + '_frag.mp4')
            os.remove('Lab3_exercise2_audio.mp4')
            os.remove('Lab3_exercise2_audio_frag.mp4')
            os.remove('Lab3_exercise2_subs.vtt')

        # Play the video in the server and use ClearKey Management there
        nginx = '/usr/local/nginx/sbin/nginx'

        # Start sever
        print("\nStarting server")
        subprocess.call("sudo -S fuser -k 80/tcp 8099/tcp", shell=True)  # Stop traffic in server ports
        subprocess.call('sudo -S ' + nginx, shell=True)

        # Launch localhost
        print("\nLaunching localhost\n")
        time.sleep(1)
        subprocess.call('xdg-open "http://localhost:80/"', shell=True, stderr=False)

        # Stop server
        while True:
            choice = input("Enter S to stop the server")
            if choice == "s" or choice == "S":
                break

        print("\nStopping server")
        subprocess.call("sudo -S " + nginx + " -s stop", shell=True)


    def exercise3(self):
        # Declare a variable to get use the sever bin as a module
        nginx = '/usr/local/nginx/sbin/nginx'

        # Build HLS stream
        hls_stream = 'ffmpeg -hwaccel cuda -hwaccel_output_format cuda -framerate 60 -thread_queue_size 1024 ' \
                     '-f x11grab -i :1 ' \
                     '-f v4l2 -i /dev/video0 ' \
                     '-f alsa -sample_rate 44100 -i hw:2,0 ' \
                     '-filter_complex ' \
                     '"[0:v]format=nv12[formated_screen];[formated_screen]hwupload[uploaded_screen]; ' \
                     '[1:v]format=nv12[formated_webcam];[formated_webcam]hwupload[uploaded_webcam]; ' \
                     '[uploaded_webcam]scale_npp=w=480:h=360:interp_algo=lanczos[resized_webcam]; ' \
                     '[uploaded_screen][resized_webcam]overlay_cuda=main_w-overlay_w:0[compact_video]; ' \
                     '[compact_video]split=3[v0][v1][v2]; ' \
                     '[v0]scale_npp=w=1920:h=1080:interp_algo=lanczos[1080p_video]; ' \
                     '[v1]scale_npp=w=1280:h=720:interp_algo=lanczos[720p_video]; ' \
                     '[v2]scale_npp=w=640:h=360:interp_algo=lanczos[360p_video]" ' \
                     '-map [1080p_video] -c:v:0 h264_nvenc -b:v:0 6000k -preset p6 -tune ll -g 48 -keyint_min 48 ' \
                     '-map [720p_video] -c:v:1 h264_nvenc -b:v:1 3000k -preset p6 -tune ll -g 48 -keyint_min 48 ' \
                     '-map [360p_video] -c:v:2 h264_nvenc -b:v:2 365k -preset p6 -tune ll -g 48 -keyint_min 48 ' \
                     '-map 2 -c:a aac -b:a 128k -ac 2 ' \
                     '-f hls ' \
                     '-hls_allow_cache 1 ' \
                     '-hls_time 4 ' \
                     '-hls_list_size 20 ' \
                     '-hls_segment_type mpegts ' \
                     '-strftime 1 ' \
                     '-hls_flags delete_segments+second_level_segment_index ' \
                     '-hls_delete_threshold 1 ' \
                     '-master_pl_name master.m3u8 ' \
                     '-hls_segment_filename "' + shm_root + 'hls/stream_%v/segment %Y-%m-%d %%d.ts" ' \
                     '-var_stream_map ' \
                     '"v:0,name:1080p,agroup:stream_audio_128k,default:yes ' \
                     'v:1,name:720p,agroup:stream_audio_128k ' \
                     'v:2,name:360p,agroup:stream_audio_128k ' \
                     'a:0,name:audio,agroup:stream_audio_128k,default:yes" ' \
                     '"' + shm_root + 'hls/stream_%v/playlist.m3u8" '\
                     '-loglevel error'

        # Check HLS stream syntax before starting
        print("Checking HLS command")
        output = Utils.check_process_syntax(hls_stream)

        # Check errors
        if len(output) > 0:
            print("Command error:\n" + output)
            return
        else:
            print("Command correct!")

        # Start streaming
        print("\nStarting streaming")
        streaming = subprocess.Popen(shlex.split(hls_stream), stderr=subprocess.PIPE)
        time.sleep(1)

        # Start sever
        print("\nStarting server")
        subprocess.call("sudo -S fuser -k 80/tcp 8099/tcp", shell=True) # Stop traffic in server ports
        subprocess.call('sudo -S ' + nginx, shell=True)

        # Launch localhost
        print("\nLaunching localhost\n")
        time.sleep(1)
        subprocess.call('xdg-open "http://localhost:80/"', shell=True, stderr=False)

        # Streaming animation
        t1 = Thread(target=self.stop)
        t2 = Thread(target=self.animate)
        t1.start()
        t2.start()
        t1.join()
        t2.join()

        # Stop streaming
        print("\nStopping streaming")
        streaming.kill()

        # Stop server
        print("\nStopping server")
        subprocess.call("sudo -S " + nginx + " -s stop", shell=True)

    @staticmethod
    def stop():
        global stop_animation

        while True:
            # Look for user input
            choice = input("Enter S to stop the streaming\n\n")

            # Break the loop
            if choice == "s" or choice == "S":
                stop_animation = True
                break

    @staticmethod
    def animate():
        position = 0
        animation1 = [" |", " /", " -", " \\"]
        animation2 = [".", "..", "...", "....", ".....", "......", "......."]
        time.sleep(1)

        while True:
            # Animation
            sys.stdout.write("\rStreaming" + animation2[position % len(animation2)] + "    ")
            time.sleep(2)
            position += 1

            # Break loop
            if stop_animation is True:
                break


# Main
if __name__ == "__main__":
    # Check the given path is right and contains the BBB video
    assert os.path.exists(work_root), "Invalid root"

    # Change working directory
    os.chdir(work_root)

    # Set the video we are going to work with and check that it exists in the current working directory
    video_name = "Chainsaw Man Episode 11.mkv"
    assert os.path.isfile(work_root + video_name), video_name + " video not found"

    # Get screen resolution
    screen_resolution = Utils.get_screen_resolution()

    # Create your lab instance
    L3 = Lab3(video_name, int(screen_resolution[0]), int(screen_resolution[1]))

    # Choose an exercise
    while True:
        choice = input("Enter the number of the exercise (S to stop): ")
        if choice == "1":
            L3.exercise1()
        elif choice == "2":
            L3.exercise2()
        elif choice == "3":
            L3.exercise3()
        elif choice == "s" or choice == "S":
            break
        else:
            print("Enter a right expression\n")