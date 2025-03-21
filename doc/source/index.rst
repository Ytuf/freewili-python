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

free-wili module requires Python 3.10 or newer and libusb installed for your platform.

.. code-block:: bash
    :caption: freewili module installation

      pip install freewili

Windows
^^^^^^^

- Install libusb from https://libusb.info/
  
  - This must be in your system path (C:\\windows\\System32)
  
  - libusb archive is in 7z format. Use https://7-zip.org/ to extract 


.. image:: libusb-windows.png

Linux
^^^^^

Install libusb using your package manager.

.. code-block:: bash
    :caption: Ubuntu/Debian libusb

      apt install libusb

MacOS
^^^^^

Install libusb using brew

.. code-block:: bash
    :caption: macOS libusb install through brew

      brew install libusb

Contents
--------
.. toctree::
   :maxdepth: 3

   index
   examples
   fw
   serial_util
   image
   usb_util
   types
   dev
   framing