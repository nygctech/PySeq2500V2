#!/usr/bin/python
"""Illumina HiSeq 2500 System :: Laser

    Examples:
    #Create laser object
    >>>import pyseq
    >>>green_laser = pyseq.laser.Laser('COM13', color='green')
    #Initialize the laser, default power is 10 mW.
    >>>green_laser.initialize()
    >>>green_laser.status()
    >>>True
    #Set the power to 100 mW
    >>>green_laser.set_power(100)
    >>>green_laser.get_power()
    >>>100
    #Turn the laser off
    >>>green_laser.turn_on(False)

Kunal Pandit 11/19
"""

import serial
import io
import time


class Laser():
    """HiSeq 2500 System :: Laser

       Attributes:
       on (bool): True if the laser is on, False if the laser is off.
       power (int): Power in mW of the laser:
       max_power: Maximum power of the laser in mW.
       min_power: Minimum power of the laser in mW.
       color: Color of the laser.
       version: Version number of the control software.
    """


    def __init__(self, com_port, baudrate = 9600, color = None, logger = None):
        """The constructor for the laser.

           Parameters:
           com_port (str): Communication port for the laser.
           baudrate (int, optional): The communication speed in symbols per second.
           color (str): The color of the laser.
           logger (log, optional): The log file to write communication with the
                pump to.

           Returns:
           laser object: A laser object to control the laser.
        """

        # Open Serial Port
        s = serial.Serial(com_port, baudrate, timeout = 1)

        # Text wrapper around serial port
        self.serial_port = io.TextIOWrapper(io.BufferedRWPair(s,s,),
                                            encoding = 'ascii',
                                            errors = 'ignore')
        self.on = False
        self.power = 0
        self.max_power = 500
        self.min_power = 0
        self.suffix = '\r'
        self.logger = logger
        self.color = color
        self.version = self.command('VERSION?')[0:-1]


    def initialize(self):
        """Turn the laser on and set the power to the default 10 mW level."""
        self.turn_on(True)
        self.set_power(10)


    def command(self, text):
        """Send a serial command to the laser and return the response.

           Parameters:
           text (str): A command to send to the laser.

           Returns:
           str: The response from the laser.
        """

        text = text + self.suffix
        self.serial_port.write(text)                                    # Write to serial port
        self.serial_port.flush()                                        # Flush serial port
        response = self.serial_port.readline()
        if self.logger is not None:
            self.logger.info(self.color+'Laser::txmt::'+text)
            self.logger.info(self.color+'Laser::rcvd::'+response)

        return  response


    def turn_on(self, state):
        """Turn the laser on or off.

           Parameters:
           state (bool): True to turn on, False to turn off.

           Returns:
           bool: True if laser is on, False if laser is off.
        """
        if state:
            while not self.get_status():
                self.command('ON')

            self.on = True
        else:
            while self.get_status():
                self.command('OFF')

            self.on = False

        return self.on


    def get_power(self):
        """Return the power level of the laser in mW (int)."""
        self.power = int(self.command('POWER?').split('mW')[0])

        return self.power


    def set_power(self, power):
        """Set the power level of the laser.

        Parameters:
        power (int): Power level to set the laser to.

        Returns:
        bool: True if the laser is on, False if the laser is off.
        """

        if power >= self.min_power and power <= self.max_power:
                self.command('POWER='+str(power))
                self.power = self.get_power()
        else:
            print('Power must be between ' +
                  str(self.min_power) +
                  ' and ' +
                  str(self.max_power))

        return self.get_status()


    def get_status(self):
        """Returns the status of laser (bool), True if on, False if off."""

        self.status = self.command('STAT?')[0:-1]

        if self.status == 'ENABLED':
            return True
        else:
            return False
