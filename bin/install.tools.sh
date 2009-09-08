#!/bin/bash
HELP_MSG="\n \
Public Videos transcoding tools installation script v 1.0 (Ubuntu)\n
Usage: sh publicvideos.install.tools.sh /your/sources/path\n
\n
The sources path is the base path for where the script should fetch the source \n
files for the different tools.\n\
"
SOURCES_PATH=$1

OGG_SRC_URL="http://svn.xiph.org/trunk/ogg"
VORBIS_SRC_URL="http://svn.xiph.org/trunk/vorbis"
THEORA_SRC_URL="http://svn.xiph.org/trunk/theora"
X264_SRC_URL="git://git.videolan.org/x264.git"
#FAAC_SRC_URL="http://downloads.sourceforge.net/faac/faac-1.28.tar.bz2"
MPLAYER_SRC_URL="svn://svn.mplayerhq.hu/mplayer/trunk"
FFMPEG_SRC_URL="svn://svn.ffmpeg.org/ffmpeg/trunk"
FFMPEG2THEORA_SRC_URL="http://svn.xiph.org/trunk/ffmpeg2theora"

starttime=$SECONDS
# success and fail messages
function success {
  echo Step "$1" Succeeded
}
function fail {
  echo Step "$1" Failed. Exiting.
  exit 1
}

# correct usage checks
function step0 {
  # displays the help message if the sources path argument is not given
  if [ -z "$SOURCES_PATH" ]; then
    echo -e $HELP_MSG
    exit 1
  fi
  # checks if the provided path for the sources exists
  if [ -d "$SOURCES_PATH" ]; then
   return
  else
    echo "Error: you need to provide a valid path for where to keep the source files. Exiting."
    exit 1
  fi
}

function step1 {
  echo && echo "STEP 1: Install version control and buinding tools (plus libfaac that we dont want to compile since it is a pain in the ass)..."
  sudo apt-get install faac libfaac-dev git-core subversion wget yasm gcc autoconf automake libtool scons pkg-config zlib1g zlib1g-dev
  return $?
}
# getsource [svn|git|tar_bz] [repository_url] [label] [folder_name]
# Retrieves the source files from the Internet and copy it to folder_name
function getsource {
  if [ "$1" = "svn" ]; then
    GET_COMMAND="svn co $2 $SOURCES_PATH/$4"
    REV_EXPR=".* revision \([0-9]*\)"
    AFTER_GET_COMMAND=
  elif [ "$1" = "git" ]; then
    GET_COMMAND="git clone $2 $SOURCES_PATH/$4"
    AFTER_GET_COMMAND="cat $SOURCES_PATH/$4/.git/refs/heads/master"
    REV_EXPR="\(.*\)"
  elif [ "$1" = "tar_bz2" ]; then
    REMOTE_FILENAME=${2##*\/}
    GET_COMMAND="wget -q -O $SOURCES_PATH/$REMOTE_FILENAME $2"
    AFTER_GET_COMMAND="tar -xjf \"$SOURCES_PATH/$REMOTE_FILENAME\" -C \"$SOURCES_PATH/\"&&mv \"$SOURCES_PATH/${REMOTE_FILENAME/.tar.bz2/}\" \"$SOURCES_PATH/$4\"&&rm \"$SOURCES_PATH/$REMOTE_FILENAME\"&&echo $2"
    REV_EXPR=".*/.*-\(.*\)\.tar\.bz2"
  fi
  echo -n "Downloading $3..."
  DOWNLOAD=`$GET_COMMAND`
  EXIT_CODE=$?
  if [ "$EXIT_CODE" != "0" ]; then 
    echo $EXIT_CODE
    return $EXIT_CODE;
  else
    if [ ! -z "$AFTER_GET_COMMAND" ]; then
      DOWNLOAD=`eval "$AFTER_GET_COMMAND"`
    fi
    REVISION=`expr "$DOWNLOAD" : "$REV_EXPR"`
    echo " done. Revision $REVISION."
  fi
}
function step2 {
  echo && echo "STEP 2: Download all sources."
  # Ogg
  if getsource svn "$OGG_SRC_URL" Ogg ogg; then OGG_REVISION="$REVISION"; else return 1; fi
  # Vorbis
  if getsource svn "$VORBIS_SRC_URL" Vorbis vorbis; then VORBIS_REVISION="$REVISION"; else return 1; fi
  # Theora
  if getsource svn "$THEORA_SRC_URL" Theora theora; then THEORA_REVISION="$REVISION"; else return 1; fi
  # x264
  if getsource git "$X264_SRC_URL" x264 x264; then X264_REVISION="$REVISION"; else return 1; fi
  # FAAC
  #if getsource tar_bz2 "$FAAC_SRC_URL" FAAC faac; then FAAC_REVISION="$REVISION"; else return 1; fi
  # MPlayer
  if getsource svn "$MPLAYER_SRC_URL" MPlayer mplayer; then MPLAYER_REVISION="$REVISION"; else return 1; fi
  # FFMPeg
  if getsource svn "$FFMPEG_SRC_URL" FFMpeg ffmpeg; then FFMPEG_REVISION="$REVISION"; else return 1; fi
  # ffmpeg2theora
  if getsource svn "$FFMPEG2THEORA_SRC_URL" ffmpeg2theora ffmpeg2theora; then FFMPEG2THEORA_REVISION="$REVISION"; else return 1; fi
}
function checkerror {
  if [ "$?" = "0" ]; then echo Done.; else fail $STEP; fi
}
function stepb3 {
  # zlib on Ubuntu Karmic alpha 5 has a bug 
  # https://bugs.launchpad.net/ubuntu/+source/faac/+bug/181389 
  # patching is needed in order to work
  echo;echo "STEP 3: Compile all sources."
  ORIGINAL_PATH=`pwd`
  cd $SOURCES_PATH

  STEP="3.1"
  echo;echo "$STEP. Compile Ogg:"
  cd ogg
  ./autogen.sh; checkerror
  make; checkerror
  sudo make install; checkerror
  echo "Press any key...";read

  STEP="3.2"
  echo;echo "$STEP. Compile Vorbis:"
  cd ../vorbis
  ./autogen.sh; checkerror
  make; checkerror
  sudo make install; checkerror
  echo "Press any key...";read

  STEP="3.3"
  echo;echo "$STEP. Compile Theora:"
  cd ../theora
  ./autogen.sh; checkerror
  make; checkerror
  sudo make install; checkerror
  echo "Press any key...";read

  STEP="3.4"
  echo;echo "$STEP. Compile x264:"
  cd ../x264
  ./configure; checkerror
  make; checkerror
  sudo make install; checkerror
  echo "Press any key...";read

#  STEP="3.5"
#  echo;echo "$STEP. Compile FAAC:"
#  cd ../faac
#  ./configure; checkerror
#  make; checkerror
#  sudo make install; checkerror
#  echo "Press any key...";read

  STEP="3.5"
  echo;echo "$STEP. Compile MPlayer/Mencoder:"
  cd ../mplayer
  ./configure --enable-encoder=libx264 --enable-encoder=libfaac; checkerror
  make; checkerror
  sudo make install; checkerror
  echo "Press any key...";read

  STEP="3.6"
  echo;echo "$STEP. Compile FFMpeg:"
  cd ../ffmpeg
  ./configure --enable-gpl --enable-nonfree --enable-pthreads --enable-libtheora --enable-libvorbis --enable-libx264 --enable-libfaac
  checkerror
  make; checkerror
  sudo make install; checkerror
  echo "Press any key...";read

  STEP="3.7"
  echo;echo "$STEP. Compile ffmpeg2theora:"
  cd ../ffmpeg2theora
  ./get_ffmpeg_svn.sh; checkerror
  scons; checkerror
  sudo scons install; checkerror
  echo "Press any key...";read

  cd $ORIGINAL_PATH
}
function printsummary {
  echo "Installed Tools:"
  echo -e "Ogg\t\t$OGG_REVISION"
  echo -e "Vorbis\t\t$VORBIS_REVISION"
  echo -e "Theora\t\t$THEORA_REVISION"
  echo -e "x264\t\t$X264_REVISION"
  echo -e "MPlayer\t\t$MPLAYER_REVISION"
  echo -e "FFMPeg\t\t$FFMPEG_REVISION"
  echo -e "ffmpeg2theora\t$FFMPEG2THEORA_REVISION"
}
step0
#STEP=1; if step1; then success $STEP; else fail $STEP; fi
#STEP=2; if step2; then success $STEP; else fail $STEP; fi
#STEP=3; if step3; then success $STEP; else fail $STEP; fi
printsummary
totaltime=$((SECONDS - starttime))
echo "Total time: $totaltime seconds."
