from PySide6.QtWidgets import (QApplication, QMainWindow, QLabel, QPushButton, 
                               QWidget, QVBoxLayout, QHBoxLayout, 
                               QComboBox)
                               
from PySide6.QtCore import Qt
                               
from maya import OpenMayaUI as omui
from shiboken6 import wrapInstance

import mayaUsd

from pxr import Usd, Sdf

class MvOpWindow(QMainWindow):
    def __init__(self):
        
        # Must wrap C++ ptr returned from mainWindow() into PySide Window
        # 1. Python cannot work with the C++ object directly
        # 2. Wrap as Python QT window to use QT objects 
        maya_window_ptr = omui.MQtUtil.mainWindow()
        Qt_window = wrapInstance(int(maya_window_ptr), QMainWindow)
        
        # Referencing parent class without explicitly naming
        super().__init__(parent=Qt_window)
        
        # Initialize GUI
        self.initGUI()
        
        self.stage       = None
        self.src_layers  = None
        self.src_layer   = None
        self.src_obj     = None
        self.src_prop    = None
        self.dest_layers = None
        self.dest_layer  = None
        
        # When the window opens, load all layers to populate combo box
        self.getSourceLayers()
        
        
    def initGUI(self):
        
        # Window properties
        # -------------------------------------
        self.dimX = 300
        self.dimY = 175
        self.setWindowTitle("Move Opinion")
        self.setMinimumSize(self.dimX, self.dimY)
        self.setMaximumSize(self.dimX, self.dimY)
        
        # Layouts
        # -------------------------------------
        self.main_layout  = QVBoxLayout()
        
        self.vbox1_layout = QVBoxLayout()
        
        self.vbox2_layout = QVBoxLayout()

        self.hbox1_layout = QHBoxLayout()
        self.hbox2_layout = QHBoxLayout()
        
        # Labels
        # -------------------------------------
        
        # Source layer label
        self.src_layer_lbl = QLabel()
        self.src_layer_lbl.setText("Source Layer")
        self.src_layer_lbl.setMinimumSize(1,1)
        self.src_layer_lbl.setAlignment(Qt.AlignRight)
        
        # Source object label
        self.src_obj_lbl = QLabel()
        self.src_obj_lbl.setText("Source Object")
        self.src_obj_lbl.setMinimumSize(1,1)
        self.src_obj_lbl.setAlignment(Qt.AlignRight)
        
        # Source property label
        self.src_prop_lbl = QLabel()
        self.src_prop_lbl.setText("Source Property")
        self.src_prop_lbl.setMinimumSize(1,1)
        self.src_prop_lbl.setAlignment(Qt.AlignRight)
        
        # Destination layer label
        self.dest_layer_lbl = QLabel()
        self.dest_layer_lbl.setText("Destination Layer")
        self.dest_layer_lbl.setMinimumSize(1,1)
        self.dest_layer_lbl.setAlignment(Qt.AlignRight)
        
        # Comboboxes
        # -------------------------------------
        
        # Source layer combo box
        self.src_layer_cb = QComboBox()
        self.src_layer_cb.setCurrentIndex(1)
        self.src_layer_cb.view().setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.src_layer_cb.currentIndexChanged.connect(self.onSrcLayerSelected)
        self.src_layer_cb.setEditable(False)
        
        # Source object combo box
        self.src_obj_cb = QComboBox()
        self.src_obj_cb.setCurrentIndex(1)
        self.src_obj_cb.view().setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.src_obj_cb.currentIndexChanged.connect(self.onSrcObjSelected)
        self.src_obj_cb.setEditable(False)
        
        # Source property combo box
        self.src_prop_cb = QComboBox()
        self.src_prop_cb.setCurrentIndex(1)
        self.src_prop_cb.view().setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.src_prop_cb.currentIndexChanged.connect(self.onSrcPropSelected)
        self.src_prop_cb.setEditable(False)
        
        # Destination layer combo box
        self.dest_layer_cb = QComboBox()
        self.dest_layer_cb.setCurrentIndex(1)
        self.dest_layer_cb.view().setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.dest_layer_cb.currentIndexChanged.connect(self.onDestLayerSelected)
        self.dest_layer_cb.setEditable(False)
        
        # Buttons
        # -------------------------------------
        
        # Refresh button
        self.refresh_btn = QPushButton()
        self.refresh_btn.setText("Refresh")
        self.refresh_btn.clicked.connect(self.onRefreshBtnClicked)
        
        # Move button
        self.move_btn = QPushButton()
        self.move_btn.setText("Move")
        self.move_btn.clicked.connect(self.onMoveBtnClicked)
        
        # Build GUI
        # -------------------------------------
        self.vbox1_layout.addWidget(self.src_layer_lbl)
        self.vbox1_layout.addWidget(self.src_obj_lbl)
        self.vbox1_layout.addWidget(self.src_prop_lbl)
        self.vbox1_layout.addWidget(self.dest_layer_lbl)
        
        self.vbox2_layout.addWidget(self.src_layer_cb)
        self.vbox2_layout.addWidget(self.src_obj_cb)
        self.vbox2_layout.addWidget(self.src_prop_cb)
        self.vbox2_layout.addWidget(self.dest_layer_cb)
        
        self.hbox1_layout.addLayout(self.vbox1_layout)
        self.hbox1_layout.addLayout(self.vbox2_layout)
        
        self.hbox2_layout.addWidget(self.refresh_btn)
        self.hbox2_layout.addWidget(self.move_btn)
        
        self.main_layout.addLayout(self.hbox1_layout)
        self.main_layout.addLayout(self.hbox2_layout)
        
        self.dummy = QWidget()
        self.dummy.setLayout(self.main_layout)
        self.setCentralWidget(self.dummy)
        
    def getSourceLayers(self):
        # Find root layer of the main stage and then open the stage
        self.stage = mayaUsd.ufe.getStage('|main_stage|main_stageShape')
        
        # Get layer stack from stage but exclude session layers and get names of each layer
        src_layers_SDFs = self.stage.GetLayerStack(includeSessionLayers=False)
        src_layers_names = [layer_SDF.GetDisplayName() for layer_SDF in src_layers_SDFs]
        
        # Create single list of pairs from two lists then cast to dict
        self.src_layers = dict(zip(src_layers_names, src_layers_SDFs))        
        
        # Add each layer display name to the src layer combo box
        for layer_name in self.src_layers.keys():
            self.src_layer_cb.addItem(layer_name)
            

    def onSrcLayerSelected(self):
       # Remove all entries from dest and obj combo boxes before adding
       self.dest_layer_cb.clear()
       self.src_obj_cb.clear()
       
       # Get text in combobox
       src_layer_name = self.src_layer_cb.currentText()
       
       if src_layer_name:
           # Find layer in dict for given name
           self.src_layer = self.src_layers[src_layer_name]
           
           # Open stage for specific layer
           temp_stage = Usd.Stage.Open(self.src_layer)
           
           # Get all prims in stage that exist in layer and add to combo box
           for prim in temp_stage.TraverseAll():
               primspec = self.src_layer.GetPrimAtPath(prim.GetPath())
               
               if primspec:
                   self.src_obj_cb.addItem(str(prim.GetPath()))
           
           # Add all layers to dest layers except for the selected src layer
           self.dest_layers = {key : value for key, value in self.src_layers.items() if key != src_layer_name}
           
           # Add dest layers to combobox
           for layer_name in self.dest_layers.keys():
               self.dest_layer_cb.addItem(layer_name)
                                    
    def onSrcObjSelected(self):
        # Remove all entries from authored properties combo box
        self.src_prop_cb.clear()
        
        # Get text in combobox
        self.src_obj = self.src_obj_cb.currentText()
                   
        # Get primspec at src_layer for selected prim
        if self.src_obj:
            prim = self.src_layer.GetPrimAtPath(self.src_obj)
        
            if prim:
                # Add all authored attributes to combo box
                self.src_prop_cb.addItem('') # Add initial whitespace to combo box
                for attr in prim.attributes:
                    self.src_prop_cb.addItem(attr.name)
                    
                self.src_prop_cb.setCurrentIndex(0)
            
            
    def onSrcPropSelected(self):
        # Get source property
        self.src_prop = self.src_prop_cb.currentText()
        
    
    def onDestLayerSelected(self):
        # Get destination layer
        dest_layer_name = self.dest_layer_cb.currentText()
        
        if dest_layer_name:
            self.dest_layer = self.dest_layers[dest_layer_name]
        
        
    def onMoveBtnClicked(self):
        if self.src_obj:
            # Get prim from selected object path in source layer
            stage_src = Usd.Stage.Open(self.src_layer)
            prim_src = stage_src.GetPrimAtPath(self.src_obj)
            primspec_src = self.src_layer.GetPrimAtPath(self.src_obj)
            
            if self.dest_layer:
                # Get prim from selected object path in destination, if it exists
                stage_dest = Usd.Stage.Open(self.dest_layer)
                prim_dest = stage_dest.GetPrimAtPath(self.src_obj)
                primspec_dest = self.dest_layer.GetPrimAtPath(self.src_obj)
            
            if self.src_prop:
                # Get attribute we want to move from source object and destination, if it exists
                attr_src = prim_src.GetAttribute(self.src_prop)
                attr_dest = prim_dest.GetAttribute(self.src_prop)
                    
                # If attribute exists at destination, overwrite value, else create attr and set
                if attr_dest:
                    if attr_dest.Get() != attr_src.Get():
                        attr_dest.Set(attr_src.Get())
                else:
                    prim_dest.CreateAttribute(self.src_prop, attr_src.GetTypeName(), custom=False)
                    attr_dest.Set(attr_src.Get())
                 
                # If the transfer was succesful, delete property from source
                if attr_dest.Get() == attr_src.Get():
                    prim_src.RemoveProperty(self.src_prop)
                                
            else:
                # For each authored attribute on the src object, move over to destination
                for attr in primspec_src.attributes:
                    attr_src = prim_src.GetAttribute(attr.name)
                    attr_dest = prim_dest.GetAttribute(attr.name)

                    # If attribute exists at destination, overwrite value, else create attr and set
                    if attr_dest:
                        if attr_dest.Get() != attr_src.Get():
                            attr_dest.Set(attr_src.Get())
                    else:
                        prim_dest.CreateAttribute(attr_src.GetName(), attr_src.GetTypeName(), custom=False)
                        attr_dest.Set(attr_src.Get())
                 
                    # If the transfer was succesful, delete property from source
                    if attr_dest.Get() == attr_src.Get():
                        prim_src.RemoveProperty(attr_src.GetName())
                       
            self.cleanLayer(primspec_src.path)
                
            self.onRefreshBtnClicked()
                          
            
    def onRefreshBtnClicked(self):
       # Remove all entries from combo boxes and variables
       self.clearMembers()
       self.dest_layer_cb.clear()
       self.src_layer_cb.clear()
       self.src_obj_cb.clear()
       
       # Re-grab source layers
       self.getSourceLayers()
       
       
    def clearMembers(self):
       # Clear variables
       self.stage       = None
       self.src_layers  = None
       self.src_layer   = None
       self.src_obj     = None
       self.src_prop    = None
       self.dest_layers = None
       self.dest_layer  = None
       
    def cleanLayer(self, prim_path):
        primspec = self.src_layer.GetPrimAtPath(prim_path)
    
        if primspec:
            for child in primspec.nameChildren:
                printPrimTree(self.src_layer, child.path)
        
            if primspec.attributes:
                return
            elif primspec.nameChildren:
                return
            else:
                stage = Usd.Stage.Open(self.src_layer)
                stage.RemovePrim(primspec.path)


my_window = MvOpWindow()
my_window.show()

del my_window