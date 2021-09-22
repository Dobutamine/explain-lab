import math

class ComplianceFluid:
  def __init__(self, model, **args):
    # initialize the super class
    super().__init__()
    
    # properties
    self.name = ""            # name of the compliance
    self.type = "compliance"  # type of the model component
    self.subtype = "blood"    # subtype of the model component.
    self.is_enabled = True    # determines whether or not the compliance is enabled
    self.vol = 0              # holds the volume in liters
    self.u_vol = 0            # holds the unstressed volume in liters
    self.pres = 0             # holds the transmural pressure in mmHg
    self.recoil_pressure = 0  # holds the recoil pressure in mmHg
    self.pres_outside = 0     # holds the pressure which is exerted on the compliance from the outside
    self.el_base = 1          # holds the baseline elastance
    self.el_k = 0             # holds the constant for the non-linear elastance function
    
    # set the independent properties (name, description, type, subtype, is_enabled, vol, u_vol, el_base, el_k)
    for key, value in args.items():
      setattr(self, key, value)

    # get a reference to the model
    self.model = model

  def model_step (self):
    self.calculate_pressure()
        
  def calculate_pressure (self):
    if self.is_enabled:
      # calculate the volume above the unstressed volume
      vol_above_unstressed = self.vol - self.u_vol

      # calculate the elastance, which is volume dependent in a non-linear way
      elastance = self.el_base + self.el_k * pow(vol_above_unstressed, 2)

      # calculate pressure in the compliance
      self.recoil_pressure = vol_above_unstressed * elastance

      # calculate the transmural pressure
      self.pres = self.recoil_pressure + self.pres_outside


  def volume_in (self, dvol, comp_from):
    if self.is_enabled:
      # add volume
      self.vol += dvol

      # mix the content of the compliances depending on what they contain (blood/gas)
      if self.subtype == 'blood':
        # use the blood mixing function of the blood model to mix the blood
        # self.model.models['blood'].mix_blood(self, comp_from)
        pass

      if self.subtype == 'gas':
        # use the gas mixing function of the gas model to mix the gas
        # self.model.models['gas'].mix_gas(self, comp_from)
        pass

      # guard against negative volumes (will probably never occur in this routine)
      return self.protect_mass_balance

  def volume_out (self, dvol, comp_from):
    if self.is_enabled:
      # add volume
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