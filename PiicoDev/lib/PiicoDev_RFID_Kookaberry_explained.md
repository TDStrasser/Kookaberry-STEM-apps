# Explaining `PiicoDev_RFID_Kookaberry.py`

This document explains how the `PiicoDev_RFID_Kookaberry.py` script works for students and other beginners who are new to MicroPython and RFID programming [file:1]. The script is a MicroPython library for the Kookaberry environment that talks to a PiicoDev RFID reader/writer over I2C, detects RFID tags, reads their ID, and can also read or write numbers, text, and some URI data [file:1].

## What this script is for

The script is a reusable **library module**, not a complete beginner program by itself, so its main job is to provide functions that another program can call [file:1]. The file header says it was adapted for Kookaberry MicroPython and removes the dependency on the original PiicoDev Unified Library, which means the code talks more directly to the hardware using the I2C bus supplied by the caller [file:1].

In practical terms, a student program imports the class, creates an RFID object, and then uses methods such as `tagPresent()`, `readID()`, `readText()`, or `writeText()` to interact with a tag [file:1]. The example in the header shows exactly that pattern: create `SoftI2C`, pass it into `PiicoDev_RFID(i2c)`, and repeatedly check whether a tag is present before reading its ID [file:1].

## The big idea

An RFID reader does not work like a keyboard or button, where data simply appears when pressed. Instead, the microcontroller must send commands to the RFID module, the RFID module communicates by radio with the tag, and the returned bytes are then checked and interpreted by the script [file:1].

This script is designed in layers:

- At the lowest level, it reads and writes hardware registers over I2C [file:1].
- In the middle, it sends RFID commands such as request, anti-collision, select, authenticate, read, and write [file:1].
- At the top level, it gives friendly functions such as `readID()`, `readNumber()`, `writeText()`, and `readText()` [file:1].

That layered design is important because beginners can use the top-level functions without needing to understand every hardware register first [file:1].

## Imports and constants

Near the top of the file, the script imports `sleep_ms` and later imports `struct` plus `ticks_ms` renamed as `now` [file:1]. `sleep_ms` is used for short timing delays, `struct` converts Python numbers into raw bytes and back again, and `now()` is used for timeout timing when reading text [file:1].

The script also defines many constants such as `_I2C_ADDRESS`, register addresses like `_REG_COMMAND`, and command codes like `_CMD_TRANCEIVE` and `_CMD_SOFT_RESET` [file:1]. These constants are just readable names for numbers the RFID chip expects, so the code is much easier to understand than if it used raw numbers everywhere [file:1].

There are also constants for different tag operations and memory layouts, including:

- `_TAG_CMD_REQIDL`, `_TAG_CMD_ANTCOL1`, `_TAG_CMD_ANTCOL2`, `_TAG_CMD_ANTCOL3` for finding and identifying tags [file:1].
- `_NTAG_PAGE_ADR_MIN` and `_NTAG_PAGE_ADR_MAX` for NTAG user memory pages [file:1].
- `_CLASSIC_ADR` for the MIFARE Classic memory locations chosen by this library [file:1].
- `_SLOT_NO_MIN` and `_SLOT_NO_MAX` so the same public functions can work with both NTAG and Classic tags using a slot concept [file:1].

## The class

The main class is called `PiicoDev_RFID` [file:1]. A class is a template for creating an object that bundles together data and functions, so after a student writes `rfid = PiicoDev_RFID(i2c)`, the variable `rfid` becomes an object that “knows” how to talk to the RFID hardware [file:1].

Inside the class, three status values are defined: `OK = 1`, `NOTAGERR = 2`, and `ERR = 3` [file:1]. These are simple codes used throughout the program so functions can report success, a missing tag, or a general error without always raising exceptions [file:1].

## What happens in `__init__`

The `__init__` method runs when the RFID object is created [file:1]. It stores the I2C bus in `self.i2c`, chooses the I2C address either from the optional `asw` switch settings or from the default address, clears some internal state flags, resets the RFID module, writes several setup values into chip registers, enables interrupt-related settings, and then turns on the antenna [file:1].

That means the object is ready to use as soon as it is created. For beginners, the key point is that all the “start-up plumbing” is hidden inside `__init__`, so the student does not need to manually configure every register in their main script [file:1].

## Helper functions for registers

Several short methods handle low-level register access:

- `_wreg(reg, val)` writes one byte to a register [file:1].
- `_wfifo(reg, val)` writes multiple bytes into the FIFO buffer [file:1].
- `_rreg(reg)` reads one byte from a register [file:1].
- `_sflags(reg, mask)` sets selected bits in a register [file:1].
- `_cflags(reg, mask)` clears selected bits in a register [file:1].

These functions are important because almost every hardware action in the rest of the script depends on them [file:1]. When teaching beginners, it helps to explain that a register is like a tiny control box inside the RFID chip, and these helper functions are the safe, consistent way to adjust those boxes [file:1].

## How `_tocard()` works

The `_tocard()` method is one of the most important parts of the whole file because it sends a command and data to the RFID chip, waits for the chip to finish, and then reads back any returned bytes [file:1]. It first chooses interrupt settings based on whether the operation is authentication or transceive, clears old interrupts, flushes the FIFO buffer, loads the outgoing bytes, starts the command, and then waits in a loop until the relevant interrupt bits show that the command has finished or timed out [file:1].

If the chip reports no error, `_tocard()` gathers the received bytes and calculates how many valid bits were returned [file:1]. It finally returns three values: a status code, a list of received bytes, and the number of valid bits, which gives the rest of the script the raw result of an RFID transaction [file:1].

A good beginner mental model is this: `_tocard()` is like the script’s “mailroom.” Other functions prepare a message, `_tocard()` delivers it to the RFID hardware, waits for a reply, and hands the reply back [file:1].

## CRC checking

The `_crc()` method asks the RFID chip itself to calculate a CRC value for a list of bytes [file:1]. CRC stands for cyclic redundancy check, which is a way of adding extra bytes so the receiving device can detect corrupted data [file:1].

Rather than calculating CRC in pure Python, the script uses the RFID chip’s built-in co-processor by loading the data into FIFO, starting the CRC command, waiting for completion, and then reading the result registers [file:1]. This keeps the code simpler and uses the hardware the way it was designed to be used [file:1].

## Detecting and identifying a tag

The script uses a series of functions to detect and identify a nearby tag [file:1]. `_request()` sends a request command to invite a tag into the right communication state, `_anticoll()` performs anti-collision so one tag’s UID can be read correctly, and `_selectTag()` tells the reader which tag should be the active one for later operations [file:1].

The `_readTagID()` method combines those steps into a full ID-reading sequence [file:1]. It starts with anti-collision level 1, selects the tag, checks whether the UID contains the cascade byte `0x88`, and if needed continues to level 2 and level 3 to build the complete UID for larger tags such as NTAG devices [file:1].

When successful, `_readTagID()` returns a dictionary with:

- `success`: whether the read worked [file:1].
- `id_integers`: the UID as a list of integers [file:1].
- `id_formatted`: the UID as a colon-separated uppercase hex string such as `04:AB:12:CD` [file:1].
- `type`: either `ntag` or `classic`, inferred from the UID length used by this script [file:1].

This is a useful teaching example because students can see a raw hardware process being turned into friendly Python data structures [file:1].

## Public functions for tag detection

The public method `readTagID()` is a safer wrapper around the lower-level tag-detection logic [file:1]. It first calls `_detectTag()`, tries again if no tag is seen immediately, and then calls `_readTagID()` only when a tag is actually present [file:1].

The method `readID(detail=False)` is a convenience wrapper for beginners [file:1]. By default it returns only the formatted ID string, but if `detail=True` it returns the full dictionary from `readTagID()` [file:1].

The method `tagPresent()` is even simpler: it calls `readTagID()` and returns only `True` or `False` depending on whether a tag was read successfully [file:1]. That is why it is so useful in student `while True:` loops [file:1].

## Why there are NTAG and Classic paths

The script supports two families of RFID tags: NTAG and MIFARE Classic [file:1]. They behave similarly at a high level, but their memory layouts and access rules are different, so the script often reads the tag type first and then sends the operation to the correct helper function [file:1].

For NTAG tags, data is written page by page using 4-byte pages starting at page 4 in user memory [file:1]. For Classic tags, the script uses selected register or block addresses from `_CLASSIC_ADR`, and some operations also require authentication with Key A before reading or writing [file:1].

This is a good example of abstraction in programming. The student can call one public function such as `writeText()`, while the library hides the device-specific differences underneath [file:1].

## Classic authentication helpers

MIFARE Classic tags need extra steps before protected memory can be used [file:1]. The helper methods `_classicSelectTag()`, `_classicAuth()`, and `_classicStopCrypto()` handle selecting the tag, authenticating a memory address with the default key, and then turning off the encryption state after the operation [file:1].

The default key in this script is six bytes of `0xFF`, stored in `_CLASSIC_KEY` [file:1]. That works for many factory-default educational tags, but it is also a useful point to teach students that some RFID systems use access keys and authentication rather than leaving memory open for anyone to read or write [file:1].

## Reading and writing raw pages or registers

The method `_writePageNtag(page, data)` writes one 4-byte page to an NTAG tag [file:1]. The method `_classicWrite(addr, data)` writes a full 16-byte block to a Classic tag, but it first sends a write command, waits for an acknowledgement, then sends the block data and waits for another acknowledgement [file:1].

The method `_read(addr)` reads data using command `0x30` and returns the received bytes when successful [file:1]. The method `_readClassicData(register)` wraps that read process for Classic tags by repeatedly waiting for a tag, selecting it, authenticating the requested block, reading the data, and then stopping crypto mode [file:1].

These lower-level functions are not usually the first thing beginners need to call directly. They are the building blocks used by the friendlier `readNumber()`, `writeNumber()`, `readText()`, and `writeText()` methods [file:1].

## How numbers are stored

The method `writeNumber(number, slot=35)` stores a Python integer on the tag by packing it into bytes with `struct.pack('l', number)` [file:1]. The script then reads the tag ID until a valid tag is found, checks whether the tag is NTAG or Classic, and calls the matching helper to write those bytes into the correct location [file:1].

For NTAG, `_writeNumberToNtag()` writes the bytes to one page using `page_adr_min + slot`, while for Classic, `_writeNumberToClassic()` pads the byte list out to a full 16-byte block and writes it to the block address selected from `_CLASSIC_ADR` [file:1]. The `slot` idea gives a simple student-friendly way to choose where a value is stored without needing to think about low-level addresses at first [file:1].

The method `readNumber(slot=35)` performs the reverse process [file:1]. It finds the tag, reads the relevant bytes from the correct place, and then uses `struct.unpack('l', bytes(bytearray_number[:4]))` to rebuild the original integer [file:1].

A useful teaching point here is that RFID memory stores bytes, not Python objects. The `struct` module is what converts between a Python integer and the byte pattern that actually fits into tag memory [file:1].

## How text is written

The method `writeText(text, ignore_null=False)` adds a null terminator `\0` to the text, reads the tag type, and then sends the job to `_writeTextToNtag()` or `_writeTextToClassic()` [file:1]. Adding the null character is important because it marks the end of the stored text when reading it back later [file:1].

For NTAG, `_writeTextToNtag()` slices the text into 4-character chunks, converts each character into its numeric byte value with `ord()`, pads the chunk to 4 bytes if needed, and writes it page by page from `_NTAG_PAGE_ADR_MIN` to `_NTAG_PAGE_ADR_MAX` [file:1]. For Classic, `_writeTextToClassic()` does the same kind of work in 16-byte chunks across a limited set of chosen blocks [file:1].

The `ignore_null` option changes the stopping behaviour [file:1]. If it is `False`, writing stops as soon as a chunk contains a null byte, which is usually the normal end-of-text marker; if it is `True`, the method keeps writing full content even when null bytes are present in the data [file:1].

## How text is read

The method `readText(timeout=0)` waits until a tag is found, unless an optional timeout expires, and then chooses the correct helper based on tag type [file:1]. `_readTextFromNtag()` reads page data in order and joins the bytes into characters, while `_readTextFromClassic()` does the same across the selected Classic blocks [file:1].

Both text-reading helpers look for a null byte in the returned data [file:1]. When one is found, the accumulated string is split at `\0`, and only the real text before that terminator is returned [file:1].

This is another useful beginner concept: the tag does not inherently know how long a string is, so the script stores a special end marker and later uses that marker to decide where the text ends [file:1].

## URI writing

The method `writeURI(uri)` builds an NDEF-style message and then stores it by calling `writeText(ndef, ignore_null=True)` [file:1]. In other words, it prepares the extra bytes that tell phones or other readers that the stored content is a URI record, not just plain text [file:1].

The code comment says this is currently supported only for NTAG213-style tags [file:1]. For students, the main lesson is that a web link on an NFC tag is not just the characters of the URL by themselves; it is usually wrapped in a small message format that other devices know how to interpret [file:1].

## Example workflow

A typical student program using this library might follow this sequence [file:1]:

1. Import `PiicoDev_RFID`, `Pin`, and `SoftI2C` [file:1].
2. Create the I2C object using the Kookaberry pin names [file:1].
3. Create the RFID object with `rfid = PiicoDev_RFID(i2c)` [file:1].
4. Repeatedly check `rfid.tagPresent()` in a loop [file:1].
5. When a tag is present, call `rfid.readID()`, `rfid.readText()`, or another public method [file:1].

For example:

```python
from PiicoDev_RFID_Kookaberry import PiicoDev_RFID
from machine import Pin, SoftI2C
from time import sleep_ms

i2c = SoftI2C(sda=Pin("P3B"), scl=Pin("P3A"))
rfid = PiicoDev_RFID(i2c)

while True:
    if rfid.tagPresent():
        print("Tag ID:", rfid.readID())
    sleep_ms(100)
```

This small program relies on the library to do all of the hard work: hardware setup, polling, anti-collision, and UID formatting [file:1].

## Programming ideas students can learn from this file

This script is a strong teaching example because it demonstrates several important programming ideas in one place [file:1]:

- Encapsulation: complex hardware logic is wrapped inside a class [file:1].
- Abstraction: beginners can call simple methods without understanding every register [file:1].
- Byte handling: data is often stored and moved as byte arrays, not as plain Python strings or numbers [file:1].
- Error handling: functions return status values, retry detection, and sometimes catch exceptions to avoid crashing [file:1].
- Reuse: the same low-level functions support many higher-level features [file:1].

When explaining the file to students, it can help to separate “what a user calls” from “what the library does behind the scenes.” That distinction makes a long hardware library feel much less intimidating [file:1].

## Things beginners should notice carefully

A few details in the file are especially worth pointing out during teaching [file:1]:

- Names starting with an underscore, such as `_read()` or `_crc()`, are intended as internal helper methods [file:1].
- Public methods without the underscore, such as `readID()` or `writeText()`, are the ones a student is more likely to use directly [file:1].
- The script contains loops that retry operations until a tag is detected or a write succeeds, which is common in hardware programming because communication is not always perfect on the first attempt [file:1].
- Some methods print simple error messages such as `Authentication error` or `Failed to select tag`, which helps debugging during classroom use [file:1].

There is also a declared `maximum_characters = 144` inside `writeText()`, but that value is not actually enforced by the code afterward [file:1]. That is a helpful reminder for students that real code can often be improved, and reading code critically is part of learning to program well [file:1].

## In plain language

A simple way to describe the whole script is this: it is a translator between student-friendly Python commands and the low-level byte commands required by an RFID reader chip [file:1]. The user writes clear code such as `rfid.readText()`, and the library handles I2C transfers, tag detection, checksums, memory addressing, and formatting behind the scenes [file:1].

That is why library code often looks much more complicated than the programs that use it. Its job is to hide the difficult parts so the main student program can stay short and readable [file:1].
