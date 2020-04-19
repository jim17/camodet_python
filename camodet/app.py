import numpy as np
import cv2
import time
import sys

try:
    from camodet.settings import Settings
except:
    from settings import Settings


class create_mask():
    def __init__(self, cap):
        hasframes, frame = cap.read()
        name = "ROI mask | (r)Rectangles (p)Paint (1-9)Brush size (left-click)Erase all (q)Exit and Save"
        cv2.namedWindow(name,cv2.WINDOW_NORMAL)
        cv2.setMouseCallback(name, self.draw_mask)
        self.rectangles = []
        self.currentRectangle = []
        self.circles = []
        self.draw = False
        self.brush_size = 5
        self.paint_option = 'paint'

        while(True):
            # ROI mask
            frame_mask = frame.copy()
            roi_mask = np.full(frame.shape, 255, dtype="uint8")

            # Draw rectangle around ROI
            for rectangle in self.rectangles:
                cv2.rectangle(frame_mask, rectangle[0], rectangle[1], (0,255,0), cv2.FILLED)
                cv2.rectangle(roi_mask, rectangle[0], rectangle[1], (0,0,0), cv2.FILLED)
            # Draw circles from Paint
            for circle in self.circles:
                cv2.circle(frame_mask, circle[0], circle[1], (0,255,0), cv2.FILLED)
                cv2.circle(roi_mask, circle[0], circle[1], (0,0,0), cv2.FILLED)

            cv2.imshow(name, frame_mask)

            # Wait 1ms
            key = chr(cv2.waitKey(1) & 0xFF)
            if( key == 'q' ):
                break
            elif( key == 'r' ):
                  self.paint_option = 'rectangles'
            elif( key == 'p' ):
                  self.paint_option = 'paint'
            elif( key in "123456789" ):
                  self.brush_size = int(key)

        # Save it as image
        if(self.rectangles != []):
            roi_mask = cv2.cvtColor(roi_mask, cv2.COLOR_BGR2GRAY)
            cv2.imwrite('roi_mask.png', roi_mask)

        # Write last mask into archive
        sys.exit(0)

    def draw_mask(self, event, x, y, flags, param):
        if(self.paint_option == 'rectangles'):
            # Record starting (x,y) coordinates on left mouse button click
            if event == cv2.EVENT_LBUTTONDOWN:
                self.currentRectangle = [(x,y)]
            # Record ending (x,y) coordintes on left mouse bottom release
            elif event == cv2.EVENT_LBUTTONUP:
                self.currentRectangle.append((x,y))
                # Add to list
                self.rectangles.append(self.currentRectangle)
            # Right click to empty rectangles
            elif event == cv2.EVENT_RBUTTONDOWN:
                self.rectangles = []

        elif(self.paint_option == 'paint'):
            # Record starting (x,y) coordinates on left mouse button click
            if event == cv2.EVENT_LBUTTONDOWN:
                self.draw = True
            # Record ending (x,y) coordintes on left mouse bottom release
            elif event == cv2.EVENT_LBUTTONUP:
                self.draw = False
            # Right click to empty circles
            elif event == cv2.EVENT_RBUTTONDOWN:
                self.circles = []
            # Draw circles on mouse move
            elif event == cv2.EVENT_MOUSEMOVE and self.draw:
                self.circles.append([(x, y), self.brush_size*5])
    

def main():
    # Load Settings
    settings = Settings()
    ret = settings.load_from_args(sys.argv[1:])
    if(ret != 0):
        sys.exit(ret)

    # Print OpenCv version
    print ("OpenCv version: %s" % cv2.__version__)

    # Select Backend
    backend_options = {
        1 : cv2.CAP_FFMPEG,
        2 : cv2.CAP_DSHOW
    }
    if( settings.backend in backend_options.keys() ):
        backend = backend_options[settings.backend]
    else:
        backend = cv2.CAP_ANY

    # Select video input
    if(settings.input_source != ""):
        cap = cv2.VideoCapture(settings.input_source, backend)
    else:
        cap = cv2.VideoCapture(0, backend)

    # Check if camera is opened
    if not cap.isOpened():
        raise IOError("Cannot open the selected video/camera")

    # Limit video fps
    cap.set(cv2.CAP_PROP_FPS,settings.fps)

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print ("Video Height {0} Width {1}".format(height, width))

    # Init values
    started = False
    do_mask = False
    motion = False
    record = False
    counter = settings.counter_start
    element = cv2.getStructuringElement( cv2.MORPH_RECT, (7,7) )
    codec = cv2.VideoWriter_fourcc(*'XVID')

    tframe0 = time.time()
    tframe1 = tframe0
    fps = 0

    # Interactive ROI mask generation
    if( settings.mask_template ):
        create_mask(cap)

    # Load the ROI mask image and binaryze
    if( settings.mask_file != "" ):
        do_mask = True
        mask = cv2.imread(settings.mask_file, cv2.IMREAD_GRAYSCALE)
        while(mask.shape[0] > settings.max_width):
            # Downsampling to settings.max_width
            mask = cv2.pyrDown(mask)

        ret, bin_mask = cv2.threshold(mask, 15, 255, cv2.THRESH_BINARY)
        

    # Infinite Loop
    while(True):
        # Capture frame-by-frame
        hasframes, frame = cap.read()
        
        # None
        if(not hasframes):
            continue
        elif(np.shape(frame) == ()):
            continue
        # All black
        elif(np.sum(frame) == 0):
            continue

        # Compute frames per second
        tframe1 = time.time()
        deltaT = tframe1 - tframe0
        if(deltaT > 0):
            fps = 1/(deltaT)
        else:
            continue

        # Skip frame if input stream go faster
        if(int(fps) > settings.fps):
            continue

        # Store last time stamp only if processed
        tframe0 = tframe1

        # Standarize frame
        # frame = cv2.resize(frame, (640,420))

        # Resize frame
        pyr1 = frame.copy()
        while(pyr1.shape[0] > settings.max_width):
            # Downsampling to settings.max_width
            pyr1 = cv2.pyrDown(pyr1)

        frame2 = cv2.cvtColor(pyr1, cv2.COLOR_BGR2GRAY)
        frame3 = cv2.GaussianBlur(frame2, (settings.noise, settings.noise), 5, 5)

        # Force no difference on first iteration
        if( not started):
            frame3_prev = frame3.copy()
            started = True

        # Difference between this frame and the previous one
        frame4 = cv2.absdiff(frame3, frame3_prev)
        frame3_prev = frame3.copy()
        
        ret, frame5 = cv2.threshold(frame4, 15, 255, cv2.THRESH_BINARY)
        
        # Discard changes annotated in the binary mask
        if(do_mask):
            frame5 = cv2.bitwise_and(bin_mask, frame5)
        
        # Dilate image
        frame6 = cv2.dilate(frame5, element, iterations=2)
        
        # Find Contours
        # Countours are defined as the line joining all the points
        # This is used to discard small objects
        contours, hierarchy = cv2.findContours(frame6, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if(settings.draw_contours):
            frame7 = np.zeros(frame6.shape)
            frame7 = cv2.drawContours(frame7, contours, -1, (255,255,255), 3)

        # Loop contours, compute frames motion
        frames_motion = 0
        for c in contours:
            if( settings.area > cv2.contourArea(c) ):
                frame_motion = 0
                continue
            frames_motion+=1
        
        # Check number of frames in movement
        if (frames_motion >= settings.frames_trigger):
            motion = True
        else:
            motion = False

        # Record Actions
        if( (motion) and (not record) ):
            record = True
            tstart = time.time()
            tend = time.time() + settings.seconds_after
            name = settings.output_name + str(counter) + '.avi'
            counter = counter + 1            
            print("Recording...", name)
            if(settings.record_video):
                output = cv2.VideoWriter(name, cv2.CAP_FFMPEG, codec, settings.fps, frame.shape[:2])
        # Motion stopped while recording
        elif( (motion) and (record) ):
            tend = time.time() + settings.seconds_after
        elif( (record) and (tend < time.time()) ):
            print("Stop recording...")
            record = False
            total_time_record = tend - tstart
            print("Time recorded: %0.2f seconds" % (total_time_record))
            # Close video writer
            if(settings.record_video):
                output.release()
        
        # Our operations on the frame come here
        if( settings.cam_name != "" ):
            cv2.putText(frame, settings.cam_name, (5, 25), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)
        
        if( settings.timestamp ):
            # Overlay Text Settings
            text = time.strftime("%Y-%m-%d-%H:%M:%S") + " fps:%0.1f" % (fps)
            cv2.putText(frame, text, (5,frame.shape[0]-5), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)

        # Input Frame
        if( settings.show_input ):
            cv2.namedWindow('Input',cv2.WINDOW_NORMAL)
            cv2.imshow('Input', frame)

        # Display the debug frame
        frame_display = {
            1 : frame3, # Nose reduction
            2 : frame4, # Frame diff
            3 : frame5, # Threshold
            4 : frame6, # Dilated
        }
        if( settings.debug in frame_display.keys() ):
            cv2.namedWindow('Debug',cv2.WINDOW_NORMAL)
            cv2.imshow('Debug', frame_display[settings.debug])

        # Draw contours 
        if( settings.draw_contours ):
            cv2.namedWindow('Contours',cv2.WINDOW_NORMAL)
            cv2.imshow('Contours',frame7)

        # Write image
        if(record and settings.record_video):
            output.write(frame)
        
        # Wait 1ms
        if( (cv2.waitKey(1) & 0xFF) == ord('q') ):
            break

    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
