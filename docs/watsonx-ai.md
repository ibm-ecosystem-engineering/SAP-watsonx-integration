## Use case: quick response to hazardous waste incidents by analyzing supplier's data sheets

Chemicals in a supply chain must include a Material Safety Data Sheet (MSDS) that details the crucial occupational safety and health information of the chemicals. The demo use case shows how text classification could be applied to supply chain data that includes hazardous materials. The text classification model takes an MSDS input, and outputs a recommended handling procedure. It enables an operator to quickly select the correct procedure for the situation.

## MSDS dataset

The data used in the demo is taken from this Kaggle dataset: https://www.kaggle.com/datasets/eliseu10/material-safety-data-sheets.

The original MSDS dataset contains Material Safety Data Sheet files in the `.txt` format. The data was collected from hazard.com. The dataset contains 2 types of files with different structure:

1. f1 type: 17,454 files (155.4MB)
2. f2 type: 23,6507 files (1.3GB)

The dataset has been prepared and downsampled to quickly train the text classification models.

