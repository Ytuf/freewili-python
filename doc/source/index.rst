Free-Wili
========

.. image:: ../../logo.jpg

Python API to interact with Free-Wili devices. 
Included are two CLI executables to interact with a Free-Wili without writing any code. 
`fwi-serial` for interacting with the Free-Wili and `fwi-convert` for converting png or jpg images to fwi format.

See https://freewili.com/ for more device information.

See https://github.com/freewili/freewili-python for source code.

Installation
------------

free-wili module requires Python 3.10 or newer.

.. code-block:: bash
    :caption: freewili module installation

      pip install freewili


Linux
^^^^^

udev rules are required to access the Free-Wili device without root privileges.

.. code-block:: bash
    :caption: /etc/udev/rules.d/99-freewili.rules

      # Intrepid Control System, Inc.
      SUBSYSTEM=="usb", ATTRS{idVendor}=="093c", GROUP="users", MODE="0666"
      KERNEL=="ttyUSB?", ATTRS{idVendor}=="093c", GROUP="users", MODE="0666"
      KERNEL=="ttyACM?", ATTRS{idVendor}=="093c", GROUP="users", MODE="0666"

      # FT232H
      SUBSYSTEM=="usb", ATTR{idVendor}=="0403", ATTR{idProduct}=="6014", GROUP="users", MODE="0666"
      # RP2040 CDC
      SUBSYSTEM=="usb", ATTR{idVendor}=="2e8a", ATTR{idProduct}=="000a", GROUP="users", MODE="0666"
      # RP2040 UF2
      SUBSYSTEM=="usb", ATTR{idVendor}=="2e8a", ATTR{idProduct}=="0003", GROUP="users", MODE="0666"
      # RP2350 UF2
      SUBSYSTEM=="usb", ATTR{idVendor}=="2e8a", ATTR{idProduct}=="000f", GROUP="users", MODE="0666"


udev rules must be reloaded after creating or modifying the rules file. Reboot or run the following commands:

.. code-block:: bash
    :caption: udev reload rules

      sudo udevadm control --reload-rules
      sudo udevadm trigger

Contents
--------
.. toctree::
   :maxdepth: 2

   cli
   dev
   examples
   api/index