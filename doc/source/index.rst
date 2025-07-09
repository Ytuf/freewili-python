FreeWili
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
    
      # FT232H
      SUBSYSTEM=="usb", ATTR{idVendor}=="0403", ATTR{idProduct}=="6014", GROUP="users", MODE="0777"

      # RP2040 CDC
      SUBSYSTEM=="usb", ATTR{idVendor}=="2e8a", ATTR{idProduct}=="000a", GROUP="users", MODE="0777"

      # RP2040 UF2
      SUBSYSTEM=="usb", ATTR{idVendor}=="2e8a", ATTR{idProduct}=="0003", GROUP="users", MODE="0777"

Contents
--------
.. toctree::
   :maxdepth: 3

   index
   cli
   dev
   examples
   api