import pandas as pd
import numpy as np
from math import pi

import squarify
import plotly.plotly as py
import plotly.graph_objs as go


from bokeh.layouts import column,row
from bokeh.models import Button,Select,RangeSlider,DataTable,TableColumn,RadioGroup,CheckboxGroup,Div,Markup
from bokeh.plotting import figure, curdoc
from bokeh.io import output_file, show ,output_notebook
from bokeh.transform import cumsum,factor_cmap
from bokeh.models import ColumnDataSource,FactorRange
from bokeh.models.widgets import Paragraph

# Create pandas Data Frame from CSV file
df = pd.read_csv('student-por.csv')

##########################################################################################################

# Create Pie Chart to display the Gender Frequency of the Students
pie_data = df.groupby('sex').size().reset_index(name='count')
angle = pie_data['count']/pie_data['count'].sum() * 2*pi
color = ['cyan','lightgreen']
sex = ['M','F']
pie_chart = figure(title="Gender(Male Vs Female)", toolbar_location='right',
            x_range=(-0.5, 1.0))
        
columnData = ColumnDataSource(data= dict(angle=angle,color = color,sex=sex,data = pie_data))

checkbox_group = CheckboxGroup(
        labels=["GP", "MS"], active=[0, 1])

def updatepie(attr,old,new):    
    if len(new) == 1:
        print(new[0])
        if new[0] == 0:
            tempData = df[(df['school']== 'GP')]
            pie_data = tempData.groupby('sex').size().reset_index(name='count')
            angle = pie_data['count']/pie_data['count'].sum() * 2*pi
            columnData.data['angle'] = angle
            columnData.data['data'] = pie_data
            print(new[0])
        elif new[0] == 1:
            tempData = df[(df['school']== 'MS')]
            pie_data = tempData.groupby('sex').size().reset_index(name='count')
            angle = pie_data['count']/pie_data['count'].sum() * 2*pi
            columnData.data['angle'] = angle
            columnData.data['data'] = pie_data
            print(new[0])
        
    

checkbox_group.on_change('active', updatepie)

pie_chart.wedge(x=0, y=1, radius=0.4, start_angle=cumsum('angle', include_zero=True), 
               end_angle=cumsum('angle'),
        line_color="white", fill_color='color', legend='sex', source=columnData)
pie_chart.axis.axis_label=None
pie_chart.axis.visible=False
pie_chart.grid.grid_line_color = None
col2 = column(checkbox_group,pie_chart)
##########################################################################################################

# Create Stacked Bar Chart
dataG3 = df.groupby(['G3','sex']).size().reset_index(name='counts')
dfG3 = df.G3.unique().tolist()
dfG3.sort()


G3 = []

for val in dfG3:
    G3.append(str (val))
    
male = []
female = []

for val in dfG3:
    females = dataG3[(dataG3['G3']== val) & (dataG3['sex']== 'F')]
    males = dataG3[(dataG3['G3']== val) & (dataG3['sex']== 'M')]
    if males.empty:
        male.append(0)
    else:
        male.append(males['counts'].iloc[0])
    if females.empty:
        female.append(0)
    else:
        female.append(females['counts'].iloc[0])
sex = ['M', 'F']
dataSource = {'Grade': G3,
              'M': male,
              'F': female 
             }
palette = ["#c9d9d3", "#718dbf"]

x = [ (G, s) for G in G3 for s in sex ]

counts = sum(zip(dataSource['M'], dataSource['F']), ())

source = ColumnDataSource(data=dict(x=x, counts=counts))

stacked_bar = figure(x_range=FactorRange(*x), plot_width=800, title="Grade Counts by Sex",
           toolbar_location='right')

stacked_bar.vbar(x='x', top='counts', width=1, source=source, line_color="white",
       fill_color=factor_cmap('x', palette=palette, factors=sex, start=1, end=2))

stacked_bar.y_range.start = 0
stacked_bar.x_range.range_padding = 0.1
stacked_bar.xaxis.major_label_orientation = 1
stacked_bar.xgrid.grid_line_color = None
##########################################################################################################

#Create the bar chart for Alcohol Frquency range
dalco = df.groupby('Dalc').size().reset_index(name='counts')

x = dalco['Dalc'].apply(str).tolist()
y = dalco['counts'].tolist()

bar = figure(x_range=x, title="Alcohol consumption per day",
           toolbar_location='right')
bar.xaxis.axis_label = 'Quantity of Alcohol'
bar.yaxis.axis_label = 'Count'

bar.vbar(x=x, top=y, width=0.9)

bar.xgrid.grid_line_color = None
bar.y_range.start = 0
##########################################################################################################

N = df.shape[0]
x = df['traveltime']
y = df['G3']
radii = np.random.random(size=N)

source = ColumnDataSource(data=dict(x=x, y=y,data=df))

colors = [
    "#%02x%02x%02x" % (int(r), int(g), 150) for r, g in zip(50+2*x, 30+2*y)
]

TOOLS="hover,crosshair,pan,wheel_zoom,zoom_in,zoom_out,box_zoom"

p = figure(tools=TOOLS,  title="Grade Variation based on the Studytime , Travel time , Absences")

p.scatter('x', 'y',source =source,line_width=3, line_alpha=0.6)          

p.xaxis.axis_label = 'Grade'
p.yaxis.axis_label = 'traveltime'
                   
select = Select(title="Select Field:", 
                value="traveltime", 
                options=["studytime", "traveltime","absences"])

def select_callback(attr,old,new):
    source.data['y'] = df[new]
    p.yaxis.axis_label = new

select.on_change('value',select_callback)
##########################################################################################################

source1 = ColumnDataSource(data=dict())

slider = RangeSlider(title="Grade", start=0, end=20, value=(0, 20), step=1, format="0,0")
slider.on_change('value', lambda attr, old, new: update())

def update():
    current = df[(df['G3'] >= slider.value[0]) & (df['G3'] <= slider.value[1])].dropna()
    source1.data = {
        'school' : current.school,
        'sex'    : current.sex,
        'age'    : current.age,
        'G3'     : current.G3
    }

columns = [
    TableColumn(field="school", title="School Name"),
    TableColumn(field="sex", title="Gender"),
    TableColumn(field="age", title="Age (years)"),
    TableColumn(field="G3", title="Grade")
]

update()
data_table = DataTable(source=source1, columns=columns,width=1000)
##########################################################################################################
#Create Chart for displaying the Frquency of Reason

radio_group = RadioGroup(
        labels=["GP", "MS"], active=0)


tempData = df[(df['school']== 'GP')]
dfReason = tempData.groupby('reason').size().reset_index(name='counts')        
x1 = dfReason['reason']
y1 = dfReason['counts']

dataSource = ColumnDataSource(data=dict(x1=x1,y1=y1,data=dfReason))

def make_plot(attr,old,new):
    if new == 0:
        tempData = df[(df['school']== 'GP')]
        dfReason = tempData.groupby('reason').size().reset_index(name='counts')
        dataSource.data['x1'] = dfReason['reason']
        dataSource.data['y1'] = dfReason['counts']
        dataSource.data['data'] = dfReason
    elif new == 1:
        tempData = df[(df['school']== 'MS')]        
        dfReason = tempData.groupby('reason').size().reset_index(name='counts')      
        dataSource.data['x1'] = dfReason['reason']
        dataSource.data['y1'] = dfReason['counts']
        dataSource.data['data'] = dfReason

Reason_bar = figure(x_range= x1, title="Reason Count",
            toolbar_location='right')
Reason_bar.vbar(x='x1',top='y1', source = dataSource, width=0.9)
Reason_bar.xgrid.grid_line_color = None
Reason_bar.y_range.start = 0
Reason_bar.xaxis.axis_label = "Reason"
Reason_bar.yaxis.axis_label = "Count"
radio_group.on_change('active', make_plot) 

col1 = column(radio_group,Reason_bar)
##########################################################################################################
div = Div(text="""Student Performance Analysis""",
width=1000, height=40)

markup = Markup( text="""<p>Student Grade depends on Study hours, Travel Time</p>""")

para = Paragraph(text="""Why Bokeh Library:
We have choosen Python Programming language because there are more interaction techniques are available with different libraries. From this We used Bokeh,Matplotlib and  Seaborn which gives us the clear view for our idea. We started with R programming(R shiny) and some of the python libraries like Plotly,Dash etc . 
Here, we found a problem while executing the process. So we have gone through with Bokeh package with the Dashboard.

INTERACTIVE FUNCTIONS:
sliders
Radiobutton
zoom in and out
dropdown list
hovering
crosshair""",
width=800, height=100)

row1 = row(div)
row2 = row(slider,data_table)
row3 = row(col2,stacked_bar)
row4 = row(bar,column(select,p))
row5 = row(para)
##########################################################################################################

# put the button and plot in a layout and add to the document

curdoc().add_root(column(row1,row2,row3,row4,row5))
curdoc().title = "Student Performance Analysis"