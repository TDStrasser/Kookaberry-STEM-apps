# Kookaberry Digital Technology Apps
This is a repository of pre-coded digital technology apps for use with the Kookaberry micro-computer.
Digital Technology encompasses digital logic, and the binary or symbolic encoding, transmission and decoding of information.

The digital technology apps in this repository include the following:
- **ASCII** - Shows the printable ASCII characters and their codes in binary, hexadecimal and decimal formats.
  - The first ASCII character shown is selected at random.
  - Press the following buttons to navigate: C (previous) or D (next)
  - Press button A to exit the app.
- **BinaryNumbers** - A decimal to binary number conversion demonstration and puzzle setter. There are three modes:
  1. The user can adjust a decimal number up and down and see the binary equivalent
  2. The user picks a random decimal number and manually solves the binary - a show button displays the answer
  3. The user picks a random binary number and manually solves the decimal - a show button displays the answer
  - The control buttons are: A=exit B=next mode C/D adjust or choose options within a mode
  - See the description here https://learn.auststem.com.au/app/binarynumbers-app/
- **Braille** - Displays the alphabet and the Braille equivalent.  The app also provides some training examples of Braille to convert back to text. There are three modes:
  1. The user can see and adjust a printable character up and down and see the Braille equivalent
  2. The user picks a random word and manually writes it out in Braille - a show button displays the answer
  3. The user picks a sequence of Braille symbols and manually decodes it into characters to form a word - a show button displays the answer
  - The control buttons are: A=exit B=next mode C/D adjust or choose options within a mode
- **HexNumbers** - A decimal to hexadecimal number conversion demonstration and puzzle setter.  There are three modes:
  1. The user can adjust a decimal number up and down and see the hexadecimal equivalent
  2. The user picks a random decimal number and manually solves the hexadecimal - a show button displays the answer
  3. The user picks a random hexadecimal number and manually solves the decimal - a show button displays the answer
  - The control buttons are: A=exit B=next mode C/D adjust or choose options within a mode
- **Logic** - Implements a selection of logic gates between digital inputs and a digital output. The logic gates available are AND, OR, NAND, NOR, and XOR.
  - The logic gates respond to real digital inputs on plugs **P4** and **P5**.
  - The currently active logic gate's digital output is sent to plug **P2**.
  - The green, orange and red LEDs indicate the states of the inputs and the logic output.
  - The control buttons are: A=exit B=Logic (go to next logic gate) C=toggle P4 D=toggle P5.
  - Kookaberries running this app may be physically interconnected to form more elaborate logic schemes.
  - Connecting real peripherals to P4, P5 and P2 allows the app to read real-world logical inputs and control digital devices.
  - See the description here https://learn.auststem.com.au/app/logic-app/
- **MorseCode** - A Morse Code demonstrator, encoder and decoder. There are three modes:
  1. The values of the alphanumeric Morse Codes are shown
  2. Messages stored as text are encoded and sent as Morse Code
  3. Messages received from another Morse Code app are decoded and shown as text.
  - Plug P1 is the morse code digital input, plug P2 is the morse code digital output.
  - The control buttons are: A=exit B=next mode C/D adjust or choose options within a mode.
  - See the description here https://learn.auststem.com.au/app/morsecode/
- **OctalNumbers** - A decimal to octal number conversion demonstration and puzzle setter.  There are three modes:
  1. The user can adjust a decimal number up and down and see the octal equivalent
  2. The user picks a random decimal number and manually solves the octal - a show button displays the answer
  3. The user picks a random octal number and manually solves the decimal - a show button displays the answer
  - The control buttons are: A=exit B=next mode C/D adjust or choose options within a mode
- **Semaphore** - Sends and receives one of three signals over the radio: a hand wave, a like, and a digital output (LED, Buzzer etc).
  - The control buttons are: A=exit B, C, D initiate the respective transmissions over the Kookaberry's radio.
  - Use two or more Kookaberries with the same app. All will receive the transmissions and report accordingly.
  - There is a dependency on having the library module *KappUtils.mpy* in the Kookaberry's *lib* folder, as it is used to set up the radio.
  - See the description here https://learn.auststem.com.au/app/semaphore/