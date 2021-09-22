import math

class TimeVaryingElastanceFluid:
  def __init__(self, model, **args):
    # initialize the super class
    super().__init__()
    
    # properties
    self.name = ""                        # name of the compliance
    self.type = "time_varying_elastance"  # type of the model component
    self.subtype = "blood"                # subtype of the model component.
    self.is_enabled = True                # determines whether or not the compliance is enabled
    self.vol = 0                          # holds the volume in liters
    self.u_vol = 0                        # holds the unstressed volume in liters
    self.pres = 0                         # holds the transmural pressure in mmHg
    self.recoil_pressure = 0              # holds the recoil pressure in mmHg
    self.pres_outside = 0                 # holds the pressure which is exerted on the compliance from the outside
    self.el_min = 1                       # holds the minimal elastance
    self.el_max = 1                       # holds the maximal elastance
    self.varying_elastance_factor = 0     # holds the varying elastance factor
    self.el_k = 0                         # holds the constant for the non-linear elastance function
    
    # set the independent properties (name, description, type, subtype, is_enabled, vol, u_vol, el_min, el_max, el_k)
    for key, value in args.items():
      setattr(self, key, value)


  def model_step(self):
    self.calculate_pressure()
    
  def calculate_pressure (self):
    if self.is_enabled:
      # calculate the volume above the unstressed volume
      vol_above_unstressed = self.vol - self.u_vol

      # calculate the elastance, which is volume dependent in a non-linear way and dependent on the varying elastance factor
      elastance = self.el_min + ((self.el_max - self.el_min) * self.varying_elastance_factor) + self.el_k * pow(vol_above_unstressed, 2)

      # calculate pressure the recoil pressure
      self.recoil_pressure = vol_above_unstressed * elastance

      # calculate the transmural pressure
      self.pres = self.recoil_pressure + self.pres_outside

  def volume_in (self, dvol, comp_from):
    if self.is_enabled:
      # change volume
      self.vol += dvol

      # guard against negative volumes (will probably never occur in this routine)
      return self.protect_mass_balance

  def volume_out (self, dvol, comp_from):
    if self.is_enabled:
      # change volume
      self.vol -= dvol

      # guard against negative volumes (will probably never occur in this routine)
      return self.protect_mass_balance
      
  def protect_mass_balance (self):
    if (self.vol < 0):
      # if there's a negative volume it might corrupt the mass balance of the model so we have to return the amount of volume which could not be displaced to the caller of this function
      _nondisplaced_volume = -self.vol
      # set the current volume to zero
      self.vol = 0
      # return the amount volume which could not be removed
      return _nondisplaced_volume
    else:
      # massbalance is guaranteed
      return 0