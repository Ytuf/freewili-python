FreeWili documentation
======================

Python API to interact with Free-Wili devices. See https://freewili.com/ for more device information.


Installation
============

free-wili module requires Python 3.10 or newer and libusb installed for your platform.

.. code-block:: bash
    :caption: freewili module installation

      pip install freewili

Windows
-------

Install libusb from https://libusb.info/ This must be in your system path (C:\windows\System32)

Linux
-----

Install libusb using your package manager.

.. code-block:: bash
    :caption: Ubuntu/Debian libusb

      apt install libusb

MacOS
-----

Install libusb using brew

.. code-block:: bash
    :caption: macOS libusb install through brew

      brew install libusb

Contents
========
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