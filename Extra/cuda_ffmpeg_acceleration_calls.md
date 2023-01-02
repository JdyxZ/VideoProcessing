ffmpeg -y -vsync 0 -hwaccel cuda -hwaccel_output_format cuda -i BBB.mp4 -c:a copy -c:v h264_nvenc -b:v 5M output.mkv

ffmpeg -benchmark -y -hwaccel cuda -hwaccel_output_format cuda -i MiA1.mkv -vf subtitles=MiA1.mkv -pix_fmt yuv420p -c:v hevc_nvenc -preset slow -rc vbr_hq -b:v 6M -maxrate:v 10M output.mkv

ffmpeg -benchmark -y -hwaccel cuvid -i MiA1.mkv -c:v hevc_cuvid -vf subtitles=MiA1.mkv output.mkv

ffmpeg -benchmark -y -i MiA1.mkv -vf subtitles=MiA1.mkv output.mkv

ffmpeg -benchmark -y -hwaccel cuda -hwaccel_output_format cuda -i MIA_FILM_H264.mkv -c:a copy -c:v hevc_nvenc -preset:v p7 -tune:v hq -cq:v 19 -b:v 0 -rc:v vbr -pix_fmt:v p010le -b_ref_mode disabled -vf subtitles=MIA_FILM_H264.mkv -sn MIA_FILM_H265.mkv

ffmpeg -benchmark -y -hwaccel cuda -hwaccel_output_format cuda -i Mia01.mkv -c:a copy -c:v hevc_nvenc -preset:v p7 -tune:v hq -cq:v 19 -b:v 0 -rc:v vbr -pix_fmt:v p010le -b_ref_mode disabled -vf subtitles=Mia01.mkv -sn Mia01_H265.mkv

ffmpeg -i MIA_FILM_H264.mkv -c:a copy -c:v libaom-av1 -crf 20 -b:v 0 -cpu-used 0 -row-mt 1 -tiles 2x2 -pix_fmt yuv420p10le -y MIA_FILM_H265.mkv


# Benchmarks
AV1
bench: utime=10824.800s stime=13.834s rtime=1117.088s
bench: maxrss=6297068kB

h265
bench: utime=2267.272s stime=2.718s rtime=171.538s
bench: maxrss=1151304kB

VP8
bench: utime=1133.847s stime=0.800s rtime=96.577s
bench: maxrss=268516kB

VP9
bench: utime=2157.816s stime=3.909s rtime=249.672s
bench: maxrss=562936kB



ffmpeg_command = 'ffmpeg -hwaccel cuda -hwaccel_output_format cuda -i "' + self.video_name + '" -filter_complex "' \
'[0:v]split=3[v1][v2][v3];' \
'[v1]copy[1080p_video];' \
'[v2]scale=w=1280:h=720:flags=lanczos[720p_video];' \
'[v3]scale=w=640:h=360:flags=lanczos[360p_video]" ' \
'-map [1080p_video] -c:v:0 hevc_nvenc -preset fast -b:v:0 6000k -g 48 -sc_threshold 0 -keyint_min 48 ' \
'-map [720p_video] -c:v:1 hevc_nvenc -preset fast -b:v:1 3000k -g 48 -sc_threshold 0 -keyint_min 48 ' \
'-map [360p_video] -c:v:2 hevc_nvenc -preset fast -b:v:2 365k -g 48 -sc_threshold 0 -keyint_min 48 ' \
'c:a copy -y output.mkv'

