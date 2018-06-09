# Kora

# Table of contents
1. [What Is Kora](#whatIsKora)
2. [Packages](#packages)
    1. [Software Needed](#softwareNeeded)
    2. [Preinstalled Packages](#preinstalledPackages)
4. [Getting Started](#gettingStarted)
5. [Explaining The Source Code](#sourceCode)
    1. [User-Kora Interaction Logging](#interactionLogging)
    2. [Extrude Command](#extrudeCmd)  
    3. [Save Command](#saveCmd)  
    4. [Save As Command](#saveAsCmd)  
6. [Next Steps](#nextSteps)
7. [Authors](#authors)

<a name="whatIsKora"></a>
## What Is Kora
Kora is a proof of concept project that integrates a natural language processing library into Autodesk's Fusion 360 3-D computer aided design software.
Kora is a speech-based virtual assistant for Fusion that lets users perform a subset of tasks within the product such as saving a document by verbally instructing it to perform the task.
Kora offers users a tool that decreases the time required to achieve their goals within Fusion by offering an interface that runs in parallel with and complements the keyboard and mouse.


<a name="packages"></a>
## Packages

  <a name="softwareNeeded"></a>
  #### Software Needed
  Since _Autodesk's Fusion 360_ runs Add-Ins in their own environment, all software packages needed to run Kora had to be packaged within the Kora Add-In itself.
  Lucky for you, this means the only software that needs to be install is MongoDB.
  For this project we used v3.6.2, but any version newer than this will do.

  A user also needs to make an account at https://wit.ai to obtain their Server Access Token.

  <a name="preinstalledPackages"></a>
  #### Preinstalled Packages
  The software packages that are already packaged within the Kora source code are:
  - _PyAudio_ version 0.2.9. This is used for streaming audio from the user
  - _PortAudio_. This is an executable within PyAudio that PyAudio uses to stream audio.
  - _PyMongo_ version 3.61. PyMongo is the low-level driver wrapping the MongoDB API into Python.
  - _Mongoengine_ version 0.15.0. MongoEngine is a Document-Object Mapper for working with MongoDB from Python.




<a name="gettingStarted"></a>
## Getting Started
  Make sure you first read the Packages heading above.
  1.
    Install Kora into the Fusion 360 Add-Ins folder.
    The Add-Ins folder is generally in

  **Windows:**
  _C:/Users/<users\>/AppData/Roaming/Autodesk/"Autodesk Fusion 360"/API/AddIns_

  **Mac:**
  _/Users/<users\>/Library/"Application Support"/Autodesk/"Autodesk Fusion 360"/API/AddIns_

  2. Name the installed repository Kora. It is important that the installed repository is named Kora, to match the Add-In name.
  3. Go to wit.ai's website and get your _Server Access Token_ and paste it in _Kora/main/config.py WIT_AI_CLIENT_ACCESS_TOKEN_
  3. In Fusion click on the _ADD-INS_ dropdown in the top right of the ribbon, and click _Scripts and Add-Ins..._
  4. Click the _Add-Ins_ tab at the top
  5. Click _Create_
  6. Click _Python_ as the language and enter _Kora_ as the Add-In name
  7. In Folder Location, browse to the Kora folder that you placed in the Add-Ins directory in step 2
  8. Kora is now set up as an Add-In. Double click the _Kora_ Add-In
  9. Click the _Add-Ins_ tab at the top
  10. Click _Activate Kora_





<a name="sourceCode"></a>
## Explaining The Source Code

 <a name="interactionLogging"></a>
 ##### User-Kora Interaction Logging  
 ***
 Inside of _Kora/main/modules/logging_ is the relevant code.
 ** interaction.py ** has the _Mongoengine_ class that outlines how the user-kora interaction document should be stored. ** logInteraction.py ** is the python decorator responsible for the actual storing of the interaction document. It first calls ** mongoSetup.py ** to initiate the connection to the mongoDB daemon.

 The *logInteraction()* decorator is placed above the *executeCommand()* function in **fusion_execute_intent.py**. *executeCommand()* is the function called when Kora has a response back from Wit.ai and Kora wants to figure out what command to execute then execute it. Before that happens, the JSON containing the Wit.ai response and some extra, is routed through *logInteraction()*. *logInteraction()* then extracts information from the JSON then lets the JSON continue onto the *executeCommand()*. When *executeCommand()* returns, it returns to *logInteraction()* where the remaining fields needed to store the interaction document are extracted.
 *logInteraction()* then inserts the interaction document into the mongoDB database.


 <a name="extrudeCmd"></a>
 ##### Extrude Command  
 ***
 All of the commands are located in <em>Kora/main/modules/fusion_execute_intent/tasks</em>. The _extrude()_ function is given a sting representing what the user said, the magnitude, and the units.
_extrude()_ checks if there is a "down" in the sentence. If there is and the magnitude is currently positive, then the magnitude is changed to negative. Next, _extrude()_ converts the _magnitude_ to the equivalent magnitude in terms of centimeters (the API only excepts centimeters) if the _units_ are not already centimeters.
_extrude()_ then scans through all of the profiles and faces in the project and extrudes them by _magnitude_ _units_. If there are no profiles or faces selected, then Kora prompts the user to select the profile or face they would like extruded.



 <a name="saveCmd"></a>
 ##### Save Command  
 ***
_save()_ first checks that the project has been saved before. If it hasn't then Kora prompts the user to input what they want the project to be called and then hands off the flow of control to _saveAs()_. If the project has been saved already, i.e. the project has a name, then _save()_ goes ahead and saves the project.


 <a name="saveAsCmd"></a>
 ##### Save As Command  
 ***
_saveAs()_ first checks if the call is coming from _save()_. If it is, then it creates a copy of the project and saves it as the supplied filename. Otherwise, _saveAs()_ firs converts the supplied filename to camelcase and then creates a copy of the file and saves it under the camelcased filename.




<a name="nextSteps"></a>
## Next Steps
1. Reduce Kora's latency. Right now it takes on average 3.5 seconds after the user stops speaking until Fusion executes the command. This is all on Wit.ai's side. Kora is simply passing the audio on to Wit and then waiting for a response. The code is set up such that pivoting to a new natural language processor shouldn't be too difficult.
2. Adding a wake-word to Kora. Instead of Kora always listening in the background, add a "Kora" wake-word would be much more user friendly.



<a name="authors"></a>
## Authors
Kora was developed by ...
- Austin Row rowa@oregonstate.edu
- Jeremy Fischer fischjer4@gmail.com

For their undergraduate senior project at Oregon State University
