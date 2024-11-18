# Kookaberry Utility Apps
This is a repository of pre-coded utility apps for use with the Kookaberry micro-computer:
- **_Config** - Sets / edits and stores the configuration parameters for use by the Kookaberry apps. Its use is a pre-requisite to properly configure the Kookaberry for use by many apps that use the Kookaberry radio and / or datalogging functions.
  - Creates a JSON-encoded *Kookapp.cfg* configuration file in the root folder of the Kookaberry's file storage system. 
  - A splash screen on the display shows the Kookaberry's operating system version information 
  - The default radio channel is set to 83 (from the firmware default channel 7) to avoid interference from nearby WiFi access points.
  - Permits editing of the Kookaberry's radio channel, ID number (used by datalogging apps), and datalogging interval.
  - See the description at https://learn.auststem.com.au/app/_config/
  - There are hardware or library dependencies to use this app.
  - Other apps will require the *Kapputils.mpy* library module to read the configuration created by this app.
