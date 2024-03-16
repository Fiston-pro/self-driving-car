import cv2
import numpy as np
import requests

# Function to get video stream frames from ESP32-CAM
def get_stream_frame(url):
    stream = requests.get(url, stream=True)
    if stream.status_code == 200:
        bytes_data = bytes()
        for chunk in stream.iter_content(chunk_size=1024):
            bytes_data += chunk
            a = bytes_data.find(b'\xff\xd8')
            b = bytes_data.find(b'\xff\xd9')
            if a != -1 and b != -1:
                jpg = bytes_data[a:b + 2]
                bytes_data = bytes_data[b + 2:]
                frame = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
                yield frame

# Function to preprocess the frame for lane detection
def preprocess_frame(frame):
    # Convert the frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Apply Canny edge detection
    edges = cv2.Canny(blurred, 50, 150)
    
    return edges

# Function to detect and track lanes
def detect_lanes(frame):
    # Preprocess the frame
    edges = preprocess_frame(frame)
    
    # Define a region of interest (ROI)
    height, width = frame.shape[:2]
    roi_vertices = [(0, height), (width // 2, height // 2), (width, height)]
    mask = np.zeros_like(edges)
    cv2.fillPoly(mask, np.array([roi_vertices], dtype=np.int32), 255)
    masked_edges = cv2.bitwise_and(edges, mask)
    
    # Apply Hough transform to detect lines
    lines = cv2.HoughLinesP(masked_edges, 1, np.pi/180, threshold=50, minLineLength=100, maxLineGap=50)
    
    # Draw the detected lines on the frame
    line_image = np.zeros_like(frame)
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            cv2.line(line_image, (x1, y1), (x2, y2), (0, 255, 0), 3)
    
    # Combine the line image with the original frame
    result = cv2.addWeighted(frame, 0.8, line_image, 1, 0)
    
    return result, lines

# Function to calculate steering based on lane positions
def calculate_steering(frame_center, lane_centers, width):
    if len(lane_centers) == 0:
        return "straight"  # No lanes detected, maintain current direction
    
    # Calculate the average lane center
    avg_lane_center = sum(lane_centers) / len(lane_centers)
    
    # Calculate the deviation from the center
    deviation = avg_lane_center - frame_center
    
    # Determine the steering direction based on deviation
    if deviation < -width / 4:
        return "left"
    elif deviation > width / 4:
        return "right"
    else:
        return "straight"

# Main function to capture frames from the ESP32-CAM stream, detect lanes, and control the car
def main():
    # URL of the ESP32-CAM stream
    stream_url = 'http://<ESP32_CAM_IP_ADDRESS>:81/stream'
    
    # Define the width of the frame
    frame_width = 640
    
    # Initialize the previous steering direction
    prev_steering = "straight"
    
    for frame in get_stream_frame(stream_url):
        # Detect and track lanes
        result, lines = detect_lanes(frame)
        
        # Calculate the center of the frame
        frame_center = frame_width // 2
        
        # Calculate the center of each lane
        lane_centers = []
        if lines is not None:
            for line in lines:
                x1, _, x2, _ = line[0]
                lane_center = (x1 + x2) // 2
                lane_centers.append(lane_center)
        
        # Calculate steering direction based on lane positions
        steering = calculate_steering(frame_center, lane_centers, frame_width)
        
        # Control the car based on the steering direction
        if steering != prev_steering:
            # Send control commands to the ESP32-CAM API
            if steering == "left":
                print("Turning left")
                # Send API endpoint to turn left
            elif steering == "right":
                print("Turning right")
                # Send API endpoint to turn right
            else:
                print("Going straight")
                # Send API endpoint to maintain current direction
            
            # Update the previous steering direction
            prev_steering = steering
        
        # Display the result with detected lanes
        cv2.imshow("Lane Detection", result)
        
        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # Close all windows
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
