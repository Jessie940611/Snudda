import os
import re
import numpy as np
import h5py
import scipy
import scipy.optimize
import matplotlib.pyplot as plt
import matplotlib
import neuron
import json
import copy
import time

# TODO 2020-10-19
#
# We need to make sure params contains the nmda_ratio and other parameters
# that are important for mod file (but not optimised for at this stage)
# Please fix.
#
#
# python3 OptimiseSynapsesFull.py DATA/Yvonne2020/M1RH-ipsi_MSN_D1_20Hz_depressing.json --synapseParameters ../data/synapses/v3/M1RH-ipsi_D1-MSN.json --st glut
#
#
# TODO 2020-10-09
#
# We are no longer reading data from Yvonne's HDF5 directly, instead we are
# reading data from a JSON file, that Ilaria created from Igor exports.
#
# Consequences and TODO:
# - We no longer need CellID to identify which cell we are optmising,
#   each JSON file only contains one dataset (and it is an averaged dataset)
# - Holding voltage is no longer extractable from data, we need to set it
# - Create a JSON optmisation parameter file which contains the holding voltage
#   to be used, as well as the modelbounds (currently in getModelBounds)
# - The JSON data is now loaded into self.data, go through all functions
#   remove references to CellID, and extract the data directly from the
#   self.data variable.
#
#

# TODO 2020-07-15
#
# Make it so that the code can run in serial mode also, to simplify debugging
#

#
# TODO 2020-07-02
# -- We just wrote parallelOptimiseSingleCell -- need to make sure we call it
#    the function will optimise one cellID, using all workers available
#    need to debug the code, to make sure it works... have fun! :)
#

#
# TODO 2020-06-16
# -- We need to make sure one neuron can be optimised by all workers
#    collectively, right now one worker does one cell alone
#
# -- Determine synapse locations, pass it to all workers
# -- Best random is easy to parallelise, just do the work, then gather it at
#    the master node.
# -- Difficult: How to parallise scipy.optimize.minimize
#    Possible idea: let func to optimize handle vectors, and then each
#    position in vector is sent to one worker.

#
#
# TODO (depricated):
# 1. Remove the old soma optimisation code, not needed anymore
# 2. Place the inital synapses, then find out the sectionID,X,
# 3. Pass sectionID, sectionX to all workers, so they use same synapselocations
# 4. Optimise.
#

# !!! Add check that if the voltage is 0 or 5, then the trace is skipped entirely

from run_synapse_run import RunSynapseRun


############################################################################

# JSON can not handle numpy arrays or numpy ints/floats, fix with a
# custom serialiser


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        print("NumpyEncoder: " + str(type(obj)))

        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            # return super(NumpyEncoder, self).default(obj)
            return json.JSONEncoder.default(self, obj)


############################################################################

class OptimiseSynapsesFull(object):

    ############################################################################

    # optMethod not used anymore, potentially allow user to set sobol or refine

    # datafile is JSON file from Ilaria's Igor extraction

    def __init__(self, datafile, synapse_type="glut", load_cache=True,
                 role="master", d_view=None, verbose=True, log_file_name=None,
                 opt_method="sobol", pretty_plot=False,
                 model_bounds="model_bounds.json",
                 neuron_set_file="neuronSet.json",
                 synapse_parameter_file=None):

        # Parallel execution role, "master" or "servant"
        self.role = role

        self.parallel_setup_flag = False  # Set to True when servants are done setup
        self.d_view = d_view
        self.verbose = verbose
        self.log_file_name = log_file_name
        self.opt_method = opt_method
        self.num_smoothing = 200  # How many smoothing points do we use?
        self.sim_time = 1.8
        self.neuron_set_file = neuron_set_file

        self.debug_pars_flag = False
        self.debug_pars = []
        self.cell_properties = None

        self.pretty_plot = pretty_plot

        print("Init optMethod = " + str(opt_method))

        if self.log_file_name is not None and len(self.log_file_name) > 0:
            print("Log file: " + self.log_file_name)
            self.log_file = open(self.log_file_name, 'w')
        else:
            self.log_file = None

        self.fig_resolution = 300

        self.datafile = datafile

        self.write_log("Loading " + str(datafile))
        with open(datafile, "r") as f:
            self.data = json.load(f)

            self.volt = np.array(self.data["data"]["mean_norm_trace"])
            self.sample_freq = self.data["metadata"]["sample_freq"]

            dt = 1 / self.sample_freq
            self.time = 0 + dt * np.arange(0, len(self.volt))

            self.stim_time = np.array(self.data["metadata"]["stim_time"]) * 1e-3  # ms

            self.cell_type = self.data["metadata"]["cell_type"]

        self.synapse_parameter_file = synapse_parameter_file

        if synapse_parameter_file:
            with open(synapse_parameter_file, 'r') as f:
                print(f"Reading synapse parameters from {synapse_parameter_file}")
                tmp = json.load(f)
                self.synapse_parameters = tmp["data"]
        else:
            self.synapse_parameters = {}

        self.cache_file_name = str(self.datafile) + "-parameters-full.json"
        self.load_cache = load_cache
        self.synapse_type = synapse_type

        self.rsr_synapse_model = None
        self.rsr_delta_model = None

        self.model_info = None

        with open(model_bounds, 'r') as f:
            print(f"Loading model bounds from {model_bounds}")
            self.model_bounds = json.load(f)

        if load_cache:
            self.load_parameter_cache()
        else:
            self.parameter_cache = dict([])

        if self.role == "master":
            self.setup_parallel(d_view=d_view)

    ############################################################################

    def __delete__(self):

        if self.hFile is not None:
            self.hFile.close()

        # Save the parameter cache before closing
        self.save_parameter_cache()

        if self.log_file is not None:
            self.log_file.close()
            self.log_file = None

    ############################################################################

    def save_parameter_cache(self):

        if self.role != "master":
            self.write_log("No servants are allowed to write output to json, ignoring call.")
            return

        self.write_log("Saving parameters to cache file: " + str(self.cache_file_name))

        try:
            with open(self.cache_file_name, "w") as f:
                json.dump(self.parameter_cache, f, indent=2, cls=NumpyEncoder)
                f.close()
        except:
            import traceback
            tstr = traceback.format_exc()
            self.write_log(tstr)

            self.write_log("Failed to save cache file ... " + str(self.cache_file_name))

    ############################################################################

    def load_parameter_cache(self):

        if os.path.exists(self.cache_file_name):
            try:
                self.write_log("Loading cache file " + str(self.cache_file_name))
                with open(self.cache_file_name, "r") as f:
                    tmp_dict = json.load(f)

                    self.parameter_cache = dict([])
                    for k in tmp_dict:
                        self.parameter_cache[int(k)] = tmp_dict[k]

                    f.close()
            except:
                import traceback
                tstr = traceback.format_exc()
                self.write_log(tstr)

                self.write_log("Unable to open " + str(self.cache_file_name))
                self.parameter_cache = dict([])
        else:
            # No cache file to load, create empty dictionary
            self.parameter_cache = dict([])

    ############################################################################

    def add_parameter_cache(self, name, value):

        self.parameter_cache[name] = value

    ############################################################################

    def get_parameter_cache(self, name):

        if name in self.parameter_cache:
            return self.parameter_cache[name]
        else:
            return None

    ############################################################################

    def get_cell_type(self, cell_id):

        # If the text is byte encoded, decode it first
        all_cell_types = [x if type(x) != bytes else x.decode() for x in self.getData("w_cell").flatten()]

        return all_cell_types[cell_id]

    ############################################################################

    def get_cell_id(self, data_type, cell_type):

        # If the text is byte encoded, decode it first
        all_cell_types = [x if type(x) != bytes else x.decode() for x in self.getData("w_cell").flatten()]

        # Just a check that our assumption on the ID is correct
        # tmp = self.getData("w_num").astype(int)
        # assert (tmp == np.arange(0,len(tmp)+1)).all(), "Numering mis-match!"

        cell_id_s = [x for x, y in enumerate(all_cell_types) if cell_type.lower() in y.lower()]

        valid_id_s = self.get_valid_cell_id(data_type)

        valid_cell_id_s = np.array(list(set(cell_id_s).intersection(valid_id_s)))

        return valid_cell_id_s

    ############################################################################

    def get_all_cell_id(self):

        return np.arange(0, len(self.getData("w_cell").flatten()), dtype=int)

    ############################################################################

    def get_valid_cell_id(self, data_type):

        all_idx = self.get_all_cell_id()

        helper = lambda x: self.checkValidData(data_type, x)
        valid_flag = [x for x in map(helper, all_idx)]

        self.write_log("Valid data: " + str(sum(valid_flag)))

        return all_idx[valid_flag]

    ############################################################################

    def get_user_id(self, id_string, data_type=None):

        id_list = [int(x) for x in id_string.split(",")]

        if data_type is not None:
            valid_id = self.get_valid_cell_id(data_type)
            valid_id_list = [x for x in id_list if x in valid_id]
            return valid_id_list

        else:
            return id_list

    ############################################################################

    # parDict is the parameters that are associated with cellID

    def plot_data(self,
                  params=None,
                  show=True,
                  skip_time=0.3,
                  pretty_plot=None):

        if params is None:
            params = self.synapse_parameters

        if pretty_plot is None:
            pretty_plot = self.pretty_plot

        if pretty_plot:
            matplotlib.rcParams.update({'font.size': 24})
        else:
            matplotlib.rcParams.update({'font.size': 5})

        if self.volt is None:
            self.write_log(f"{self.cell_id}: Nothing to plot (volt)")
            return

        best_params = self.get_parameter_cache("param")
        synapse_position_override = (self.get_parameter_cache("sectionID"),
                                     self.get_parameter_cache("sectionX"))
        min_error = self.get_parameter_cache("error")

        v_plot = None
        t_plot = None
        i_plot = None

        if best_params is not None:
            u, tau_r, tau_f, tau_ratio, cond = best_params

            params = {"U": u,
                      "tauR": tau_r,
                      "tauF": tau_f,
                      "cond": cond,
                      "tau": tau_r * tau_ratio}

            plot_model = self.setup_model(params=params, synapse_position_override=synapse_position_override)

            (t_plot, v_plot, i_plot) = plot_model.run2(pars=params)

        t_idx = np.where(skip_time <= self.time)[0]

        plt.figure()

        plt.plot(self.time[t_idx] * 1e3, self.data[t_idx] * 1e3, 'r-')
        if v_plot is not None:
            t2_idx = np.where(skip_time <= t_plot)[0]
            plt.plot(t_plot[t2_idx] * 1e3, v_plot[t2_idx] * 1e3, 'k-')
        # plt.title(dataType + " " + str(cellID))

        if not pretty_plot:
            title_str = self.cell_type

            title_str += "\nU=%.3g, tauR=%.3g, tauF=%.3g, tau=%.3g,\ncond=%.3g" \
                        % (params["U"], params["tauR"], params["tauF"], params["tau"], params["cond"])

            plt.title(title_str)

        if pretty_plot:
            # Draw scalebars
            v_scale_x = 1200
            # vMax = np.max(vPlot[np.where(tPlot > 0.050)[0]])
            v_base = v_plot[-1]
            y_scale_bar = v_base * 1e3 + float(np.diff(plt.ylim())) / 4
            v_scale_y1 = y_scale_bar + 1
            v_scale_y2 = y_scale_bar
            t_scale_y = y_scale_bar
            t_scale_x1 = v_scale_x
            t_scale_x2 = v_scale_x + 100

            plt.plot([v_scale_x, v_scale_x], [v_scale_y1, v_scale_y2], color="black")
            plt.plot([t_scale_x1, t_scale_x2], [t_scale_y, t_scale_y], color="black")

            plt.text(v_scale_x - 100, v_scale_y2 + 0.20 * float(np.diff(plt.ylim())), \
                     ("%.0f" % (v_scale_y1 - v_scale_y2)) + " mV",
                     rotation=90)
            plt.text(v_scale_x, v_scale_y2 - float(np.diff(plt.ylim())) / 10,
                     ("%.0f" % (t_scale_x2 - t_scale_x1) + " ms"))

            # Mark optogenetical stimulation
            y_height = float(np.diff(plt.ylim())) / 13

            t_stim = self.getStimTime() * 1e3
            y_stim_marker1 = v_plot[-1] * 1e3 - 1.5 * y_height
            y_stim_marker2 = v_plot[-1] * 1e3 - 2.5 * y_height
            for ts in t_stim:
                plt.plot([ts, ts], [y_stim_marker1, y_stim_marker2], color="cyan")

            plt.axis("off")

            # import pdb
            # pdb.set_trace()

        plt.xlabel("Time (ms)")
        plt.ylabel("Volt (mV)")

        if not os.path.exists("figures/"):
            os.makedirs("figures/")

        base_name = os.path.splitext(os.path.basename(self.datafile))[0]
        fig_name = "figures/" + base_name + ".pdf"
        plt.savefig(fig_name, dpi=self.fig_resolution)

        if show:
            plt.ion()
            plt.show()
        else:
            plt.ioff()
            plt.close()

    ############################################################################

    def get_cell_properties(self):

        if self.cell_properties is None:
            with open(self.neuron_set_file, 'r') as f:
                self.cell_properties = json.load(f)

        cell_type = self.data["metadata"]["cell_type"]

        return self.cell_properties[cell_type].copy()

    ############################################################################

    def extract_input_res_tau(self, t, v, cur_amp, cur_start, cur_end, base_start, base_end):

        # We assume SI units
        t_idx_base = np.where(np.logical_and(base_start < t, t < base_end))[0]
        v_base = np.mean([v[x] for x in t_idx_base])

        t_idx_peak = np.where(np.logical_and(cur_start < t, t < cur_end))[0]
        v_peak = np.min(v[t_idx_peak])
        # vPeak = np.max([v[x] for x in tIdxPeak])

        assert np.abs(v_peak - v_base) > np.abs(np.max(v[t_idx_peak]) - v_base), \
            "The code assumes a hyperpolarising pulse, not a peak maximum"

        rm = (v_peak - v_base) / cur_amp

        idx_post_pulse = np.where(cur_end < t)[0]
        idx_max_post_pulse = idx_post_pulse[np.argmax(v[idx_post_pulse])]
        t_max_post_pulse = t[idx_max_post_pulse]

        t_idx_decay = np.where(np.logical_and(cur_end < t, t < t_max_post_pulse))[0]

        decay_func = lambda x, a, b, c: a * np.exp(-x / b) + c

        t_ab_fit = t[t_idx_decay] - t[t_idx_decay[0]]
        v_ab_fit = v[t_idx_decay]

        p0d = [-0.005, 0.01, -0.06]

        if np.isnan(v_ab_fit).any() or np.isinf(v_ab_fit).any():
            self.write_log("We have inifinite or nan values in the voltage")
            import pdb
            pdb.set_trace()

        try:
            fit_params, pcov = scipy.optimize.curve_fit(decay_func, t_ab_fit, v_ab_fit, p0=p0d)
            tau = fit_params[1]

        except:
            import traceback
            tstr = traceback.format_exc()
            self.write_log(tstr)

            plt.figure()
            plt.plot(t_ab_fit, v_ab_fit)
            plt.ion()
            plt.show()

            import pdb
            pdb.set_trace()

        if False:
            plt.figure()
            plt.plot(t_ab_fit, v_ab_fit, '-r')
            plt.plot(t_ab_fit, decay_func(t_ab_fit,
                                          fit_params[0],
                                          fit_params[1],
                                          fit_params[2]))
            plt.xlabel("t")
            plt.ylabel("v")
            plt.title("Tau extraction")
            plt.ion()
            plt.show()

            # self.writeLog("RM = " + str(RM) + " tau = " + str(tau))

        # Return membrane resistance and tau
        return rm, tau

        ############################################################################

    # x is somaDiameter, Gleak ...

    def opt_helper_function(self, x, input_res_steady_state, tau_delta, plot_results=False):

        soma_diameter, soma_gleak = x

        print(f"somaDiameter = {soma_diameter}")
        print(f"somaGleak = {soma_gleak}")

        # Set soma diameter and Gleak (convert to natural units!)
        self.rsr_delta_model.soma.L = soma_diameter * 1e6
        self.rsr_delta_model.soma.diam = soma_diameter * 1e6
        self.rsr_delta_model.soma.gl_hh = soma_gleak * 1e-4

        # We probably dont need to disable the short hyperpolarising pulse...

        # Update the holding current (use same holding voltage as before by default)
        self.rsr_delta_model.update_holding_current()

        # Run the simulation
        neuron.h.tstop = self.rsr_delta_model.time * 1e3  # Must set tstop
        neuron.h.run()

        (rm, tau) = self.extract_input_res_tau(t=np.array(self.rsr_delta_model.t_save) * 1e-3,
                                               v=np.array(self.rsr_delta_model.v_save) * 1e-3,
                                               cur_amp=self.cur_inj,
                                               cur_start=self.cur_start,
                                               cur_end=self.cur_end,
                                               base_start=self.base_start,
                                               base_end=self.base_end)

        # Return input resistance and tau
        opt_error = np.abs((rm - input_res_steady_state) * (tau_delta - tau))

        if plot_results:
            plt.figure()
            plt.plot(self.rsr_delta_model.t_save,
                     self.rsr_delta_model.v_save)
            plt.xlabel("Time (ms)")
            plt.ylabel("Volt (mV)")
            plt.title("RM = " + str(rm) + ", tau = " + str(tau))
            plt.ion()
            plt.show()

        return opt_error

    ############################################################################

    def get_peak_idx(self):

        p_time = np.array(self.data["metadata"]["stim_time"]) * 1e-3
        freq = self.data["metadata"]["freq"]

        assert np.abs(1.0 - freq / (p_time[1] - p_time[0])) < 0.01, "frequency mismatch"

        p_window = 1.0 / (2 * freq) * np.ones(p_time.shape)
        p_window[-1] *= 5

        peak_info = self.find_peaks_helper(p_time=p_time,
                                           p_window=p_window,
                                           time=self.time,
                                           volt=self.volt)

        return peak_info["peakIdx"]

    ############################################################################

    def get_peak_idx2(self, stim_time, time, volt):

        freq = 1.0 / (stim_time[1] - stim_time[0])

        p_window = 1.0 / (2 * freq) * np.ones(stim_time.shape)
        p_window[-1] *= 5

        peak_info = self.find_peaks_helper(p_time=stim_time,
                                           p_window=p_window,
                                           time=time,
                                           volt=volt)

        return peak_info["peakIdx"]

    ############################################################################

    # Find peaks within pStart[i] and pStart[i]+pWindow[i]
    # The value is not the amplitude of the peak, just the voltage at the peak

    def find_peaks_helper(self, p_time, p_window, time=None, volt=None):

        peak_idx = []
        peak_time = []
        peak_volt = []

        for pt, pw in zip(p_time, p_window):
            t_start = pt
            t_end = pt + pw

            t_idx = np.where(np.logical_and(t_start <= time, time <= t_end))[0]
            assert len(t_idx) > 0, f"No time points within {t_start} and {t_end}"

            if self.synapse_type == "glut":
                p_idx = t_idx[np.argmax(volt[t_idx])]
            elif self.synapse_type == "gaba":
                # We assume that neuron is more depolarised than -65, ie gaba is
                # also depolarising
                p_idx = t_idx[np.argmax(volt[t_idx])]
            else:
                self.write_log("Unknown synapse type : " + str(self.synapse_type))
                import pdb
                pdb.set_trace()

            peak_idx.append(int(p_idx))
            peak_time.append(time[p_idx])
            peak_volt.append(volt[p_idx])

        # Save to cache -- obs peakVolt is NOT amplitude of peak, just volt

        peak_dict = {"peakIdx": np.array(peak_idx),
                    "peakTime": np.array(peak_time),
                    "peakVolt": np.array(peak_volt)}  # NOT AMPLITUDE

        #    if(cellID is not None):
        #      self.addParameterCache("peaks",peakDict)

        return peak_dict

    # (peakIdx,peakTime,peakVolt)

    ############################################################################

    def find_trace_heights(self, time, volt, peak_idx):

        decay_func = lambda x, a, b, c: a * np.exp(-x / b) + c

        v_base = np.mean(volt[int(0.3 * peak_idx[0]):int(0.8 * peak_idx[0])])

        peak_height = np.zeros((len(peak_idx, )))
        peak_height[0] = volt[peak_idx[0]] - v_base

        decay_fits = []

        for idx_b in range(1, len(peak_idx)):

            if peak_height[0] > 0:
                if idx_b < len(peak_idx) - 1:
                    p0d = [0.06, 0.05, -0.074]
                else:
                    p0d = [1e-5, 100, -0.074]

                    if self.synapse_type == "gaba":
                        p0d = [1e-8, 10000, -0.0798]
            else:
                # In some cases for GABA we had really fast decay back
                if idx_b < len(peak_idx) - 1:
                    p0d = [-0.06, 0.05, -0.0798]
                else:
                    p0d = [-1e-5, 1e5, -0.0798]

            idx_a = idx_b - 1

            peak_idx_a = peak_idx[idx_b - 1]  # Prior peak
            peak_idx_b = peak_idx[idx_b]  # Next peak

            if idx_b < len(peak_idx) - 1:
                # Not the last spike
                idx_start = int(peak_idx_a * 0.9 + peak_idx_b * 0.1)
                idx_end = int(peak_idx_a * 0.1 + peak_idx_b * 0.9)
            else:
                # Last spike, use only last half of decay trace
                idx_start = int(peak_idx_a * 0.5 + peak_idx_b * 0.5)
                idx_end = int(peak_idx_a * 0.05 + peak_idx_b * 0.85)  # might need 0.85 as last

            try:
                assert idx_start < idx_end
            except:
                import traceback
                tstr = traceback.format_exc()
                self.write_log(tstr)

                plt.figure()
                plt.plot(time, volt)
                plt.xlabel("Time (error plot)")
                plt.ylabel("Volt (error plot)")
                plt.ion()
                plt.show()
                plt.title("ERROR!!!")
                import pdb
                pdb.set_trace()

            t_ab = time[idx_start:idx_end]
            v_ab = volt[idx_start:idx_end]

            t_ab_fit = t_ab - t_ab[0]
            v_ab_fit = v_ab

            try:

                try:
                    fit_params, pcov = scipy.optimize.curve_fit(decay_func, t_ab_fit, v_ab_fit, p0=p0d)
                except:
                    import traceback
                    tstr = traceback.format_exc()
                    self.write_log(tstr)

                    self.write_log("!!! Failed to converge, trying with smaller decay constant")
                    p0d[1] *= 0.01
                    fit_params, pcov = scipy.optimize.curve_fit(decay_func, t_ab_fit, v_ab_fit, p0=p0d)

                t_b = time[peak_idx_b] - t_ab[0]
                v_base_b = decay_func(t_b, fit_params[0], fit_params[1], fit_params[2])

                peak_height[idx_b] = volt[peak_idx_b] - v_base_b

                v_fit = decay_func(t_ab - t_ab[0], fit_params[0], fit_params[1], fit_params[2])
                decay_fits.append((t_ab, v_fit))

            except:
                self.write_log("Check that the threshold in the peak detection before is OK")
                # self.plot(name)
                import traceback
                tstr = traceback.format_exc()
                self.write_log(tstr)

                if True:
                    plt.figure()
                    plt.plot(t_ab, v_ab, 'r')
                    plt.title("Error in findTraceHeights")
                    plt.xlabel("time")
                    plt.ylabel("volt")
                    # plt.plot(tAB,vFit,'k-')
                    plt.ion()
                    plt.show()

                import pdb
                pdb.set_trace()

        # import pdb
        # pdb.set_trace()

        return peak_height.copy(), decay_fits, v_base

    ############################################################################

    def setup_model(self, params={},
                    synapse_density_override=None,
                    n_synapses_override=None,
                    synapse_position_override=None):

        t_stim = self.stim_time

        # Read the info needed to setup the neuron hosting the synapses
        c_prop = self.get_cell_properties()

        if synapse_position_override is not None:
            synapse_section_id, synapse_section_x = synapse_position_override
        else:
            synapse_section_id, synapse_section_x = None, None

        if synapse_density_override is not None:
            synapse_density = synapse_density_override
        else:
            synapse_density = c_prop["synapseDensity"]

        if n_synapses_override is not None:
            n_synapses = n_synapses_override
        else:
            n_synapses = c_prop["nSynapses"]

        # !!! We need to get the baseline depolarisation in another way

        self.rsr_synapse_model = \
            RunSynapseRun(neuron_morphology=c_prop["neuronMorphology"],
                          neuron_mechanisms=c_prop["neuronMechanisms"],
                          neuron_parameters=c_prop["neuronParameters"],
                          neuron_modulation=c_prop["neuronModulation"],
                          stim_times=t_stim,
                          num_synapses=n_synapses,
                          synapse_density=synapse_density,
                          holding_voltage=c_prop["baselineVoltage"],
                          synapse_type=self.synapse_type,
                          params=params,
                          time=self.sim_time,
                          log_file=self.log_file,
                          synapse_section_id=synapse_section_id,
                          synapse_section_x=synapse_section_x)

        return self.rsr_synapse_model

    ############################################################################

    def neuron_synapse_swarm_helper(self, pars, t_spikes, peak_height, smooth_exp_trace):

        if self.debug_pars_flag:
            self.debug_pars.append(pars)

        res = np.zeros((pars.shape[0]))

        for idx, p in enumerate(pars):
            peak_h, t_sim, v_sim = self._neuron_synapse_swarm_helper(p, t_spikes)

            # Calculating error in peak height
            h_diff = np.abs(peak_h - peak_height)
            h_diff[0] *= 3
            h_diff[-1] *= 3
            h_error = np.sum(h_diff) / len(h_diff)

            # Calculate error in decay fit
            sim_trace, sim_time = self.smoothing_trace(v_sim, self.num_smoothing,
                                                       time=t_sim,
                                                       start_time=self.decayStartFit,
                                                       end_time=self.decayEndFit)

            # We only want to use the bit of the trace after max
            idx_max = np.argmax(smooth_exp_trace)

            # We divide by number of points in vector, to get the average deviation
            # then we multiply by 10000 to get an error comparable to the others
            decay_error = np.sum((smooth_exp_trace[idx_max:] - sim_trace[idx_max:]) ** 2) \
                          / (self.num_smoothing - idx_max + 1) * 2000

            if False:
                plt.figure()
                plt.plot(smooth_exp_trace[idx_max:])
                plt.plot(sim_trace[idx_max:])
                plt.ion()
                plt.show()
                import pdb
                pdb.set_trace()

            res[idx] = h_error + decay_error

        return res

    ############################################################################

    def smoothing_trace(self, original_trace, num_parts, time=None, start_time=None, end_time=None):

        if time is not None:
            t_flag = np.ones((len(original_trace),), dtype=bool)

            if end_time is not None:
                t_flag[np.where(time > end_time)[0]] = False

            if start_time is not None:
                t_flag[np.where(time < start_time)[0]] = False

            # tIdx = np.where(tFlag)[0]
            trace = original_trace[t_flag]
            t = time[t_flag]
        else:
            trace = original_trace
            t = time

        N = int(np.round(len(trace) / num_parts))

        smooth_trace = np.convolve(trace, np.ones((N,)) / N, mode='valid')

        idx = np.linspace(0, len(smooth_trace) - 1, num=num_parts, dtype=int)

        return smooth_trace[idx], t[idx]

    ############################################################################

    def _neuron_synapse_swarm_helper(self,
                                     pars,
                                     t_spikes):

        u, tau_r, tau_f, tau_ratio, cond = pars
        tau = tau_r * tau_ratio

        # TODO: Check where parms come from, is it a dictionary?
        peak_heights, t_sim, v_sim = self.run_model(t_spikes, u,
                                                    tau_r, tau_f, cond, tau,
                                                    params=params,
                                                    return_trace=True)

        return peak_heights, t_sim, v_sim

    ############################################################################

    def neuron_synapse_helper(self,
                              t_spike, u, tau_r, tau_f,
                              tau_ratio=None,
                              cond=1e-7, tau=None):

        assert tau_ratio is None or tau is None, \
            "Only one of tau and tauRatio should be defined"

        if tau_ratio is not None:
            tau = tau_r * tau_ratio
        elif tau is None:
            assert False, "tau or tauRatio must be specified"

        peak_heights = self.run_model(t_spike, u, tau_r, tau_f, cond, tau)

        return peak_heights

    ############################################################################

    # !!! OBS tauRatio is inparameter

    def neuron_synapse_helper_glut(self, t_spike,
                                   u, tau_r, tau_f, tau_ratio, cond,
                                   smooth_exp_trace8, smooth_exp_trace9, exp_peak_height,
                                   return_type="peaks"):

        if self.debug_pars_flag:
            self.debug_pars.append([u, tau_r, tau_f, tau_ratio, cond])

        params = self.synase_parameters
        tau = tau_r * tau_ratio

        peak_h, t_sim, v_sim = self.run_model(t_spike, u,
                                              tau_r, tau_f, cond, tau,
                                              params=params,
                                              return_trace=True)

        # Calculate error in decay fit
        sim_trace8, sim_time8 = self.smoothing_trace(v_sim, self.num_smoothing,
                                                     time=t_sim,
                                                     start_time=self.decay_start_fit8,
                                                     end_time=self.decay_end_fit8)

        sim_trace9, sim_time9 = self.smoothing_trace(v_sim, self.num_smoothing,
                                                     time=t_sim,
                                                     start_time=self.decay_start_fit9,
                                                     end_time=self.decay_end_fit9)

        # We only want to use the bit of the trace after max
        idx_max8 = np.argmax(smooth_exp_trace8)
        idx_max9 = np.argmax(smooth_exp_trace9)

        # Calculating error in peak height
        h_diff = np.abs(peak_h - exp_peak_height)
        h_diff[0] *= 3
        h_diff[-2] *= 2
        h_diff[-1] *= 3

        # This is to prevent the model spiking
        spike_penalty = np.sum(peak_h > 0.03) * 1

        h_error = np.sum(h_diff) / len(h_diff)

        decay_error8 = np.sum((smooth_exp_trace8[idx_max8:] - sim_trace8[idx_max8:]) ** 2) \
                        / (self.num_smoothing - idx_max8 + 1) * 10000

        decay_error9 = np.sum((smooth_exp_trace9[idx_max9:] - sim_trace9[idx_max9:]) ** 2) \
                        / (self.num_smoothing - idx_max9 + 1) * 10000

        fit_error = h_error + decay_error8 + decay_error9 + spike_penalty

        if spike_penalty > 0:
            self.write_log("Action potential detected in trace. Penalising!")

        if False:
            peak_base = v_sim[-1]
            plt.figure()
            plt.plot(t_sim, v_sim, 'k-')
            plt.plot(sim_time8, sim_trace8, 'y--')
            plt.plot(sim_time8, smooth_exp_trace8, 'r--')
            plt.plot(sim_time9, sim_trace9, 'y--')
            plt.plot(sim_time9, smooth_exp_trace9, 'r--')

            for tp, expH, modH in zip(t_spike, exp_peak_height, peak_h):
                plt.plot([tp, tp], [peak_base, expH + peak_base], 'r-', linewidth=3)
                plt.plot([tp, tp], [peak_base, modH + peak_base], 'b-')
            plt.title("hE = %g, dE8 = %g, dE9 = %g" \
                      % (h_error, decay_error8, decay_error9))

            plt.ion()
            plt.show()

        if return_type == "peaks":
            return peak_h
        elif return_type == "error":
            return fit_error
        elif return_type == "full":
            return fit_error, peak_h, t_sim, v_sim
        else:
            assert False, "Unknown return type: " + str(return_type)

    ############################################################################

    def run_model(self, t_spike, u, tau_r, tau_f, cond, tau,
                  params={},
                  return_trace=False):

        # self.writeLog("Running neuron model")

        assert self.rsr_synapse_model is not None, \
            "!!! Need to call setupModel first"

        # Should we make a copy of params, to not destroy it? ;)
        params["U"] = u
        params["tauR"] = tau_r
        params["tauF"] = tau_f
        params["cond"] = cond
        params["tau"] = tau

        # self.writeLog("params=" + str(params))

        (t_sim, v_sim, i_sim) = self.rsr_synapse_model.run2(pars=params)

        if t_sim.shape != v_sim.shape:
            self.write_log("Shape are different, why?!")
            import pdb
            pdb.set_trace()

        peak_idx = self.get_peak_idx2(time=t_sim, volt=v_sim, stim_time=t_spike)
        peak_height, decay_fits, v_base = self.find_trace_heights(t_sim, v_sim, peak_idx)

        if return_trace:
            return peak_height, t_sim, v_sim
        else:
            return peak_height

    ############################################################################

    # This should read from a JSON file instead

    def get_model_bounds(self):

        cell_type = self.data["metadata"]["cell_type"]

        mb = self.model_bounds[cell_type]

        param_list = ["U", "tauR", "tauF", "tauRatio", "cond"]
        lower_bound = [mb[x][0] for x in param_list]
        upper_bound = [mb[x][1] for x in param_list]

        return lower_bound, upper_bound

    ############################################################################

    def sobol_scan(self, synapse_model,
                   t_stim, h_peak,
                   model_bounds,
                   smooth_exp_trace8, smooth_exp_trace9,
                   n_trials=6, load_params_flag=False,
                   parameter_sets=None,
                   return_min_error=False):

        assert self.synapse_type == "glut", \
            "GABA synapse not supported yet in new version"

        if parameter_sets is None:
            parameter_sets = self.setup_parameter_set(model_bounds, n_trials)

        # zip(*xxx) unzips xxx -- cool.
        u_sobol, tau_r_sobol, tau_f_sobol, tau_ratio_sobol, cond_sobol = zip(*parameter_sets)

        # tauSobol = np.multiply(tauRatioSobol,tauRSobol)

        min_pars = None
        min_error = np.inf

        if load_params_flag:
            # If we should load params then do so first
            min_pars = self.get_parameter_cache("synapse")

            # --- now parameters are read from cache, but we can in future
            # have them read from a work-log with parameters to do etc

            # What was error of the cached parameterset
            if min_pars is not None:
                min_error = self.neuron_synapse_helper_glut(t_stim,
                                                            u=min_pars[0],
                                                            tau_r=min_pars[1],
                                                            tau_f=min_pars[2],
                                                            tau_ratio=min_pars[3] / min_pars[1],
                                                            cond=min_pars[4],
                                                            smooth_exp_trace8=smooth_exp_trace8,
                                                            smooth_exp_trace9=smooth_exp_trace9,
                                                            exp_peak_height=h_peak,
                                                            return_type="error")

        idx = 0

        for u, tau_r, tau_f, tau_ratio, cond \
                in zip(u_sobol, tau_r_sobol, tau_f_sobol, tau_ratio_sobol, \
                       cond_sobol):

            idx += 1
            if idx % 50 == 0:
                self.write_log("%d / %d : minError = %g" % (idx, len(u_sobol), min_error))
                self.write_log(str(min_par))

            error = self.neuron_synapse_helper_glut(t_stim, u, tau_r, tau_f, tau_ratio,
                                                    cond,
                                                    smooth_exp_trace8=smooth_exp_trace8,
                                                    smooth_exp_trace9=smooth_exp_trace9,
                                                    exp_peak_height=h_peak,
                                                    return_type="error")
            try:
                if error < min_error:
                    min_error = error
                    min_par = np.array([u, tau_r, tau_f, tau_ratio, cond])

                    # TODO, write intermediate results to file, in case of a crash...

            except:
                import traceback
                tstr = traceback.format_exc()
                self.write_log(tstr)

                import pdb
                pdb.set_trace()

                # For big runs we do no want to give up. Let's try again...
                continue

        if return_min_error:
            return min_par, min_error
        else:
            return min_par

    ############################################################################

    def best_random(self, synapse_model,
                    t_stim, h_peak,
                    model_bounds,
                    n_trials=5000, load_params_flag=False):

        assert n_trials >= 1, "nTrials should be a positive integer"

        min_error = np.inf
        min_par = None

        for idx in range(0, n_trials):
            if idx % 100 == 0:
                self.write_log(f"Pre-trial : {idx}/{n_trials}")

            if idx == 0 and load_params_flag:
                # If we should load params then do so first
                pars = self.get_parameter_cache("synapse")
            else:
                pars = None

            if pars is not None:
                u = pars["U"]
                tau_r = pars["tauR"]
                tau_f = pars["tauF"]
                tau = pars["tau"]
                cond = pars["cond"]
            else:
                u = np.random.uniform(model_bounds[0][0], model_bounds[1][0])
                tau_r = np.random.uniform(model_bounds[0][1], model_bounds[1][1])
                tau_f = np.random.uniform(model_bounds[0][2], model_bounds[1][2])
                tau = tau_r * np.random.uniform(model_bounds[0][3], model_bounds[1][3])
                cond = np.random.uniform(model_bounds[0][4], model_bounds[1][4])

            try:
                peak_heights = self.run_model(t_stim, u, tau_r, tau_f, tau, cond)

                error = np.abs(peak_heights - h_peak)
                error[0] *= 3
                error[1] *= 2
                error[-1] *= 3
                error = np.sum(error)

                if error < min_error:
                    min_error = error
                    min_par = np.array([u, tau_r, tau_f, tau / tau_r, cond])

            except:
                import traceback
                tstr = traceback.format_exc()
                self.write_log(tstr)

                # For big runs we do no want to give up. Let's try again...
                continue

        return min_par

    ############################################################################

    def optimise_cell(self):

        assert False, "obsolete"

        try:
            # self.fitCellProperties(dataType,cellID)
            self.fitTrace()
            self.plot_data(show=False)

            # We need to extract the dictionary associated with cellID and
            # return the result so that the main function can plug it into the
            # central parameter cache -- OR DO WE?

            return self.getSubDictionary(cellID)

        except:

            import traceback
            tstr = traceback.format_exc()
            self.write_log(tstr)
            self.add_parameter_cache("error", tstr)

    ############################################################################

    def parallel_optimise_single_cell(self, n_trials=10000, post_opt=False):

        # !!! Future improvement. Allow continuation of old optimisation by
        # reading synapse location and old parameter set, so that is not thrown away

        if self.role == "master":

            # 1. Setup workers
            params = self.synapse_parameters

            # 2. Setup one cell to optimise, randomise synapse positions
            synapse_model = self.setup_model(params=params)

            # (volt,time) = self.getData(dataType,cellID)
            peak_idx = self.get_peak_idx2(stim_time=self.stim_time,
                                         time=self.time,
                                         volt=self.volt)
            t_spikes = self.time[peak_idx]

            sigma = np.ones(len(peak_idx))
            sigma[-1] = 1. / 3

            peak_height, decay_fits, v_base = self.find_trace_heights(self.time, self.volt, peak_idx)

            # 2b. Create list of all parameter points to investigate
            model_bounds = self.get_model_bounds()
            parameter_points = self.setup_parameter_set(model_bounds, n_trials)

            # 3. Send synapse positions to all workers, and split parameter points
            #    between workers

            if self.d_view is not None:
                self.setup_parallel(self.d_view)

                self.d_view.scatter("parameterPoints", parameter_points, block=True)

                self.d_view.push({"params": params,
                                 "synapseSectionID": synapse_model.synapse_section_id,
                                 "synapseSectionX": synapse_model.synapse_section_x,
                                 "modelBounds": model_bounds,
                                 "stimTime": self.stim_time,
                                 "peakHeight": peak_height},
                                 block=True)

                cmd_str_setup = \
                    "ly.sobolWorkerSetup(params=params," \
                    + "synapsePositionOverride=(synapseSectionID,synapseSectionX))"

                self.d_view.execute(cmd_str_setup, block=True)

                cmd_str = "res = ly.sobolScan(synapseModel=ly.synapseModel, \
                                     tStim = stimTime, \
                                     hPeak = peakHeight, \
                                     parameterSets=parameterPoints, \
                                     modelBounds=modelBounds, \
                                     smoothExpTrace8=ly.smoothExpVolt8, \
                                     smoothExpTrace9=ly.smoothExpVolt9, \
                                     returnMinError=True)"

                self.write_log("Executing workers, bang bang")
                self.d_view.execute(cmd_str, block=True)

                # 5. Gather worker data
                self.write_log("Gathering results from workers")
                res = self.d_view["res"]

                # * unpacks res variable
                par_sets, par_error = zip(*res)

                min_error_idx = np.argsort(par_error)

                import pdb
                pdb.set_trace()

                # We save parameter set, synapse locations, error value
                best_par = (par_sets[min_error_idx[0]],
                            (synapse_model.synapse_section_id, synapse_model.synapse_section_x),
                            par_error[min_error_idx[0]])

            else:

                # No dView, run in serial mode...
                # !!!
                self.sobol_worker_setup(params=params,
                                        synapse_position_override=(synapse_model.synapse_section_id,
                                                                   synapse_model.synapse_section_x))

                par_set, par_error = self.sobol_scan(synapse_model=synapse_model,
                                                     t_stim=self.stim_time,
                                                     h_peak=peak_height,
                                                     model_bounds=model_bounds,
                                                     smooth_exp_trace8=ly.smooth_exp_volt8,
                                                     smooth_exp_trace9=ly.smooth_exp_volt9,
                                                     return_min_error=True)

                best_par = (par_set,
                            (synapse_model.synapse_section_id, synapse_model.synapse_section_x), par_error)

            self.add_parameter_cache("param", best_par[0])
            self.add_parameter_cache("sectionID", synapse_model.synapse_section_id)
            self.add_parameter_cache("sectionX", synapse_model.synapse_section_x)
            self.add_parameter_cache("error", best_par[2])

            self.save_parameter_cache()
            self.write_log(f"Sobol search done. Best parameter {best_par}")

            if post_opt:
                # This updates parameters and saves new parameter cache
                self.get_refined_parameters()

    ############################################################################

    # This sets up the model also, so can be run in a self-contained loop
    # We might later want to let the workers do this, but then they cant
    # write to cache --- THAT WILL LEAD TO DATA CORRUPTION!!

    def get_refined_parameters(self):

        assert self.role == "master", \
            "You do not want to run this on workers in parallel, " \
            + " since it writes directly to parameter cache. " \
            + " That could lead to corrupted data."

        # Load parameters from disk
        self.load_parameter_cache()
        model_bounds = self.get_model_bounds()

        start_par = self.get_parameter_cache("param")
        section_x = self.get_parameter_cache("sectionX")
        section_id = self.get_parameter_cache("sectionID")
        start_par_error_val = self.get_parameter_cache("error")

        synapse_position_override = (section_id, section_x)

        # Make sure we have correct taus etc for synapse
        params = self.synapse_parameters

        peak_idx = self.get_peak_idx2(stim_time=self.stim_time,
                                     time=self.time,
                                     volt=self.volt)
        t_spikes = time[peak_idx]

        peak_height, decay_fits, v_base = self.find_trace_heights(self.time, self.volt, peak_idx)

        self.sobol_worker_setup(params, synapse_position_override=synapse_position_override)

        func = lambda x: \
            self.neuron_synapse_helper_glut(t_spike=self.stim_time,
                                            u=x[0],
                                            tau_r=x[1],
                                            tau_f=x[2],
                                            tau_ratio=x[3],
                                            cond=x[4],
                                            smooth_exp_trace8=self.smooth_exp_volt8,
                                            smooth_exp_trace9=self.smooth_exp_volt9,
                                            exp_peak_height=peak_height,
                                            return_type="error")

        m_bounds = [x for x in zip(model_bounds[0], model_bounds[1])]
        start_par = self.get_parameter_cache("param")

        res = scipy.optimize.minimize(func,
                                      x0=start_par,
                                      bounds=m_bounds)

        fit_params = res.x
        min_error = res.fun

        if min_error >= start_par_error_val:
            print("Refinement failed. Sobol parameters are better match than new fitting")
            # Dont overwrite the old parameters

        else:
            self.add_parameter_cache("param", fit_params)
            self.add_parameter_cache("error", min_error)

            self.save_parameter_cache()

            print(f"Old error: {start_par_error_val}, New error: {min_error}")

    ############################################################################

    def sobol_worker_setup(self, params, synapse_position_override=None):

        # TODO: These variables should be defined as None in init
        self.synapse_model = self.setup_model(params=params,
                                              synapse_position_override=synapse_position_override)
        self.decay_start_fit8 = 0.45
        self.decay_end_fit8 = 0.8

        self.decay_start_fit9 = 1.0
        self.decay_end_fit9 = 1.3

        self.smooth_exp_volt8, self.smooth_exp_time8 \
            = self.smoothing_trace(self.volt, self.num_smoothing,
                                   time=self.time,
                                   start_time=self.decay_start_fit8,
                                   end_time=self.decay_end_fit8)

        self.smooth_exp_volt9, self.smooth_exp_time9 \
            = self.smoothing_trace(self.volt, self.num_smoothing,
                                   time=self.time,
                                   start_time=self.decay_start_fit9,
                                   end_time=self.decay_end_fit9)

    ############################################################################

    def setup_parameter_set(self, modelBounds, nSets):

        import chaospy
        distribution = chaospy.J(chaospy.Uniform(modelBounds[0][0],
                                                 modelBounds[1][0]),
                                 chaospy.Uniform(modelBounds[0][1],
                                                 modelBounds[1][1]),
                                 chaospy.Uniform(modelBounds[0][2],
                                                 modelBounds[1][2]),
                                 chaospy.Uniform(modelBounds[0][3],
                                                 modelBounds[1][3]),
                                 chaospy.Uniform(modelBounds[0][4],
                                                 modelBounds[1][4]))

        u_sobol, tau_r_sobol, tau_f_sobol, tau_ratio_sobol, cond_sobol \
            = distribution.sample(nSets, rule="sobol")

        parameter_sets = [x for x in zip(u_sobol, \
                                         tau_r_sobol, tau_f_sobol, tau_ratio_sobol, \
                                         cond_sobol)]

        return parameter_sets

    ############################################################################

    def parallel_optimise_cells(self, data_type, cell_id_list=None):

        assert False, "Only doing one cell at a time"

        if self.role == "master":

            if cell_id_list is None:
                cell_id_list = self.get_valid_cell_id(data_type)

            # self.printCellProperties(dataType,cellIDlist)

            if self.d_view is None:
                self.write_log("We are in serial mode, use serial code..")
                for c in cell_id_list:
                    self.optimise_cell(data_type, c)

                # Save parameters to file
                self.save_parameter_cache()
                return

            self.write_log("Optimising in parallel")

            self.setup_parallel(self.d_view)
            self.d_view.scatter("cellIDlist", cell_id_list, block=True)
            self.d_view.push({"dataType": data_type}, block=True)

            try:

                cmdStr = "res = ly.parallelOptimiseCells(dataType=dataType,cellIDlist=cellIDlist)"
                self.write_log("Starting execution")
                self.d_view.execute(cmdStr, block=True)
                self.write_log("Execution finished, gathering results")
                # res = self.dView.gather("res",block=True)
                res = self.d_view["res"]

                # res now contains a list of dictionaries, each dictionary from one worker, we need
                # to merge these
                self.write_log("Results gathered, merging dictionary")
                for m in res:
                    # self.parameterCache.update(m)
                    for k in m:
                        self.parameter_cache[int(k)] = m[k]

                self.save_parameter_cache()

                self.write_log("Done.")
            except:
                import traceback
                tstr = traceback.format_exc()
                self.write_log(tstr)
                import pdb
                pdb.set_trace()

        else:
            try:
                # Servant runs here
                for cellID in cell_id_list:
                    self.optimise_cell(data_type, cellID)

                return self.getSubDictionary(cell_id_list)

            except:
                import traceback
                tstr = traceback.format_exc()
                self.write_log(tstr)
                import pdb
                pdb.set_trace()

    ############################################################################

    def setup_parallel(self, d_view=None):

        assert self.role == "master", "Only master should call setupParallel"

        if d_view is None:
            self.write_log("No dView, no parallel")
            return
        else:
            self.d_view = d_view

        if self.parallel_setup_flag:
            # Already setup servants
            return

        with self.d_view.sync_imports():
            from run_synapse_run import RunSynapseRun
            from OptimiseSynapsesFull import NumpyEncoder
            from OptimiseSynapsesFull import OptimiseSynapsesFull

        self.write_log("Setting up workers: " \
                       + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

        # Create unique log file names for the workers
        if self.log_file_name is not None:
            engine_log_file = [self.log_file_name + "-" \
                             + str(x) for x in range(0, len(self.d_view))]
        else:
            engine_log_file = [[] for x in range(0, len(self.d_view))]

        n_workers = len(self.d_view)
        self.d_view.scatter("engineLogFile", engine_log_file)

        self.d_view.push({"datafile": self.datafile,
                         "synapseType": self.synapse_type,
                         "synapseparameters": self.synapse_parameter_file,
                         "loadCache": self.load_cache,
                         "role": "servant"})

        cmd_str = "ly = OptimiseSynapsesFull(datafile=datafile, synapseParameterFile=synapseparameters, synapseType=synapseType,loadCache=loadCache,role=role,logFileName=engineLogFile[0])"
        self.d_view.execute(cmd_str, block=True)
        self.parallel_setup_flag = True

    ############################################################################

    def write_log(self, text, flush=True):  # Change flush to False in future, debug
        if self.log_file is not None:
            self.log_file.write(text + "\n")

            if self.verbose:
                print(text)

            if flush:
                self.log_file.flush()
        else:
            if self.verbose:
                print(text)

                ############################################################################

    def plot_debug_pars(self):

        try:
            n_iter = len(self.debug_pars)
            n_points = self.debug_pars[0].shape[0]
            n_pars = self.debug_pars[0].shape[1]

            assert n_pars == 6, "Should be six parameters"

            u_all = np.zeros((n_points, n_iter))
            tau_r = np.zeros((n_points, n_iter))
            tau_f = np.zeros((n_points, n_iter))
            tau_ratio = np.zeros((n_points, n_iter))
            cond = np.zeros((n_points, n_iter))

            for ctr, par in enumerate(self.debug_pars):
                u_all[:, ctr] = par[:, 0]
                tau_r[:, ctr] = par[:, 1]
                tau_f[:, ctr] = par[:, 2]
                tau_ratio[:, ctr] = par[:, 3]
                cond[:, ctr] = par[:, 4]

            plt.figure()
            plt.plot(u_all, cond, '-')
            plt.xlabel("U")
            plt.ylabel("cond")

            plt.figure()
            plt.plot(tau_r, tau_f, '-')
            plt.xlabel("tauR")
            plt.ylabel("tauF")

            plt.figure()
            plt.plot(u_all)
            plt.xlabel("Uall")

            plt.ion()
            plt.show()

            import pdb
            pdb.set_trace()

        except:
            import traceback
            tstr = traceback.format_exc()
            self.write_log(tstr)

            import pdb
            pdb.set_trace()

    ############################################################################


if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(description="Extract synaptic parameters from electrophysiological recordings")
    parser.add_argument("datafile", help="JSON DATA file")
    parser.add_argument("--synapseParameters", help="Static synapse parameters (JSON)",
                        default=None)
    parser.add_argument("--st", help="Synapse type (glut or gaba)",
                        choices=["glut", "gaba"])
    parser.add_argument("--optMethod",
                        help="Optimisation method",
                        choices=["sobol", "stupid", "swarm"],
                        default="sobol")
    parser.add_argument("--plot", action="store_true",
                        help="plotting previous optimised model")
    parser.add_argument("--prettyplot", action="store_true",
                        help="plotting traces for article")

    args = parser.parse_args()

    optMethod = args.optMethod

    print("Reading file : " + args.datafile)
    print("Synapse type : " + args.st)
    print("Synapse params :" + args.synapseParameters)
    print("Optimisation method : " + optMethod)

    print("IPYTHON_PROFILE = " + str(os.getenv('IPYTHON_PROFILE')))

    if (os.getenv('IPYTHON_PROFILE') is not None \
            or os.getenv('SLURMID') is not None):
        from ipyparallel import Client

        rc = Client(profile=os.getenv('IPYTHON_PROFILE'),
                    debug=False)

        # http://davidmasad.com/blog/simulation-with-ipyparallel/
        # http://people.duke.edu/~ccc14/sta-663-2016/19C_IPyParallel.html
        d_view = rc.direct_view(targets='all')  # rc[:] # Direct view into clients
        lb_view = rc.load_balanced_view(targets='all')
    else:
        d_view = None

    log_file_name = "logs/" + os.path.basename(args.datafile) + "-log.txt"
    if not os.path.exists("logs/"):
        os.makedirs("logs/")

    # "DATA/Yvonne2019/M1RH_Analysis_190925.h5"
    ly = OptimiseSynapsesFull(datafile=args.datafile,
                              synapse_parameter_file=args.synapseParameters,
                              synapse_type=args.st, d_view=d_view,
                              role="master",
                              log_file_name=log_file_name, opt_method=optMethod)

    if args.plot or args.prettyplot:

        if args.prettyplot:
            pretty_plot_flag = True
        else:
            pretty_plot_flag = False

        ly.plot_data(show=True, pretty_plot=pretty_plot_flag)

        exit(0)

    ly.parallel_optimise_single_cell(n_trials=12)
