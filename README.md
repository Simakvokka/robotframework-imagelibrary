**About**

**ImageLibrary** is designed to automate cases involving various types of screen processing with RoboFramework.


*It operates with:*

- OpenCV
- PIL
- TesseractOCR


**Installation**

pip install robotframework-imagelibrary

**Keywords**

[Keyword documentation](https://simakvokka.github.io/robotframework-imagelibrary/ImageLibrary.html)


Search for lates 0.2.0 version before big refactoring on https://pypi.org/project/robotframework-imagelibrary/#history 



**Buttons guide**

[Buttons documentation](https://simakvokka.github.io/robotframework-imagelibrary/ButtonsGuide.html)


*Installation Requirements*

- **[Python](https://www.python.org/downloads/)**  **3.5+** 

- **Robot Framework**

- **[TesseractOCR](https://github.com/tesseract-ocr/tesseract)** 

    For number and text recognition. May not be installed if not planned to use.</br>
    Install the [3.02 version for your OS](https://github.com/tesseract-ocr/tesseract/wiki)
	

* Important info *

Image Library *MUST* be initialized in `Suite Setup` before use by calling the keyword `Init` with specified arguments (see docs).

When `Init` is called library reads the yaml config and tries to locate given templates images (png files) in the provided dir with stored screenshots. If any name is not found library will throw and error.

If all the data is correct library memorizes it and creates keyword objects (templates, buttons, zones) to use them in Keywords call. This helps to pass to Keyword desired arguments just as names to make them more readable.

All the objects are destroyed when test execution is complete.


*Usage*

Implement the _ImageLibrary_ into robot test suite file with specifying (optional) the _output_ directory to store screenshots.

If directory not specified - execution dir is used.

_Example_

`Library ImageLibrary     screenshot_folder=${CURDIR}${/}output`


Create the *yaml* config file (read from [Keyword documentation](https://simakvokka.github.io/robotframework-imagelibrary/ImageLibrary.html)) and specify *windows* and its

contents: zones, templates, buttons and window existence criteria.

Call in Keywords window contents by its name.

_Example_ 

`${is_on_screen} =  Is Template On Screen    template=gummi` 
`Wait For Window` - main window supposed to be called and mustn't be passed as argument
`Wait For Show    window=settings` 
`${num} =  Get Number From Zone    zone=price   resize_after=30   contrast=1`


**Zones**
	Coordinates are taken in such format  [x, y, w, h]:  [123, 34, 12, 10]
	 
	 | x - from the top left corner of the desired window
	 
	 | y - top position from the desired window
	 
	 | w - width
	 
	 | h - height

