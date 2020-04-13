import numpy as np
import cv2
import time

try:
    from camodet.settings import Settings
except:
    from settings import Settings

def main():
    # Load Settings
    settings = Settings()
    settings.load_from_args()

    # Print OpenCv version
    print ("OpenCv version: %s" % cv2.__version__)

    cap = cv2.VideoCapture(0)

    # Limit video fps
    cap.set(cv2.CAP_PROP_FPS,settings.fps)

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print ("Video Height {0} Width {1}".format(height, width))

    # Overlay Text Settings
    font                   = cv2.FONT_HERSHEY_SIMPLEX
    bottomLeftCornerOfText = (15,height-15)
    fontScale              = 1
    fontColor              = (0,255,255)
    lineType               = 2

    # Init values
    started = False
    do_mask = False
    motion = False
    record = False
    element = cv2.getStructuringElement( cv2.MORPH_RECT, (7,7) )
    codec = cv2.VideoWriter_fourcc(*'XVID')

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
            print("Recording...")
            record = True
            tstart = time.time()
            tend = time.time() + settings.seconds_after
            name = settings.output_name+time.strftime("%Y-%m-%d-%H%M%S")+'.avi'
            if(settings.record_video):
                output = cv2.VideoWriter(name, codec, settings.fps, (640,480))
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
        
        if(record and settings.record_video):
            output.write(frame)

        # Our operations on the frame come here
        #cv2.putText(frame,'Time =12:00:01', bottomLeftCornerOfText, font, fontScale, fontColor, lineType)

        # Display the resulting frame
        cv2.imshow('frame',frame)
        cv2.imshow('frame2',frame2)
        cv2.imshow('frame3',frame3)
        cv2.imshow('frame4',frame4)
        cv2.imshow('frame5',frame5)
        cv2.imshow('frame6',frame6)
        if settings.draw_contours:
            cv2.imshow('frame7',frame7)
        
        # Wait 1ms
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()