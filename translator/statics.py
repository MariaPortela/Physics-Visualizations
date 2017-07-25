"""
Created to generate HTML pages with embedded PlotlyJS using Python commands defined in this script.
- Akash B

This file deals with creating static plots, to which interactive features can be added using other files in the library.
"""

from translator.helpers import jsify, escape, var, Data, Document


class Graph:
    objects = {}                                                              # JS data objects.

    def __init__(self, div_id="plot"):
        """
        Sets up HTML
        :param div_id: HTML Id of the div in which graph is placed.
        """
        self.type = escape(type)
        self.instance_objects = {}
        self.data = {}                                        # Dictionary that contains all data objects w/ attributes.
        self.script = ""                                      # Variable to store HTML/JS script as and when generated.
        self.div_id = escape(div_id)                          # HTML div where graph will be located.
        self.layout = "var layout"                            # String to contain layout parameters for graph.
        return

    def __repr__(self):
        return str(self.script)

    def finish_plot(self, v_name=None, **kwargs):
        """
        Formats objects as JSON, then updates instance and class dictionaries.
        :param v_name: Name of JS object.
        :param kwargs: Attributes of JS object.
        :return:
        """
        if v_name:
            v_name = str(v_name)

        else:
            v_name = str(self.type[1:-1])

        v_name = "{v_name}".format(v_name=v_name + str(len(self.objects)))
        data = Data(**kwargs).json                         # Processing keyword arguments and converting to JSON.
        data_js = jsify(data=data, variable_name=v_name)     # Making JS data object.
        v_name = escape(v_name)
        self.objects[v_name] = str(data_js)                # Storing current plot's attributes in class' dictionary.
        self.instance_objects[v_name] = str(data_js)       # Storing current plot's attributes in instance's dictionary.
        return

    def show_all(self, **kwargs):
        """
        Writes self.objects dictionary as a JS script, i.e. all plots declared in all instances that inherit from class
        Graph.
        :return:
        """
        plots = "["

        # Setting raw data (lists) to variable names in JS.
        for variable, value in self.objects.items():
            self.script += "var {variable} = {value}; \n".format(variable=var(variable, True), value=value)

        self.script += "\n"  # Beautifying.

        for v_name, obj in self.objects.items():  # Writing JS objects (that will be plotted)
            obj = var(obj, decode=True)  # Escaping all references to variables

            self.script += obj
            plots += v_name[1:-1] + ", "

        plots = plots[:-2]
        plots += "]"

        self.make_layout(**kwargs)

        self.script += self.layout
        self.script += "Plotly.newPlot({div_v_name}, {plots}, layout);".format(div_v_name=escape(self.div_id),
                                                                               plots=plots)
        return self.script

    def show(self, **kwargs):
        """
        Writes objects in self.data as a JS script, i.e. only the plots that exist in the declared instance.
        :param kwargs: Any attribute-value pair that needs to be written to the layout variable.
        :return:
        """
        plots = "["

        # Setting raw data (lists) to variable names in JS.
        for variable, value in self.data.items():
            self.script += "var {variable} = {value}; \n".format(variable=var(variable, True), value=value)

        self.script += "\n"                                     # Beautifying.

        for v_v_name, obj in self.instance_objects.items():         # Writing JS objects (that will be plotted)
            obj = var(obj, decode=True)                         # Escaping all references to variables

            self.script += obj
            plots += v_v_name[1:-1] + ", "

        plots = plots[:-2]
        plots += "]"

        self.make_layout(**kwargs)

        self.script += self.layout
        self.script += "Plotly.newPlot({div_v_name}, {plots}, layout);".format(div_v_name=escape(self.div_id),
                                                                               plots=plots)
        return self.script

    def make_layout(self, **kwargs):
        """
        Configures aesthetics of the plot.
        :param kwargs: Attributes and corresponding values passed into PlotlyJS, per the PlotlyJS documentation.
        :return:
        """

        if len(kwargs.items()) > 0:
            layout_params = Data(**kwargs).json             # Processing layout parameters.
            layout_js = jsify(data=layout_params)           # Converting to JS object.
            self.layout += " = " + layout_js + "\n"         # Writing JS to self.layout

        else:
            self.layout += "; \n"                           # If no arguments passed in, then var layout remains empty.
        return


class Surface(Graph):
    def __init__(self, z=None, div_id="surface_plot", **kwargs):
        """
        Generates script to make PlotlyJS 3D Surface plot.
        :param z: List containing data for all surfaces, each surface in an inner list.
        :param div_id: ID of the HTML div tag this plot will be drawn in.
        :param width: Width of plot
        :param height: Height of plot
        :param kwargs: Attributes of the surface plot.
        """
        Graph.__init__(self, div_id=div_id)
        self.type = escape("surface")

        if z:
            self.plot(z=z, type=self.type, **kwargs)

        return

    def plot(self, z, **kwargs):
        """

        :param z: List containing lines that make up the surface.
        :param kwargs: Attributes of the plot.
        :return:
        """

        # Sanity check - is data in correct format?
        if str(type(z)) != "<class 'list'>" or len(z) == 0:
            raise TypeError("Expected list of length >= 1, not {type} of length {length}"
                            .format(type=str(type(z)), length=len(z)))

        v_name_z = var("z" + str(len(self.data)))
        self.data[v_name_z] = z
        self.finish_plot(z=v_name_z, **kwargs)
        return


class Scatter3D(Graph):
    def __init__(self, x=None, y=None, z=None, mode="markers", div_id="scatter3d_plot", **kwargs):
        """
        :param x: List containing x-axis values
        :param y: List containing y-axis values
        :param mode: Show markers, markers+lines or lines.
        :param div_id: ID of the HTML div tag this plot will be drawn in.
        :param width: Width of plot
        :param height: Height of plot
        :param kwargs: Attributes of the scatter plot.
        """
        Graph.__init__(self, div_id=div_id)
        self.type = escape("scatter3d")

        if x and y and z:
            self.plot(x=x, y=y, z=z, mode=mode, type=self.type, **kwargs)
        return

    def plot(self, x, y, z, mode="markers", **kwargs):
        """

        :param x: List containing x-axis values
        :param y: List containing y-axis values
        :param z: List containing z-axis values
        :param mode: Show "markers", "markers+lines" or "lines". Default to "markers".
        :param kwargs: Attributes of the scatter plot.
        :return:
        """
        # Sanity check - is data in correct format?
        if str(type(x)) != "<class 'list'>" or str(type(y)) != "<class 'list'>" or str(type(z)) != "<class 'list'>" \
                or len(x) != len(y) != len(z) or len(x) == 0 or len(y) == 0 or len(z) == 0:
            raise TypeError("Expected x, y and z to be of type list of equal length > 0, not {type_x}, {type_y} and "
                            "{type_z} of lengths {len_x}, {len_y} and {len_z}"
                            .format(type_x=str(type(x)), type_y=str(type(y)), type_z=str(type(z)),
                                    len_x=str(len(x)), len_y=str(len(y)), len_z=str(len(z))))

        # Assigning names for JS variables when written to JS script.
        v_name_x = var("x" + str(len(self.data)))
        v_name_y = var("y" + str(len(self.data)))
        v_name_z = var("z" + str(len(self.data)))

        # Adding data to instance dictionary.
        self.data[v_name_x] = x
        self.data[v_name_y] = y
        self.data[v_name_z] = z

        self.finish_plot(x=v_name_x, y=v_name_y, z=v_name_z, mode=mode, **kwargs)
        return


class Sphere(Graph):
    pass


class Scatter2D(Graph):
    def __init__(self, x=None, y=None, mode="markers", div_id="scatter_plot", **kwargs):
        """
        :param x: List containing x-axis values
        :param y: List containing y-axis values
        :param mode: Show markers, markers+lines or lines.
        :param div_id: ID of the HTML div tag this plot will be drawn in.
        :param width: Width of plot
        :param height: Height of plot
        :param kwargs: Attributes of the scatter plot.
        """
        Graph.__init__(self, div_id=div_id)
        self.type = escape("scatter")

        if x and y:
            self.plot(x=x, y=y, mode=mode, type=self.type, **kwargs)

        return

    def plot(self, x, y, mode="markers", **kwargs):
        """

        :param x: List containing x-axis values
        :param y: List containing y-axis values
        :param mode: Show "markers", "markers+lines" or "lines". Default to "markers".
        :param kwargs: Attributes of the scatter plot.
        :return:
        """
        # Sanity check - is data in correct format?
        if str(type(x)) != "<class 'list'>" or str(type(y)) != "<class 'list'>" \
                or len(x) != len(y) or len(x) == 0 or len(y) == 0:
            raise TypeError("Expected both x and y to be of type list of equal length > 0, not {type_x} and {type_y}"
                            "of lengths {len_x} and {len_y}"
                            .format(type_x=str(type(x)), type_y=str(type(y)), len_x=str(len(x)), len_y=str(len(y))))

        # Assigning names for JS variables when written to JS script.
        v_name_x = var("x" + str(len(self.data)))
        v_name_y = var("y" + str(len(self.data)))

        # Adding data to instance dictionary.
        self.data[v_name_x] = x
        self.data[v_name_y] = y

        self.finish_plot(x=v_name_x, y=v_name_y, mode=mode, **kwargs)
        return


class Circle(Graph):
    pass
