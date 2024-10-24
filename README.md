# Intrinsic timing of brood care in shell-dwelling cichlids

This repository contains the source code for the data analysis and processing methods described in the paper:

***Intrinsic timing of brood care in shell-dwelling cichlids***

Ash V. Parker, Manuel Stemmer, Swantje Graetsch, Alessandro Dorigo, Oriolson Rodriguez Ramirez, Abdelrahman Adel, Alex Jordan and Herwig Baier.

Please contact Ash Parker (ashley.parker@bi.mpg.de) or Swantje Graetsch (swantje.graetsch@bi.mpg.de) if you have any questions.

## Instructions

This repository is a collection of various methods, with the source code for each in its own separate folder. Every method requires a particular conda environment to run, and has a corresponding ```environment.yaml``` or ```requirements.txt``` file to install it.

If not done before, install conda following the instructions in the [official Anaconda documentation](https://docs.conda.io/projects/conda/en/latest/user-guide/index.html).

The functions in the *Argos*, *Boris* and *YOLO-Gooey* modules require individual environments, while *Phototaxis* and *InShell* have the same requirements and share an environment. In this sense, you should create and activate the environment(s) in a way corresponding to the method to be used. 

For *Argos*:

```
pip install -r ./Argos/requirements.txt
```

For *Boris*:
```
conda env create -f ./Boris/environment.yml
conda activate boris
```

For *YOLO-Gooey*:
```
conda env create -f ./YOLO-Gooey/environment.yml
conda activate yolo_gooey
```

For *Phototaxis* or *InShell*:
```
conda env create -f ./Phototaxis/environment.yml
conda activate inShell
```
OR
```
conda env create -f ./InShell/environment.yml
conda activate inShell
```
**Note:** The creation/activation of the latter environment should only occur once per machine, as the ```./Phototaxis/environment.yml``` and ```./InShell/environment.yml``` files define the same environment. If the environment already exists, you'll likely encounter an error indicating that the environment and its name is already in use. Conda will verify the existing environments and prevent creating duplicates.

Every method's specific instructions are found in the ```README.md``` files, inside each method folder.