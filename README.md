# Prediction Of Helminths Infection Pipeline (POHI)

This project process accelerometry data and uses machine learning to predict small ruminants(Goats and sheep) health.

## Project/Repo Structure
to replicate the results in our paper run main.py

## How To Use
```bash
Usage: ml.py [OPTIONS]

  ML

  Args:
      output_dir: Output directory
      dataset_folder: Dataset input directory
      class_healthy: Label for healthy class
      class_unhealthy: Label for unhealthy class
      stratify: Enable stratiy for cross validation
      s_output: Output sample files
      cwt: Enable freq domain (cwt)
      n_scales: n scales in dyadic array [2^2....2^n].
      temp_file: csv file containing temperature features.
      hum_file: csv file containing humidity features.
      n_splits: Number of splits for repeatedkfold cv.
      n_repeats: Number of repeats for repeatedkfold cv.
      cv: RepeatedKFold
      wavelet_f0: Mother Wavelet frequency for CWT
      sfft_window: STFT window size
      n_process:Number of threads to use.

Options:
  --output-dir DIRECTORY          [required]
  --dataset-folder DIRECTORY      [required]
  --preprocessing-steps TEXT      [default: QN, ANSCOMBE, LOG, DIFF]
  --class-healthy-label TEXT      [default: 1To1]
  --class-unhealthy-label TEXT    [default: 1To2]
  --stratify TEXT                 [default: n]
  --n-scales INTEGER              [default: 30]
  --hum-file PATH                 [default: .]
  --temp-file PATH                [default: .]
  --n-splits INTEGER              [default: 5]
  --n-repeats INTEGER             [default: 10]
  --epochs INTEGER                [default: 20]
  --n-process INTEGER             [default: 6]
  --output-samples / --no-output-samples
                                  [default: True]
  --output-cwt / --no-output-cwt  [default: True]
  --cv TEXT                       [default: RepeatedKFold]
  --wavelet-f0 INTEGER            [default: 6]
  --sfft-window INTEGER           [default: 60]
  --install-completion [bash|zsh|fish|powershell|pwsh]
                                  Install completion for the specified shell.
  --show-completion [bash|zsh|fish|powershell|pwsh]
                                  Show completion for the specified shell, to
                                  copy it or customize the installation.

  --help                          Show this message and exit.
```

##Blue Crystal 4
```bash
module load tools/git/2.18.0
module load languages/anaconda3/3.7
conda create --prefix /user/work/fo18103/PredictionOfHelminthsInfection/vgoat python=3.7
conda activate /user/work/fo18103/PredictionOfHelminthsInfection/vgoat
export PATH=/user/work/fo18103/PredictionOfHelminthsInfection/vgoat/bin/:$PATH
python -m pip install --upgrade pip
make environment
```

### Citation

Consider citing ours and Miguel's works in your own research if this repository has been useful:
```
@article {Montout2020.08.03.234203,
	author = {Axel X. Montout and Ranjeet S. Bhamber and Debbie S. Lange and Doreen Z. Ndlovu and Eric R. Morgan and Christos C. Ioannou and Thomas H. Terrill and Jan A. van Wyk and Tilo Burghardt and Andrew W. Dowsey},
	title = {Early prediction of declining health in small ruminants with accelerometers and machine learning},
	elocation-id = {2020.08.03.234203},
	year = {2023},
	doi = {10.1101/2020.08.03.234203},
	publisher = {Cold Spring Harbor Laboratory},
	URL = {https://www.biorxiv.org/content/early/2023/04/21/2020.08.03.234203},
	eprint = {https://www.biorxiv.org/content/early/2023/04/21/2020.08.03.234203.full.pdf},
	journal = {bioRxiv}
}

```
