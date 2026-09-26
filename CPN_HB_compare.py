import numpy as np
import time
from func_CPNSampler import CPNSampler, integrated_autocorr_time
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor, as_completed
import os
from pathlib import Path

def run_simulation(args):
    """
    Run CP^N Monte Carlo simulation with specified rand_z

    Returns: runtime, observables dictionary
    """
    rand_z, Lx, Ly, N, beta, alpha, therm, meas, hb_frac = args

    # Initialize sampler
    sampler = CPNSampler(Lx=Lx, Ly=Ly, N=N, beta=beta, alpha=alpha)
    
    # Timing setup
    start_time = time.time()
    
    # Equilibration phase (no measurements)
    for _ in tqdm(range(therm), desc="therm", leave=False):
        sampler.sweep(heatbath_fraction=hb_frac, rand_z=rand_z)
    
    # Measurement phase
    observables = {
        "E": [], "mag_sus": [],
        "w_U": [], "w_z": [],
        "topo_sus_U": [], "topo_sus_z": []
    }
    
    for _ in tqdm(range(meas), desc="meas", leave=False):
        sampler.sweep(heatbath_fraction=hb_frac, rand_z=rand_z)
        # Measure observables
        observables["E"].append(sampler.energy_density())
        observables["mag_sus"].append(sampler.PP_corr_k()[0,0])
        w_U, w_z = sampler.wilson_loop11()
        observables["w_U"].append(w_U)
        observables["w_z"].append(w_z)
        Q_U, Q_z = sampler.topo_charge()
        observables["topo_sus_U"].append(Q_U**2 / Lx / Ly)
        observables["topo_sus_z"].append(Q_z**2 / Lx / Ly)
    
    # Calculate runtime
    runtime = time.time() - start_time
    
    # Convert to numpy arrays for analysis
    for key in observables:
        observables[key] = np.array(observables[key])
    
    return runtime, observables

def analyze_observables(observables):
    """
    Analyze observables: mean, autocorrelation time, error

    Returns: dictionary with stats
    """
    stats = {}
    for key, data in observables.items():
        # Autocorrelation time
        tau = integrated_autocorr_time(data)
        
        # Error (95% confidence interval with autocorrelation correction)
        # Effective sample size = N / tau
        eff_n = len(data) / tau
        se = np.std(data, ddof=1) / np.sqrt(eff_n)
        error = 1.96 * se
        
        # Mean value
        mean = np.mean(data)
        
        stats[key] = {
            "mean": mean,
            "tau": tau,
            "error": error,
        }
    return stats

if __name__ == "__main__":
    N = 2
    L = 30

    therm = 500
    meas = 5000
    hb_frac = 0.4

    run_times = 10
    n_workers = 10
    beta_alpha_list = [(b, 0) for b in np.arange(5,21)/10]
    for beta, alpha in beta_alpha_list:
        print(f"beta = {beta}, alpha = {alpha}:")
        args = (True, L, L, N, beta, alpha, therm, meas, hb_frac)
        runtime_True = 0
        observables = {
            "E": [], "mag_sus": [],
            "w_U": [], "w_z": [],
            "topo_sus_U": [], "topo_sus_z": []
        }
        with ProcessPoolExecutor(max_workers=n_workers) as pool:
            futures = [pool.submit(run_simulation, args) for _ in range(run_times)]

            for fut in tqdm(as_completed(futures), total=run_times, desc=f"collecting True"):
                time_t, obs_t = fut.result()
                runtime_True += time_t
                observables["E"].extend(obs_t["E"])
                observables["mag_sus"].extend(obs_t["mag_sus"])
                observables["w_U"].extend(obs_t["w_U"])
                observables["w_z"].extend(obs_t["w_z"])
                observables["topo_sus_U"].extend(obs_t["topo_sus_U"])
                observables["topo_sus_z"].extend(obs_t["topo_sus_z"])
        stats_True = analyze_observables(observables)

        args = (False, L, L, N, beta, alpha, therm, meas, hb_frac)
        runtime_False = 0
        observables = {
            "E": [], "mag_sus": [],
            "w_U": [], "w_z": [],
            "topo_sus_U": [], "topo_sus_z": []
        }
        with ProcessPoolExecutor(max_workers=n_workers) as pool:
            futures = [pool.submit(run_simulation, args) for _ in range(run_times)]

            for fut in tqdm(as_completed(futures), total=run_times, desc=f"collecting True"):
                time_t, obs_t = fut.result()
                runtime_False += time_t
                observables["E"].extend(obs_t["E"])
                observables["mag_sus"].extend(obs_t["mag_sus"])
                observables["w_U"].extend(obs_t["w_U"])
                observables["w_z"].extend(obs_t["w_z"])
                observables["topo_sus_U"].extend(obs_t["topo_sus_U"])
                observables["topo_sus_z"].extend(obs_t["topo_sus_z"])
        stats_False = analyze_observables(observables)

        data = {'N': N, 'L': L, 'beta': beta, 'alpha': alpha,
                'therm': therm, 'meas': meas, 'hb_frac': hb_frac, 'run_times': run_times,
                'runtime_True': runtime_True, 'stats_True': stats_True,
                'runtime_False': runtime_False, 'stats_False': stats_False}
        
        script_path = Path(__file__).resolve()
        script_dir = script_path.parent
        folder = f'data/data_N{N}_L{L}'
        folder_path = script_dir / folder
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        file_name = f"stats_N{N}_L{L}_beta{beta}_alpha{alpha}.npy"
        np.save(folder_path / file_name, data)