import math

class Ecg:
  def __init__(self, model, **args):
    # initialize the super class
    super().__init__()

    # state properties (accessible from outside)
    self.heart_rate = 0
    self.pq_time = 0
    self.qrs_time = 0
    self.qt_time = 0
    self.cqt_time = 0.3
    self.ncc_atrial = 0
    self.ncc_ventricular = -1
    self.measured_heart_rate = 0
    self.ecg_signal = 0

    # local state properties
    self._sa_node_period = 0
    self._sa_node_counter = 0
    self._pq_running = False
    self._pq_time_counter = 0
    self._qrs_running = False
    self._qrs_time_counter = 0
    self._qt_running = False
    self._ventricle_is_refractory = False
    self._qt_time_counter = 0
    self._measured_hr_time_counter = 0
    self._measured_qrs_counter = 0
    self._p_wave_signal_counter = 0
    self._qrs_wave_signal_counter = 0
    self._t_wave_signal_counter = 0

    # set the independent properties
    for key, value in args.items():
      setattr(self, key, value)

    # store a reference to the rest of the model
    self.model = model

    # get the modeling stepsize from the model
    self._t = model.modeling_stepsize

  def model_step(self):
    if (self.is_enabled):
      self.model_cycle()

  def model_cycle(self):
        # calculate the correct qt time
        self.cqt_time = self.qtc() - self.qrs_time

        # calculate the sa_node_time in seconds depending on the heart_rate
        if self.heart_rate > 0:
            self._sa_node_period = 60 / self.heart_rate
        else:
            self._sa_node_period = 60

        # has the sa node period elapsed?
        if self._sa_node_counter > self._sa_node_period:
            # reset the sa node time counter
            self._sa_node_counter = 0
            # signal that the pq time starts running
            self._pq_running = True
            # reset atrial activation function factor
            self.ncc_atrial = -1

        # has the pq time elapsed?
        if self._pq_time_counter > self.pq_time:
            # reset the pq time counter
            self._pq_time_counter = 0
            # signal that the pq time counter has stopped
            self._pq_running = False
            # check whether the ventricles are not refractory to another depolarisation
            if self._ventricle_is_refractory == False:
                # signal that the qrs time starts running
                self._qrs_running = True
                # reset the ventricular activation function factor
                self.ncc_ventricular = -1
                # increase the measured qrs counter with 1 beat
                self._measured_qrs_counter += 1

        # has the qrs time elapsed?
        if self._qrs_time_counter > self.qrs_time:
            # reset the qrs time counter
            self._qrs_time_counter = 0
            # reset the ecg signal to zero
            self.ecg_signal = 0
            # signal that the qrs time counter has stopped
            self._qrs_running = False
            # signal that the qt time starts running
            self._qt_running = True
            # signal that the ventricles are going into the refractory state
            self._ventricle_is_refractory = True

        # has the qt time elapsed?
        if self._qt_time_counter > self.cqt_time:
            # reset the qt time counter
            self._qt_time_counter = 0
            # signal that the qt time counter has stopped
            self._qt_running = False
            # signal that the ventricles are no longer in a refractory state
            self._ventricle_is_refractory = False

        # increase the ecg timers
        # the sa node timer is always running
        self._sa_node_counter += self._t
        # increase the pq time counter if pq time is running
        if self._pq_running:
            self._pq_time_counter += self._t
            # increase the p wave signal counter
            self._p_wave_signal_counter += 1
            # build the p wave
            self.buildDynamicPWave()
        else:
            # reset the p wave signal counter if pq is not running
            self._p_wave_signal_counter = 0

        # increase the qrs time counter if qrs time is running
        if self._qrs_running:
            self._qrs_time_counter += self._t
            # increase the qrs wave signal counter
            self._qrs_wave_signal_counter += 1
            # build the qrs wave
            self.buildQRSWave()
        else:
            # reset the qrs wave signal counter if qrs is not running
            self._qrs_wave_signal_counter = 0

        # increase the qt time counter if qt time is running
        if self._qt_running:
            self._qt_time_counter += self._t
            # increase the t wave signal counter
            self._t_wave_signal_counter += 1
            # build the t wave
            self.buildDynamicTWave()
        else:
            # reset the t wave signal counter if qt is not running
            self._t_wave_signal_counter = 0

        # if nothing is running, so there's no electrical activity then reset the ecg signal
        if self._qt_running == False and self._qrs_running == False and self._qt_running == False:
            self.ecg_signal = 0

        # calculate the measured heart_rate based on the ventricular rate every 5 seconds
        if self._measured_hr_time_counter > 5:
            self.measured_heart_rate = 60.0 / (self._measured_hr_time_counter / self._measured_qrs_counter)
            self._measured_qrs_counter = 0
            self._measured_hr_time_counter = 0
        
        # increase the time counter for measured heart_rate routine
        self._measured_hr_time_counter += self._t

        # increase the contraction timers
        self.ncc_atrial += 1
        self.ncc_ventricular += 1

  def qtc(self):
        # calculate the heart rate correct qt time
        if self.heart_rate > 10:
            return self.qt_time * math.sqrt(60.0 / self.heart_rate)
        else:
            return self.qt_time * math.sqrt(60.0 / 10.0)

  def buildDynamicPWave(self):
        pass

  def buildQRSWave(self):
        pass

  def buildDynamicTWave(self):
        pass