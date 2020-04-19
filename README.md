# camodet
__CAmera MOtion DETection application written in python language.__

Fast, simple and stable motion detection application that works with any local and remote cameras or video sources.

This Project is a port of camodet original project written in C++ to python <https://github.com/oyzzo/camodet>.

## Features

* __Fast__! It can run on most machines! even old netbooks or raspberri pi!
* __No Installation__ or set up needed. Just run it!.
* __Flexible__. Customize just the parameter you need using the command line parameters.
* __Noise reduction__. No problem with noisy cameras!
* __Area threshold__. Reduce false positives and useless recordings of too small movements.
* __Time window__ to record after motion stopped.
* __Supports all the cameras__ or video sources thanks to OpenCV, flash, MJPEG, flv, etc...
* Use Remote cameras or __network video streams__ as video source!
* __Video files__ can also be used as an input for motion detection, useful for fine tunning parameters on different cases.
* __Headless mode__, no window output for servers.
* __Visual debug__ mode shows how the video is processed in any step! It's great for finding the right values that work for your camera. 
* __Portable__. Compile it on any platform supported by OpenCV3.
* __Written in__ python!__ port it to any platform just by installing it using pip.
* __Add camera name__, if the camera does not support it, camodet labels the videos using a camera name label.
* __Add date and time__ to the video, very usefull to see in the recordings.
* __Any shape ROI mask__, use a black/white mask image to only detect motion in the desired areas, ignoring the rest.

## Build
(Only required if you want to create the package from source)

```
$ python setup.py bdist_wheel
```

## Install

[Download](https://github.com/jim17/camodet_python/releases/latest) and extract the sources, then inside:
```
python -m pip install camodet_python_release_xxx.whl
```

## Usage

To get a list with a description of all parameters use the -h flag:
```
$ python -m camodet -h

Usage: python -m camodet [options]
Options:
    -h              Print this help message.
    -i input_video: The source for motion detection.
    -o output_name: The name for the output recordings.
                    A number and extension will be automatically added after it:
                      e.g. output_name23.avi
    -b number:      Selects backend of OpenCv VideoCaptureAPI
                    0 Auto | 1 FFMPEG | 2 DirectShow (videoInput)
    -s:             Open window showing the input video.
    -D:             Date and time labelled to video.
    -a seconds:     Seconds to record after the motion has stopped.
    -c number:      Counter number to skip using in the output name (Default 0).
    -g              Interactive ROI mask generation (saved as roi_mask.png)
    -l cam_name:    Label camera name on video.
    -m mask_image:  Mask image to use for ROI motion detection. Black areas are ignored, White areas checked.
    -t number:      Threshold area (sqare pixels) to trigger detection.
                    Movements below this area are ignored (Default 600).
    -n number:      Noise reduction level (Default 21).
    -f number:      FPS to process from input source (Default 5).
    -k number:      Number of consecutive frames with motion to trigger motion event (Default 2).
    -x command:     Command to be executed when motion is detected.
    -C              Draw Contours on current image
    -M number:      Max width of frame to be processed for motion detection, if input is larger it will be downsized to this value. (Default 640).
    -d number:      Show intermediate images in a debug window. Number can be:
                    0: None | 1: noise reduction | 2: frames difference | 3: threshold | 4:dilated(final).
    -r              Skip Record into a file to avoid loading HDD during debug.
```

### Basic usage

Detecting motion on the system camera using default parameters without openning window:
```
$ python -m camodet
```

If a window showing the input is needed:
```
$ python -m camodet -s
```

### Input video stream

For using an IP camera stream as input for the motion detection, the -i flag has to be used:
```
$ python -m camodet -s -i http://camera1.mairie-brest.fr/mjpg/video.mjpg?resolution=640x480
```

### Debug window for calibration

For finding the right values for each parameter a debug window is provided with the -d N flag, with N a number between 1 and 4.
The number after -d will tell camodet wich motion detection step to show.
 * 1: Noise reduction -> Useful to test different noise reduction values for the -n flag. The image should be blurry enough to not see random noise, but no more.
 * 2: Difference -> This step shows the difference of frames, actual raw movement. If no movement is shown, too much -n is applied. If false movement is triggered by noise, increment the noise reduction -n flag.
 * 3: Threshold -> Objects movement below an area (in pixels) are ignored, this threshold area is specified with -t flag. If this step is shown in the debug window it'll show white the movements detected. If something has to move too fast to be detected, decrement the -t flag.
 * 4: This step shows the final motion detected (in white) as aditional processing steps are applied.
 
 Note that when the correct values for each parameter are found, the -d flag can be omitted.
 
 For example, testing a lower noise reduction for the input stream video:
 ```
 $ python -m camodet -s -i http://camera1.mairie-brest.fr/mjpg/video.mjpg?resolution=640x480 -d 1 -n 3
 ```
 
 ### Record after movement stops
 
 If there are objects in movement that stops for a seconds, then move agains, it'd generate two video files. To wait recording after a motion has been triggered during a time, for other motion to be included in the recording, the -s seconds flag can be used:
 
 For example, to wait 10 seconds after motion has stopped:
 ```
 $ python -m camodet -s -i http://camera1.mairie-brest.fr/mjpg/video.mjpg?resolution=640x480 -n 3 -a 10
 ```

 ### Adding text over the video
 
 When browsing through several video recordings it may be usefull to tag the recordings with time and date, as well as camera names. Some cameras already generate the video with the desired labels. Otherwise in camodet it can be done with the -D (for date/time) and -l camera_name flags.
 
 ```
  $ python -m camodet -s -i http://camera1.mairie-brest.fr/mjpg/video.mjpg?resolution=640x480 -n 3 -D -l "Camera1"
 ```
 
 ### Recording names
 
 The recordings of the motion detected will be named using a default name and increasing a counter. To specify the name the -o filename flag can be used. If the number in the name is wanted to start counting from a different number than 1 (e.g. to not overwrite existing recordings) the -c number can be used.
 
 For example to generate recordings named Street10.avi onwards:
 ```
  $ python -m camodet -s -i http://camera1.mairie-brest.fr/mjpg/video.mjpg?resolution=640x480 -n 3 -D -l "Camera1" -c 10 -o "Street"
 ```
 
 ### ROI / Mask
 
 In some cases, the camera frame will include some areas were continuous movement happens, but we want to detect motion in a smaller area of the image. For example if we have a camera on the back yard and the image includes a little bit of street. We don't want a recording generated everytime a car passes on the street, so we'll use a mask to ignore that area of the video.
 
 The mask is an image with white and black. The black areas will be ignored from the motion detection, and the wite areas will be used to detect motion and trigger a recording. With the -g flag an image is generated so we can draw on top of it and use it as a mask.
 
 So it'd require three steps:
 
 1) Generate the mask base using a frame from the camera:
 
  ```
  $ python -m camodet -s -i http://camera1.mairie-brest.fr/mjpg/video.mjpg?resolution=640x480 -g
 ```
 
 2) In the generated mask.png paint black the ignored areas. Then white the rest of the image.
 
 3) Start camodet using this mask image:
 
  ```
  $ python -m camodet -s -i http://camera1.mairie-brest.fr/mjpg/video.mjpg?resolution=640x480 -n 3 -D -l "Camera1" -m roi_mask.png
 ```