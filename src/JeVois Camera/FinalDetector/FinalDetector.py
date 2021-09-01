import libjevois as jevois
import cv2 as cv
import numpy as np


class FinalDetector:
    # ###################################################################################################
    ## Constructor
    def __init__(self):
        # Instantiate a JeVois Timer to measure our processing framerate:
        self.timer = jevois.Timer("processing timer", 100, jevois.LOG_INFO)
           
        self.start_point = (60, 40)
        self.end_point = (220, 200)
        self.color = (0,0,255)
        self.thickness = 2
       
        self.light_red = (0,140, 60) # v is required to remove other colours from the mask of red
        self.dark_red =  (179,255,255)
        
        self.light_green = (40,150,60)      # h: color
        self.dark_green =  (80,255,255)  # s: amount of color, if white background --> increase (removes white)
                                         # v: luminosity, if dark background --> increase (removes black)
        self.light_blue = (80,190,40)   # 40 for preventing dark background from being detected as blue
        self.dark_blue =  (170,255,255) 
        
        self.min_area = 470 #  min detectable area
        self.max_area = 10000 #  max detectable area
        
  
    # ###################################################################################################
    ## Process function with no USB output
    def processNoUSB(self, inframe):
        # Get the next camera image (may block until it is captured) and here convert it to OpenCV BGR. If you need a
        # grayscale image, just use getCvGRAY() instead of getCvBGR(). Also supported are getCvRGB() and getCvRGBA():
        inimg = inframe.getCvBGR()

        height = inimg.shape[0]
        width = inimg.shape[1]
                
        
        display = inimg[120:360,160:480] # display this image 
        cv.rectangle(inimg, (240,180), (400,300), (0,255,255), 2)
        resize = inimg[180+2:300-2,240+2:400-2]  # work with this image
        smooth = cv.medianBlur(resize, 11)
         
        
        #  Color Detection
        test = smooth[53:59, 76:81] #test this region for color
        hsv = cv.cvtColor(test, cv.COLOR_BGR2HSV)
        hsv1 = cv.cvtColor(resize, cv.COLOR_BGR2HSV)
                                      
        #  Masks 
        maskgreen = cv.inRange(hsv, self.light_green, self.dark_green)
        maskblue = cv.inRange(hsv, self.light_blue, self.dark_blue)
        maskred = cv.inRange(hsv, self.light_red, self.dark_red)
        
        maskgreen1 = cv.inRange(hsv1, self.light_green, self.dark_green)
        maskblue1 = cv.inRange(hsv1, self.light_blue, self.dark_blue)
        maskred1 = cv.inRange(hsv1, self.light_red, self.dark_red)


        #  Results
        resgreen = cv.bitwise_and(test, test, mask = maskgreen) #resize
        resblue = cv.bitwise_and(test, test, mask = maskblue)  
        resred = cv.bitwise_and(test, test, mask = maskred)
        
        resgreen1 = cv.bitwise_and(smooth, smooth, mask = maskgreen1) #resize
        resblue1 = cv.bitwise_and(smooth, smooth, mask = maskblue1)  
        resred1 = cv.bitwise_and(smooth, smooth, mask = maskred1)

        def draw_contours(res):
            xs = []
            ys = []
            ws = []
            hs = []
            kernel = np.ones((5,5),np.uint8)
            dst = cv.adaptiveThreshold(res, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY_INV, 3, 2)
            edges2 = cv.morphologyEx(dst, cv.MORPH_CLOSE, kernel, iterations = 1)
            #edges2 = cv.morphologyEx(edges1, cv.MORPH_DILATE, kernel, iterations = 1)
            #outframe.sendCv(edges2)
            contours, hierarchy = cv.findContours(edges2,cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
            for _ in contours:
                area = cv.contourArea(_)
                if area > self.min_area and area < self.max_area:
                    x,y,w,h = cv.boundingRect(_)
                    xs.append(x)
                    ys.append(y)
                    ws.append(w)
                    hs.append(h)
                    mid = np.array([x+80, y+60])/2 + np.array([x+80+w, y+60+h])/2
                    mid_gap = np.linalg.norm(mid - np.array([160, 118]))
                    #jevois.sendSerial(str(mid_gap))
                    if mid_gap < 100:
                        cv.rectangle(display, (x+80, y + 60), (x + 80 + w, y + 60 + h), (36,255,12), 2)
                        #if len(xs) >= 1:
                         #   cv.rectangle(display, (max(xs) + 80, max(ys) +60 ),(max(xs) + 80 + min(ws), max(ys) + 60 + min(hs)), (36, 255, 12),2 )
                          #  return max(xs), max(ys), min(ws), min(hs)
            return None
        
        # Split Channels
        hgreen, sg, vg = cv.split(cv.cvtColor(resgreen, cv.COLOR_BGR2HSV))
        hblue, sb, vb = cv.split(cv.cvtColor(resblue, cv.COLOR_BGR2HSV))
        hred, sr, vr = cv.split(cv.cvtColor(resred, cv.COLOR_BGR2HSV))    

        if 100 <= cv.minMaxLoc(hblue)[1] < 160:
            jevois.sendSerial('Blue')                    
       
        elif 20 <= cv.minMaxLoc(hgreen)[1] < 95:
            jevois.sendSerial('Green')
        
        elif cv.minMaxLoc(hred)[1] >= 165:
            jevois.sendSerial('Red')
            
        else:
            jevois.sendSerial('...')
        
        
        
    # ###################################################################################################
    ## Process function with USB output
    def process(self, inframe, outframe):
        # Get the next camera image (may block until it is captured) and here convert it to OpenCV BGR. If you need a
        # grayscale image, just use getCvGRAY() instead of getCvBGR(). Also supported are getCvRGB() and getCvRGBA():
        inimg = inframe.getCvBGR()
        height = inimg.shape[0]
        width = inimg.shape[1]
        #jevois.sendSerial(str(height))
        
        
        display = inimg[120:360,160:480] # display this image 
        cv.rectangle(inimg, (240,180), (400,300), (0,255,255), 2)
        resize = inimg[180+2:300-2,240+2:400-2]  # work with this image
        smooth = cv.medianBlur(resize, 11)
         
        
        # Cube Detection
        
        '''gray = cv.cvtColor(resize,cv.COLOR_BGR2GRAY)
        gray =np.float32(gray)
        dst = cv.cornerHarris(gray,2,3,0.04)
        dst = cv.dilate(dst,None)
        corners = resize
        corners[dst>0.01*np.max(dst),:]=[128,0,128]
        '''
        #outframe.sendCv(resize)
        #cv.circle(inimg, (int(width/2),int(height/2)-3), 3, (255,255,255), 1)
        
        #  Color Detection
        test = smooth[53:59, 76:81] #test this region for color
        hsv = cv.cvtColor(test, cv.COLOR_BGR2HSV)
        hsv1 = cv.cvtColor(resize, cv.COLOR_BGR2HSV)
        
        def out(img, clr):
            #cv.rectangle(inimg, (240,180), (400,300), (255,0,0), 2)
            cv.rectangle(img, (0, 0), (330, 21), (45, 45, 45), -1)
            cv.rectangle(img, (0, 216), (330, 245), (45, 45, 45), -1)
            cv.putText(img, "JeVois ColorDetector", (1, 17), cv.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255))
            cv.putText(img, 'Color Detected: {} ' .format(clr), (1, 234), cv.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255))
            cv.circle(inimg, (int(width/2),int(height/2)-3), 3, (255,255,255), 2)
            outframe.sendCv(img)
            jevois.sendSerial(clr)
        
                                      
        #  Masks 
        maskgreen = cv.inRange(hsv, self.light_green, self.dark_green)
        maskblue = cv.inRange(hsv, self.light_blue, self.dark_blue)
        maskred = cv.inRange(hsv, self.light_red, self.dark_red)
        
        maskgreen1 = cv.inRange(hsv1, self.light_green, self.dark_green)
        maskblue1 = cv.inRange(hsv1, self.light_blue, self.dark_blue)
        maskred1 = cv.inRange(hsv1, self.light_red, self.dark_red)


        #  Results
        resgreen = cv.bitwise_and(test, test, mask = maskgreen) #resize
        resblue = cv.bitwise_and(test, test, mask = maskblue)  
        resred = cv.bitwise_and(test, test, mask = maskred)
        
        resgreen1 = cv.bitwise_and(smooth, smooth, mask = maskgreen1) #resize
        resblue1 = cv.bitwise_and(smooth, smooth, mask = maskblue1)  
        resred1 = cv.bitwise_and(smooth, smooth, mask = maskred1)

        def draw_contours(res):
            xs = []
            ys = []
            ws = []
            hs = []
            kernel = np.ones((5,5),np.uint8)
            dst = cv.adaptiveThreshold(res, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY_INV, 3, 2)
            edges2 = cv.morphologyEx(dst, cv.MORPH_CLOSE, kernel, iterations = 2)
            #outframe.sendCv(edges2)
            contours, hierarchy = cv.findContours(edges2,cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
            for _ in contours:
                area = cv.contourArea(_)
                if area > self.min_area and area < self.max_area:
                    x,y,w,h = cv.boundingRect(_)
                    xs.append(x)
                    ys.append(y)
                    ws.append(w)
                    hs.append(h)
                    mid = np.array([x+80, y+60])/2 + np.array([x+80+w, y+60+h])/2
                    mid_gap = np.linalg.norm(mid - np.array([160, 118]))
                    #jevois.sendSerial(str(mid_gap))
                    if mid_gap < 15:
                        cv.rectangle(display, (x+80, y + 60), (x + 80 + w, y + 60 + h), (36,255,12), 2)
                        if len(xs) >= 1:
                            cv.rectangle(display, (max(xs) + 80, max(ys) +60 ),(max(xs) + 80 + min(ws), max(ys) + 60 + min(hs)), (36, 255, 12),2 )
                            return max(xs), max(ys), min(ws), min(hs)
        
        #draw_contours(maskgreen1)
        #outframe.sendCv(maskgreen1)
        
        # Split Channels
        hgreen, sg, vg = cv.split(cv.cvtColor(resgreen, cv.COLOR_BGR2HSV))
        hblue, sb, vb = cv.split(cv.cvtColor(resblue, cv.COLOR_BGR2HSV))
        hred, sr, vr = cv.split(cv.cvtColor(resred, cv.COLOR_BGR2HSV))    

                
        if 100 <= cv.minMaxLoc(hblue)[1] < 160:
            #outframe.sendCv(maskblue1)
            draw_contours(maskblue1)
            out(display, 'Blue')
                
        elif 20 <= cv.minMaxLoc(hgreen)[1] < 95:
            #outframe.sendCv(maskgreen1)
            draw_contours(maskgreen1)
            out(display, 'Green')
        
        
        elif cv.minMaxLoc(hred)[1] >= 165:
            #outframe.sendCv(resred1)
            draw_contours(maskred1)
            out(display, 'Red')
            
        else:
            out(display, '...')
                
    # ###################################################################################################
    ## Parse a serial command forwarded to us by the JeVois Engine, return a string
    def parseSerial(self, str):
        jevois.LINFO("parseserial received command [{}]".format(str))
        if str == "hello":
            return self.hello()
        return "ERR Unsupported command"
    
    # ###################################################################################################
    ## Return a string that describes the custom commands we support, for the JeVois help message
    def supportedCommands(self):
        # use \n seperator if your module supports several commands
        return "hello - print hello using python"

    # ###################################################################################################
    ## Internal method that gets invoked as a custom command
    def hello(self):
        return "Hello from python!"
        
