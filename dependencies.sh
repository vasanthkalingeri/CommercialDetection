echo "Installing ffmpeg"
sudo add-apt-repository ppa:mc3man/trusty-media
sudo apt-get update
sudo apt-get install ffmpeg gstreamer0.10-ffmpeg

echo "Installing OpenCV"
sudo apt-get install python-opencv

echo "Insatlling numpy"
sudo apt-get install python-numpy

echo "Installing scipy"
sudo apt-get install python-scipy

echo "Installing dejavu"
git clone git@github.com:vasanthkalingeri/dejavu.git
cd dejavu
sudo python setup.py install

echo "Installing mysql"
sudo apt-get install mysql-server
sudo apt-get install mysql-client
