# Self Driving Car
We use ESP32-cam and OpenCv to drive a car through a lane

## GET STARTED

- Start by connecting the esp32 cam correctly with FTDI programmer (Read for more: [here](https://randomnerdtutorials.com/program-upload-code-esp32-cam/))
- Upload the code
- Remove the loop on esp32, then click the button once


### Incase you get errors while uploading to ESP32 Cam
- Make sure you unplug other stuff on esp32Cam
- make a loop on a FTDI programmer btn middle pin and 5v(depending on where you connect esp32 cam, for now we connect on 5V)
- Make a loop on ESP32 cam btn IO0 and Gnd
- When you connect from FTDI to ESP32 use 5v and Gnd which are close together
- You can also try to reset the ESP32 Cam

### Requirements
- L9110S H-bridge Dual DC Stepper Motor Driver Controller Board
- Car chassis
- ESP32 CAM

### Limitations
- I tried to use 4 wheels to increase torque and the electricity was getting low and making stuff misbehave so i just stuck on 2 wheels and it was working fine

