*** Settings ***
# Add Library to your tests. If you want to store all saved screenshots during the library keywords execution
# in the specific place pass an optional argument screenshot_folder as path. If not passed the current execution dir is used
Library         ImageLibrary        screenshot_folder=${CURDIR}${/}output

# In Suite Setup keyword init the Image Library with special keyword Init.
Suite Setup 	On Suite Setup

*** Keywords ***
On Suite Setup
    # Get window area to specify only the area of a currently running program (Library will use it for zones). If you need the whole window
    # just don't pass arguent area to Init keyword.
    ${windowArea} =     Get Window Area

    # Keyword to initialize the Image Library. Pass settings as list with paths to yaml config files, references as list with paths to template images
    # and optional area if you want to work only with currently active window.
    # You need also to specify the area region by using keyword Get Window Area which will automatically detect the active window or pass your own.
    Init                settings=${Settings}     references=${References}   area=${windowArea}


*** Variables ***
# List with yaml configs
@{SETTINGS}     ${CURDIR}${/}config.yaml
# List with template images dirs
@{REFERENCES}   ${CURDIR}${/}images

