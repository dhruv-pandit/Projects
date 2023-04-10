# Political Spatial Data Analysis

This project contains Python code for performing a spatial data analysis on a elections in portugal. dataset. 

## Requirements

To run the code in this project, you'll need the following:

- Python 3.11
- Jupyter Notebook
- Pandas
- Geopandas
- Matplotlib

## Usage

To run the spatial data analysis, open the `politics_eda.ipynb` notebook in Jupyter Notebook and execute the code. The notebook will load the dataset from the `dataset` folder and perform the analysis.

## Report

The final report for this project is located in a Word document in the root folder of the project.

If you have any questions or issues with this project, please contact the author at dhruv.pandit2001@outlook.com

## Project Summary
This project aims to study and understand the behavioral patterns of the voting population in Portugal based on key indicators from the 2019 Portuguese legislative election. The software used for this project includes Qgis, GeoDa, and Python 3.10.


The project focuses on the political classification of the parties into left-wing, central-left, and central-right. The right-wing parties will not be considered in this study as they won a small number of votes in the 2019 legislative elections. The project aims to identify which regions of Portugal belong to which political classification and to determine how one region affects the voting population's preference of the neighboring region. The project also aims to understand which variables explain the voters' behavior.

The dataset includes 30 variables that provide information on geographical location, insights into the demographic makeup of the population, and key indicators in municipalities based on the previous Portuguese legislative election turnout. Some variables were added or transformed, while others were dropped. The added variables were used to further the study on the well-being of the population, construction of principal components, and to see if those variables explain if the population will prefer right, left, or central parties.

The political parties were classified into left, center-left, center-right, and right. The dataset was manipulated, and the percentage of votes for each political party was replaced by the percentage of votes each wing received. The final dataset consisted of 35 variables, and the demographic variables were standardized using a StandardScaler, as were the remaining numerical variables used in the PCA. The percentages for each political block were weighted according to the total voters in each associated municipality. The TotStudEnr was also weighted according to the total population in each municipality.

Principal Component Analysis (PCA) was used to identify the most important variables that contribute to the variation in the dataset. PCA transformed the original data into a new set of variables called principal components. These principal components are linear combinations of the original variables, which capture the maximum amount of variation in the dataset. 

For more information, please refer to the Appendix section of this paper for the final list of variables used in the dataset.