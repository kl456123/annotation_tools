import vtk
from utils import *
from actor import *
from box_widget import *
from callback import SelectionCallback
##################################
#######box selection####
##################################


######################################
####frustum selection ################
######################################

class Selection(object):
    def __init__(self, input_filter, displayer, point_renderer, debug=False, velo_only=False):
        self.in_velo = velo_only
        self.selected_actor = None
        self.box_widget = None
        self.angle = 0
        self.SetInput(input_filter)

        # set renderer
        # self.SetRenderer(renderer)

        # set displayer
        self.SetDisplayer(displayer)

        # initialize the last filter
        self.ResetHistory()

        self.debug = debug

        self._continue = False

        # self.displayer = displayer

        self.box_centers = [0, 0, 0]
        self.point_renderer = point_renderer

        self.selected_actor = PolyDataActor(self.input.GetOutputPort())
        self.point_renderer.AddActor(self.GetActor())

        self.ResetWidgetAndActor()

        self.RegisterSelectionCallback()

    def RegisterSelectionCallback(self):
        self.selection_callback = SelectionCallback(self)

    def IsObjectSelected(self):
        return self.GetCurrentBoxWidget().selected

    # def SetBorderWidget(self,borderwidget):
    #     self

    def GetCurrentBoxWidget(self):
        return self.box_widget

    # def SetRenderer(self,renderer):
    #     # bind renderer to selection
    #     # so that actor that selection make can pass on to the renderer
    #     # for render immediately
    #     self.renderer = renderer

    def SetDisplayer(self, displayer):
        # bind displayer to selection
        # it is necessary to make box widget connect with interactor
        self.displayer = displayer

    def ResetHistory(self):
        self.extract_geometry_filters = []
        self.last_filters = []

        self.last_filter = self.input

    def ResetWidgetAndActor(self):
        # reset actor
        # if self.selected_actor is not None:
        self.selected_actor.SetInput(self.input.GetOutputPort())

        # pass on actor to renderer
        # self.point_renderer.AddActor(self.GetActor())
        # re = vtk.vtkRenderer()

        # reset box widget
        if self.box_widget is not None:
            self.box_widget.Off()
            # del self.box_widget
        self.box_widget = BoxWidget(
            self.point_renderer, self.displayer, self.input)
        self.displayer.pc_style_picker.SetCurrentBoxWidget(self.box_widget)

    def Reset(self):
        self.angle = 0

        if not self.IsObjectSelected():
            # no more new thing need to reset
            return
        # reset input ,box widget and actor
        self.ResetHistory()

        self.ResetWidgetAndActor()

        # exit from continue mode
        self.SetContinue(False)

    def SetInput(self, vtkAlgo):
        # the oldest filter for reset
        self.input = vtkAlgo
        assert isinstance(vtkAlgo, vtk.vtkAlgorithm),\
            print("arguement should be the type of vtkAlgorithmOutput")

    def GetActor(self):
        return self.selected_actor.actor

    def GetContinue(self):
        return self._continue

    def SetContinue(self, con):
        self._continue = con

    def AddFilter(self, func):
        if not self.GetContinue():
            # reset history
            self.ResetHistory()

        extract_geometry_filter = vtk.vtkExtractGeometry()
        # set filter function
        extract_geometry_filter.SetImplicitFunction(func)

        # connect the last output
        # some bug here, so I use SetInputData() instead.
        # extract_geometry_filter.SetInputConnection(self.last_filters[-1].GetOutputPort())
        extract_geometry_filter.SetInputConnection(
            self.last_filter.GetOutputPort())

        # save last_filter
        self.last_filters.append(self.last_filter)

        # update the last output
        self.last_filter = vtk.vtkVertexGlyphFilter()
        self.last_filter.SetInputConnection(
            extract_geometry_filter.GetOutputPort())

        # append to the list for saving
        self.extract_geometry_filters.append(extract_geometry_filter)

        # set the last filter to the input of mapper
        self.selected_actor.SetInput(self.last_filter.GetOutputPort())
        self.selected_actor.Update()

    def Color(self, color_name="green"):

        # num of points
        num_points = self.selected_actor.GetNumberOfPoints()
        num_cells = self.selected_actor.GetNumberOfCells()

        # generate colors
        selected_colors = GenerateColors(num_points, color_name=color_name)

        # set attribution of points
        self.selected_actor.SetScalars(selected_colors)

        if self.debug:
            print("Points: ", num_points)
            print("Cells: ", num_cells)
        #
        #
        #
        self.box_widget.SetMyactor(self.selected_actor)
        # self.box_widget.PlaceWidget()
