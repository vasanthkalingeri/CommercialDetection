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
sudo add-apt-repository ppa:mc3man/trusty-media
sudo apt-get update
sudo apt-get install ffmpeg gstreamer0.10-ffmpeg
sudo apt-get install python-dev python-numpy libtbb2 libtbb-dev libjpeg-dev libpng-dev libtiff-dev libjasper-dev libdc1394-22-dev

echo "Installing OpenCV"
sudo apt-get install python-opencv

echo "Insatlling numpy"
#sudo apt-get install python-numpy

echo "Installing scipy"
sudo apt-get install python-scipy

echo "Installing pyaudio"
wget https://people.csail.mit.edu/hubert/pyaudio/packages/python-pyaudio_0.2.8-1_amd64.deb;
sudo dpkg -i python-pyaudio_0.2.8-1_amd64.deb

echo "Installing matplotlib"
sudo apt-get install python-matplotlib

echo "Installing pydub"
cd /home/vasanth/packages/pydub-0.14.0
sudo python setup.py install

echo "Installing mysql"
sudo apt-get install mysql-server
sudo apt-get install mysql-client
sudo apt-get install python-dev libmysqlclient-dev

echo "Installing django"
sudo apt-get install python-django

echo "Installing mysqldb"
sudo apt-get install python-mysql

echo "Installing dejavu"
git clone https://github.com/vasanthkalingeri/dejavu.git
cd dejavu
sudo python setup.py install

echo "Installing apache"
sudo apt-get install apache2 libapache2-mod-wsgi

#When port audio has trouble installing run the following
#Download the .deb package of portaudio, the following is for amd64

#wget libportaudio-ocaml_0.2.0-1+b2_amd64.deb
#sudo dpkg -i libportaudio-ocaml_0.2.0-1+b2_amd64.deb
##If dependency errors
#sudo apt-get -f install 
