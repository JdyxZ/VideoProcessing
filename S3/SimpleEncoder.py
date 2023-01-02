from tkinter import *
from customtkinter import *
from PIL import ImageTk, Image
from Utils import Utils
import os
import subprocess
import shlex
import time
import emoji


class SimpleEncoder(CTk):
    def __init__(self):
        # Create a Tkinter custom app instance
        super().__init__()

        # Get current root
        self.root = os.getcwd()

        # Set up the themes of the app
        set_appearance_mode("dark")
        set_default_color_theme("blue")

        # Get screen sizes
        screen_resolution = Utils.get_screen_resolution()
        self.screen_width = int(screen_resolution[0])
        self.screen_height = int(screen_resolution[1])

        # Create root
        # Reference:
        # https://www.youtube.com/watch?v=NoTM8JciWaQ
        # https://stackoverflow.com/questions/11176638/tkinter-tclerror-error-reading-bitmap-file
        self.title("Simple Encoder")
        self.geometry(str(self.screen_width // 2) + "x" + str(self.screen_height - 150))
        self.minsize(self.screen_width // 2, self.screen_height // 2)
        self.resizable(True, True)
        self.update()

        # Configure root grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # App global variables
        self.current_filepath = ""
        self.current_filename = ""
        self.ffmpeg_command = ""
        self.output_name = ""
        self.tk_process = None
        self.process_killed = False

        # App codec variables
        self.crf_var = IntVar()
        self.bit_rate_var = IntVar()
        self.speed_var = IntVar()
        self.preset = StringVar()
        self.tune_mode = StringVar()

        self.h265_presets = \
            [
            "ultrafast", "superfast", "veryfast", "faster", "fast", "medium", "slow", "slower", "veryslow", "placebo"
            ]
        self.h265_tune_modes = \
            [
            "disable", "psnr", "ssim", "grain", "zerolatency", "fastdecode"
            ]

        # Set default values to codec variables
        self.crf_var.set(30)
        self.bit_rate_var.set(1000)
        self.speed_var.set(5)
        self.preset.set(self.h265_presets[5])
        self.tune_mode.set(self.h265_tune_modes[0])

        # Create main frame
        self.main_frame = CTkFrame(self)
        self.main_frame.pack(fill="both", expand=1)
        self.main_frame.bind("<Configure>", self.handle_configure)

        # Create a canvas and append a scrollbar
        # Reference: https://www.youtube.com/watch?v=0WafQCaok6g
        self.canvas = Canvas(self.main_frame, bg='gray17')
        self.canvas.pack(side=LEFT, fill="both", expand=1)
        self.scrollbar = CTkScrollbar(self.main_frame, orientation="vertical", command=self.canvas.yview)
        self.scrollbar.pack(side=RIGHT, fill="y")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        # Create the app frame
        self.app_frame = CTkFrame(self.canvas)
        self.canvas.create_window((0,0), window=self.app_frame, anchor="nw")

        # Create widget frames
        self.file_manager = CTkFrame(self.app_frame, corner_radius=10)
        self.codec_tabs = CTkTabview(self.app_frame, width=self.screen_width//2 - 50)
        self.codec_tabs.add("VP8")
        self.VP8_tab = self.codec_tabs.tab("VP8")
        self.codec_tabs.add("VP9")
        self.VP9_tab = self.codec_tabs.tab("VP9")
        self.codec_tabs.add("AV1")
        self.AV1_tab = self.codec_tabs.tab("AV1")
        self.codec_tabs.add("h265")
        self.h265_tab = self.codec_tabs.tab("h265")
        self.bash_frame = CTkFrame(self.app_frame, corner_radius=10)
        self.output_frame = CTkFrame(self.app_frame, corner_radius=10)

        # Set initial tab
        self.codec_tabs.set("VP8")

        # Place widget frames
        self.file_manager.pack(padx=10, pady=20, fill="both", expand=1)
        self.codec_tabs.pack(padx=10, pady=20, fill="both", expand=1)
        self.bash_frame.pack(padx=10, pady=20, fill="both", expand=1)
        self.output_frame.pack(padx=10, pady=20, fill="both", expand=1)

        # Configure frame grids
        self.file_manager.columnconfigure((0,1,2), weight=1)
        self.file_manager.rowconfigure((0,1), weight=1)
        self.VP8_tab.columnconfigure((0,1,2), weight=1)
        self.VP8_tab.rowconfigure((0,1,2,3), weight=1)
        self.VP8_tab.columnconfigure(1, weight=4)
        self.VP9_tab.columnconfigure((0,1,2), weight=1)
        self.VP9_tab.rowconfigure((0,1,2), weight=1)
        self.VP9_tab.columnconfigure(1, weight=4)
        self.AV1_tab.columnconfigure((0,1,2), weight=1)
        self.AV1_tab.rowconfigure((0,1,2), weight=1)
        self.AV1_tab.columnconfigure(1, weight=4)
        self.h265_tab.columnconfigure((0,1,2,3), weight=1)
        self.h265_tab.rowconfigure((0,1,2), weight=1)
        self.bash_frame.rowconfigure((0,1,2,3), weight=1)
        self.bash_frame.columnconfigure(0, weight=1)
        self.output_frame.rowconfigure((0,1,2,3,4,5), weight=1)
        self.output_frame.columnconfigure((0,1), weight=1)

        # File manager
        self.file_label = CTkLabel\
            (self.file_manager, text="Open File", font=CTkFont(family="Ubuntu", weight="bold", size=14))
        self.file_opener = CTkButton\
            (self.file_manager, text="Open", font=CTkFont(family="Ubuntu", weight="bold"), command=self.file_dialog)
        self.file_name = CTkLabel(self.file_manager, text="", font=CTkFont(family="Ubuntu", weight="bold"))
        self.remove_file = CTkButton\
            (self.file_manager, text="Remove", font=CTkFont(family="Ubuntu",weight="bold"), command=self.remove_file)

        self.file_label.grid(row=0, column=0, columnspan=3, pady=10, sticky="nsew")
        self.file_opener.grid(row=1, column=0, pady=10)
        self.file_name.grid(row=1, column=1, pady=10)

        # VP8 Frame
        self.encoder_settings = \
            CTkLabel(self.VP8_tab, text="Encoder Settings", font=CTkFont(family="Ubuntu", weight="bold", size=14))
        self.crf_label = CTkLabel(self.VP8_tab, text="CRF", font=CTkFont(family="Ubuntu"))
        self.crf_slider = CTkSlider\
            (
                self.VP8_tab,
                variable=self.crf_var,
                from_=-1, to=63,
                number_of_steps=65,
                command=lambda e: self.slider_event(e)
            )
        self.VP8_crf_value = CTkLabel(self.VP8_tab, text=str(self.crf_var.get()), font=CTkFont(family="Ubuntu"))
        self.bit_rate_label = CTkLabel(self.VP8_tab, text="Bitrate", font=CTkFont(family="Ubuntu"))
        self.bit_rate_slider = CTkSlider\
            (self.VP8_tab, variable=self.bit_rate_var, from_=1, to=100000, command=lambda e: self.slider_event(e))
        self.VP8_bit_rate_value = CTkLabel\
            (self.VP8_tab, text=str(self.bit_rate_var.get()) + " kb/s", font=CTkFont(family="Ubuntu"))
        self.speed_label = CTkLabel(self.VP8_tab, text="Speed", font=CTkFont(family="Ubuntu"))
        self.speed_slider = CTkSlider\
            (
                self.VP8_tab,
                variable=self.speed_var,
                from_=-16, to=16,
                number_of_steps=33,
                command=lambda e: self.slider_event(e)
            )
        self.VP8_speed_value = CTkLabel(self.VP8_tab, text=str(self.speed_var.get()) + "x")

        self.encoder_settings.grid(row=0, column=0, columnspan=3, pady=10)
        self.crf_label.grid(row=1, column=0, pady=15)
        self.crf_slider.grid(row=1, column=1, pady=10, sticky="ew")
        self.VP8_crf_value.grid(row=1, column=2, pady=10)
        self.bit_rate_label.grid(row=2, column=0, pady=10)
        self.bit_rate_slider.grid(row=2, column=1, pady=10, sticky="ew")
        self.VP8_bit_rate_value.grid(row=2, column=2, pady=10)
        self.speed_label.grid(row=3, column=0, pady=10)
        self.speed_slider.grid(row=3, column=1, pady=10, sticky="ew")
        self.VP8_speed_value.grid(row=3, column=2, pady=10)

        # VP9 Frame
        self.encoder_settings = CTkLabel\
            (self.VP9_tab, text="Encoder Settings", font=CTkFont(family="Ubuntu", weight="bold", size=14))
        self.crf_label = CTkLabel(self.VP9_tab, text="CRF", font=CTkFont(family="Ubuntu"))
        self.crf_slider = CTkSlider\
            (
                self.VP9_tab,
                variable=self.crf_var,
                from_=-1, to=63,
                number_of_steps=65,
                command=lambda e: self.slider_event(e))
        self.VP9_crf_value = CTkLabel(self.VP9_tab, text=str(self.crf_var.get()))
        self.speed_label = CTkLabel(self.VP9_tab, text="Speed", font=CTkFont(family="Ubuntu"))
        self.speed_slider = CTkSlider\
            (
                self.VP9_tab,
                variable=self.speed_var,
                from_=-8, to=8,
                number_of_steps=17,
                command=lambda e: self.slider_event(e)
            )
        self.VP9_speed_value = CTkLabel(self.VP9_tab, text=str(self.speed_var.get()) + "x")

        self.encoder_settings.grid(row=0, column=0, columnspan=3, pady=10)
        self.crf_label.grid(row=1, column=0, pady=10)
        self.crf_slider.grid(row=1, column=1, pady=10, sticky="ew")
        self.VP9_crf_value.grid(row=1, column=2, pady=10)
        self.speed_label.grid(row=2, column=0, pady=10)
        self.speed_slider.grid(row=2, column=1, pady=10, sticky="ew")
        self.VP9_speed_value.grid(row=2, column=2, pady=10)

        # AV1 Frame
        self.encoder_settings = CTkLabel\
            (self.AV1_tab, text="Encoder Settings", font=CTkFont(family="Ubuntu", weight="bold", size=14))
        self.crf_label = CTkLabel(self.AV1_tab, text="CRF", font=CTkFont(family="Ubuntu"))
        self.crf_slider = CTkSlider\
            (
                self.AV1_tab,
                variable=self.crf_var,
                from_=0, to=63,
                number_of_steps=64,
                command=lambda e: self.slider_event(e)
            )
        self.AV1_crf_value = CTkLabel(self.AV1_tab, text=str(self.crf_var.get()))
        self.speed_label = CTkLabel(self.AV1_tab, text="Speed", font=CTkFont(family="Ubuntu"))
        self.speed_slider = CTkSlider\
            (
                self.AV1_tab,
                variable=self.speed_var,
                from_=-1, to=13,
                number_of_steps=15,
                command=lambda e: self.slider_event(e)
            )
        self.AV1_speed_value = CTkLabel(self.AV1_tab, text=str(self.speed_var.get()) + "x")

        self.encoder_settings.grid(row=0, column=0, columnspan=3, pady=10)
        self.crf_label.grid(row=1, column=0, pady=10)
        self.crf_slider.grid(row=1, column=1, pady=10, sticky="ew")
        self.AV1_crf_value.grid(row=1, column=2, pady=10)
        self.speed_label.grid(row=2, column=0, pady=10)
        self.speed_slider.grid(row=2, column=1, pady=10, sticky="ew")
        self.AV1_speed_value.grid(row=2, column=2, pady=10)

        # h265 Frame
        self.encoder_settings = CTkLabel\
            (self.h265_tab, text="Encoder Settings", font=CTkFont(family="Ubuntu", weight="bold", size=14))
        self.crf_label = CTkLabel(self.h265_tab, text="CRF", font=CTkFont(family="Ubuntu"))
        self.crf_slider = CTkSlider\
            (
                self.h265_tab,
                variable=self.crf_var,
                from_=0, to=63,
                number_of_steps=64,
                command=lambda e: self.slider_event(e)
            )
        self.h265_crf_value = CTkLabel(self.h265_tab, text=str(self.crf_var.get()))
        self.preset_label = CTkLabel(self.h265_tab, text="Preset", font=CTkFont(family="Ubuntu"))
        self.preset_combo = CTkOptionMenu(self.h265_tab, variable=self.preset, values=self.h265_presets)
        self.tune_label = CTkLabel(self.h265_tab, text="Tune", font=CTkFont(family="Ubuntu"))
        self.tune_combo = CTkOptionMenu(self.h265_tab, variable=self.tune_mode, values=self.h265_tune_modes)

        # Reference:
        # https://stackoverflow.com/questions/21893288/tkinter-columconfigure-and-rowconfigure

        self.encoder_settings.grid(row=0, column=0, pady=10, columnspan=4, sticky="nsew")
        self.crf_label.grid(row=1, column=0, pady=10, padx=60)
        self.crf_slider.grid(row=1, column=1, columnspan=2, pady=10, sticky="ew")
        self.h265_crf_value.grid(row=1, column=3, pady=10)
        self.preset_label.grid(row=2, column=0, pady=10)
        self.preset_combo.grid(row=2, column=1, pady=10, sticky="w")
        self.tune_label.grid(row=2, column=2, pady=10)
        self.tune_combo.grid(row=2, column=3, pady=10, sticky="w")

        # Bash frame
        self.bash_label = CTkLabel\
            (self.bash_frame, text="Additional Options", font=CTkFont(family="Ubuntu", weight="bold", size=14))
        self.bash_entry = CTkEntry\
            (
                self.bash_frame,
                placeholder_text="Write additional codec options here if desired",
                height=40,
                font=CTkFont(family="Ubuntu")
            )
        self.bash_message = CTkTextbox(self.bash_frame, state="disabled", font=CTkFont(family="Ubuntu"))
        self.check_syntax_button = CTkButton\
            (
                self.bash_frame,
                text="Check Syntax",
                font=CTkFont(family="Ubuntu", weight="bold"),
                command=self.check_syntax
            )

        self.bash_label.grid(row=0, column=0, pady=15, sticky="nsew")
        self.bash_entry.grid(row=1, column=0, pady=15, sticky="ew")
        self.bash_message.grid(row=2, column=0, pady=10, sticky="ew")
        self.check_syntax_button.grid(row=3, column=0, pady=10, ipady=15)

        # Output frame
        self.output_label = CTkLabel\
            (self.output_frame, text="Output Settings", font=CTkFont(family="Ubuntu",weight="bold", size=14))
        self.output_entry = CTkEntry\
            (
                self.output_frame,
                placeholder_text="Write the name of the output video with its extension",
                height=40,
                font=CTkFont(family="Ubuntu")
            )
        self.output_message = CTkTextbox(self.output_frame, state="disabled", font=CTkFont(family="Ubuntu"))
        self.progress_bar = CTkProgressBar\
            (self.output_frame, orientation="horizontal", height=10, mode="determinate", corner_radius=15)
        self.progress_percentage = CTkLabel(self.output_frame, text="0%", font=CTkFont(family="Ubuntu", weight="bold"))
        self.process_button = CTkButton\
            (self.output_frame, text="Process", font=CTkFont(family="Ubuntu", weight="bold"), command=self.process)
        self.stop_button = CTkButton\
            (
                self.output_frame,
                text="Stop",
                font=CTkFont(family="Ubuntu", weight="bold"),
                state="disabled",
                command=self.stop_process
            )

        self.output_label.grid(row=0, column=0, pady=15, columnspan=2, sticky="nsew")
        self.output_entry.grid(row=1, column=0, pady=15, columnspan=2, sticky="ew")
        self.output_message.grid(row=2, column=0, pady=10, columnspan=2, sticky="ew")
        self.process_button.grid(row=5, column=0, padx=15, pady=15, ipady=15, sticky="nse")
        self.stop_button.grid(row=5, column=1, padx=15, pady=15, ipady=15, sticky="nsw")

        # Debug windows
        self.debug_windows()

    # App functions
    def build_ffmpeg_command(self):

        # Get some vars
        current_tab = self.codec_tabs.get()
        codec = ""
        crf = ""
        speed = ""
        tune = ""
        additional_options = self.bash_entry.get()
        if current_tab == "VP8":
            codec = "libvpx "
            crf = "-crf " + str(self.crf_var.get()) + " -b:v 0 "
            speed = "-cpu-used " + str(self.speed_var.get()) + " "
        elif current_tab == "VP9":
            codec = "libvpx-vp9 "
            crf = "-crf " + str(self.crf_var.get()) + " -b:v 0 "
            speed = "-cpu-used " + str(self.speed_var.get()) + " "

        elif current_tab == "AV1":
            codec = "libsvtav1 "
            crf = "-crf " + str(self.crf_var.get()) + " "
            speed = "-preset " + str(self.speed_var.get()) + " "

        elif current_tab == "h265":
            codec = "libx265 "
            crf = "-crf " + str(self.crf_var.get()) + " "
            speed = "-preset " + self.preset.get() + " "
            tune = ("-tune " + self.tune_mode.get() if self.tune_mode.get() != "disable" else "") + " "
            if additional_options.find("log-level=error") == -1:
                index = additional_options.find("-x265-params")
                count = len("-x265-params")
                if index != -1:
                    additional_options = \
                        additional_options[:index + count + 1] + "log-level=error:" + additional_options[index + count + 1:]
                else:
                    additional_options += "-x265-params log-level=error"

        channels = \
            (Utils.get_stream_value(self.current_filepath, "a", None, "channels").splitlines(False)
             if self.current_filepath else "")

        self.output_name = self.output_entry.get()

        # Command
        self.ffmpeg_command = "ffmpeg -i '" + self.current_filename + "' -c:a copy -c:v " + codec + \
                         crf + speed + tune + additional_options + \
                         " -map 0:v:0 " + \
                         " ".join \
                            (
                                # Map all audio tracks to their related channel
                                ["-map 0:a:" + str(position) for position, _ in enumerate(channels)]
                            ) + \
                         " -y '" + self.output_name + "' -loglevel error -progress pipe:1"

    def check_syntax(self, only_return=False, force_search=False):
        # References:
        # https://www.youtube.com/watch?v=3YmZWV7iBJE
        # https://pypi.org/project/emoji/

        # Build ffmpeg command
        self.build_ffmpeg_command()

        # Change working directory
        if self.current_filepath:
            index = self.current_filepath.rfind("/")
            current_directory = self.current_filepath[:index]
            os.chdir(current_directory)

        # Define some vars
        output_message = "Command:\n" + self.ffmpeg_command + "\n\nChecks: "
        error_found = False

        # Checks
        if not self.current_filename:
            output_message += emoji.emojize(":cross_mark_button:\n Error: No video input has been chosen")
            error_found = True
        elif not self.output_name:
            output_message += emoji.emojize(":cross_mark_button:\n Error: No video output name has been specified")
            error_found = True
        elif self.output_name.find(".mkv") == -1 and self.output_name.find(".mp4") == -1:
            output_message += emoji.emojize(":cross_mark_button:\n Error: Video output extension is missing or is wrong"
                                            " (available video containers are mkv and mp4)")
            error_found = True
        else:
            # Check syntax errors
            result = Utils.check_process_syntax(self.ffmpeg_command, self.output_name)

            error_found = (True if (force_search and "error" in result.lower()) else
                           (False if force_search else len(result) > 0))

            if error_found:
                output_message += emoji.emojize(":cross_mark_button:\n") + result

        # Append good feedback if no errors have been found
        if not error_found:
            output_message += emoji.emojize(":check_mark_button:\n No errors have been found!")

        # Show message in the bash text box
        if not only_return:
            self.bash_message.configure(state="normal", text_color=("red" if error_found else "green"))
            self.bash_message.delete("0.0", END)
            self.bash_message.insert("0.0", output_message)
            self.bash_message.configure(state="disabled")

        # Return
        return error_found

    def process(self):
        # References:
        # https://www.youtube.com/watch?v=Grbx15jRjQA

        # Check syntax before processing
        error = self.check_syntax(only_return=True, force_search=True)

        # Error management
        if error:
            self.output_message.configure(state="normal")
            self.output_message.delete("0.0", END)
            self.output_message.insert("0.0", "It seems there is some syntax error in your ffmpeg command. Try to check syntax")
            self.output_message.configure(state="disabled")
            return

        # Disable process button and enable stop button while processing
        self.process_button.configure(state="disabled")
        self.stop_button.configure(state="normal")

        # Reset and place progress widgets
        self.output_message.configure(state="normal")
        self.output_message.delete("0.0", END)
        self.output_message.configure(state="disabled")
        self.progress_bar.set(0)
        self.progress_percentage.configure(text="0%")
        self.progress_bar.grid(row=3, column=0, padx=100, pady=15, columnspan=2, sticky="ew")
        self.progress_percentage.grid(row=4, column=0, pady=5, columnspan=2, sticky="nswe")
        self.debug_windows()

        # Get num frames
        num_frames = Utils.get_num_frames(self.current_filename)

        # Process
        Utils.sequential_call(self.ffmpeg_command, num_frames, tk_app=self)

        # Drop progress widgets
        self.progress_bar.grid_forget()
        self.progress_percentage.grid_forget()

        # Enable again process button and disable stop button
        self.process_button.configure(state="normal")
        self.stop_button.configure(state="disabled")

    def stop_process(self):
        self.tk_process.kill()
        self.process_killed = True

    def file_dialog(self):
        # Reference: https://www.youtube.com/watch?v=Aim_7fC-inw

        # Current directory
        index = 0
        if self.current_filepath:
            index = self.current_filepath.rfind("/")
            current_directory = self.current_filepath[:index]
        else:
            current_directory = self.root

        # File dialog
        result = filedialog.askopenfilename\
            (
                initialdir=current_directory,
                title="Select a video file",
                filetypes=(("valid files", ("*.mkv", "*.mp4")),
                           ("mkv files", "*.mkv"), ("mp4 files", "*.mp4"), ("all files", "*.*"))

            )
        if result:
            self.current_filepath = result

        # Update filename and show remove button
        if self.current_filepath:
            index = self.current_filepath.rfind("/")
            self.current_filename = self.current_filepath[index + 1:]
            self.file_name.configure(text=self.current_filename)
            self.remove_file.grid(row=1, column=2, pady=10)

    def debug_windows(self):
        # Debug: Make scroll functional since the first moment
        current_height = self.winfo_height()
        self.geometry(str(self.winfo_width()) + "x" + str(self.screen_height))
        self.update()
        self.geometry(str(self.winfo_width()) + "x" + str(current_height))

    def remove_file(self):
        # Reset current filename
        self.current_filename = ""

        # Update filename and hide remove button
        self.file_name.configure(text="")
        self.remove_file.grid_forget()

    def handle_configure(self, event=0):
        # Reference:
        # https://stackoverflow.com/questions/43306771/is-there-a-way-to-check-for-changes-in-python-tk-windows
        try:
            self.codec_tabs.configure(width=self.winfo_width() - 50)
        except:
            NONE

    def slider_event(self, event=0):
        self.VP8_bit_rate_value.configure(text=str(self.bit_rate_var.get()) + " kb/s")
        self.VP8_crf_value.configure(text=str(self.crf_var.get()))
        self.VP8_speed_value.configure(text=str(self.speed_var.get()) + "x")
        self.VP9_crf_value.configure(text=str(self.crf_var.get()))
        self.VP9_speed_value.configure(text=str(self.speed_var.get()) + "x")
        self.AV1_crf_value.configure(text=str(self.crf_var.get()))
        self.AV1_speed_value.configure(text=str(self.speed_var.get()) + "x")
        self.h265_crf_value.configure(text=str(self.crf_var.get()))


# Main loop run
if __name__ == "__main__":
    app = SimpleEncoder()
    app.mainloop()
