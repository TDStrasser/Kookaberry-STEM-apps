# Kookaberry RFID Apps
This is a repository of pre-coded RFID apps for use with the Kookaberry micro-computer:
- **PN532_RFID_Test_Tags** - A test script to exercise various RFID tags:
  - Port **P3** is attached to a PN532 based RFID reader.
  - The script uses the REPL console only - it does not use the Kookaberry display or buttons
  - Various tag operating modes are available: 0=read only, 1=write number, 2=write text, 3=write URI

- **PN532_RFID_vending_demo** - Vending machine demonstrator using writeable RFID tags.
  - Port **P3** is attached to a PN532 based RFID reader.
  - The script uses the Kookaberry display and buttons.
  - Store a number representing a stored purchasing balance on writeable tags
  - Display the balance on any written tag
  - Purchase a variety of selectable items and deduct the value of the item from the stored balance
  - Prevents purchases for tags with insufficient balance
  - Tops up the balance on tags
