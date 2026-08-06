import tkinter
from tkinter import messagebox
import tkinter.font as tkFont
import serial
from threading import Thread
from serial.tools import list_ports
import time
import sys, os

class MainWindow(tkinter.Frame):
    '''Class for the main window toplevel'''
    def __init__ (self, parent, *args, **kwargs):
        #Initialise parent class
        tkinter.Frame.__init__(self, parent, *args, **kwargs)
        #Assign parent object
        self.parent = parent

        #Setup the grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        #Create larger font for buttons and menus
        self.menuFont = tkFont.Font(size=15)
        self.buttonColour = "#BABABA"

        self.thisPath = os.path.abspath(".")
        try:
            self.thisPath = sys._MEIPASS
        except:
            pass

        #Create a frame for each of the windows
        self.displayFrame = tkinter.Frame(self)
        self.displayFrame.grid(row=0, column=0, sticky="NESW")
        self.loadingFrame = tkinter.Frame(self)
        self.loadingFrame.grid(row=0, column=0, sticky="NESW")
        self.maintenanceFrame = tkinter.Frame(self)
        self.maintenanceFrame.grid(row=0, column=0, sticky="NESW")
        self.connectFrame = tkinter.Frame(self)
        self.connectFrame.grid(row=0, column=0, sticky="NESW")
        
        #Frame for settings when connection
        self.connectOptionsFrame = tkinter.Frame(self.connectFrame)
        self.connectOptionsFrame.pack(expand=True)

        #Which port has been chosen
        self.selectedPort = tkinter.StringVar()
        self.selectedPort.set("Port 1")
        #Drop down option menu (with default values, will be overridden)
        self.portOption = tkinter.OptionMenu(self.connectOptionsFrame, self.selectedPort, "Port 1", "Port 2", "Port 3", "Port 4")
        self.portOption.configure(font=self.menuFont, bg=self.buttonColour, activebackground=self.buttonColour)
        self.parent.nametowidget(self.portOption.menuname).configure(font=self.menuFont)
        self.portOption.pack(side="left", anchor="center", fill="x")

        #Which type of machine is being accessed
        self.selectedType = tkinter.IntVar()
        self.selectedType.set(0)

        #A set of radio buttons to allow the suer to choose the machine type
        self.radioFrame = tkinter.Frame(self.connectOptionsFrame)
        self.radioFrame.pack(side="left", anchor="center", fill="x")

        #Set of variables used to assign the correct image to the reactors (binary bit values)
        self.selectValue = 8
        self.heatValue = 4
        self.mixValue = 2
        self.agitateValue = 1

        #What state each of the reactors is in as an integer value (4 binary bits give a value from 0 to 15)
        self.reactorValues = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        #How many reactors this machine is using
        self.numberReactorsInUse = 0

        #File names for reactior images
        self.reactorImageNames = ["reactorTopDown", 
                                  "reactorTopDownAgitating",
                                  "reactorTopDownMixing",
                                  "reactorTopDownMixingAgitating",
                                  "reactorTopDownHeating",
                                  "reactorTopDownHeatingAgitating",
                                  "reactorTopDownHeatingMixing",
                                  "reactorTopDownHeatingMixingAgitating",
                                  "reactorTopDownSelected", 
                                  "reactorTopDownSelectedAgitating",
                                  "reactorTopDownSelectedMixing",
                                  "reactorTopDownSelectedMixingAgitating",
                                  "reactorTopDownSelectedHeating",
                                  "reactorTopDownSelectedHeatingAgitating",
                                  "reactorTopDownSelectedHeatingMixing",
                                  "reactorTopDownSelectedHeatingMixingAgitating"]
        self.reactorStateImages = []
        #Alternate images for black swan reactors (without feeders)
        self.reactorSwanImageNames = ["reactorSwanTopDown", 
                                      "reactorSwanTopDown",
                                      "reactorSwanTopDownMixing",
                                      "reactorSwanTopDownMixing",
                                      "reactorSwanTopDownHeating",
                                      "reactorSwanTopDownHeating",
                                      "reactorSwanTopDownHeatingMixing",
                                      "reactorSwanTopDownHeatingMixing",
                                      "reactorSwanTopDownSelected", 
                                      "reactorSwanTopDownSelected",
                                      "reactorSwanTopDownSelectedMixing",
                                      "reactorSwanTopDownSelectedMixing",
                                      "reactorSwanTopDownSelectedHeating",
                                      "reactorSwanTopDownSelectedHeating",
                                      "reactorSwanTopDownSelectedHeatingMixing",
                                      "reactorSwanTopDownSelectedHeatingMixing"]
        #Alternate images for medusa reactors (without mixer or heater)
        self.reactorMedusaImageNames = ["reactorMedusaTopDown", 
                                      "reactorMedusaTopDownAgitating",
                                      "reactorMedusaTopDown",
                                      "reactorMedusaTopDownAgitating",
                                      "reactorMedusaTopDown",
                                      "reactorMedusaTopDownAgitating",
                                      "reactorMedusaTopDown",
                                      "reactorMedusaTopDownAgitating",
                                      "reactorMedusaTopDownSelected", 
                                      "reactorMedusaTopDownSelectedAgitating",
                                      "reactorMedusaTopDownSelected",
                                      "reactorMedusaTopDownSelectedAgitating",
                                      "reactorMedusaTopDownSelected",
                                      "reactorMedusaTopDownSelectedAgitating",
                                      "reactorMedusaTopDownSelected",
                                      "reactorMedusaTopDownSelectedAgitating"]
        
        self.reactorSwanStateImages = []
        self.reactorMedusaStateImages = []
        #Which type of reactor to use (one with or without feeding/agitating)
        self.reactorNormals = [[True, True, True, True, True, True, True, True, True, True], #Ray
                               [True, True, True, True, True, True, True, True, True, True], #Ray-3
                               [True, True, True, True, True, True, True, True, True, True], #Ray-I
                               [True, True, True, True, True, True, True, True, True, True], #Caterpillar
                               [True, True, True, True, True, True, True, True, True, True], #Lobster
                               [True, True, True, True, True, True, True, True, True, True], #Lobster-I
                               [True, True, True, True, False, False, False, False, False, False], #Black Swan
                               [True, True, True, True, True, True, True, True, True, True]] #Medusa

        #Select the current reactor type information
        self.reactorTypes = self.reactorNormals[self.selectedType.get()]

        #Iterate through reactor file names and load the images
        for name in self.reactorImageNames:
            image = tkinter.PhotoImage(file=self.pathTo("images/{0}.png").format(name))
            self.reactorStateImages.append(image)
        for name in self.reactorSwanImageNames:
            image = tkinter.PhotoImage(file=self.pathTo("images/{0}.png").format(name))
            self.reactorSwanStateImages.append(image)
        for name in self.reactorMedusaImageNames:
            image = tkinter.PhotoImage(file=self.pathTo("images/{0}.png").format(name))
            self.reactorMedusaStateImages.append(image)
        
        #List of machine names and identifiers, used for CONTINUE_??? command to identify correct machine
        self.machineList = ["Ray", "Ray-I", "Caterpillar", "Lobster", "Lobster-I", "Black Swan", "Medusa"]
        self.machineIdentifiers = ["ray", "ray-i", "caterpillar", "lobster", "lobster-i", "blackswan", "medusa"]
        self.machineRadioButtons = []

        #Constants used to refer to each machine type (so the correct index is used)
        self.RAY = 0
        self.RAYI = 1
        self.CATERPILLAR = 2
        self.LOBSTER = 3
        self.LOBSTERI = 4
        self.BLACKSWAN = 5
        self.MEDUSA = 6
        
        #Arrays describing how the machines reactors and feeders are laid out
        #Machine shape: [Reactor number, row, column]
        #Machine feeders: [Feeder number, [reactors], [rowPos, colPos, height, width]]
        self.machineShape = [[["1", 2, 4], ["2", 2, 3]], #Ray
                             [["1", 2, 4], ["2", 2, 3]], #Ray-I
                             [["1", 2, 4], ["2", 2, 3], ["3", 2, 2], ["4", 2, 1], ["5", 2, 0]], #Caterpillar
                             [["1", 2, 4], ["2", 2, 3], ["3", 2, 2], ["4", 3, 2], ["5", 3, 3], ["6", 3, 4]], #Lobster
                             [["1", 2, 4], ["2", 2, 3], ["3", 3, 3], ["4", 3, 4]], #Lobster-I
                             [["1", 2, 4], ["2", 2, 3], ["3", 3, 3], ["4", 3, 4], ["5", 0, 4], ["6", 0, 3], ["7", 5, 3], ["8", 5, 4], ["9", 5, 0], ["10", 5, 1]], #Black Swan
                             [["1", 3, 4], ["2", 3, 3], ["3", 3, 2], ["4", 3, 1], ["5", 3, 0], ["6", 2, 4], ["7", 2, 3],    ["8", 2, 2], ["9", 2, 1], ["10", 2, 0]]] #Medusa
        self.machineFeeders = [[["1", [0, 1], [1, 3, 1, 2]]], #Ray
                               [["1", [0, 1, 2], [1, 2, 1, 3]]], #Ray-3
                               [["1", [0, 1, 2, 3, 4], [1, 0, 1, 5]],], #Caterpillar
                               [["1", [0, 1, 2], [1, 2, 1, 3]], ["2", [3, 4, 5], [4, 2, 1, 3]]], #Lobster
                               [["1", [0], [1, 4, 1, 1]], ["2", [1], [1, 3, 1, 1]], ["3", [2], [4, 3, 1, 1]], ["4", [3], [4, 4, 1, 1]]], #Lobster-I
                               [["1", [0], [1, 4, 1, 1]], ["2", [1], [1, 3, 1, 1]], ["3", [2], [4, 3, 1, 1]], ["4", [3], [4, 4, 1, 1]]], #Black Swan
                               [["1", [0, 1, 2, 3, 4], [1, 0, 1, 5]], ["2", [5, 6, 7, 8, 9], [4, 0, 1, 5]]]] #Medusa
        
        self.machineNumbers = [{"mixers" : 2, "heaters" : 2, "agitators" : 2}, #Ray
                               {"mixers" : 2, "heaters" : 2, "agitators" : 2}, #Ray-I
                               {"mixers" : 5, "heaters" : 5, "agitators" : 5}, #Caterpillar
                               {"mixers" : 6, "heaters" : 6, "agitators" : 6}, #Lobster
                               {"mixers" : 4, "heaters" : 4, "agitators" : 4}, #Lobster-I
                               {"mixers" : 8, "heaters" : 10, "agitators" : 4}, #Black Swan
                               {"mixers" : 1, "heaters" : 0, "agitators" : 10}] #Medusa

        #Setup radio buttons with the machine labels
        self.radioFrame.grid_columnconfigure(0, weight=1)
        for i in range(0, len(self.machineList)):
            self.radioFrame.grid_rowconfigure(i, weight=1)

        for i in range(0, len(self.machineList)):
            if i > 1:
                radioButton = tkinter.Radiobutton(self.radioFrame, text=self.machineList[i], variable=self.selectedType, value=i, command=self.typeChanged, font=self.menuFont)
                radioButton.grid(row=i, column=0, sticky="W")
                self.machineRadioButtons.append(radioButton)

        #Create the connect button
        self.connectButton = tkinter.Button(self.connectOptionsFrame, text="Connect", command=self.connectPressed, font=self.menuFont, bg=self.buttonColour)
        self.connectButton.pack(side="left", anchor="center", fill="x")

        #Fill the loading frame so it can display information to the user
        self.loadingTextFrame = tkinter.Frame(self.loadingFrame)
        self.loadingTextFrame.pack(expand=True)
        self.loadingFailureFrame = tkinter.Frame(self.loadingFrame)
        self.loadingText = tkinter.Label(self.loadingTextFrame, text="Connecting To Machine", font=self.menuFont)
        self.loadingText.pack(anchor="center", fill="x")
        self.loadingFailureText = tkinter.Label(self.loadingFailureFrame, text="Connection Failed Please Try Again", font=self.menuFont)
        self.loadingFailureText.pack(side="top", anchor="center", fill="x")
        self.loadingBackButton = tkinter.Button(self.loadingFailureFrame, text="Back", command=self.failureBack, font=self.menuFont, bg=self.buttonColour)
        self.loadingBackButton.pack(side="bottom", anchor="center")

        #Variables to store information about the serial connection and information received
        self.connected = False
        self.connectedPort = None
        self.serialConnection = None
        self.currentMessage = ""
        self.receivedMessages = []
        self.portLabels = []

        self.gettingStatus = False
        self.statusDelay = 2.0

        self.lastMessageSent = 0
        self.messageDelay = 0.2

        #Setup grid for the main machine display
        self.displayFrame.grid_rowconfigure(0, weight=1)
        self.displayFrame.grid_rowconfigure(1, weight=1)        
        self.displayFrame.grid_rowconfigure(2, weight=10)
        self.displayFrame.grid_rowconfigure(3, weight=1)
        self.displayFrame.grid_columnconfigure(0, weight=1)
        self.displayFrame.grid_columnconfigure(1, weight=1)
        
        #Frame to display the overview of the machine
        self.machineOverviewFrame = tkinter.Frame(self.displayFrame)
        self.machineOverviewFrame.grid(row=2, column=1)

        #Create a frame for the control buttons
        self.controlButtons = tkinter.Frame(self.displayFrame)
        self.controlButtons.grid(row=0, column=1, sticky="NESW")
        self.controlButtons.grid_rowconfigure(0, weight=1)
        for i in range(0, 3):
            self.controlButtons.grid_columnconfigure(i, weight=1)
        #Add buttons to control frame
        self.controlSelectAllButton = tkinter.Button(self.controlButtons, text="Select All", command=lambda : self.reactorSelectionButtonPressed(True, False, False))
        self.controlSelectAllButton.grid(row=0, column=0, sticky="NESW")
        self.controlInvertButton = tkinter.Button(self.controlButtons, text="Invert Selection", command=lambda : self.reactorSelectionButtonPressed(False, True, False))
        self.controlInvertButton.grid(row=0, column=1, sticky="NESW")
        self.controlClearButton = tkinter.Button(self.controlButtons, text="Clear Selection", command=lambda : self.reactorSelectionButtonPressed(False, False, True))
        self.controlClearButton.grid(row=0, column=2, sticky="NESW")
        #Header label
        self.topDownLabel = tkinter.Label(self.displayFrame, text="Top Down Overview", font=self.menuFont)
        self.topDownLabel.grid(row=1, column=1, sticky="NESW")

        #Create frame to show machine top down
        self.reactorGrid = tkinter.Frame(self.machineOverviewFrame)
        self.reactorGrid.pack(anchor="center", fill="x")
        for i in range(0, 6):
            self.reactorGrid.grid_rowconfigure(i, weight=1)
        for i in range(0, 6):
            self.reactorGrid.grid_columnconfigure(i, weight=1)
        
        #Create reactor buttons using default images
        self.reactorButtons = []
        self.reactorTopDownImage = tkinter.PhotoImage(file=self.pathTo("images/reactorTopDown.png"))
        self.reactorTopDownSelectedImage = tkinter.PhotoImage(file=self.pathTo("images/reactorTopDownSelected.png"))
        #Iterate through maximum reactors
        for i in range(0, 10):
            #Create button
            reactor = tkinter.Button(self.reactorGrid, text=str(i + 1), image=self.reactorTopDownImage, compound="top", command=lambda x = i: self.changeSelectedReactor(x))
            #Calculate position in grid
            r = int(i / 5)
            c = i - (r * 5)
            if r == 1:
                c = 5 - c
            #Place the buttons
            reactor.grid(row=r, column=c, sticky="NESW")
            #Store in list
            self.reactorButtons.append(reactor)

        #Create buttons for feeders
        self.feederButtons = []
        #Iterate through maximum feeders
        for i in range(0, 4):
            #Create the button
            feeder = tkinter.Button(self.reactorGrid, text="Feeder " + str(i + 1), command=lambda x=i : self.openSingleFeeder(x))
            #Add to grid
            feeder.grid(row=0, column=0, sticky="NESW")
            #Add to list
            self.feederButtons.append(feeder)
            feeder.grid_remove()
        
        #Add visual representation of the power sockets on the machine for frame of reference
        self.powerSocketsButton = tkinter.Button(self.reactorGrid, text="⦿\n\n⦿", state="disabled", disabledforeground="black")
        self.powerSocketsButton.grid(row=2, column=5, rowspan=2, sticky="NS")

        #Lists to store the state of each of the reactor values
        self.reactorSelected = [False, False, False, False, False, False, False, False, False, False]
        self.reactorMixing = [False, False, False, False, False, False, False, False, False, False]
        self.reactorAgitating = [False, False, False, False, False, False, False, False, False, False]
        self.reactorHeating = [False, False, False, False, False, False, False, False, False, False]
        self.reactorTargetTemp = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.reactorCurrentTemp = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        #Lists to store the state of the feeder values
        self.feederFeeding = [False, False, False, False]
        self.feederDuration = [0, 0, 0, 0]
        self.feederDelay = [0, 0, 0, 0]

        #Whether in maintenance mode - overrides enable/disable
        self.maintenanceMode = False
        
        #Create buttons for config
        self.extraButtonsFrame = tkinter.Frame(self.displayFrame)
        self.extraButtonsFrame.grid(row=3, column=1)
        self.maintenanceModeButton = tkinter.Button(self.extraButtonsFrame, text="Maintenance Mode", command=self.startMaintenance)
        self.maintenanceModeButton.grid(row=0, column=1)
        
        #Create reactor view frame
        self.reactorViewFrame = tkinter.Frame(self.displayFrame)
        self.reactorViewFrame.grid(row=0, column=0, rowspan=3, sticky="NESW")
        self.reactorViewFrame.grid_rowconfigure(0, weight=1)
        self.reactorViewFrame.grid_rowconfigure(1, weight=5)
        self.reactorViewFrame.grid_rowconfigure(2, weight=2)
        self.reactorViewFrame.grid_columnconfigure(0, weight=1)

        #Label to show which reactors are selected
        self.reactorNameLabel = tkinter.Label(self.reactorViewFrame, text="No Reactor Selected")
        self.reactorNameLabel.grid(row=0, column=0, sticky="NESW")

        #Frame to hold the image of the reactors
        self.reactorImageFrame = tkinter.Frame(self.reactorViewFrame)
        self.reactorImageFrame.grid(row=1, column=0, sticky="NSEW")
        self.reactorImageFrame.grid_rowconfigure(0, weight=1)
        self.reactorImageFrame.grid_columnconfigure(0, weight=1)

        #Frame to hold the reactor information
        self.reactorDataFrame = tkinter.Frame(self.reactorViewFrame)
        self.reactorDataFrame.grid(row=2, column=0, sticky="NESW")
        self.reactorDataFrame.grid_columnconfigure(0, weight=1)
        for i in range(0, 4):
            self.reactorDataFrame.grid_rowconfigure(i, weight=1)
        
        #Load and rescale the images of the reactors
        self.reactorBasicImage = tkinter.PhotoImage(file=self.pathTo("images/reactorOutlined.png"))
        self.reactorBasicImage = self.reactorBasicImage.zoom(6, 6)
        self.reactorDisplayLabel = tkinter.Label(self.reactorImageFrame, image=self.reactorBasicImage)
        self.reactorDisplayLabel.grid(row=0, column=0, sticky="NESW")

        #Versions with outlines
        self.reactorMixerImage = tkinter.PhotoImage(file=self.pathTo("images/reactorOutlinedMixer.png"))
        self.reactorMixerImage = self.reactorMixerImage.zoom(6, 6)
        self.reactorHeaterImage = tkinter.PhotoImage(file=self.pathTo("images/reactorOutlinedHeater.png"))
        self.reactorHeaterImage = self.reactorHeaterImage.zoom(6, 6)
        self.reactorAgitatorImage = tkinter.PhotoImage(file=self.pathTo("images/reactorOutlinedAgitator.png"))
        self.reactorAgitatorImage = self.reactorAgitatorImage.zoom(6, 6)
        self.reactorFeederImage = tkinter.PhotoImage(file=self.pathTo("images/reactorOutlinedFeeder.png"))
        self.reactorFeederImage = self.reactorFeederImage.zoom(6, 6)

        #Medusa image variations
        self.reactorMedusaBasicImage = tkinter.PhotoImage(file=self.pathTo("images/reactorOutlinedMedusa.png"))
        self.reactorMedusaBasicImage = self.reactorMedusaBasicImage.zoom(6, 6)
        self.reactorMedusaAgitatorImage = tkinter.PhotoImage(file=self.pathTo("images/reactorOutlinedAgitatorMedusa.png"))
        self.reactorMedusaAgitatorImage = self.reactorMedusaAgitatorImage.zoom(6, 6)
        self.reactorMedusaFeederImage = tkinter.PhotoImage(file=self.pathTo("images/reactorOutlinedFeederMedusa.png"))
        self.reactorMedusaFeederImage = self.reactorMedusaFeederImage.zoom(6, 6)

        #Frame to hold mixer information
        self.reactorMixerFrame = tkinter.Frame(self.reactorDataFrame)
        self.reactorMixerFrame.grid(row=0, column=0, sticky="NSEW")
        #Information label
        self.reactorMixerLabel = tkinter.Label(self.reactorMixerFrame, text="Mixer: Enabled")
        self.reactorMixerLabel.pack(side="left")
        #Button to open mixer settings
        self.reactorMixerButton = tkinter.Button(self.reactorMixerFrame, text="Configure Mixing", command=lambda : self.openSettings("mixer"))
        self.reactorMixerButton.pack(side="right")
        #Bindings to allow hovering
        self.reactorMixerFrame.bind("<Enter>", lambda event, x=0 : self.changeHighlight(x))
        self.reactorMixerFrame.bind("<Leave>", lambda event, x= -1 : self.changeHighlight(x))
        for key, child in self.reactorMixerFrame.children.items():
            child.bind("<Enter>", lambda event, x=0 : self.changeHighlight(x))
            child.bind("<Leave>", lambda event, x= -1 : self.changeHighlight(x))

        #Frame to hold heater information
        self.reactorHeaterFrame = tkinter.Frame(self.reactorDataFrame)
        self.reactorHeaterFrame.grid(row=1, column=0, sticky="NSEW")
        #Information labels
        self.reactorCurrentTempLabel = tkinter.Label(self.reactorHeaterFrame, text="Current Temp: 15")
        self.reactorCurrentTempLabel.pack(side="top", anchor="nw")
        self.reactorTargetTempLabel = tkinter.Label(self.reactorHeaterFrame, text="Target Temp: 35")
        self.reactorTargetTempLabel.pack(side="left", anchor="s")
        #Button to open heater settings
        self.reactorChangeTempSettingsButton = tkinter.Button(self.reactorHeaterFrame, text="Configure Heating", command=lambda : self.openSettings("heater"))
        self.reactorChangeTempSettingsButton.pack(side="right")
        #Bindings to allow hovering
        self.reactorHeaterFrame.bind("<Enter>", lambda event, x=1 : self.changeHighlight(x))
        self.reactorHeaterFrame.bind("<Leave>", lambda event, x= -1 : self.changeHighlight(x))
        for key, child in self.reactorHeaterFrame.children.items():
            child.bind("<Enter>", lambda event, x=1 : self.changeHighlight(x))
            child.bind("<Leave>", lambda event, x= -1 : self.changeHighlight(x))

        #Frame to hold agitator information
        self.reactorAgitatorFrame = tkinter.Frame(self.reactorDataFrame)
        self.reactorAgitatorFrame.grid(row=2, column=0, sticky="NSEW")
        #Information label
        self.reactorAgitatorLabel = tkinter.Label(self.reactorAgitatorFrame, text="Agitator: Enabled")
        self.reactorAgitatorLabel.pack(side="left")
        #Button to open agitator settings
        self.reactorAgitatorButton = tkinter.Button(self.reactorAgitatorFrame, text="Configure Agitation", command=lambda : self.openSettings("agitator"))
        self.reactorAgitatorButton.pack(side="right")
        #Bindings to allow hovering
        self.reactorAgitatorFrame.bind("<Enter>", lambda event, x=2 : self.changeHighlight(x))
        self.reactorAgitatorFrame.bind("<Leave>", lambda event, x= -1 : self.changeHighlight(x))
        for key, child in self.reactorAgitatorFrame.children.items():
            child.bind("<Enter>", lambda event, x=2 : self.changeHighlight(x))
            child.bind("<Leave>", lambda event, x= -1 : self.changeHighlight(x))

        #Frame to hold feeder information
        self.reactorFeederFrame = tkinter.Frame(self.reactorDataFrame)
        self.reactorFeederFrame.grid(row=3, column=0, sticky="NSEW")
        #Information labels
        self.reactorFeederStateLabel = tkinter.Label(self.reactorFeederFrame, text="Feeding: No")
        self.reactorFeederStateLabel.pack(side="left")
        self.reactorFeederTimingLabel = tkinter.Label(self.reactorFeederFrame, text="Timing: 1s every 60min")
        self.reactorFeederTimingLabel.pack(side="left")
        #Button to open feeder settings
        self.reactorFeederSettingsButton = tkinter.Button(self.reactorFeederFrame, text="Configure Feeding", command=lambda : self.openSettings("feeder"))
        self.reactorFeederSettingsButton.pack(side="right")
        #Bindings to allow hovering
        self.reactorFeederFrame.bind("<Enter>", lambda event, x=3 : self.changeHighlight(x))
        self.reactorFeederFrame.bind("<Leave>", lambda event, x= -1 : self.changeHighlight(x))
        for key, child in self.reactorFeederFrame.children.items():
            child.bind("<Enter>", lambda event, x=3 : self.changeHighlight(x))
            child.bind("<Leave>", lambda event, x= -1 : self.changeHighlight(x))

        #Window to hold controls for motor and heater settings
        self.setupWindow = tkinter.Toplevel(self)
        self.setupWindow.grid_columnconfigure(0, weight=1)
        self.setupWindow.grid_rowconfigure(0, weight=1)
        self.setupWindow.grid_rowconfigure(1, weight=4)
        self.setupShape = [700, 450]
        self.setupWindow.geometry("{0}x{1}".format(self.setupShape[0], self.setupShape[1]))
        self.setupWindow.minsize(self.setupShape[0], self.setupShape[1])
        self.setupWindowTitle = tkinter.Label(self.setupWindow, text="Temperature Setup, Reactor 1", font=self.menuFont)
        self.setupWindowTitle.grid(row=0, column=0, columnspan=2, sticky="NSEW")
        self.setupWindow.protocol("WM_DELETE_WINDOW", self.closeSettings)

        #For each settings type, iterate reactors and create settings info, pack to frames
        #Create frames for different settings groups
        self.mixerSettingsFrame = tkinter.Frame(self.setupWindow)
        self.heaterSettingsFrame = tkinter.Frame(self.setupWindow)
        self.agitatorSettingsFrame = tkinter.Frame(self.setupWindow)
        self.feederSettingsFrame = tkinter.Frame(self.setupWindow)
        #Grid to the same place so they cover each other
        self.mixerSettingsFrame.grid(row=1, column=0, sticky="NESW")
        self.heaterSettingsFrame.grid(row=1, column=0, sticky="NESW")
        self.agitatorSettingsFrame.grid(row=1, column=0, sticky="NESW")
        self.feederSettingsFrame.grid(row=1, column=0, sticky="NESW")

        #Mixer settings frame configuration
        self.mixerSettingsFrame.grid_rowconfigure(0, weight=1)
        self.mixerSettingsFrame.grid_rowconfigure(1, weight=1)
        self.mixerSettingsFrame.grid_rowconfigure(2, weight=1)
        self.mixerSettingsFrame.grid_columnconfigure(0, weight=1)
        self.mixerSettingsFrame.grid_columnconfigure(1, weight=1)

        #Create frame to show mixer information
        self.mixerSettingsDisplayFrame = tkinter.Frame(self.mixerSettingsFrame)
        self.mixerSettingsDisplayFrame.grid(row=0, column=0, columnspan=2, sticky="NESW")

        self.mixerSettingsObjects = []
        #Create 10 reactors worth of template objects to show each reactors information (10 is the maximum number)
        for reactorNum in range(0, 10):
            mixFrame = tkinter.Frame(self.mixerSettingsDisplayFrame)
            #Labels to show information
            titleLabel = tkinter.Label(mixFrame, text="Mixer {0}".format(reactorNum + 1))
            stateLabel = tkinter.Label(mixFrame, text="State: Off", fg="red")
            timingLabel = tkinter.Label(mixFrame, text="0s On\n0s Off")
            titleLabel.pack()
            stateLabel.pack()
            timingLabel.pack()
            #Create object and store in list
            mixerObject = {"frame" : mixFrame, "mainLabel" : titleLabel, "stateLabel" : stateLabel, "timingLabel" : timingLabel}
            self.mixerSettingsObjects.append(mixerObject)
        
        #Pack objects into frame
        for mixObject in self.mixerSettingsObjects:
            mixObject["frame"].pack(side="left", expand="y")

        #Frame to hold mixer mode controls
        self.mixerModeFrame = tkinter.Frame(self.mixerSettingsFrame)
        self.mixerModeFrame.grid(row=1, column=0)

        #Buttons to change state of selected mixers
        self.mixerModeLabel = tkinter.Label(self.mixerModeFrame, text="Change Mixer State")
        self.mixerModeLabel.pack()
        self.mixerModeOffButton = tkinter.Button(self.mixerModeFrame, text="Always Off", command=lambda : self.settingChange(0, 0))
        self.mixerModeOffButton.pack()
        self.mixerModeOnButton = tkinter.Button(self.mixerModeFrame, text="Always On", command=lambda : self.settingChange(0, 1))
        self.mixerModeOnButton.pack()

        #Entry fields to allow the mixer timings to be changed
        self.mixerTimingEntry = NumberGroup(self.mixerSettingsFrame, titles=["On Time", "Off Time"], header="Timed Mode", valueHandler=self.setMixerTiming)
        self.mixerTimingEntry.grid(row=1, column=1)

        #Heater settings frame configuration
        self.heaterSettingsFrame.grid_rowconfigure(0, weight=1)
        self.heaterSettingsFrame.grid_rowconfigure(1, weight=1)
        self.heaterSettingsFrame.grid_rowconfigure(2, weight=1)
        self.heaterSettingsFrame.grid_columnconfigure(0, weight=1)

        self.heaterSettingsDisplayFrame = tkinter.Frame(self.heaterSettingsFrame)
        self.heaterSettingsDisplayFrame.grid(row=0, column=0, sticky="NESW")

        self.heaterSettingsObjects = []
        #Objects to display heater settings for selected reactors
        for reactorNum in range(0, 10):
            heatFrame = tkinter.Frame(self.heaterSettingsDisplayFrame)
            titleLabel = tkinter.Label(heatFrame, text="Heater {0}".format(reactorNum + 1))
            stateLabel = tkinter.Label(heatFrame, text="State: Off", fg="red")
            targetLabel = tkinter.Label(heatFrame, text="Target: 0°C")
            currentLabel = tkinter.Label(heatFrame, text="Current: 0°C")
            titleLabel.pack()
            stateLabel.pack()
            targetLabel.pack()
            currentLabel.pack()
            #Create object and add to list
            heaterObject = {"frame" : heatFrame, "mainLabel" : titleLabel, "stateLabel" : stateLabel, "targetLabel" : targetLabel, "currentLabel" : currentLabel}
            self.heaterSettingsObjects.append(heaterObject)
        
        #Pack the settings objects
        for heatObject in self.heaterSettingsObjects:
            heatObject["frame"].pack(side="left", expand="y")

        #Entry to allow the target temperature to be changed
        self.heatTargetVar = tkinter.IntVar()
        self.heaterTimeEntry = NumberGroup(self.heaterSettingsFrame, titles=["Target Temperature"], header="Change Target Temperature", valueHandler=self.setHeaterTemp)
        self.heaterTimeEntry.grid(row=1, column=0)

        #Agitator settings configuration
        self.agitatorSettingsFrame.grid_rowconfigure(0, weight=1)
        self.agitatorSettingsFrame.grid_rowconfigure(1, weight=1)
        self.agitatorSettingsFrame.grid_rowconfigure(2, weight=1)
        self.agitatorSettingsFrame.grid_columnconfigure(0, weight=1)

        self.agitatorSettingsDisplayFrame = tkinter.Frame(self.agitatorSettingsFrame)
        self.agitatorSettingsDisplayFrame.grid(row=0, column=0, sticky="NESW")

        self.agitatorSettingsObjects = []
        #Objects to display the agitator settings of selected reactors
        for reactorNum in range(0, 10):
            agiFrame = tkinter.Frame(self.agitatorSettingsDisplayFrame)
            titleLabel = tkinter.Label(agiFrame, text="Agitator {0}".format(reactorNum + 1))
            stateLabel = tkinter.Label(agiFrame, text="State: Off", fg="red")
            timingLabel = tkinter.Label(agiFrame, text="0s Before Feed")
            titleLabel.pack()
            stateLabel.pack()
            timingLabel.pack()
            #Create the object and add to the list
            agitatorObject = {"frame" : agiFrame, "mainLabel" : titleLabel, "stateLabel" : stateLabel, "timingLabel" : timingLabel}
            self.agitatorSettingsObjects.append(agitatorObject)
        
        #Pack the objects
        for agiObject in self.agitatorSettingsObjects:
            agiObject["frame"].pack(side="left", expand="y")

        #Entry to allow the changing of the agitation before feeding
        self.agiTimeVar = tkinter.IntVar()
        self.agitatorTimeEntry = NumberGroup(self.agitatorSettingsFrame, titles=["Agitate Before Feed (s)"], header="Change Agitation Duration", valueHandler=self.setAgitatorTiming)
        self.agitatorTimeEntry.grid(row=1, column=0)

        #Feeder settings configuration
        self.feederSettingsFrame.grid_rowconfigure(0, weight=1)
        self.feederSettingsFrame.grid_rowconfigure(1, weight=1)
        self.feederSettingsFrame.grid_rowconfigure(2, weight=1)
        self.feederSettingsFrame.grid_columnconfigure(0, weight=1)
        self.feederSettingsFrame.grid_columnconfigure(1, weight=1)

        self.feederSettingsDisplayFrame = tkinter.Frame(self.feederSettingsFrame)
        self.feederSettingsDisplayFrame.grid(row=0, column=0, columnspan=2, sticky="NESW")

        self.feederSettingsObjects = []
        #Objects to display the feeder settings for selected reactors
        for feederNum in range(0, 4):
            feedFrame = tkinter.Frame(self.feederSettingsDisplayFrame)
            titleLabel = tkinter.Label(feedFrame, text="Feeder {0}".format(feederNum + 1))
            stateLabel = tkinter.Label(feedFrame, text="State: Off", fg="red")
            onTimeLabel = tkinter.Label(feedFrame, text="Feed For: 0s")
            offTimeLabel = tkinter.Label(feedFrame, text="Every 0min")
            nextFeedLabel = tkinter.Label(feedFrame, text="Next Feed: 00:00:00")
            titleLabel.pack()
            stateLabel.pack()
            onTimeLabel.pack()
            offTimeLabel.pack()
            nextFeedLabel.pack()
            #Create the object and add to the list
            feederObject = {"frame" : feedFrame, "mainLabel" : titleLabel, "stateLabel" : stateLabel, "onTimeLabel" : onTimeLabel, "offTimeLabel" : offTimeLabel, "nextFeedLabel" : nextFeedLabel}
            self.feederSettingsObjects.append(feederObject)
        
        #Pack the objects
        for feedObject in self.feederSettingsObjects:
            feedObject["frame"].pack(side="left", expand="y")

        #Entries to allow the feed time and delay between feeds to be changed
        self.feederTimeEntry = NumberGroup(self.feederSettingsFrame, titles=["Feeding Time (s)", "Time Between Feeds (m)"], header="Change Feed Timings", valueHandler=self.setFeederTiming)
        self.feederTimeEntry.grid(row=1, column=0, columnspan=2)

        #Hide the settings window
        self.setupWindow.withdraw()

        #Setup and create maintenance window
        for i in range(0, 10):
            self.maintenanceFrame.grid_columnconfigure(i, weight=1)
        self.maintenanceFrame.grid_rowconfigure(0, weight=1)
        self.maintenanceFrame.grid_rowconfigure(1, weight=4)
        self.maintenanceFrame.grid_rowconfigure(2, weight=1)
        self.maintenanceFrame.grid_rowconfigure(3, weight=1)

        #Header label
        self.maintenanceTitleLabel = tkinter.Label(self.maintenanceFrame, text="Maintenance Controls", font=self.menuFont)
        self.maintenanceTitleLabel.grid(row=0, column=0, columnspan=10, sticky="NESW")

        self.maintenanceReactors = []
        self.maintenanceFeeders = []
        #Iterate through all possible reactors
        for i in range(0, 10):
            #Create frame for reactor
            mRFrame = tkinter.Frame(self.maintenanceFrame)
            for r in range(0, 7):
                mRFrame.grid_rowconfigure(r, weight=1)
            mRFrame.grid_columnconfigure(0, weight=1)
            #Add title
            mRTitle = tkinter.Label(mRFrame, text="Reactor {0}".format(i + 1))
            #Add label and button for mixers
            mRMixLabel = tkinter.Label(mRFrame, text="Mixer: Off")
            mRMixButton = tkinter.Button(mRFrame, text="Toggle\nMixer", command=lambda x = i: self.maintenanceMixer(x))
            #Add label and button for heaters
            mRHeatLabel = tkinter.Label(mRFrame, text="Heater: Off")
            mRHeatButton = tkinter.Button(mRFrame, text="Toggle\nHeater", command=lambda x = i: self.maintenanceHeater(x))
            #Add label and button for agitators
            mRAgiLabel = tkinter.Label(mRFrame, text="Agitator: Off")
            mRAgiButton = tkinter.Button(mRFrame, text="Toggle\nAgitator", command=lambda x = i: self.maintenanceAgitator(x))
            #Add all the items to the frame
            mRTitle.grid(row=0, column=0, sticky="NESW")
            mRMixLabel.grid(row=1, column=0, sticky="NESW")
            mRMixButton.grid(row=2, column=0, sticky="NESW")
            mRHeatLabel.grid(row=3, column=0, sticky="NESW")
            mRHeatButton.grid(row=4, column=0, sticky="NESW")
            mRAgiLabel.grid(row=5, column=0, sticky="NESW")
            mRAgiButton.grid(row=6, column=0, sticky="NESW")
            #Store the object in a list and add it to the main frame
            maintenanceObject = {"frame" : mRFrame, "mix" : mRMixLabel, "heat" : mRHeatLabel, "agi" : mRAgiLabel, "mixButton" : mRMixButton, "heatButton" : mRHeatButton, "agiButton" : mRAgiButton}
            mRFrame.grid(row=1, column=i, sticky="NESW")
            self.maintenanceReactors.append(maintenanceObject)

        #Iterate through feeders
        for i in range(0, 4):
            #Create frame for each feeder
            mFFrame = tkinter.Frame(self.maintenanceFrame)
            #Header label
            mFTitle = tkinter.Label(mFFrame, text="Feeder {0}".format(i + 1))
            #Current feed state label
            mFStateLabel = tkinter.Label(mFFrame, text="Not Feeding")
            #Button to toggle feeder on/off
            mFStateButton = tkinter.Button(mFFrame, text="Toggle Feeder", command=lambda x = i: self.maintenanceFeeder(x))
            mFTitle.pack()
            mFStateLabel.pack()
            mFStateButton.pack()
            #Store in object and add to frame
            maintenanceFeedObject = {"frame" : mFFrame, "state" : mFStateLabel}
            mFFrame.grid(row=2, column=i, sticky="NESW")
            self.maintenanceFeeders.append(maintenanceFeedObject)

        self.maintenanceControlFrame = tkinter.Frame(self.maintenanceFrame)
        self.maintenanceControlFrame.grid(row=3, column=0, columnspan=10, sticky="NESW")

        #Buttons to toggle everything on and everything off
        self.maintenanceAllOffButton = tkinter.Button(self.maintenanceControlFrame, text="All Off", command=self.maintenanceOff)
        self.maintenanceAllOffButton.pack()
        self.maintenanceAllOnButton = tkinter.Button(self.maintenanceControlFrame, text="All On", command=self.maintenanceOn)
        self.maintenanceAllOnButton.pack()

        #Not currently updating reactor information
        self.runningUpdates = False
        #No reactor is currently selected
        self.changeSelectedReactor(-1)

        #Which screen is currently being displayed
        self.currentMain = 0
        #If waiting for a response from the serial connection
        self.awaitingConnection = False
        #If waiting for a response to a sent message
        self.awaitingMessage = False
        #If waiting for the machine to start
        self.awaitingStartup = False
        self.loading = True

        #Which reactors are selected to show up in settings
        self.currentSettingsReactors = []
        self.currentSettingsType = -1

        #Messages received from the device but not yet handled
        self.pendingMessages = []

        #Which reactors are associated with each feeder - loaded from machine type
        self.feederAssocReactors = [[], [], [], []]
        self.selectedFeeders = []
        self.accessedFeeders = []

        #Making another attempt to get a valid response from the device
        self.retrying = False

        #[[mix state, mix enabled, mix on time, mix off time], [heat state, heat enabled, heat current temp, heat target temp], [agitate state, agitate enabled, agitate time]]
        self.statusReactorData = []
        #[feed status, feed enabled, feed on for, feed off for, feed off until, [next hour, next min, next sec]]
        self.statusFeederData = []
        #[timeUnix, date, maintenance]
        self.statusExtraData = []
        
        #Whether to show the debugging screen - displays all sent and received messages in a separate window
        self.debugging = False

        if self.debugging:
            self.debugWindow = tkinter.Toplevel(self)
            self.debugShape = [400, 300]
            self.debugWindow.geometry("{0}x{1}".format(self.debugShape[0], self.debugShape[1]))
            self.debugWindow.minsize(self.debugShape[0], self.debugShape[1])
            self.debugWindow.grid_rowconfigure(0, weight=1)
            self.debugWindow.grid_columnconfigure(0, weight=1)
            self.debugWindowObject = DebugWindow(self.debugWindow)
            self.debugWindowObject.grid(row=0, column=0, sticky="NESW")

        self.performScan()

    def pathTo(self, path):
        return os.path.join(self.thisPath, path)
    
    def changeMainFrame(self, target : int) -> bool:
        '''Change which frame is currently being displayed'''
        #Store the current screen
        oldMain = self.currentMain
        changed = False
        #Attempt to switch to the new screen
        try:
            if target == 0:
                self.connectFrame.tkraise()
                self.performScan()
                changed = True
            elif target == 1:
                self.loadingFrame.tkraise()
                changed = True
            elif target == 2:
                self.displayFrame.tkraise()
                changed = True
            elif target == 3:
                self.maintenanceFrame.tkraise()
                changed = True
            
            #If successfull store the newly selected screen
            if changed:
                self.currentMain = target
        except:
            pass
        
        #If change did not work, revert back to previous screen
        if not changed:
            self.currentMain = oldMain

        return changed
    
    def changeLoadingFrame(self, target: int) -> bool:
        '''Change what the loading frame is currently displaying'''
        try:
            if target == 0:
                try:
                    self.loadingFailureFrame.pack_forget()
                except:
                    pass
                self.loadingTextFrame.pack(expand=True)
                return True
            elif target == 1:
                try:
                    self.loadingTextFrame.pack_forget()
                except:
                    pass
                self.loadingFailureFrame.pack(expand=True)
                return True
        except:
            pass
        return False

    def changeHighlight(self, part: int) -> None:
        '''Change which section of the reactor image is highlighted'''
        #If not a medusa
        if self.selectedType.get() != self.MEDUSA:
            #If nothing selected or invalid value
            if part > 3 or part < 0 or sum(self.reactorSelected) < 1:
                #No highlight
                self.reactorDisplayLabel.configure(image=self.reactorBasicImage)
            else:
                #Highlight correct part
                if part == 0:
                    self.reactorDisplayLabel.configure(image=self.reactorMixerImage)
                elif part == 1:
                    self.reactorDisplayLabel.configure(image=self.reactorHeaterImage)
                elif part == 2:
                    self.reactorDisplayLabel.configure(image=self.reactorAgitatorImage)
                elif part == 3:
                    self.reactorDisplayLabel.configure(image=self.reactorFeederImage)
        else:
            #If nothing selected or invalid value
            if part > 3 or part < 0 or sum(self.reactorSelected) < 1:
                #Nothing highlighted
                self.reactorDisplayLabel.configure(image=self.reactorMedusaBasicImage)
            else:
                #Highlight correct part
                if part == 2:
                    self.reactorDisplayLabel.configure(image=self.reactorMedusaAgitatorImage)
                elif part == 3:
                    self.reactorDisplayLabel.configure(image=self.reactorMedusaFeederImage)

    def typeChanged(self) -> None:
        '''When machine type is changed'''
        machineType = self.selectedType.get()
        shape = self.machineShape[machineType]
        feedInfo = self.machineFeeders[machineType]

        self.numberReactorsInUse = len(shape)

        self.statusReactorData = []
        self.statusFeederData = []
        self.statusExtraData = [0, 0, False]
        for _reactor in range(0, self.numberReactorsInUse):
            self.statusReactorData.append([[False, False, 0, 0, 0], [False, False, 0, 0], [False, False, 0]])
        for _feeder in range(0, len(feedInfo)):
            self.statusFeederData.append([False, False, 0, 0, 0, 0])
        
        self.reactorTypes = self.reactorNormals[machineType]

    def failureBack(self) -> None:
        '''Return to the main screen when back pressed'''
        self.changeMainFrame(0)
        self.changeLoadingFrame(0)

    def connectPressed(self) -> None:
        '''Attempt to connect to selected port'''
        #If a connection does not aly exist
        if not self.connected:
            #If the current port selected exists
            if self.portLabels.index(self.selectedPort.get()) > 0:
                #Set the port of the connection
                self.connectedPort = self.selectedPort.get()
                success = True
                try:
                    self.loadingText.configure(text="Connecting To Machine")
                    self.changeLoadingFrame(0)
                    self.changeMainFrame(1)
                    #Attempt to connect
                    self.serialConnection = serial.Serial(port=self.connectedPort, baudrate=115200, timeout=0)
                except:
                    #If something went wrong
                    success = False
            
                if success:
                    self.loadingText.configure(text="Waiting For Response")
                    #Switch buttons to enable disconnect and disable connect
                    self.connected = True
                    #Start reading from the port
                    readThread = Thread(target=self.readSerial, daemon=True)
                    readThread.start()
                    #Start handling incoming messages
                    messageThread = Thread(target=self.checkMessages, daemon=True)
                    messageThread.start()

                    self.pendingMessages.append("systemget\n")

                    self.awaitingConnection = True
                    self.loading = True
                else:
                    self.loadingFailureText.configure(text="Failed To Connect, Please Try Again")
                    self.changeLoadingFrame(1)
                    #Connection failed - reset
                    self.connected = False
                    self.connectedPort = None

    def connectionReceived(self, started : bool) -> None:
        '''When a message is first received from the machine'''
        self.awaitingConnection = False
        #If the machine is already running
        if started:
            #Change loading text
            self.loadingText.configure(text="Connected To Machine, Retrieving Setup Information...")
            self.currentStatus = []
            #Request machine status
            self.pendingMessages.append("statusget\n")
        else:
            #Change loading text
            self.loadingText.configure(text="Connected To Machine, Performing Startup...")
            self.awaitingStartup = True
            self.retrying = False
            #Start the machine using the correct messages for the current machine type
            self.sendSystemSet()
            #Begin a thread to retry starting until timeout
            retryStartThread = Thread(target=self.resentContinueTimer, daemon=True)
            retryStartThread.start()
        
        #Wating for a response to continue
        self.awaitingMessage = True
    
    def sendSystemSet(self) -> None:
        '''Send the messages to start the machine for the machine type'''
        #Get the current machine
        machine = self.selectedType.get()
        #If it is a valid machine type
        if machine > 0 and machine < len(self.machineIdentifiers):
            #Send the continue message with the correct extension3
            self.sendMessage("systemset {0}\n".format(self.machineIdentifiers[machine]))

    def resentContinueTimer(self) -> None:
        '''Repeatedly send continue until a response is received or closed'''
        #If a connection has not been made and the window not closed
        while self.awaitingStartup and not self.awaitingConnection and self.currentMain == 1:
            #Wait five seconds
            time.sleep(5)
            #Check again
            if self.awaitingStartup and not self.awaitingConnection and self.currentMain == 1:
                #Resend the continue messages
                self.retrying = True
                self.sendSystemSet()

    def disconnect(self) -> None:
        '''Disconnect the serial communications'''
        try:
            #Attempt to close the serial communications
            self.serialConnection.close()
        except:
            #This will fail if it is already closed (e.g. device unplugged) which is fine, this just stops it crashing
            pass
        #Reset serial communication information
        self.serialConnection = None
        self.connected = False
        self.connectedPort = None
        self.runningUpdates = False
        #Return to default reactor information
        self.changeSelectedReactor(-1)
        #Clear selected reactors
        self.reactorSelectionButtonPressed(False, False, True)
    
    def performScan(self, target = None) -> None:
        '''Perform a scan of available ports and update option list accordingly'''
        if not self.connected:
            #List to contain available ports
            found = ["No Port Selected"]
            descs = [""]
            #Scan to find all available ports
            portData = list_ports.comports()
            #Iterate through ports
            for data in portData:
                #Add the device name of the port to the list (can be used to connect to it)
                found.append(data.device)
                descs.append("(" + data.description + ")")
            
            #If the old and new lists are different
            different = False
            #Test if the lists are different lengths
            if len(found) != len(self.portLabels):
                different = True
            else:
                #Iterate through
                for item in found:
                    #Check if they contain the same things (order unimportant)
                    if item not in self.portLabels:
                        different = True

            #If there was a change
            if different:
                #Update labels
                self.portLabels = found

                #Delete the old menu options
                menu = self.portOption["menu"]
                menu.delete(0, tkinter.END)

                i = 0
                #Iterate through labels
                for name in self.portLabels:
                    #Add the labels to the list
                    menu.add_command(label=name + " " + descs[i], command=lambda v=self.selectedPort, l=name: v.set(l))
                    i = i + 1

                targetFound = False

                if target != None:
                    if target in self.portLabels:
                        self.selectedPort.set(target)
                
                if not targetFound:
                    #If the selected item is still available
                    if self.selectedPort.get() in self.portLabels:
                        #Set the drop down value to what it was
                        self.selectedPort.set(self.selectedPort.get())
                    else:
                        #Set selected option to none
                        self.selectedPort.set(self.portLabels[0])
            
            #Scan again shortly
            self.after(150, self.performScan)
    
    def readSerial(self) -> None:
        '''While connected repeatedly read information from serial connection'''
        #If there is a connection
        if self.connected and self.serialConnection != None:
            #Attempt
            try:
                done = False
                #Until out of data
                while not done:
                    #Read the next character
                    char = self.serialConnection.read()
                    #If there is a character
                    if len(char) > 0:
                        try:
                            #Attempt from byte to string and print
                            ch = char.decode("utf-8")
                            if ch == "\n":
                                #Add to list of messages
                                self.receivedMessages.append(self.currentMessage)
                                self.currentMessage = ""
                            else:
                                if ch not in ["\r"]:
                                    self.currentMessage = self.currentMessage + ch
                        except:
                            #If it failed an unusual escape character has been read and it is simply ignored
                            pass
                    else:
                        #Finished reading - end of stream reached
                        done = True
                
                #Repeat this read function after 10ms
                self.after(10, self.readSerial)
            except Exception as e:
                print("Exception in read serial:", e)
                #Close the connection and reset the buttons
                self.serialConnection.close()
                self.serialConnection = None
                self.connected = False
                self.connectedPort = None
                self.loadingFailureText.configure(text="Connection Was Lost, Please Try Again")
                self.changeLoadingFrame(1)
                self.changeMainFrame(1)

    def checkMessages(self) -> None:
        '''Repeatedly check for a new message and handle it'''
        #If there is a message
        if len(self.receivedMessages) > 0:
            #Get the message
            nextMessage = self.receivedMessages[0]
            #Handle based on what the message is
            self.messageReceived(nextMessage)
            #Remove message from the list
            del self.receivedMessages[0]
        #If there is still a connection
        if self.serialConnection != None:
            #Repeat after a short delay
            self.after(1, self.checkMessages)
  
    def messageReceived(self, message) -> None:
        '''Handle the message that was received appropriately'''
        #Debug to output the message that was recieved to the console
        if "status" not in message:
            print("Received:", message)

        messageParts = message.strip().split(" ");
        #If it was not a timing ping and debugging
        if self.debugging:
            #Display message
            self.debugWindowObject.addText(message + "\n")
        #If waiting for initial connection
        if self.awaitingConnection:
            #If this is a timing response
            if "system" in message:
                #Determine if started yet
                alreadyStarted = messageParts[1] != "none"
                #Begin communications
                self.connectionReceived(alreadyStarted)

        if len(messageParts) > 1 and messageParts[0] == "status":
            try:
                if messageParts[1] == "start" and len(messageParts) > 3:
                    inMaintenance = messageParts[3] == "1"
                    self.statusExtraData[2] = inMaintenance
                elif messageParts[1] == "heater" and len(messageParts) > 6:
                    heaterNumber = int(messageParts[2])
                    heaterEnabled = messageParts[3] == "1"
                    target = float(messageParts[4])
                    actual = float(messageParts[5])
                    heaterOn = messageParts[6] == "1"
                    if heaterNumber > 0 and heaterNumber <= self.numberReactorsInUse:
                        self.statusReactorData[heaterNumber - 1][1] = [heaterOn, heaterEnabled, actual, target]
                elif messageParts[1] == "mixer" and len(messageParts) > 7:
                    mixerNumber = int(messageParts[2])
                    mixerEnabled = messageParts[3] == "1"
                    mixerMode = int(messageParts[4])
                    mixOnFor = int(messageParts[5])
                    mixOffFor = int(messageParts[6])
                    mixerOn = messageParts[7] == "1"
                    if mixerNumber > 0 and mixerNumber <= self.numberReactorsInUse:
                        self.statusReactorData[mixerNumber - 1][0] = [mixerOn, mixerEnabled, mixerMode, mixOnFor, mixOffFor]
                elif messageParts[1] == "feeder" and len(messageParts) > 7:
                    feederNumber = int(messageParts[2])
                    feederEnabled = messageParts[3] == "1"
                    feedOnFor = int(messageParts[4])
                    feedOffFor = int(messageParts[5])
                    feederOn = messageParts[6] == "1"
                    timeToFeed = int(messageParts[7])
                    if feederNumber > 0 and feederNumber <= len(self.statusFeederData):
                        self.statusFeederData[feederNumber - 1] = [feederOn, feederEnabled, feedOnFor, feedOffFor, timeToFeed]
                elif messageParts[1] == "agitator" and len(messageParts) > 5:
                    agitatorNumber = int(messageParts[2])
                    agitatorEnabled = messageParts[3] == "1"
                    prefeed = int(messageParts[4])
                    agitatorOn = messageParts[5] == "1"
                    if agitatorNumber > 0 and agitatorNumber <= self.numberReactorsInUse:
                        self.statusReactorData[agitatorNumber - 1][2] = [agitatorOn, agitatorEnabled, prefeed]
            except:
                print("Error handling: ", message)
        
        if len(messageParts) > 1 and messageParts[0] == "done" and messageParts[1] == "status":
            updated = self.updateFromStatus()
            if updated:
                if self.loading:
                    self.loading = False
                    self.openMachine()
                self.lastStatus = time.time()
            self.gettingStatus = False
        
        if len(messageParts) > 1 and messageParts[0] == "done" and messageParts[1] == "systemset":
            self.awaitingStartup = False
            self.pendingMessages.append("statusget\n")

        #Send the next message to be sent, if there is one
        #if time.time() - self.lastMessageSent >= self.messageDelay:
        self.sendQueuedMessage()
            
    def connectionFailed(self) -> None:
        '''Display the failed to connect correctly screen'''
        #Show correct message
        self.loadingFailureText.configure(text="Machine not configured as {0}, please check and try again.".format(self.machineList[self.selectedType.get()]))
        #Close the serial connection if possible
        try:
            self.serialConnection.close()
        except:
            pass
        self.serialConnection = None
        self.connected = False
        self.connectedPort = None
        self.awaitingConnection = False
        self.awaitingStartup = False
        #Change to failed text screen
        self.changeLoadingFrame(1)
        self.changeMainFrame(1)

    def sendQueuedMessage(self) -> None:
        '''Send the next queued message to the connected device'''
        #If there is a message to send
        if len(self.pendingMessages) > 0:
            #Get the message
            message = self.pendingMessages[0]
            
            #If this is not a startup message or the machine is waiting to start
            if "systemset" not in message or self.awaitingStartup:
                #Send the message
                self.sendMessage(message)
            
            if "statusget" in message:
                self.gettingStatus = True

            #Remove the message from the pending list
            del self.pendingMessages[0]

            #If in debug mode, display the message that was sent
            if self.debugging:
                self.debugWindowObject.addSent(message)

            self.lastMessageSent = time.time()
    
    def sendMessage(self, message : str) -> None:
        '''Send the message via serial connection'''
        #If there is a connection
        if self.connected and self.serialConnection != None:
            try:
                #Send with correct encoding
                self.serialConnection.write(message.encode("utf-8"))
                #Debug to display to console
                print("SENT:", message)
            except:
                pass
    
    def containsOnly(self, data, validChars) -> bool:
        '''Check if all chanracters in data are in validChars, if so returns True, otherwise returns False'''
        #Iterate characters
        for c in data:
            #If the character is not valid
            if c not in validChars:
                #End and return False
                return False
        
        #No invalid characters were found - return True
        return True

    def booleanOnOff(self, value: bool) -> str:
        '''Convert a boolean value to a string "On" or "Off" used for label displays'''
        if value:
            return "On"
        return "Off"

    def updateFromStatus(self) -> bool:
        '''Change the information in the reactor and feeder displays using the status data'''
        feederCount = len(self.machineFeeders[self.selectedType.get()])
        #[[mix state, mix enabled, mix mode, mix on time, mix off time], [heat state, heat enabled, heat current temp, heat target temp], [agitate state, agitate enabled, agitate time]]
        #[feed status, feed enabled, feed on for, feed off for, feed off until, [next hour, next min, next sec]]
        mixModes = ["Off", "On", "Timed"]
        
        #Attempt to set the reactor data - if something goes wrong, stop
        try:
            #Iterate through reactors being used
            for reactorNum in range(0, self.numberReactorsInUse):
                #Get the data for the current reactors
                currentMachineNumbers = self.machineNumbers[self.selectedType.get()]
                mixObject = None
                heatObject = None
                agiObject = None
                #Get the object for the mixer, heater and agitator. If there is one
                if reactorNum < currentMachineNumbers["mixers"]:
                    mixObject = self.mixerSettingsObjects[reactorNum]
                if reactorNum < currentMachineNumbers["heaters"]:
                    heatObject = self.heaterSettingsObjects[reactorNum]
                if reactorNum < currentMachineNumbers["agitators"]:
                    agiObject = self.agitatorSettingsObjects[reactorNum]

                #Get the stored status data
                reactorData = self.statusReactorData[reactorNum]
                
                #If there is a mixer
                if mixObject != None:
                    #[mix state (bool), mix enabled (bool), mix mode (int), mix on time (int), mix off time (int)]
                    mixData = reactorData[0]
                    modeText = mixModes[mixData[2]]
                    #Set the label of the state of the mixer
                    modeMessage = "State: {0}".format(modeText)
                    modeColour = "red"
                    if modeText == "On":
                        modeColour = "green"
                    elif modeText == "Timed":
                        if mixData[0]:
                            modeColour = "green"
                    mixObject["stateLabel"].configure(text=modeMessage, fg=modeColour)
                    #Set the timing label
                    mixObject["timingLabel"].configure(text="{0}s On\n{1}s Off".format(mixData[3], mixData[4]))
                    #Change the text and colour of the enabled label

                    #Store whether or not the reactor is mixing in the reactor data and maintenance info
                    self.reactorMixing[reactorNum] = mixData[0]
                    self.maintenanceReactors[reactorNum]["mix"].configure(text="Mixer: {0}".format(self.booleanOnOff(mixData[0])))

                #If there is a heater object
                if heatObject != None:
                    #[heat state (bool), heat enabled (bool), heat current temp (float), heat target temp (int)]
                    heatData = reactorData[1]
                    heatColour = "red"
                    if heatData[0]:
                        heatColour = "green"
                    heatObject["stateLabel"].configure(text="State: {0}".format(self.booleanOnOff(heatData[0])), fg=heatColour)
                    heatObject["targetLabel"].configure(text="Target: {0}°C".format(heatData[3]))
                    #Change the label to show the target temperature
                    self.reactorTargetTemp[reactorNum] = heatData[3]
                    heatObject["currentLabel"].configure(text="Current: {0}°C".format(heatData[2]))
                    #Change the text and colour of the enabled label
                    self.reactorCurrentTemp[reactorNum] = heatData[2]

                    #Store if the reactor is heating and also in maintenance
                    self.reactorHeating[reactorNum] = heatData[0]
                    self.maintenanceReactors[reactorNum]["heat"].configure(text="Heater: {0}".format(self.booleanOnOff(heatData[0])))

                #If there is an agitator object
                if agiObject != None:
                    #[agitate state (bool), agitate enabled (bool), agitate time (int)]
                    agiData = reactorData[2]
                    #If there is agitator data - may no longer be necessary due to new checks for machine information
                    if len(agiData) > 0:
                        #Set the state and timing labels
                        agiColour = "red"
                        if agiData[0]:
                            agiColour = "green"
                        agiObject["stateLabel"].configure(text="State: {0}".format(self.booleanOnOff(agiData[0])), fg=agiColour)
                        agiObject["timingLabel"].configure(text="{0}s Before Feed".format(agiData[2]))

                        #Store if currently agitating, in maintenance too
                        self.reactorAgitating[reactorNum] = agiData[0]
                        self.maintenanceReactors[reactorNum]["agi"].configure(text="Agitator: {0}".format(self.booleanOnOff(agiData[0])))
        except Exception as e:
            #If an error occurred, print it out 
            print("Error with reactor data")
            print("Exception Occurred:", e, "On Line:", sys.exc_info()[2].tb_lineno)
            #Failed to update correctly
            return False
        
        #Attempt to set the values of the feeders
        try:
            #Iterate for feeders being used
            for feederNum in range(0, feederCount):
                #Get the feeder data and object
                feedData = self.statusFeederData[feederNum]
                feederObject = self.feederSettingsObjects[feederNum]
                secondsToFeed = feedData[4]
                minutesToFeed = int(secondsToFeed / 60)
                hoursToFeed = int(minutesToFeed / 60)
                secondsToFeed = str(secondsToFeed - (minutesToFeed * 60))
                minutesToFeed = str(minutesToFeed - (hoursToFeed * 60))
                hoursToFeed = str(hoursToFeed)
                if len(secondsToFeed) < 2:
                    secondsToFeed = "0" + secondsToFeed
                if len(minutesToFeed) < 2:
                    minutesToFeed = "0" + minutesToFeed
                if len(hoursToFeed) < 2:
                    hoursToFeed = "0" + hoursToFeed
                feedColour = "red"
                if feedData[0]:
                    feedColour = "green"
                #Change text labels to show correct information
                feederObject["stateLabel"].configure(text="State: {0}".format(self.booleanOnOff(feedData[0])), fg=feedColour)
                feederObject["onTimeLabel"].configure(text="Feed For: {0}s".format(feedData[2]))
                feederObject["offTimeLabel"].configure(text="Every: {0}min".format(feedData[3]))
                feederObject["nextFeedLabel"].configure(text="Next Feed: {0}:{1}:{2}".format(hoursToFeed, minutesToFeed, secondsToFeed))
                #Update stored feeder values
                self.feederFeeding[feederNum] = feedData[0]
                self.feederDuration[feederNum] = feedData[2]
                self.feederDelay[feederNum] = feedData[3]
                #Change maintenance feeder info and buttons to display correctly depending on feed state 
                if feedData[0]:
                    self.maintenanceFeeders[feederNum]["state"].configure(text="Feeding")
                    self.feederButtons[feederNum].configure(fg="green")
                else:
                    self.maintenanceFeeders[feederNum]["state"].configure(text="Not Feeding")
                    if feedData[1]:
                        self.feederButtons[feederNum].configure(fg="black")
                    else:
                        self.feederButtons[feederNum].configure(fg="red")

        except Exception as e:
            #If an error occurred, print it out
            print("Error with feeder data")
            print("Exception Occurred:", e, "On Line:", sys.exc_info()[2].tb_lineno)
            #Update was not sucessful
            return False
        
        #Attempt to update extra information
        try:
            #If machine in maintenance mode
            if self.statusExtraData[2]:
                #If console not in maintenance mode
                if not self.maintenanceMode and "maintenanceset 0\n" not in self.pendingMessages:
                    #Close maintenance mode
                    self.pendingMessages.append("maintenanceset 0\n")
            else:
                #If console in maintenance mode
                if self.maintenanceMode and "maintenanceset 1\n" not in self.pendingMessages:
                    #Opne maintenance mode
                    self.pendingMessages.append("maintenanceset 1\n")
        except:
            #Error occurred, failed to update
            print("Error with maintenance data")
            return False
        
        #Update completed sucessfully
        return True

    def convertMessagesToNumbers(self, textArray) -> tuple:
        '''Converts list of strings made up of space separated numbers into 2d array of integers and floats'''
        #List to hold results
        numberArray = []

        failed = False
        #Iterate through lines
        for line in textArray:
            #Add a row to output
            numberArray.append([])
            #Split by spaces
            for item in line.split(" "):
                value = 0
                #Attempt as integer
                try:
                    v = int(item)
                    value = v
                except:
                    #Attempt as float
                    try:
                        v = float(item)
                        value = v
                    except:
                        #Default value
                        v = item
                        value = v
                        #Something went wrong
                        failed = True
                
                #Add item to the list
                numberArray[-1].append(value)
        
        #Return the results: 2d list of data, if there were any invalid entries (bool)
        return numberArray, failed

    def setMixerTiming(self, values) -> None:
        '''When set is pressed on the mixer timing - check values and update'''
        #If there are two values and they are valid
        if len(values) > 1:
            if values[0] != None and values[1] != None:
                try:
                    #Convert to integer
                    onTime = int(values[0])
                    offTime = int(values[1])
                    #Change the value
                    self.settingChange(1, [2, onTime, offTime])
                except:
                    messagebox.showinfo(title="Value Error", message="Values entered must be integer numbers.")
            else:
                messagebox.showinfo(title="Enter Values", message="Please enter a value for both times.")

    def setHeaterTemp(self, values) -> None:
        '''When set is pressed on the heater temperature - cehck value and update'''
        #If there is a value and it is valid
        if len(values) > 0:
            if values[0] != None:
                try:
                    #Convert to integer
                    target = int(values[0])
                    #Change the value
                    self.settingChange(0, target)
                except:
                    messagebox.showinfo(title="Value Error", message="Value entered must be an integer number.")
            else:
                messagebox.showinfo(title="Enter Value", message="Please enter a temperature value.")

    def setAgitatorTiming(self, values) -> None:
        '''When set is pressed on agitator timing - check value and update'''
        #If there is a valid value
        if len(values) > 0:
            if values[0] != None:
                try:
                    #Convert to integer
                    duration = int(values[0])
                    #Change the value
                    self.settingChange(0, duration)
                except:
                    messagebox.showinfo(title="Value Error", message="Value entered must be an integer number.")
            else:
                messagebox.showinfo(title="Enter Value", message="Please enter a time value.")
    
    def setFeederTiming(self, values) -> None:
        '''When set is pressed on feeder timing - check values and update'''
        #If the two valid values are given
        if len(values) > 1:


            if values[0] != None and values[1] != None:
                try:
                    #Convert to integers
                    feedTime = int(values[0])
                    feedDelay = int(values[1])
                    #Change the value
                    self.settingChange(0, [feedTime, feedDelay])
                except:
                    messagebox.showinfo(title="Value Error", message="Values entered must be integer numbers.")
            else:
                messagebox.showinfo(title="Enter Value", message="Please enter both time values.")
    
    def settingChange(self, option, data) -> None:
        '''When a value has been changed - send the appropiate command to the device to change this'''

        if self.currentSettingsType == 0:
            for reactorNum in self.currentSettingsReactors:
                reactorData = self.statusReactorData[reactorNum - 1][0]
                #Mixer settings
                if option == 0 and data in [0, 1]:
                    #Mode change
                    self.pendingMessages.append("mixerset {reactor} {mode} {onFor} {offFor}\n".format(reactor = reactorNum, mode = data, onFor = reactorData[3], offFor = reactorData[4]))
                if option == 1 and len(data) > 2:
                    self.pendingMessages.append("mixerset {reactor} {mode} {onFor} {offFor}\n".format(reactor = reactorNum, mode = data[0], onFor = data[1], offFor = data[2]))
        if self.currentSettingsType == 1:
            for reactorNum in self.currentSettingsReactors:
                #Heater settings
                if option == 0 and type(data) == int:
                    #Target Temperature change
                    self.pendingMessages.append("heaterset {reactor} {targetTemp}\n".format(reactor = reactorNum, targetTemp = data))
        if self.currentSettingsType == 2:
            for reactorNum in self.currentSettingsReactors:
                #Agitator settings
                if option == 0 and type(data) == int:
                    #Timing changed
                    self.pendingMessages.append("agitatorset {reactor} {time}\n".format(reactor = reactorNum, time = data))
        if self.currentSettingsType == 3:
            for feederNum in self.accessedFeeders:
                #Feeder settings
                if option == 0 and (type(data) == list and len(data) > 1):
                    #Timings changed
                    self.pendingMessages.append("feederset {feeder} {onTime} {offTime}\n".format(feeder = feederNum + 1, onTime = data[0], offTime = data[1]))

    def openMachine(self) -> None:
        '''Show the machine display to the user'''
        #Get the currently selected machine type
        machineType = self.selectedType.get()
        #Get the layout and information about the reactors and feeders
        shape = self.machineShape[machineType]
        feedInfo = self.machineFeeders[machineType]
        self.reactorTypes = self.reactorNormals[machineType]

        self.maintenanceMode = False
        #Determine number of reactors
        self.numberReactorsInUse = len(shape)

        #Iterate through all possible reactors and remove from display
        for reactor in self.reactorButtons:
            reactor.grid_forget()
        #Iterate through reactors being used
        for reactorNumber in range(0, self.numberReactorsInUse):
            #Get the reactor object
            reactor = self.reactorButtons[reactorNumber]
            buttonData = shape[reactorNumber]
            #Set the correct button text and add to the display in the correct position
            reactor.configure(text=buttonData[0])
            reactor.grid(row=buttonData[1], column=buttonData[2])
            
            if machineType != self.MEDUSA:
                if self.reactorTypes[reactorNumber]:
                    #Standard reactor appearance
                    reactor.configure(image=self.reactorStateImages[0])
                else:
                    #Black swan reactor appearance
                    reactor.configure(image=self.reactorSwanStateImages[0])
            else:
                #Medusa reactor appearance
                reactor.configure(image=self.reactorMedusaStateImages[0])
        

        #Which reactors are associated with each feeder
        self.feederAssocReactors = [[], [], [], []]
        
        #Iterate and remove feeders from display
        for feeder in self.feederButtons:
            feeder.grid_forget()
        #Iterate through used feeders
        for feederNumber in range(0, len(feedInfo)):
            #Get the information about the feeder and the object
            feederData = feedInfo[feederNumber]
            feeder = self.feederButtons[feederNumber]
            #Set button text based on number and orientation
            if feederData[2][0] == 1:
                feeder.configure(text="▼ Feeder {0} ▼".format(feederNumber + 1))
            else:
                feeder.configure(text="▲ Feeder {0} ▲".format(feederNumber + 1))
            #Add button back to grid
            feeder.grid(row=feederData[2][0], column=feederData[2][1], rowspan=feederData[2][2], columnspan=feederData[2][3])
            #Store associations - so correct feeder is displayed for each reactor
            self.feederAssocReactors[feederNumber] = feederData[1]

        if machineType != self.MEDUSA:
            #Default reactor image
            self.reactorDisplayLabel.configure(image=self.reactorBasicImage)
        else:
            #Medusa reactor image
            self.reactorDisplayLabel.configure(image=self.reactorMedusaBasicImage)
        
        #Switch to the display frame
        self.changeMainFrame(2)
        self.runningUpdates = True
        #Update the icons
        self.performReactorIconUpdate()

    def performReactorIconUpdate(self) -> None:
        '''Update the icons on the reactors so they properly show what the device is doing'''
        #Loop while still running
        if self.runningUpdates:
            #If not currently getting status and time has elapsed
            if not self.gettingStatus and time.time() - self.lastStatus > self.statusDelay:
                #Send get status message and store time
                self.pendingMessages.append("statusget\n")
                self.lastStatus = time.time()
            #Update the icons
            self.updateAllReactorIcons()
            #Repeat after delay
            self.after(100, self.performReactorIconUpdate)

    def updateAllReactorIcons(self) -> None:
        '''Change the icons on the reactors'''
        #Iterate through used reactors
        for reactor in range(0, self.numberReactorsInUse):
            #Get the correct value
            value = self.calculateReactorValue(reactor)
            #Change the value of the reactor
            self.updateReactorIcon(reactor, value)

    def calculateReactorValue(self, reactorNum : int) -> None:
        '''Calculate the correct index for the reactor given'''
        total = 0
        #If valid reactor
        if reactorNum < 0 or reactorNum >= len(self.reactorMixing) or reactorNum >= len(self.reactorAgitating) or reactorNum >= len(self.reactorHeating):
            return -1
        #Add values based on selection, mixing, heating and agitating
        if self.reactorSelected[reactorNum]:
            total = total + self.selectValue
        if self.reactorMixing[reactorNum]:
            total = total + self.mixValue
        if self.reactorHeating[reactorNum]:
            total = total + self.heatValue
        if self.reactorAgitating[reactorNum]:
            total = total + self.agitateValue

        return total

    def updateReactorIcon(self, reactorNum : int, newValue : int) -> None:
        '''Change the icon of the reactor'''
        #If the reactor exists and so does the icon
        if reactorNum > -1 and reactorNum < len(self.reactorValues) and newValue > -1 and newValue < len(self.reactorStateImages):
            #If icon has changed
            if self.reactorValues[reactorNum] != newValue:
                #Set the value of the reactor
                self.reactorValues[reactorNum] = newValue

                if self.selectedType.get() != self.MEDUSA:
                    if self.reactorTypes[reactorNum]:
                        #Standard reactor icon
                        self.reactorButtons[reactorNum].configure(image=self.reactorStateImages[newValue])
                    else:
                        #Black swan reactor icon
                        self.reactorButtons[reactorNum].configure(image=self.reactorSwanStateImages[newValue])
                else:
                    #Medusa reactor icon
                    self.reactorButtons[reactorNum].configure(image=self.reactorMedusaStateImages[newValue])

    def changeSelectedReactor(self, reactorNumber : int) -> None:
        '''Invert the selected state of the given reactor'''
        #If the reactor is valid
        if reactorNumber > -1 and reactorNumber < self.numberReactorsInUse:
            #Invert selected value
            self.reactorSelected[reactorNumber] = not self.reactorSelected[reactorNumber]
        
        self.changeReactor()

    def changeReactor(self):
        '''Update the interface to show the data for selected reactors correctly'''
        #If there are no selected reactors
        if sum(self.reactorSelected) < 1:
            #Empty values and clear labels
            self.selectedFeeders = []
            self.changeHighlight(-1)
            self.updateReactorInfoState(False)
            self.blankReactorInfoLabels()
        else:
            #Get the number of each part of the machine
            partNumbers = self.machineNumbers[self.selectedType.get()]

            mixData = []
            agitateData = []
            targetHeats = []
            currentHeats = []
            feedData = []
            feedTimings = []

            selectedFeeders = []
            #Iterate feeders
            for feederNumber in range(0, len(self.feederAssocReactors)):
                #Get the associated reactors
                assoc = self.feederAssocReactors[feederNumber]
                #Iteraete through reactors
                for reactorNumber in assoc:
                    #Add the associated feeder if not already
                    if self.reactorSelected[reactorNumber] and feederNumber not in selectedFeeders:
                        selectedFeeders.append(feederNumber)

            #Iterate used reactors
            for i in range(0, self.numberReactorsInUse):
                #If selected
                if self.reactorSelected[i]:
                    #If there is a mixer
                    if i < partNumbers["mixers"]:
                        #Add the mixing data
                        mixData.append(self.reactorMixing[i])
                    #If there is an agitator
                    if i < partNumbers["agitators"]:
                        #Add the agitator data
                        agitateData.append(self.reactorAgitating[i])
                    #If there is a heater
                    if i < partNumbers["heaters"]:
                        #Add the heating data
                        targetHeats.append(self.reactorTargetTemp[i])
                        currentHeats.append(self.reactorCurrentTemp[i])
            
            #Iterate through the selected feeders
            for i in selectedFeeders:
                #Add the data and timing data
                feedData.append(self.feederFeeding[i])
                feedTimings.append(["{0} sec".format(self.feederDuration[i]), "{0} mins".format(self.feederDelay[i])])

            #Store which feeders are currently selected
            self.selectedFeeders = selectedFeeders
            
            #Update the labels on the display
            self.updateReactorInfoState(True)
            #Change the text in the information labels
            self.setReactorInfoLabels(mixData, currentHeats, targetHeats, agitateData, feedData, feedTimings)
    
    def reactorSelectionButtonPressed(self, all : bool, inv : bool, clr : bool) -> None:
        '''When a selection control button is pressed'''
        #Iteate reactors
        for reactorNumber in range(0, self.numberReactorsInUse):
            if all:
                #Select everything
                self.reactorSelected[reactorNumber] = True
            if inv:
                #Invert selection
                self.reactorSelected[reactorNumber] = not self.reactorSelected[reactorNumber]
            if clr:
                #Select nothing
                self.reactorSelected[reactorNumber] = False
        #Update the reactor selection
        self.changeReactor()

    def updateReactorInfoState(self, enabled : bool) -> None:
        '''Change the enabled state of all the reactor information labels'''
        #Correct state value
        st = "disabled"
        if enabled:
            st = "normal"
        #Update the value for each label
        self.reactorNameLabel.configure(state=st)
        self.reactorDisplayLabel.configure(state=st)
        self.reactorMixerLabel.configure(state=st)
        self.reactorMixerButton.configure(state=st)
        self.reactorCurrentTempLabel.configure(state=st)
        self.reactorTargetTempLabel.configure(state=st)
        self.reactorChangeTempSettingsButton.configure(state=st)
        self.reactorAgitatorLabel.configure(state=st)
        self.reactorAgitatorButton.configure(state=st)
        self.reactorFeederStateLabel.configure(state=st)
        self.reactorFeederTimingLabel.configure(state=st)
        self.reactorFeederSettingsButton.configure(state=st)
    
    def blankReactorInfoLabels(self) -> None:
        '''Set the text of the reactor labels back to default (none selected)'''
        self.reactorNameLabel.configure(text="No Reactor Selected")
        self.reactorMixerLabel.configure(text="Mixer: None")
        self.reactorCurrentTempLabel.configure(text="Current Temp: None")
        self.reactorTargetTempLabel.configure(text="Target Temp: None")
        self.reactorAgitatorLabel.configure(text="Agitator: None")
        self.reactorFeederStateLabel.configure(text="Feeding: None")
        self.reactorFeederTimingLabel.configure(text="Timing: None")

    def setReactorInfoLabels(self, mixing : list, tempCur : list, tempAim : list, agitating : list, feeding : bool, timing : list) -> None:
        '''Change the reactor labels in the machine display'''
        selected = []
        #Iterate reactors being used
        for reactorNum in range(0, self.numberReactorsInUse):
            #Store the currently selected ones
            if self.reactorSelected[reactorNum]:
                selected.append(reactorNum)
        
        titleMessage = ""
        #Change the title
        if len(selected) == 1:
            #Single reactor
            titleMessage = "Reactor Number {0}".format(selected[0] + 1)
        elif len(selected) > 1:
            #Multiple reactors
            titleMessage = "Reactors Number"
            for i in range(0, len(selected) - 1):
                titleMessage = titleMessage + " " + str(selected[i] + 1)
            titleMessage = titleMessage + " and " + str(selected[-1] + 1)
        #Set the label text
        self.reactorNameLabel.configure(text=titleMessage)

        #Change the mixer information
        mixerText = "Mixer:"
        if len(mixing) < 1:
            #No information
            mixerText = mixerText + " None"
        else:
            if len(mixing) == 1:
                #Single reactor
                if mixing[0]:
                    mixerText = mixerText + " Enabled"
                else:
                    mixerText = mixerText + " Disabled"
            else:
                #Multiple reactors
                for i in range(0, len(mixing)):
                    num = selected[i]
                    if mixing[i]:
                        mixerText = mixerText + " {0}:On".format(num + 1)
                    else:
                        mixerText = mixerText + " {0}:Off".format(num + 1)

        #Temperature information
        heatCurrentText = "Current Temp:"
        if len(tempCur) < 1:
            #None selected
            heatCurrentText = heatCurrentText + " None"
        else:
            if len(tempCur) == 1:
                #Single reactor
                heatCurrentText = heatCurrentText + " {0}°C".format(tempAim[0])
            else:
                #Multiple reactors
                for i in range(0, len(tempCur)):
                    num = selected[i]
                    heatCurrentText = heatCurrentText + " {0}:{1}°C".format(num + 1, int(float(tempCur[i])))
        
        #Target temperature information
        heatTargetText = "Target Temp:"
        if len(tempAim) < 1:
            #None selected
            heatTargetText = heatTargetText + " None"
        else:
            if len(tempAim) == 1:
                #Single reactor
                heatTargetText = heatTargetText + " {0}°C".format(tempAim[0])
            else:
                #Multiple reactors
                for i in range(0, len(tempAim)):
                    num = selected[i]
                    heatTargetText = heatTargetText + " {0}:{1}°C".format(num + 1, tempAim[i])
        
        #Agitator information
        agitatorText = "Agitator:"
        if len(agitating) < 1:
            #None selected
            agitatorText = agitatorText + " None"
        else:
            if len(agitating) == 1:
                #Single reactor
                if agitating[0]:
                    agitatorText = agitatorText + " Enabled"
                else:
                    agitatorText = agitatorText + " Disabled"
            else:
                #Multiple reactors
                for i in range(0, len(agitating)):
                    num = selected[i]
                    if agitating[i]:
                        agitatorText = agitatorText + " {0}:On".format(num + 1)
                    else:
                        agitatorText = agitatorText + " {0}:Off".format(num + 1)
        
        #Set labels text
        self.reactorMixerLabel.configure(text=mixerText)
        self.reactorCurrentTempLabel.configure(text=heatCurrentText)
        self.reactorTargetTempLabel.configure(text=heatTargetText)
        self.reactorAgitatorLabel.configure(text=agitatorText)
        
        #Feeding labels
        feedText = "Feeding:"
        feedTimingText = ""
        if len(feeding) == 0:
            #None selected
            feedText = feedText + " None"
            feedTimingText = feedTimingText + " None"
        else:
            if len(feeding) == 1:
                #Single feeder
                if feeding[0]:
                    feedText = feedText + " Yes"
                else:
                    feedText = feedText + " No"
                feedTimingText = feedTimingText + " {0} every {1}".format(timing[0][0], timing[0][1])
            else:
                #Multiple feeders
                for i in range(0, len(feeding)):
                    feederNum = self.selectedFeeders[i]
                    state = "No"
                    if feeding[i]:
                        state = "Yes"
                    feedText = feedText + " {0}:{1}".format(feederNum + 1, state)
                    feedTimingText = feedTimingText + " {0}:{1} every {2}".format(i + 1, timing[i][0], timing[i][1])
                    if i != len(feeding) - 1:
                        feedTimingText = feedTimingText + "\n"

        #Set label text for feeders
        self.reactorFeederStateLabel.configure(text=feedText)
        self.reactorFeederTimingLabel.configure(text=feedTimingText)

    def openSingleFeeder(self, feederNum : int) -> None:
        '''Open settings for one feeder only'''
        self.currentSettingsType = 3
        #Reset inputs
        self.feederTimeEntry.reset()

        #Store current feeder
        self.accessedFeeders = [feederNum]

        #Remove feeder objects
        for feedObject in self.feederSettingsObjects:
            feedObject["frame"].pack_forget()
        
        #Add object for this feeder
        self.feederSettingsObjects[feederNum]["frame"].pack(side="left", fill="both", expand=True)
        #Display this settings window
        self.feederSettingsFrame.lift()
        
        #Set header message
        titleMessage = "Feeder {0}".format(feederNum + 1)
        self.setupWindowTitle.configure(text=titleMessage)
        #Display settings window
        self.setupWindow.deiconify()

    def openSettings(self, section : str) -> None:
        '''Open the settings window displaying the correct information'''
        noFeeders = False
        noItems = True
        numberParts = self.machineNumbers[self.selectedType.get()]

        #If there are selected reactors
        if sum(self.reactorSelected) > 0:
            reactorList = []
            self.currentSettingsReactors = []
            #Iterate the reactors
            for reactorNumber in range(0, len(self.reactorSelected)):
                if self.reactorSelected[reactorNumber]:
                    #Add the reactor to the list
                    reactorList.append(reactorNumber + 1)
                    self.currentSettingsReactors.append(reactorNumber + 1)
            titleMessage = ""
            if section == "mixer":
                #Mixer information
                self.currentSettingsType = 0
                #Clear inputs
                self.mixerTimingEntry.reset()
                #Remove all mixing objects and add only the ones being used
                for mixObject in self.mixerSettingsObjects:
                    mixObject["frame"].pack_forget()
                for i in range(0, self.numberReactorsInUse):
                    if self.reactorSelected[i] and i < numberParts["mixers"]:
                        self.mixerSettingsObjects[i]["frame"].pack(side="left", fill="both", expand=True)
                        noItems = False
                #Display the correct part of the window
                self.mixerSettingsFrame.lift()
                #Set the title
                if len(reactorList) < 2:
                    titleMessage = "Mixer "
                else:
                    titleMessage = "Mixers "
            elif section == "heater":
                #Heater information
                self.currentSettingsType = 1
                #Clear the inputs
                self.heaterTimeEntry.reset()
                #Remove all heating objects and add only the ones being used
                for heatObject in self.heaterSettingsObjects:
                    heatObject["frame"].pack_forget()
                for i in range(0, self.numberReactorsInUse):
                    if self.reactorSelected[i] and i < numberParts["heaters"]:
                        self.heaterSettingsObjects[i]["frame"].pack(side="left", fill="both", expand=True)
                        noItems = False
                #Display the correct part of the window
                self.heaterSettingsFrame.lift()
                #Set the title
                if len(reactorList) < 2:
                    titleMessage = "Heater "
                else:
                    titleMessage = "Heaters "
            elif section == "agitator":
                #Agitator information
                self.currentSettingsType = 2
                #Clear inputs
                self.agitatorTimeEntry.reset()
                #Remove all agitating objects and add only the ones being used
                for agiObject in self.agitatorSettingsObjects:
                    agiObject["frame"].pack_forget()
                for i in range(0, self.numberReactorsInUse):
                    if self.reactorSelected[i] and i < numberParts["agitators"]:
                        self.agitatorSettingsObjects[i]["frame"].pack(side="left", fill="both", expand=True)
                        noItems = False
                #Display the correct part of the window
                self.agitatorSettingsFrame.lift()
                #Set the title
                if len(reactorList) < 2:
                    titleMessage = "Agitator "
                else:
                    titleMessage = "Agitators "
            elif section == "feeder":
                #Feeder information
                if len(self.selectedFeeders) > 0:
                    self.currentSettingsType = 3
                    #Clear inputs
                    self.feederTimeEntry.reset()
                    self.accessedFeeders = []
                    #Remove all feeders and add only the ones being used
                    for feedObject in self.feederSettingsObjects:
                        feedObject["frame"].pack_forget()
                    for i in range(0, len(self.selectedFeeders)):
                        self.accessedFeeders.append(self.selectedFeeders[i])
                        self.feederSettingsObjects[self.selectedFeeders[i]]["frame"].pack(side="left", fill="both", expand=True)
                    #Display the correct part of the window
                    self.feederSettingsFrame.lift()
                    #Set the title
                    if len(self.selectedFeeders) < 2:
                        titleMessage = "Feeder "
                    else:
                        titleMessage = "Feeders "
                else:
                    noFeeders = True

            #If not a feeder window
            if self.currentSettingsType != 3:
                #If there are reactors
                if len(reactorList) == 1:
                    #Set the title
                    titleMessage = titleMessage + str(reactorList[0])
                else:
                    #Set the correct title for multiple reactors
                    for rNum in range(0, len(reactorList) - 1):
                        titleMessage = titleMessage + str(reactorList[rNum]) + " "
                    titleMessage = titleMessage + "and " + str(reactorList[-1])
            else:
                #Set the title for one feeder
                if len(self.selectedFeeders) == 1:
                    titleMessage = titleMessage + str(self.selectedFeeders[0] + 1)
                else:
                    #Set the title for multiple feeders
                    for feederIndex in range(0, len(self.selectedFeeders) - 1):
                        titleMessage = titleMessage + str(self.selectedFeeders[feederIndex] + 1) + " "
                    titleMessage = titleMessage + "and " + str(self.selectedFeeders[-1] + 1)

            #If there was something to display
            if (not noFeeders and section == "feeder") or not noItems:
                #Set the title
                self.setupWindowTitle.configure(text=titleMessage)
                #Open the window
                self.setupWindow.deiconify()
    
    def closeSettings(self) -> None:
        self.setupWindow.withdraw()

    def startMaintenance(self) -> None:
        '''Open the maintenance window'''
        #Get the parts of the machine
        partNumbers = self.machineNumbers[self.selectedType.get()]
        #Iterate reactors and remove all parts
        for i in range(0, 10):
            self.maintenanceReactors[i]["frame"].grid_forget()
            self.maintenanceReactors[i]["mix"].grid_forget()
            self.maintenanceReactors[i]["mixButton"].grid_forget()
            self.maintenanceReactors[i]["heat"].grid_forget()
            self.maintenanceReactors[i]["heatButton"].grid_forget()
            self.maintenanceReactors[i]["agi"].grid_forget()
            self.maintenanceReactors[i]["agiButton"].grid_forget()
            self.maintenanceFrame.grid_columnconfigure(i, weight=0)
        #Iterate reactors being used
        for i in range(0, self.numberReactorsInUse):
            #Add the mixers, heaters, and agitators back with their buttons
            if partNumbers["mixers"] > i:
                self.maintenanceReactors[i]["mix"].grid()
                self.maintenanceReactors[i]["mixButton"].grid()
            if partNumbers["heaters"] > i:
                self.maintenanceReactors[i]["heat"].grid()
                self.maintenanceReactors[i]["heatButton"].grid()
            if partNumbers["agitators"] > i:
                self.maintenanceReactors[i]["agi"].grid()
                self.maintenanceReactors[i]["agiButton"].grid()
            self.maintenanceReactors[i]["frame"].grid(row=1, column=i, sticky="NESW")
            self.maintenanceFrame.grid_columnconfigure(i, weight=1)
        #Add the labels and controls back
        self.maintenanceTitleLabel.grid(row=0, column=0, columnspan=self.numberReactorsInUse)
        self.maintenanceControlFrame.grid(row=3, column=0, columnspan=self.numberReactorsInUse, sticky="NESW")
        #Remove all feeders
        for i in range(0, 4):
            self.maintenanceFeeders[i]["frame"].grid_forget()
        feedData = self.machineFeeders[self.selectedType.get()]
        #Add back the feeders being used
        for i in range(0, len(feedData)):
            start = feedData[i][1][0]
            width = len(feedData[i][1])
            self.maintenanceFeeders[i]["frame"].grid(row=2, column=start, columnspan=width, sticky="NESW")
        self.maintenanceMode = True
        #Send message to device to begin mainteance
        self.pendingMessages.append("maintenanceset 1\n")
        #Switch to maintenance view
        self.changeMainFrame(3)
    
    def stopMaintenance(self) -> None:
        '''Close the maintenance view'''
        self.maintenanceMode = False
        #Send message to device
        self.pendingMessages.append("maintenanceset 0\n")
        #Switch to normal view
        self.changeMainFrame(2)

    def maintenanceMixer(self, reactor : int) -> None:
        '''Invert mixer'''
        if reactor > -1 and reactor < self.numberReactorsInUse:
            if self.reactorMixing[reactor]:
                self.maintenanceChange(reactor, 0, 0)
            else:
                self.maintenanceChange(reactor, 0, 1)
    
    def maintenanceHeater(self, reactor : int) -> None:
        '''Invert heater'''
        if reactor > -1 and reactor < self.numberReactorsInUse:
            if self.reactorHeating[reactor]:
                self.maintenanceChange(reactor, 1, 0)
            else:
                self.maintenanceChange(reactor, 1, 1)
    
    def maintenanceAgitator(self, reactor : int) -> None:
        '''Invert agitator'''
        if reactor > -1 and reactor < self.numberReactorsInUse:
            if self.reactorAgitating[reactor]:
                self.maintenanceChange(reactor, 2, 0)
            else:
                self.maintenanceChange(reactor, 2, 1)

    def maintenanceFeeder(self, feeder : int) -> None:
        '''Invert feeder'''
        if feeder > -1 and feeder < 4:
            if self.feederFeeding[feeder]:
                self.maintenanceChange(feeder, 3, 0)
            else:
                self.maintenanceChange(feeder, 3, 1)

    def maintenanceOff(self) -> None:
        '''Switch all off maintenance - for use with buttons'''
        self.maintenanceToggle(0)
    
    def maintenanceOn(self) -> None:
        '''Switch all on maintenance - for use with buttons'''
        self.maintenanceToggle(1)
    
    def maintenanceToggle(self, state : int) -> None:
        '''Change all values in maintenance mode to given state'''
        #Count feeders
        numberFeeders = len(self.machineFeeders[self.selectedType.get()])
        #Iterate reactors
        for i in range(0, self.numberReactorsInUse):
            #Change mixing, heating and agitating
            self.maintenanceChange(i, 0, state)
            self.maintenanceChange(i, 1, state)
            self.maintenanceChange(i, 2, state)
        #Chage feeder values
        for i in range(0, numberFeeders):
            self.maintenanceChange(i, 3, state)
    
    def maintenanceChange(self, reactor : int, event : int, data : int) -> None:
        '''Change value in maintenance mode'''
        #event : 0 = mixer 1 = heater 2 = agitator 3 = feeder
        
        #If there is a valid reactor
        if reactor < self.numberReactorsInUse and event != 3:
            #Add one for offset (0 based here)
            reactorNum = reactor + 1
            #Choose correct message based on event and add message
            if event == 0:
                self.pendingMessages.append("maintenancemixer {0} {1}\n".format(reactorNum, data))
            elif event == 1:
                self.pendingMessages.append("maintenanceheater {0} {1}\n".format(reactorNum, data))
            elif event == 2:
                self.pendingMessages.append("maintenanceagitator {0} {1}\n".format(reactorNum, data))
        
        #If this is a feeder
        if reactor < 4 and event == 3:
            #Increment value
            feederNum = reactor + 1
            #Add feeder message
            self.pendingMessages.append("maintenancefeeder {0} {1}\n".format(feederNum, data))

    def closeWindow(self) -> None:
        '''When close is pressed'''
        #On the starting screen
        if self.currentMain == 0:
            #Close the program
            self.parent.destroy()
        #If on the main screen
        elif self.currentMain == 2:
            #Disconnect and return to the start
            self.disconnect()
            self.changeMainFrame(0)
        #If on the maintenance screen
        elif self.currentMain == 3:
            #End maintenance - returns to main screen
            self.stopMaintenance()

class NumEntry(tkinter.Frame):
    '''Class for numerical entry field with a title'''
    def __init__ (self, parent, title : str, row=None, *args, **kwargs) -> None:
        #Initialise parent class
        tkinter.Frame.__init__(self, parent, *args, **kwargs)
        #Store parent object
        self.parent = parent
        #Store parameters
        self.row = row
        self.titleText = title
        #Variable to store value
        self.entryValue = tkinter.StringVar()
        #Set the value of the string
        self.entryValue.set("")
        #Add trace to handle when a value is typed
        self.entryValue.trace_add("write", self.valueChanged)
        #Store the previous value
        self.oldValue = self.entryValue.get()
        #If the row was not set
        if self.row == None:
            #Create label and entry widgets with this as parent
            self.titleLabel = tkinter.Label(self, text=self.titleText)
            self.numberEntry = tkinter.Entry(self, textvariable=self.entryValue)
            #Pack into frame
            self.titleLabel.pack(side="left")
            self.numberEntry.pack(side="left", expand=True, fill="x")
        else:
            #Create label and entry widgets using parent object
            self.titleLabel = tkinter.Label(self.parent, text=self.titleText)
            self.numberEntry = tkinter.Entry(self.parent, textvariable=self.entryValue)
            #Add to grid at given row position
            self.titleLabel.grid(row=self.row, column=0, sticky="NESW")
            self.numberEntry.grid(row=self.row, column=1, sticky="NESW")

    def getValue(self) -> float:
        """Get the value entered into the field, otherwise returns None"""
        #Get the string from the variable
        value = self.entryValue.get()
        #If nothing has been entered
        if value == "":
            return None
        else:
            #If it is a numeric value
            if self.checkNumber(value):
                #Return it as a float
                return float(value)
            else:
                return None
    
    def resetValue(self) -> None:
        """Reset the value of the entry"""
        self.entryValue.set("")
    
    def valueChanged(self, *args) -> None:
        """When the value is changed, check if it is valid and only keep change if it is"""
        #Get the variable value
        value = self.entryValue.get()
        #If the value is empty
        if value == "":
            #Store the value as previous
            self.oldValue = value
        else:
            #Test if it is a valid number
            if self.checkNumber(value):
                #Store the value as previous
                self.oldValue = value
            else:
                #Restore previous value
                self.entryValue.set(self.oldValue)
    
    def checkNumber(self, stringValue : str) -> bool:
        """Test if a string is a valid number"""
        #Possible valid characters
        validChars = "0123456789."
        #Number of decimal digits
        decimals = 0
        
        #Iterate strings
        for char in stringValue:
            #If the character is not valid
            if char not in validChars:
                #The string is not a valid number
                return False
            #If it is a decimal point
            if char == ".":
                #Increment decimal counter
                decimals = decimals + 1
        
        #If one or fewer decimal points has been found
        if decimals < 2:
            #The number is valid
            return True
        
        #The number is not valid
        return False
        
class NumberGroup(tkinter.Frame):
    '''Class to collect a group of numerical inputs and a set button'''
    def __init__ (self, parent, titles : list, header : str, valueHandler, *args, **kwargs):
        tkinter.Frame.__init__(self, parent, *args, **kwargs)
        #List to contain NumEntry objects
        self.entries = []
        #Parent object and function for handling output
        self.parent = parent
        self.handler = valueHandler
        index = 0
        #Iterate through given titles
        for title in titles:
            #Create entry object
            entry = NumEntry(self, title=title, row=index + 1)
            #Add to list
            self.entries.append(entry)
            index = index + 1
        
        #Configure rows
        for r in range(0, index + 2):
            self.grid_rowconfigure(r, weight=1)
        
        #Configure columns
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        #Add header label and set button
        self.headerLabel = tkinter.Label(self, text=header)
        self.headerLabel.grid(row=0, column=0, columnspan=2)
        self.setButton = tkinter.Button(self, text="Set", command=self.setPressed)
        self.setButton.grid(row=index + 1, column=0, columnspan=2)
    
    def setPressed(self) -> None:
        """When the set values button is pressed"""
        #List to contain values
        values = []
        #Iterate through NumEntries
        for entry in self.entries:
            #Get the value and add to list
            values.append(entry.getValue())
        #Call the handler function to process the values
        self.handler(values)

    def reset(self) -> None:
        """Reset all the NumEntries so that the window is clear"""
        for entry in self.entries:
            entry.resetValue()

class DebugWindow(tkinter.Frame):
    '''Class for the debug output frame'''
    def __init__ (self, parent, *args, **kwargs) -> None:
        #Initialise parent class
        tkinter.Frame.__init__(self, parent, *args, **kwargs)

        self.parent = parent
        self.scrollBar = tkinter.Scrollbar(self, orient="vertical")
        self.textBox = tkinter.Text(self, yscrollcommand=self.scrollBar.set)
        self.scrollBar.configure(command=self.textBox.yview)
        self.scrollBar.pack(fill="y", side="right")
        self.textBox.pack(expand=True, fill="both", side="left")

        self.textBox.tag_configure("sent", foreground="blue")
    
    def addText(self, message : str, tag = "") -> None:
        self.textBox.insert(tkinter.END, message, tag)
        self.moveToEnd()
    
    def addSent(self, message : str) -> None:
        self.addText(message, "sent")

    def moveToEnd(self) -> None:
        self.textBox.yview_moveto(1.0)


#Only run if this is the main module being run
if __name__ == "__main__":
    #Create root window for tkinter
    root = tkinter.Tk()
    #Calculate the position of the centre of the screen
    screenMiddle = [root.winfo_screenwidth() / 2, root.winfo_screenheight() / 2]
    #Set the shape of the window and place it in the centre of the screen
    screenShape = [900, 500]
    screenMiddle = [int(screenMiddle[0] - (screenShape[0] / 2)), int(screenMiddle[1] - (screenShape[1] / 2))]
    root.geometry("{0}x{1}+{2}+{3}".format(screenShape[0], screenShape[1], screenMiddle[0], screenMiddle[1]))
    root.minsize(screenShape[0], screenShape[1])
    #Allow for expanding sizes
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)
    #Set the title text of the window
    root.title("Access Device")
    #Add the editor to the root windows
    rootWindow = MainWindow(root)
    rootWindow.grid(row = 0, column=0, sticky="NESW")
    root.protocol("WM_DELETE_WINDOW", rootWindow.closeWindow)
    #Start running the root
    root.mainloop()
