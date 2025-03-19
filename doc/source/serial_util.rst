Serial Utility Module
=====================
API for interacting with a Free-Wili over serial.


Serial Examples
---------------

.. code-block:: python
    :caption: Search for FreeWilis connected over USB
        
        from freewili.serial_util import find_all
        from freewili.types import FreeWiliProcessorType
        
        # Find all main processors
        devices = serial_util.find_all(FreeWiliProcessorType.Main)
        print(f"Found {len(devices)} Main FreeWili(s)")
        for device in devices:
            print(device)

        # Find all display processors
        devices = serial_util.find_all(FreeWiliProcessorType.Display)
        print(f"Found {len(devices)} Display FreeWili(s)")
        for device in devices:
            print(device)


.. code-block:: python
    :caption: Send a file to the FreeWili
        
        from freewili.serial_util import find_all
        from freewili.types import FreeWiliProcessorType

        # Find the first Main Processor.
        first_device = freewili.find_all(FreeWiliProcessorType.Main)[0]
        # Send the file to the Main Processor.
        first_device.send_file("my_script.wasm", "/scripts/my_script.wasm").unwrap()

.. code-block:: python
    :caption: Force main processor into UF2 bootloader
    
        from freewili.serial_util import find_all
        from freewili.types import FreeWiliProcessorType

        # Find the first Main Processor.
        first_device = freewili.find_all(FreeWiliProcessorType.Main)[0]
        # Send the file to the Main Processor.
        input(f"WARNING: This will force the processor for {first_device} into UF2 bootloader, press any key to continue...")
        first_device.reset_to_uf2_bootloader().unwrap()

fwi-serial command line interface
---------------------------------

Included in the freewili module is command line interfaces to allow easy interactions with this API.

.. command-output:: fwi-serial --help


Serial Module API
-----------------
.. automodule:: freewili.serial_util
   :members:
   :show-inheritance:
   :undoc-members:
