# Import
import subprocess
import time
import threading
import asyncio
import sys
import shlex
import os


class Utils:

    @staticmethod
    def get_process_output(command):
        # Process
        return subprocess.check_output(shlex.split(command)).decode()

    @staticmethod
    def get_stream_value(media_path, stream_type, stream_channel, stream_property):
        # Command
        command = "ffprobe -v error -hide_banner -select_streams " + stream_type + \
                  (":" + stream_channel if stream_channel else "") + \
                  " -show_entries stream=" + stream_property + " -of default=noprint_wrappers=1:nokey=1 '" \
                  + media_path + "'"

        # Process
        result = subprocess.check_output(shlex.split(command), stderr=False).decode().strip()

        # Return call output
        return result

    @staticmethod
    def get_frames_info(media_path, stream_type, stream_channel, frames_properties):
        # Build command to retrieve frames info
        command = "ffprobe -v error -hide_banner -select_streams " + stream_type + \
                  (":" + stream_channel if stream_channel else "") + \
                  " -show_entries packet=" + frames_properties + " -of compact=p=0:nk=1 '" + media_path + "'"

        # Process the frames info
        frames_info = subprocess.check_output(command.split(), stderr=False).decode().strip()

        # Return call output
        return frames_info

    @staticmethod
    def get_screen_resolution():
        # Reference:
        # https://www.thecodingforums.com/threads/how-do-subprocess-popen-ls-grep-foo-shell-true-withshell-false.725178/

        # Command
        command1 = "xrandr"
        command2 = "grep *"
        # Query
        available_resolutions = subprocess.Popen(shlex.split(command1), stdout=subprocess.PIPE)
        screen_info = \
            subprocess.check_output(
                shlex.split(command2), stdin=available_resolutions.stdout, stderr=False
            ).decode().split()[0].split("x")

        return screen_info

    @staticmethod
    def get_num_frames(video_name):
        # Command
        command = "ffprobe -v error -select_streams v:0 -count_packets " \
                  "-show_entries stream=nb_read_packets -of csv=p=0 '" + video_name + "'"

        # Process
        frame_count = subprocess.check_output(shlex.split(command), stderr=subprocess.PIPE).decode()

        # Return call output
        return int(frame_count)

    @staticmethod
    def get_duration(media_path):
        # Command
        command = "ffprobe -hide_banner -i '" + media_path + "'"

        # Process
        process = subprocess.Popen(shlex.split(command), stderr=subprocess.PIPE)

        # Wait for the process to complete
        process.wait()

        # Get duration
        media_info = process.stderr.read().decode()
        start_position = media_info.find("Duration:") + len("Duration:")
        end_position = media_info.find(",", start_position)
        time = media_info[start_position:end_position]
        duration = sum(weight * float(time_interval) for weight, time_interval in zip([3600, 60, 1], time.split(":")))

        # Output
        return float(duration)

    @staticmethod
    def basic_animation(position):
        # Pycharm stdout animation:
        # https://stackoverflow.com/questions/43515165/pycharm-python-console-printing-on-the-same-line-not-working-as-intended

        ranged_position = position % 4

        if ranged_position == 0:
            sys.stdout.write("\rProcesing " + "-")
            sys.stdout.flush()
            time.sleep(1)
        elif ranged_position == 1:
            sys.stdout.write("\rProcesing " + "\\")
            sys.stdout.flush()
            time.sleep(1)
        elif ranged_position == 2:
            sys.stdout.write("\rProcesing " + "|")
            sys.stdout.flush()
            time.sleep(1)
        else:
            sys.stdout.write("\rProcesing " + "/")
            sys.stdout.flush()
            time.sleep(1)

    @staticmethod
    def sequential_advanced_animation(process, num_frames, tk_app=None):
        # Pycharm progress animation:
        # https://superuser.com/questions/1459810/how-can-i-get-ffmpeg-command-running-status-in-real-time
        # https://stackoverflow.com/questions/64105247/php-actively-refresh-exec-function-result
        # https://blog.programster.org/ffmpeg-output-progress-to-file
        # https://realpython.com/lessons/animation/

        # Declare bar width
        bar_width = 40

        # Read property and check thread status
        current_line = process.stdout.readline().decode()
        process_active = process.poll() is None

        while process_active and "progress" not in current_line:
            # If current property is the current frame
            if "frame=" in current_line:
                # Get the number of the current frame
                current_frame = int(current_line[6:-1])

                # Estimate the work done
                work_done = current_frame / num_frames

                # Pycharm console animation
                if tk_app is None:
                    # Calculate number of hashes and blanks
                    hashes = int(bar_width * work_done)
                    blanks = bar_width - hashes

                    # Finally, print the process bar
                    print('\rProcess status : [', hashes * '#', blanks * ' ', ']', f' {100 * work_done:.0f}%',
                          sep='', end='',flush=True)
                # Tkinter animation
                else:
                    # Update progress
                    tk_app.progress_bar.set(work_done)
                    tk_app.progress_percentage.configure(text=f' {100 * work_done:.0f}%')
                    tk_app.update()

            # Update thread status and progress property
            process_active = process.poll() is None
            current_line = process.stdout.readline().decode()

        # Process finished
        if not process_active:
            # Pycharm console animation
            if tk_app is None:
                print('\rProcess status : [', bar_width * '#', ']', f' {100:.0f}%', sep='', end='', flush=True)
            # Tkinter animation
            else:
                # Update progress
                tk_app.progress_bar.set(1)
                tk_app.progress_percentage.configure(text=f' {100:.0f}%')
                tk_app.update()

    @staticmethod
    def thread_advanced_animation(processes):
        # Declare some bars
        bar_width = 30
        output = "\r"

        # For each process
        for command_key, [process, num_frames] in processes.items():

            # Read property and check thread status
            current_line = process.stdout.readline().decode()
            thread_active = process.poll() is None

            while thread_active and "progress" not in current_line:

                # If current property is the current frame
                if "frame=" in current_line:

                    # Get the number of the current frame
                    current_frame = int(current_line[6:-1])

                    # Calculate number of hashes and blanks
                    work_done = current_frame / num_frames
                    hashes = int(bar_width * work_done)
                    blanks = bar_width - hashes

                    # Store thread process
                    output += 'Thread ' + command_key + ' [' + hashes * '#' + blanks * ' ' + ']' + f' {100 * work_done:.0f}%    '

                # Update thread status and progress property
                thread_active = process.poll() is None
                current_line = process.stdout.readline().decode()

            # Thread has finished
            if not thread_active:
                output += 'Thread ' + command_key + ' [' + bar_width * '#' + ']' + f' {100:.0f}%    '

        print(output, sep='', end='', flush=True)

    @staticmethod
    def sequential_call(command, num_frames=1, animation=True, force_search=False, tk_app=None):
        # Launch an asynchronous subprocess
        process = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Save the process in the Tkinter app
        if tk_app is not None:
            tk_app.tk_process = process
            tk_app.update()

        # While the process is executing, inform the user the current status
        while process.poll() is None:
            if animation:
                Utils.sequential_advanced_animation(process, num_frames, tk_app)

        # Leave a line space in case of animation working
        if animation:
            print("\n")

        # Check errors
        error_message = process.stderr.read().decode()
        error = (True if (force_search and "error" in error_message.lower()) else
                 (False if force_search else len(error_message) > 0))
        if error:
            # Pycharm console output
            if tk_app is None:
                print("Process error:")
                print(error_message + "\n")
            # Tkinter animation
            else:
                tk_app.output_message.configure(state="normal")
                tk_app.output_message.insert("0.0", "Process error:\n" + error_message)
                tk_app.output_message.configure(state="disabled")
            return 0
        else:
            # Pycharm console output
            if tk_app is None:
                print("Process successfully completed\n")
            # Tkinter animation
            else:
                tk_app.output_message.configure(state="normal")
                if tk_app.process_killed:
                    tk_app.output_message.insert("0.0", "Process aborted\n")
                    tk_app.process_killed = False
                else:
                    tk_app.output_message.insert("0.0", "Process successfully completed\n")

                tk_app.output_message.configure(state="disabled")
            return 1

    @staticmethod
    def thread_work(processes, command_key, command, num_frames):
        # Launch an asynchronous subprocess
        process = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Add current process and the command related to it
        processes[command_key] = [process, num_frames]

        # Brief note: We are able to access processes by reference since lists in python are mutable objects
        # https://stackoverflow.com/questions/986006/how-do-i-pass-a-variable-by-reference

    @staticmethod
    def register_thread_time(processes, finished_threads, start):
        # For each process
        for command_key, [process, _] in processes.items():
            # If command key is not already in the finished threads dictionary and the process has finished
            if command_key not in finished_threads.keys() and process.poll() is not None:
                # Take a mark
                mark = time.time()

                # Append finished thread
                finished_threads[command_key] = mark - start

    @staticmethod
    def threaded_call(commands, animation=True, force_search=False):
        # Declare some vars
        threads = []  # Declare a list of threads
        processes = dict()  # Declare a dictionary of processes
        finished_threads = dict()  # Declare a dictionary of finished threads

        # Create threads
        for command_key, [command, num_frames] in commands.items():
            thread = threading.Thread(target=Utils.thread_work(processes, command_key, command, num_frames))
            threads.append(thread)

        # Start the stopwatch
        start = time.time()

        # Start multithreading process
        for thread in threads:
            thread.start()

        # Join all threads
        for thread in threads:
            thread.join()

        # Wait until all threads are completed and output a custom animation if desired
        while any(process.poll() is None for _, [process, _] in processes.items()):
            # Register thread execution time
            Utils.register_thread_time(processes, finished_threads, start)

            # Thread animation
            if animation:
                Utils.thread_advanced_animation(processes)

        # Register the last thread execution time (just in case)
        Utils.register_thread_time(processes, finished_threads, start)

        # Leave a line space in case of animation working
        if animation:
            print("\n")

        # Execution time
        for command_key, execution_time in finished_threads.items():
            print("Thread " + command_key + " execution time: " + str(execution_time) + "s\n")

        # Check errors
        check_errors = False
        for command_key, [process, _] in processes.items():
            error_message = process.stderr.read().decode()
            error = (True if (force_search and "error" in error_message.lower()) else
                     (False if force_search else len(error_message) > 0))
            if error:
                print("Thread " + str(command_key) + " error:")
                print(error_message + "\n")
                check_errors = True

        # Process execution summary
        if check_errors:
            return 0
        else:
            print("Process successfully completed\n")
            return 1

    @staticmethod
    async def asynchronous_task(command_key, command, force_search):
        # Create subprocess
        process = await asyncio.create_subprocess_shell(command, stdout=False, stderr=asyncio.subprocess.PIPE)

        # Inform the user the subprocess has started
        print("Subprocess " + command_key + " has started")

        # Wait for the subprocess to finish
        _, stderr = await process.communicate()

        # Inform the subprocess has finished
        print("\nSubprocess " + command_key + " has finished")

        # Check errors
        error_message = stderr.decode()
        error = (True if (force_search and "error" in error_message.lower()) else
                 (False if force_search else len(error_message) > 0))
        if error:
            print("Subprocess " + command_key + " error:")
            print(error_message)
            return 0
        else:
            return 1

    @staticmethod
    async def asynchronous_call(commands, force_search=False):
        # Generate asynchronous tasks
        tasks = \
        [
            Utils.asynchronous_task(command_key, command, force_search) for command_key, [command, _] in commands.items()
        ]

        # Declare var results
        results = [False]

        # Start the stopwatch
        start = time.time()

        # Wait asynchronous tasks
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
        except:
            print("Error in asynchronous calls")

        # Stop the stopwatch
        end = time.time()

        # Elapsed time
        print("\nElapsed time: " + str(end - start) + "s")

        # Process execution summary
        if all(results):
            print("\nProcess successfully completed\n")
            return 1
        else:
            return 0

    @staticmethod
    async def play(media_path, player_width=None, player_height=None, force_search=False):
        # Build command
        ffplay_command = "ffplay -i '" + str(media_path) + ("' -x " + str(player_width) if player_width else "'") + \
                         (" -y " + str(player_height) if player_height else "") + " -loglevel error"

        # Play
        process = await asyncio.create_subprocess_shell(ffplay_command, stderr=subprocess.PIPE)

        # Await for process execution
        _, stderr = await process.communicate()

        # Check errors
        error_message = stderr.decode()
        error = (True if (force_search and "error" in error_message.lower()) else
                 (False if force_search else len(error_message) > 0))
        if error:
            print("Process error:")
            print(error_message, end="")
            return 0
        else:
            return 1

    @staticmethod
    def create_video_fragment(video_name, output_video, seconds):
        # Set some vars
        num_frames = Utils.get_num_frames(video_name)
        channels = Utils.get_stream_value(video_name, "a", None, "channels").splitlines(False)

        # Commands
        print("Cutting video")
        ffmpeg_command = "ffmpeg -i '" + video_name + "' -t " + str(seconds) + " -acodec copy -vcodec copy" \
                         " -map 0:v:0 " + \
                         " ".join \
                         (
                             # Map all audio tracks to their related channel
                             ["-map 0:a:" + str(position) for position, _ in enumerate(channels)]
                         ) + \
                         " -y '" + output_video + "' -loglevel error -progress pipe:1"

        # Cut the input video
        success = Utils.sequential_call(ffmpeg_command, num_frames, False)

        # If success, use the fragment of the original video to boost performance
        if success:
            return 1
        else:
            return 0

    @staticmethod
    def burn_bit_rate(videos_to_process, delete_old=True):
        # References
        # https://stackoverflow.com/questions/21363334/how-to-add-font-size-in-subtitles-in-ffmpeg-video-filter
        # https://hhsprings.bitbucket.io/docs/programming/examples/ffmpeg/video_data_visualization/drawtext_with_pts_etc.html
        # https://ffmpeg.org/pipermail/ffmpeg-user/2015-December/029484.html
        # https://trac.ffmpeg.org/ticket/7946
        # https://superuser.com/questions/1106343/determine-video-bitrate-using-ffmpeg
        # https://stackoverflow.com/questions/18094304/what-is-the-packet-size-unit-of-ffprobesimilar-to-ffmpeg
        # https://slhck.info/video/2017/02/24/vbr-settings.html
        # https://stackoverflow.com/questions/65002949/how-to-include-font-in-ffmpeg-command-without-using-the-fontfile-option
        # https://superuser.com/questions/1603314/do-i-have-to-recompile-ffmpeg-in-order-to-enable-a-new-library

        # Set suffix for the name of the output videos
        suffix = "_bitrates"

        # Create a dictionary of key_name/[command,command_frames] to process
        commands = dict()

        # Create a list of the old videos to be deleted
        videos_to_delete = list()

        # Create a filter command por each video
        for video_key, video_name in videos_to_process.items():

            # Create output name
            index = video_name.find(".")
            output_name = video_name[:index] + suffix + video_name[index:]

            # Get frames size along with positions
            frames_info = Utils.get_frames_info(video_name, "v", 0, "size,pos").splitlines()

            # Some vars
            size_accumulator = 0.0  # [Kb]
            time_accumulator = 0.0  # [s]
            global_time_accumulator = 0.0  # [s]
            text_frequency = 1.0  # [s]
            video_duration = Utils.get_duration(video_name)  # [s]
            num_frames = int(Utils.get_num_frames(video_name))  # [n]
            frame_duration = video_duration / num_frames  # [s]

            # Build command to burn the bit rate per second in the video
            command = "ffmpeg -i '" + video_name + "' -c:a copy -filter_complex \""

            # For each line in frames info
            for frame_info in frames_info:

                # Split frame info
                frame_stats = frame_info.strip().split("|")

                # Get and accumulate frame info
                size_accumulator += int(frame_stats[0]) * 0.008
                time_accumulator += frame_duration
                global_time_accumulator += frame_duration

                # Append a drawtext filter to the command and reset accumulators
                if (time_accumulator > text_frequency) or (frame_info == frames_info[-1]):
                    # Get frame bit rate
                    frame_bit_rate = str(round(size_accumulator / time_accumulator))  # [Kb/s]

                    # Append drawtext filter in the right interval of time
                    command += "drawtext=font='Ubuntu':fontsize=60:fontcolor=white" \
                               ":text='" + frame_bit_rate + " kb/s'" \
                               ":x=(w - text_w - 100):y=(text_h + 30)" \
                               ":box=1:boxcolor=black:boxborderw=20" \
                               ":enable='between" \
                               "(t," + str(global_time_accumulator - time_accumulator) + "," + \
                               str(global_time_accumulator) + ")',"

                    # Reset accumulators
                    size_accumulator = 0.0
                    time_accumulator = 0.0

            # Delete last comma
            command = command[:-1] + "\" -y '" + output_name + "' -loglevel error -progress pipe:1"

            # Append command to the list of commands
            commands[video_key] = [command, num_frames]

            # Change the video name in the dictionary
            videos_to_process[video_key] = output_name

            # Append the old video to delete
            videos_to_delete.append(video_name)

        # Execute commands concurrently through threads
        success = Utils.threaded_call(commands)

        # Delete old videos
        if success and delete_old:
            for video_name in videos_to_delete:
                os.remove(video_name)

        # Return process success
        return success

    @staticmethod
    def generate_keys(key_id_name, key_name, root=""):

        # Commands
        generate_key_command = shlex.split('openssl rand 16')
        get_key_id_command = shlex.split("hexdump -v -e '/1 \"%02X\"' " + root + key_id_name)
        get_key_command = shlex.split("hexdump -v -e '/1 \"%02X\"' " + root + key_name)
        get_base64_key_id_command = shlex.split("base64 " + root + key_id_name)
        get_base64_key_command = shlex.split("base64 " + root + key_name)

        # Create dir
        os.makedirs(root, exist_ok=True)

        # Create key files
        file_key_id = open(root + key_id_name, "w")
        file_key = open(root + key_name, "w")

        # Generate keys
        subprocess.call(generate_key_command, stdout=file_key_id)
        subprocess.call(generate_key_command, stdout=file_key)

        # Get key values
        key_id_value = subprocess.check_output(get_key_id_command).decode()
        key_value = subprocess.check_output(get_key_command).decode()

        # Create base64 key files
        file_base64_key_id = open(root + 'base46_' + key_id_name, "w")
        file_base64_key =open(root + 'base46_' + key_name, "w")

        # Get base64 keys
        subprocess.call(get_base64_key_id_command, stdout=file_base64_key_id)
        subprocess.call(get_base64_key_command, stdout=file_base64_key)

        # Close files
        file_key_id.close()
        file_key.close()
        file_base64_key_id.close()
        file_base64_key.close()

        # Return key values
        return str(key_id_value), str(key_value)

    @staticmethod
    def check_process_syntax(command, output_name=None):
        # Trow a process and wait to seconds to see if there are syntax errors
        process = subprocess.Popen(shlex.split(command), stdout=False, stderr=subprocess.PIPE)

        # Wait 2 seconds and kill the process and delete the leftovers
        time.sleep(1)
        process.kill()
        if output_name and os.path.exists(output_name):
            os.remove(output_name)

        # Return output
        return process.stderr.read().decode()
