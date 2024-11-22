# Kookaberry STELR Apps
This is a repository of pre-coded apps for use with the STELR Sustainable Housing Extension Kit for the Kookaberry micro-computer.

STELR (Science and Technology Education Leveraging Relevance) is a national initiative of the Australian Academy of Technology and Engineering (ATSE) to address the problem of low participation rates in STEM subjects at the upper secondary school level. It does this by developing teaching modules relating these subjects to highly relevant issues affecting all students.

The AustSTEM Foundation is developed a Kookaberry STELR extension kit to complement the STELR kits thereby making the collection of data by students using the teaching modules a simple and enriching experience.

See the description of the [Kookaberry STELR Extension Kit](https://learn.auststem.com.au/kookaberry-stelr-extension-kit/).
The STELR apps are compatible with the Serial Studio serial line data visualisation program. See [Visualise STELR Data with Serial Studio](https://learn.auststem.com.au/visualise-stelr-data-with-serial-studio/)

In this repository:
- **STELR Kookaberry Package** - This is a zip file containing all of the software required to use the Extension Kit.  Please note it is only compatible with the V1-x STM Kookaberry (not the V2-x RP2040 Kookaberry).  To install the software:
  1. Download the zip file to your desktop PC.
  2. Tether a STM Kookaberry to the USB port on the PC so that it mounts as a USB drive.
  3. Open the zip file with a ZIP extractor program (Windows Explorer can do this).
  4. Export / unpack the contents onto the Kookaberry's USB drive.  It should place all the files in the correct folders on the Kookaberry.
- **STELR_IRT** - Measures two temperatures using a MLX90614 infra-red (IR) temperature sensor.
  - The IR sensor measures the target object temperature and the sensor's ambient temperature.
  - Logs the measurements into a *STELR_IRT.CSV* file at an interval specified in the configuration file.
  - If a sensor is not present then a default value (-100) is recorded for that sensor.
  - The MLX90614 IR sensor is connected to plug **P3**.
  - The following library modules must be in the Kookaberry's *lib* folder: *Kapputils.mpy*, *logger.mpy*, *screenplot.mpy*
- **STELR_LxUV** - Measures visible and UV light intensities using the VEML7700 visible light sensor and an analogue UV sensor.
  - Measurements are taken whenever button B is pressed and the values are logged in the *STELR_LxUV.CSV* file on the Kookaberry's file store.
  - Manual measurement initiation allows changing of glass panels between comparative measurements.
  - If a sensor is not present then a default value (-100) is recorded for that sensor.
  - The VEML7700 sensor is coonected to plug **P3**. (The Kookaberry firmware supports this sensor)
  - The UV sensor is connected to plug **P4**. (The Kookaberry uses an inbuilt analogue input to read this sensor)
  - The following library modules must be in the Kookaberry's *lib* folder: *Kapputils.mpy*, *screenplot.mpy*
- **STELR_Temp** - Measures up to three temperature using DS18B20 onewire digital temperature sensors.
  - Logs the measurements into a *STELR_Temp.CSV* file at an interval specified in the configuration file.
  - If a sensor is not present then a default value (-100) is recorded for that sensor.
  - The DS18B20 probes should be plugged into **P1**, **P2** and **P4**. (The Kookaberry firmware supports this sensor)
  - The following library modules must be in the Kookaberry's *lib* folder: *Kapputils.mpy*, *logger.mpy*, *screenplot.mpy*