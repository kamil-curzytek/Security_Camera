from objects_recording import df
from bokeh.plotting import output_file, figure, show
from bokeh.models import HoverTool, ColumnDataSource

#converting times to strings
df["Start_string"] = df["Start"].dt.strftime("%Y-%m-%d %H:%M:%S")
df["End_string"] = df["End"].dt.strftime("%Y-%m-%d %H:%M:%S")

#creating cds object 
cds = ColumnDataSource(df) 

#configuring figure/plot
p = figure(x_axis_type = 'datetime', height = 100, width = 500, sizing_mode='scale_width', title = "Motion Graph")
p.title.text_font_size = "25px"
p.yaxis.minor_tick_line_color=None
p.yaxis.ticker.desired_num_ticks=1

#adding hover tool to show details when mouse is on the graph
hover = HoverTool(tooltips=[("Start","@Start_string"), ("End","@End_string")])
p.add_tools(hover)

#defining quad graph
q = p.quad(left = "Start", right = "End", bottom = 0, top = 1, color = "green", source=cds)

output_file("Graph.html")

show(p)