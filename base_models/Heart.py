import math

class Heart:
  def __init__(self, model, **args):
    # initialize the super class
    super().__init__()

    # set the independent properties
    for key, value in args.items():
      setattr(self, key, value)

    # dependent properties (accessible from outside)
    self.aaf = 0.0
    self.vaf = 0.0

    # store a reference to the rest of the model
    self.model = model

    # get the modeling stepsize from the model
    self._t = model.modeling_stepsize

  def model_step(self):
    if (self.is_enabled):
      self.model_cycle()

  def model_cycle(self):
    self.ecg_model = self.model.components['ecg']

    # get the relevant timings from the ecg model
    ncc_atrial = self.ecg_model.ncc_atrial
    atrial_duration = self.ecg_model.pq_time
    ncc_ventricular = self.ecg_model.ncc_ventricular
    ventricular_duration = self.ecg_model.cqt_time + self.ecg_model.qrs_time

    # varying elastance activation function of the atria
    if ncc_atrial >= 0 and (ncc_atrial < atrial_duration / self._t):

      s = math.sin((ncc_atrial * self._t * math.pi) /  atrial_duration)
      self.aaf = math.sin((ncc_atrial * self._t * math.pi) / atrial_duration - s / self.a)
      
    else:
      self.aaf = 0

    # varying elastance activation function of the ventricles
    if ncc_ventricular >= 0 and (ncc_ventricular < ventricular_duration / self._t):

      s = math.sin((ncc_ventricular * self._t * math.pi) /  ventricular_duration)
      self.vaf = math.sin((ncc_ventricular * self._t * math.pi) / ventricular_duration - s / self.a)

    else:
      self.vaf = 0

    # transfer the activation function to the heart compartments
    self.model.components['RA'].varying_elastance_factor = self.aaf
    self.model.components['RV'].varying_elastance_factor = self.vaf
    self.model.components['LA'].varying_elastance_factor = self.aaf
    self.model.components['LV'].varying_elastance_factor = self.vaf
  