# raspi_opencv_motion
## you need to compile and install opencv with gstreamer support
### Install these dependencies
`sudo apt install libgtk2.0-dev cmake python3-dev gcc g++ libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev git pkg-config libavcodec-dev libavformat-dev libswscale-dev gstreamer1.0-plugins-bad gstreamer1.0-plugins-good gstreamer1.0-plugins-ugly`
### Clone opencv
`git clone https://github.com/opencv/opencv.git`
### make build directory
`cd ~/opencv
mkdir build
cd build`
### configure opencv
`cmake -D CMAKE_BUILD_TYPE=Release -D CMAKE_INSTALL_PREFIX=/usr/local -D BUILD_NEW_PYTHON_SUPPORT=ON -D BUILD_opencv_python3=ON -D WITH_GSTREAMER=ON -D WITH_GTK=ON ..`
### make opencv
`make -j12`
### install opencv
`sudo make install`
### copy over opencv to python
I don't know why it didn't work on its own, but I had to manually copy it
`sudo cp ~/opencv/build/lib/python3/cv2.cpython-36m-x86_64-linux-gnu.so /usr/local/lib/python3.6/dist-packages/cv2.so`

## Now run something like this on your raspberry pi
`raspivid -n -t 0 -w 1280 -h 720 -ex antishake -awb fluorescent -fps 25 -b 2000000 -o - | gst-launch-1.0 -v fdsrc ! h264parse ! rtph264pay config-interval=1 pt=96 ! gdppay ! tcpserversink host=RASPI_IP_ADDR port=5000`

You should now be able to run the python code in this repo, just change the ip address to your own.
