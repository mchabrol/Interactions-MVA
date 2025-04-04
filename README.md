# Interactions-MVA

This project is an adaptation of [Pymarket](https://github.com/kenokrieger/pymarket),  
which implements the **Bornholdt Ising Model** in Python.

## Modifications and improvements

This project takes inspiration from **Pymarket**, while adding the following improvements:
- **Refactoring into object-oriented programming (OOP)**:
- **Reorganization and modularization of the code** for better readability.
- **Optimized spin updates** with more efficient subgrid management.
- **Added visualizations** to observe market evolution over time.

The original implementation of **Pymarket** can be found here:  
➡️ [Pymarket on GitHub](https://github.com/kenokrieger/pymarket)

This model is based on the paper:  
**Bornholdt, S. (2001).** *Expectation bubbles in a spin model of markets: Intermittency from frustration across scales.* [arXiv:cond-mat/0105224](http://arxiv.org/abs/cond-mat/0105224).

---

## Main Notebooks

Three main notebooks are:

- **`main.ipynb`**: Implements the base model described in the paper. It reproduces the results of the paper and serves as a reference for the other experiments.
- **`main_neutral_agents_fixed.ipynb`**: Introduces a fixed fraction of neutral agents and observes the evolution of the system.
- **`effect_of_alpha.ipynb`**: Analyzes the effect of the coupling parameter $\alpha$ in the case of a fixed fraction of neutral agents. This notebook explores how $\alpha$ influences the system’s polarization.

Each notebook is accompanied by a corresponding `.py` file, containing the functions implementing these experiments.

---
## Code Architecture

```plaintext
Interactions-MVA/
│
├── images/                                     
│
├── source/                    
│   ├── __pycache__/             
│   ├── neutralspinsystem_fixed.py
│   ├── spinsystem.py            
│   ├── utils.py
│             
│── effect_of_alpha.ipynb   
│── main.ipynb             
│── main_neutral_agents_fixed.ipynb 
│
│── multising.conf    
├── README.md                 
│
└── .gitignore
```

## **License**

The original implementation of **Pymarket** is under the MIT license.
