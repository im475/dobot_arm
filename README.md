<h1 align="center">Research Project</h1>
<p align="center">Computer Vision and Robotics</p>

<p align="center">
  <img src="https://github.com/im475/dobot_arm/blob/main/pics/dobot_belt_jevois.png">
</p>

## Overview
Using the [JeVois Camera](http://www.jevois.org/) I designed a machine vision module that is able to identify the colour and shape of some boxes. I developed the module using red, green and blue boxes but it can be easily modified to detect accurately combinations of those colours such as yellow, cyan and magenta. The [Dobot Magician](https://www.dobot.cc/dobot-magician/product-overview.html) together with a [Conveyor Belt](https://www.dobot.cc/products/conveyor-belt-kit-overview.html), would then be used to move and sort the boxes based on their colour. In order to do so, I attached a suction cup at the tip of the robotic arm that is used to lift and move the boxes. Difficulties arose while developing the machine vision module since image noise and background caused many errors and difficulties. Mechanical limitations of the robotic arm were also an issue since it required calibration regularly. The programming language that I used to program the Dobot Magician and the JeVois Camera was Python. The main libraries used were OpenCV, pySerial and threading.



## Dependancies
1. [Python 3.9+](https://www.python.org/downloads/windows/)
2. Download the [DobotStudio](https://www.dobot.cc/downloadcenter/dobot-magician.html?sub_cat=70#sub-download) and get started with the Dobot Magician :tada:
3. Useful Python libraries:
   * [OpenCV](https://docs.opencv.org/4.5.2/d6/d00/tutorial_py_root.html)
   * [pySerial](https://pythonhosted.org/pyserial/)
   * [threading](https://docs.python.org/3/library/threading.html)
