import math

class Ans:
  def __init__(self, model, **args):
    # initialize the super class
    super().__init__()

    # set the independent properties
    for key, value in args.items():
      setattr(self, key, value)
  
  def model_step(self):
    pass