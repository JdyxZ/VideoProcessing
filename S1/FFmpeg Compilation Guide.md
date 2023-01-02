# MAIN BUILD
Standard compilation guide source: https://trac.ffmpeg.org/wiki/CompilationGuide/Ubuntu

# USEFUL INFO PAGES
- Remove Cuda & Nvidia Drivers: https://stackoverflow.com/questions/56431461/how-to-remove-cuda-completely-from-ubuntu
- Remove CUDA Tool Kit Version: https://docs.nvidia.com/cuda/cuda-installation-guide-linux/index.html (8.6. Uninstallation)
- Problems with nvcc or change nvcc cuda tool kit version manually: https://askubuntu.com/questions/885610/nvcc-version-command-says-nvcc-is-not-installed
- Solve not founding file libavdevice.so.5x (Just rebooting your system works): https://stackoverflow.com/questions/12901706/ffmpeg-error-in-linux -> use (/home/your_username/ffmpeg_build/lib/)

# STEP 1
sudo apt-get update -qq && sudo apt-get upgrade && sudo apt-get -y install \
	autoconf \
	automake \
	build-essential \
	cmake \
	git-core \
	libass-dev \
	libfreetype6-dev \
	libgnutls28-dev \
	libmp3lame-dev \
	libsdl2-dev \
	libtool \
	libva-dev \
	libvdpau-dev \
	libvorbis-dev \
	libxcb1-dev \
	libxcb-shm0-dev \
	libxcb-xfixes0-dev \
	meson \
	ninja-build \
	pkg-config \
	texinfo \
	wget \
	yasm \
	zlib1g-dev \
	libunistring-dev \
	libaom-dev \
	libdav1d-dev \
	nasm \
	build-essential \
	yasm \
	cmake \
	libtool \
	libc6 \
	libc6-dev \
	unzip \
	wget \
	libnuma1 \
	libmp3lame-dev \
	libx264-dev \
	libx265-dev \
	libnuma-dev \
	libvpx-dev \
	libfdk-aac-dev \
	libopus-dev \
	libdav1d-dev \
	v4l-utils \
	libssl-dev \
	libssl-doc \
	npm \
	fontconfig-config \
	cuda \
	python3-pip && \
	pip3 install --user meson

	
# STEP 2
sudo apt autoremove

# STEP 3
mkdir -p ~/ffmpeg_sources ~/bin

# STEP 4: AOM Encoder
cd ~/ffmpeg_sources && \
git -C aom pull 2> /dev/null || git clone --depth 1 https://aomedia.googlesource.com/aom && \
mkdir -p aom_build && \
cd aom_build && \
PATH="$HOME/bin:$PATH" cmake -G "Unix Makefiles" -DCMAKE_INSTALL_PREFIX="$HOME/ffmpeg_build" -DENABLE_TESTS=OFF -DENABLE_NASM=on ../aom && \
PATH="$HOME/bin:$PATH" make && \
make install

# STEP 5: AV1 Encoder
cd ~/ffmpeg_sources && \
git -C SVT-AV1 pull 2> /dev/null || git clone https://gitlab.com/AOMediaCodec/SVT-AV1.git && \
mkdir -p SVT-AV1/build && \
cd SVT-AV1/build && \
PATH="$HOME/bin:$PATH" cmake -G "Unix Makefiles" -DCMAKE_INSTALL_PREFIX="$HOME/ffmpeg_build" -DCMAKE_BUILD_TYPE=Release -DBUILD_DEC=OFF -DBUILD_SHARED_LIBS=OFF .. && \
PATH="$HOME/bin:$PATH" make && \
make install

# STEP 6: Video Quality Metrics (Definir bien la variable HOME o da problemas)
cd ~/ffmpeg_sources && \
wget https://github.com/Netflix/vmaf/archive/v2.1.1.tar.gz && \
tar xvf v2.1.1.tar.gz && \
mkdir -p vmaf-2.1.1/libvmaf/build &&\
cd vmaf-2.1.1/libvmaf/build && \
meson setup -Denable_tests=false -Denable_docs=false --buildtype=release --default-library=static .. --prefix "$HOME/ffmpeg_build" --bindir="$HOME/ffmpeg_build/bin" --libdir="$HOME/ffmpeg_build/lib" && \
ninja && \
ninja install

# STEP 7 (Only for NVIDIA users to enable hardware acceleration): Install Cuda Tool Kit

// Reference: https://developer.nvidia.com/cuda-downloads?target_os=Linux&target_arch=x86_64&Distribution=Ubuntu&target_version=22.04&target_type=deb_local

//WARNING!: If you have an older CUDA Tool Kit version installed try to remove it first. At the beginning of this guide there are some useful pages to do so. To sum up:

//- First try this: sudo /usr/local/cuda-<your cuda version goes here>/bin/cuda-uninstaller 
// - Else try this: sudo rm -rf /usr/local/cuda-<your cuda version goes here>

cd ~/ffmpeg_sources
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-ubuntu2204.pin
sudo mv cuda-ubuntu2204.pin /etc/apt/preferences.d/cuda-repository-pin-600
wget https://developer.download.nvidia.com/compute/cuda/11.8.0/local_installers/cuda-repo-ubuntu2204-11-8-local_11.8.0-520.61.05-1_amd64.deb
sudo dpkg -i cuda-repo-ubuntu2204-11-8-local_11.8.0-520.61.05-1_amd64.deb

cd ~/ffmpeg_sources
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-ubuntu2204.pin
sudo mv cuda-ubuntu2204.pin /etc/apt/preferences.d/cuda-repository-pin-600
wget https://developer.download.nvidia.com/compute/cuda/12.0.0/local_installers/cuda-repo-ubuntu2204-12-0-local_12.0.0-525.60.13-1_amd64.deb
sudo dpkg -i cuda-repo-ubuntu2204-12-0-local_12.0.0-525.60.13-1_amd64.deb
sudo cp /var/cuda-repo-ubuntu2204-12-0-local/cuda-*-keyring.gpg /usr/share/keyrings/
sudo apt-get update
sudo apt-get -y install cuda

//Once you have downloaded and install this command, try to run nvcc --version in the bash. If you find trouble or nvcc recognises and older cuda version, there is a page that at the beginning of this guida that addresses this problem

# STEP 8 (Only for NVIDIA users to enable hardware acceleration): Install FFmpeg Nvidia Codecs headers

// Reference: https://docs.nvidia.com/video-technologies/video-codec-sdk/ffmpeg-with-nvidia-gpu/

cd ~/ffmpeg_sources
git clone https://git.videolan.org/git/ffmpeg/nv-codec-headers.git
cd nv-codec-headers
make
sudo make install

//STEP 10 (Warning! Put your CUDA version in the extras if you are install Nvidia hardware acceleration)
cd ~/ffmpeg_sources && \
wget -O ffmpeg-snapshot.tar.bz2 https://ffmpeg.org/releases/ffmpeg-snapshot.tar.bz2 && \
tar xjvf ffmpeg-snapshot.tar.bz2 && \
cd ffmpeg && \
PATH="$HOME/bin:$PATH" PKG_CONFIG_PATH="$HOME/ffmpeg_build/lib/pkgconfig" ./configure \
  --prefix="$HOME/ffmpeg_build" \
  --pkg-config-flags="--static" \
  --extra-cflags="-I$HOME/ffmpeg_build/include" \
  --extra-ldflags="-L$HOME/ffmpeg_build/lib" \
  --extra-libs="-lpthread -lm" \
  --ld="g++" \
  --bindir="$HOME/bin" \
  --enable-gpl \
  --enable-gnutls \
  --enable-libaom \
  --enable-libass \
  --enable-libfdk-aac \
  --enable-libfreetype \
  --enable-libfontconfig \
  --enable-libmp3lame \
  --enable-libopus \
  --enable-libsvtav1 \
  --enable-libdav1d \
  --enable-libvorbis \
  --enable-libvpx \
  --enable-libx264 \
  --enable-libx265 \
  --enable-nonfree \
  --enable-4l2 \
  --extra-cflags=-I/usr/local/cuda-12.0/include \
  --extra-ldflags=-L/usr/local/cuda-12.0/lib64 \
  --enable-cuvid \
  --enable-vaapi \
  --enable-libnpp \
  --enable-cuda-nvcc \
  --enable-cuda-llvm \
  --enable-nvenc \
  --disable-static \
  --enable-shared && \
PATH="$HOME/bin:$PATH" make && \
make install && \
hash -r

//Don't use the following if you are not enabling nvidia hardware acceleration:  
  --extra-cflags=-I/usr/local/cuda-<place here your cuda version>/include \
  --extra-ldflags=-L/usr/local/cuda-<place here your cuda version>/lib64 \
  --enable-cuvid \
  --enable-vaapi \
  --enable-libnpp \
  --enable-cuda-nvcc \
  --enable-cuda-llvm \
  --enable-nvenc \
  --disable-static \
  --enable-shared

//STEP 11
source ~/.profile

//STEP 12
Reboot your system

//STEP 14
check everything is alright -> ffmpeg -version (it should output a strange number like N-109043-ga7ccfdc0d7)

//STEP 15: Delete ffmpeg sources
rm -rf ~/ffmpeg_sources

//STEP 15 (Optional)
Check Nvidia Hardware acceleration

ffmpeg -h encoder=hevc_nvenc

//Updating (Warning! This will delete all the work)
rm -rf ~/ffmpeg_build ~/home/bin{ffmpeg,ffprobe,ffplay,x264,x265}


# Bento 4 tools

git clone https://github.com/axiomatic-systems/Bento4.git
cd ~/Downloads/Bento4/

mkdir cmakebuild
cd cmakebuild
cmake -DCMAKE_BUILD_TYPE=Release ..
make

cmake --install

sudo cp -r /home/haylo/Downloads/Bento4/Source/Python/utils/ /usr/local/bin && \
sudo cp -r /home/haylo/Downloads/Bento4/Source/Python/wrappers /usr/local/bin

vim .bashrc
add -> export PATH="/usr/local/bin/wrappers:$PATH"


# NGINX

sudo apt-get install libssl-dev libssl-doc

cd ~/Downloads
git clone https://github.com/arut/nginx-rtmp-module.git 
git clone https://github.com/nginx/nginx.git 
cd nginx
./auto/configure --add-module=../nginx-rtmp-module 
make 
sudo make install

vim .bashrc
add -> export PATH="/usr/local/nginx/sbin:$PATH"




