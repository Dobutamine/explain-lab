import json, importlib

# import the perfomance counter module to measure the model performance
from time import perf_counter

# import the model interface module
from helpers.interface import Interface

class Engine:
  # when a model class is instantiated the model loads de normal neonate json definition by default.
  def __init__(self, filename = 'definitions/normal_neonate_24h.json'):
        
    
    # define a dictionary with all the components
    self.components = {}

    # define a variable holding the current model clock
    self.model_clock = 0

    # load and process the model definition file
    self.model_definition = self.load_csv_definition_file(filename)

    # initialize all model components with the parameters from the JSON file
    self.initialize(self.model_definition)

    # define some model performance properties
    self.step_duration = 0
    self.run_duration = 0

  def load_csv_definition_file(self, filename):
    # open the JSON file
    json_file = open(filename)
    # convert the JSON file to a python dictionary object
    properties = json.load(json_file)
    return properties
  

  # initialize all elements and models
  def initialize(self, model_definition):
    # get the model stepsize from the model definition
    self.modeling_stepsize = model_definition['modeling_stepsize']
    # get the model name from the model definition
    self.name= model_definition['name']
    # get the model description from the model definition
    self.description = model_definition['description']
    # get the set weight from the model definition
    self.weight = model_definition['weight']

    # process the definition file to find all needed model classes
    self.component_objects = {}
    for component in model_definition['components']:
      _model_type = component['model_type']
      try:
        _model_class = importlib.import_module('.' + _model_type, 'base.models')
        self.component_objects[_model_type] = getattr(_model_class, _model_type)
      except:
        print(f"{_model_type} not found in the base_models folder")

    # we now have all the properties in a dictionary and all the component objects in another dictionary
    # process the elements
    # intialize a dictionary holding all model elements
    self.components = {}
    for component in model_definition['components']:
        # initialize all the componenys
        try:
            self.components[component['name']] = self.component_objects[component['model_type']](self, **component)
        except:
            print(f"The model engine can't find the {component['model_type']} model.")
   
    # initialize the model interface
    self.io = Interface(self)

  # calculate a number of seconds
  def calculate(self, time_to_calculate):
    # calculate the number of steps needed (= time in seconds / modeling stepsize in seconds)
    no_steps = int(time_to_calculate / self.modeling_stepsize)
    
    # start the performance counter
    perf_start = perf_counter()

    # execute the model steps
    for _ in range(no_steps):
        for comp in self.components:
            self.components[comp].model_step()


        # call the user interface
        self.io.model_step(self.model_clock)

        # increase the model clock
        self.model_clock += self.modeling_stepsize


    # stop the performance counter
    perf_stop = perf_counter()

    # store the performance metrics
    self.run_duration = perf_stop - perf_start
    self.step_duration = (self.run_duration / no_steps) * 1000