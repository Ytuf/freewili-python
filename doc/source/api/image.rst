image
========

.. automodule:: freewili.image
   :members:
   :undoc-members:
   :show-inheritance:

Image Example
---------------

.. code-block:: python
    :caption: Convert an image to an fwi file
        
        from freewili.image import convert
        
        # Convert PNG to FWI
        match image.convert("my_image.png", "my_image.fwi"):
            case Ok(msg):
                print(msg)
            case Err(msg):
                exit_with_error(msg)

