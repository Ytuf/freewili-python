Image Module
================
API for converting image files to Free-Wili (fwi) files.


Image Examples
--------------

.. code-block:: python
    :caption: Convert an image to an fwi file
        
        from freewili.image import convert
        
        # Convert PNG to FWI
        match image.convert("my_image.png", "my_image.fwi"):
            case Ok(msg):
                print(msg)
            case Err(msg):
                exit_with_error(msg)


fwi-convert command line interface
----------------------------------

Included in the freewili module is command line interfaces to allow easy interactions with this API.

.. command-output:: fwi-convert --help

Image module API
----------------

.. automodule:: freewili.image
   :members:
   :show-inheritance:
   :undoc-members:
