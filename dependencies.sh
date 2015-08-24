#Things to be installed:
#    ffmpeg >= 2.6.2
#    pydub >= 0.11
#    pyaudio >= 0.2.7
#    numpy >= 1.8.2
#    scipy >= 0.13.3
#    matplotlib >= 1.3.1
#    mysqldb >= 1.2.3
#    opencv >= 2.4.8
#    django >= 1.6.1

echo "Installing ffmpeg"
sudo apt-get install build-essential libmp3lame-dev libvorbis-dev libtheora-dev libspeex-dev yasm pkg-config libfaac-dev libopenjpeg-dev libx264-dev libvpx-dev
mkdir software
cd software
wget http://ffmpeg.org/releases/ffmpeg-2.7.2.tar.bz2
cd ..
mkdir src
cd src
tar xvjf ../software/ffmpeg-2.7.2.tar.bz2
cd ffmpeg-2.7.2
./configure --enable-gpl --enable-postproc --enable-swscale --enable-avfilter --enable-libmp3lame --enable-libvorbis --enable-libtheora --enable-libx264 --enable-libspeex --enable-shared --enable-pthreads --enable-libopenjpeg --enable-libfaac --enable-nonfree --enable-libvpx
sudo make -j 2
sudo make install
sudo ldconfig

echo "Installing python-pip"
sudo apt-get install python-pip

echo "Installing OpenCV"
sudo apt-get install python-opencv

echo "Insatlling numpy"
sudo pip install numpy;

echo "Installing scipy"
sudo pip install scipy;

echo "Installing pyaudio"
#For x86, change amd64 to x86 and it works
wget https://people.csail.mit.edu/hubert/pyaudio/packages/python-pyaudio_0.2.8-1_amd64.deb;
sudo dpkg -i python-pyaudio_0.2.8-1_amd64.deb

echo "Installing matplotlib"
sudo pip install matplotlib;

echo "Installing pydub"
sudo pip install pydub;

echo "Installing mysql"
sudo apt-get install mysql-server
sudo apt-get install mysql-client
sudo apt-get install python-dev libmysqlclient-dev

echo "Installing django"
sudo pip install django;

echo "Installing mysqldb"
sudo apt-get install python-mysql

echo "Installing dejavu"
git clone https://github.com/vasanthkalingeri/dejavu.git
cd dejavu
sudo python setup.py install

echo "Installing nginx"
sudo apt-get install nginx

echo "Installing gunicorn"
pip install gunicorn

#When port audio has trouble installing run the following
#Download the .deb package of portaudio, the following is for amd64, change it to x86 if required.

#wget libportaudio-ocaml_0.2.0-1+b2_amd64.deb
#sudo dpkg -i libportaudio-ocaml_0.2.0-1+b2_amd64.deb
##If dependency errors
#sudo apt-get -f install 
