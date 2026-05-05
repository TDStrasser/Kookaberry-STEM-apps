# Kookaberry Audio Apps
This is a repository of pre-coded audio apps for use with the Kookaberry micro-computer:
- **SoundSpectrum** - Measures the speech audio spectrum using an analogue microphone plugged into plug P5
  - It demonstrates the application of the Goertzel algorithm embodied in the goertzel library module (in the lib folder)
  - It continuously samples and accumulates the power spectrum whenever sufficient audio signal is detected
  - It finishes sampling when the A button is pressed and finalises the spectrum
  - It logs the spectrum into SoundSpectrum.csv when complete

