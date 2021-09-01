# Internship Project, Univerity of Cyprus



## Overview
Using the JeVois camera I designed a machine vision module that could be used to identify the colour and shape of some boxes. I developed the module based on red, green and blue boxes but it can be easily modified to detect accurately combinations of those colours such as yellow, cyan and magenta. The Dobot Magician arm together with a conveyor belt, would then be used to move and sort the boxes based on their colour. In order to do so, I attached a suction cup at the tip of the robotic arm that could be used to lift and move the boxes. Difficulties arose while developing the machine vision module since image noise and background caused many errors and difficulties. Mechanical limitations of the robotic arm were also an issue since it required calibration regularly. The programming language that I used to program the robotic arm and the JeVois camera was Python. The main libraries used were OpenCV, pySerial and threading.



## Dependancies
* Python 3.9+

