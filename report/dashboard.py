from fasthtml.common import *
import matplotlib.pylab as plt
from matplotlib import colormaps
import matplotlib.pyplot
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import numpy as np
import pandas as pd

# Import QueryBase, Employee, Team from employee_events
from employee_events import QueryBase, Employee, Team

# import the load_model function from the utils.py file
from utils import load_model

"""
Below, we import the parent classes
used for subclassing
"""
from base_components import (
    Dropdown,
    BaseComponent,
    Radio,
    MatplotlibViz,
    DataTable
    )

from combined_components import FormGroup, CombinedComponent


# Create a subclass of base_components/dropdown
# called `ReportDropdown`
class ReportDropdown(Dropdown):
    
    # Overwrite the build_component method
    # ensuring it has the same parameters
    # as the Report parent class's method
    def build_component(self, entity_id, model):
        
        #  Set the `label` attribute so it is set
        #  to the `name` attribute for the model
        self.label = model.name.title()
        
        # Return the output from the
        # parent class's build_component method
        return super().build_component(entity_id, model)
    
    # Overwrite the `component_data` method
    # Ensure the method uses the same parameters
    # as the parent class method
    def component_data(self, entity_id, model):
        
        # Using the model argument
        # call the employee_events method
        # that returns the user-type's
        # names and ids
        return model.names() # returns a list of tuples containing the employee/team names and id's
        

# Create a subclass of base_components/BaseComponent
# called `Header`
class Header(BaseComponent):

    # Overwrite the `build_component` method
    # Ensure the method has the same parameters
    # as the parent class
    def build_component(self, entity_id, model):
                
        # Using the model argument for this method
        # return a fasthtml H1 objects
        # containing the model's name attribute
        return H1(f'{model.name.title()} Performance', cls='container')
          

# Create a subclass of base_components/MatplotlibViz
# called `LineChart`
class LineChart(MatplotlibViz):
    
    # Overwrite the parent class's `visualization`
    # method. Use the same parameters as the parent
    def visualization(self, entity_id, model):
        
        # Pass the `asset_id` {entity_id rather ??} argument to
        # the model's `event_counts` method to
        # receive the x (Day) and y (event count)
        df_EventCounts = model.event_counts(entity_id)
        
        # Use the pandas .fillna method to fill nulls with 0
        df_EventCounts.fillna(0, inplace=True)
        
        # User the pandas .set_index method to set
        # the date column as the index
        df_EventCounts.set_index('event_date', inplace=True) # do we need to convert to datetime ?
        
        # Sort the index
        df_EventCounts.sort_index(inplace = True) # will sort in ascending manner
        
        # Use the .cumsum method to change the data
        # in the dataframe to cumulative counts
        df_EventCounts = df_EventCounts.cumsum()
        
        
        # Set the dataframe columns to the list
        # ['Positive', 'Negative']
        df_EventCounts.columns = ['Positive', 'Negative']
        
        # Initialize a pandas subplot
        # and assign the figure and axis
        # to variables
        fig, ax = plt.subplots(figsize=(12,9))


        # To add a color scale/intensity to the visualisation:
        # create and choose a colormap (eg: 'viridis', 'RdYlGn', 'coolwarm')
        cmap = colormaps.get_cmap('coolwarm')
        
        # plot lines using colors from the color map
        df_EventCounts['Positive'].plot(ax=ax, color=cmap(0.8), label='Positive')
        df_EventCounts['Negative'].plot(ax=ax, color=cmap(0.2), label='Negative')
        
        # create a ScalarMapable to generate the colorbar
        # Normalise defines the data range the color scale represents
        norm = mcolors.Normalize(vmin = df_EventCounts.min().min(), vmax=df_EventCounts.max().max())
        sm = cm.ScalarMappable(cmap=cmap, norm = norm)
        sm.set_array([]) #required for matplotlib to link data to the bar

        # add color bar to figure
        cbar = fig.colorbar(sm, ax=ax)
        cbar.set_label('Cumulative Count Intensity', rotation=270, labelpad=15)

        # pass the axis variable
        # to the `.set_axis_styling`
        # method
        # Use keyword arguments to set 
        # the border color and font color to black. 
        # Reference the base_components/matplotlib_viz file 
        # to inspect the supported keyword arguments
        self.set_axis_styling(ax, bordercolor='black', fontcolor='black')
        
        # Set title and labels for x and y axis
        ax.set_title(f'{model.name.title()} Cumulative Events', fontsize=20, pad = 20)
        ax.set_xlabel('Event Date', fontsize = 12)
        ax.set_ylabel('Event Count', fontsize = 12)
        ax.legend()


# Create a subclass of base_components/MatplotlibViz
# called `BarChart`
class BarChart(MatplotlibViz):

    # Create a `predictor` class attribute
    # assign the attribute to the output
    # of the `load_model` utils function
    predictor = load_model()

    # Overwrite the parent class `visualization` method
    # Use the same parameters as the parent
    def visualization(self, entity_id, model):
        
        # Using the model and asset_id {'entity_id ?} arguments
        # pass the `asset_id` to the `.model_data` method
        # to receive the data that can be passed to the machine
        # learning model
        df_modelData = model.model_data(entity_id)
        
        # Using the predictor class attribute
        # pass the data to the `predict_proba` method
        probablilities = self.predictor.predict_proba(df_modelData)
        
        # Index the second column of predict_proba output
        # The shape should be (<number of records>, 1)
        prob_positive_class = probablilities[:,[1]] # change the single column to a 2D array format which sckit-learn needs for futher processing
        #prob_positive_class = probablilities[:,1].reshape(-1,1) # can also use this method to do the line above        
        
        # Below, create a `pred` variable set to
        # the number we want to visualize
        #
        # If the model's name attribute is "team"
        # We want to visualize the mean of the predict_proba output
        pred = None

        if model.name == 'team':
              pred = prob_positive_class.mean()

        # Otherwise set `pred` to the first value
        # of the predict_proba output
        else:
            pred = prob_positive_class[0,0] # ensure we select the first value from the 2D array to pass into ax.barh which needs a 1D scalar
        
        # Initialize a matplotlib subplot
        fig, ax = plt.subplots(figsize=(12,9))
        
        # To add a color scale/intensity to the plot:
        # Setup the Color Scale
        # 'RdYlGn_r' goes from Green (low risk) to Red (high risk)
        cmap = colormaps.get_cmap('RdYlGn_r')
        norm = mcolors.Normalize(vmin=0, vmax=1)
        bar_color = cmap(norm(pred)) # Pick the specific color for our prediction value

        # Plot the bar with the dynamic color
        ax.barh([''], [pred], color=bar_color, edgecolor='black', height=0.6)

        #Add the Colorbar (The Visual Scale)
        sm = cm.ScalarMappable(cmap=cmap, norm=norm)
        sm.set_array([])
        cbar = fig.colorbar(sm, ax=ax, orientation='vertical', pad=0.05)
        cbar.set_label('Risk Level (0 = Low, 1 = High)', fontsize=12)

        # Run the following code unchanged
        ax.set_xlim(0, 1)
        ax.set_title('Predicted Recruitment Risk', fontsize=20, pad=20)
        
        # pass the axis variable
        # to the `.set_axis_styling` method
        self.set_axis_styling(ax = ax, bordercolor='black', fontcolor='black')

        # Add a text label on the bar showing the exact percentage
        ax.text(pred + 0.01, 0, f'{pred:.2%}', va='center', fontsize=14, fontweight='bold')

 
# Create a subclass of combined_components/CombinedComponent
# called Visualizations       
class Visualizations(CombinedComponent):
    
    # Set the `children`
    # class attribute to a list
    # containing an initialized
    # instance of `LineChart` and `BarChart`
    children = [LineChart(), BarChart()]

    # Leave this line unchanged
    outer_div_type = Div(cls='grid')
            
# Create a subclass of base_components/DataTable
# called `NotesTable`
class NotesTable(DataTable):

    # Overwrite the `component_data` method
    # using the same parameters as the parent class
    def component_data(self, entity_id, model):
        """
        Returns a Pandas DataFrame of the 'notes' table containing notes about employees and teams

        """         
        # Using the model and entity_id arguments
        # pass the entity_id to the model's .notes 
        # method. Return the output
        return model.notes(entity_id).sort_values(by='note_date', ascending=False)
    

class DashboardFilters(FormGroup):

    id = "top-filters"          # id, action and method defined for the HTML form (**div_args for the form)
    action = "/update_data"
    method="POST"

    children = [
        Radio(
            values=["Employee", "Team"],
            name='profile_type',
            hx_get='/update_dropdown',
            hx_target='#selector'
            ),
        ReportDropdown(
            id="selector",
            name="user-selection")
        ]
    
    outer_div_type = Div(cls='grid')
    
# Create a subclass of CombinedComponents
# called `Report`
class Report(CombinedComponent):

    # Set the `children`
    # class attribute to a list
    # containing initialized instances 
    # of the header, dashboard filters,
    # data visualizations, and notes table
    children = [
        Header(), 
        DashboardFilters(),
        Visualizations(),
        NotesTable(),
    ]

# Initialize a fasthtml app 
app, route = fast_app()

# Initialize the `Report` class
report = Report()


# Create a route for a get request
# Set the route's path to the root
@route("/")
def get():

    # Call the initialized report
    # pass the integer 1 and an instance
    # of the Employee class as arguments
    # Return the result
    return report(1, Employee())

# Create a route for a get request
# Set the route's path to receive a request
# for an employee ID so `/employee/2`
# will return the page for the employee with
# an ID of `2`. 
# parameterize the employee ID 
# to a string datatype
@route('/employee/{id}')
def get(id:str):

    # Call the initialized report
    # pass the ID and an instance
    # of the Employee SQL class as arguments
    # Return the result
    return report(id, Employee())

# Create a route for a get request
# Set the route's path to receive a request
# for a team ID so `/team/2`
# will return the page for the team with
# an ID of `2`. 
# parameterize the team ID 
# to a string datatype
@route('/team/{id}')
def get(id:str):
    
    # Call the initialized report
    # pass the id and an instance
    # of the Team SQL class as arguments
    # Return the result
   return report(id, Team())


# Keep the below code unchanged!
@app.get('/update_dropdown{r}')
def update_dropdown(r):
    
    dropdown = DashboardFilters.children[1] # refering to the ReportDropdown in the children of Dashboard filters
    print('PARAM', r.query_params['profile_type'])
    if r.query_params['profile_type'] == 'Team':
        return dropdown(None, Team())
    elif r.query_params['profile_type'] == 'Employee':
        return dropdown(None, Employee())


@app.post('/update_data')
async def update_data(r):
    from fasthtml.common import RedirectResponse
    data = await r.form()
    profile_type = data._dict['profile_type']
    id = data._dict['user-selection']
    if profile_type == 'Employee':
        return RedirectResponse(f"/employee/{id}", status_code=303)
    elif profile_type == 'Team':
        return RedirectResponse(f"/team/{id}", status_code=303)
    


serve()
