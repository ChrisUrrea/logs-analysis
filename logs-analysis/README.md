# Deep Learning Pipeline

An implementation of a deep learning pipeline that starts from 
the raw data files and ends with final model fitting and testing.

## Program Summary:
*Main Files:
Modules are meant to run sequentially, files start with `#_` syntax 
where the first number represents the step i.e. `1_` being the first step.
  * 1_pool_data.py:
    *Reads all the raw data tables from `raw_path` and joins them into one pooled
    dataframe.
    *labels `items` by unique `ITEM_KEYS` combinations, then filtering 
    all items by recent activity `THRESH_DATE` and number of transactions `THRESH_SIZE`.
    *Saves the final dataframe as `ABT_filtered.feather`
    
  * 2_preprocess_items.py:
    * Reads `ABT_filtered.feather` and groups it by each item dataframes to be run in parallel
    * preprocesses each item dataframe by applying function `item_transforms`, 
      the list of transformations, to each item
    * Joins back all item dataframes to one dataframe, saved as `ABT_preprocessed.feather` to `output_path`
    
  * 3_encode_and_split.py:
    * Reads `ABT_filtered.feather` and finalizes the list of categorical and continuous
      variables to be used for modeling
    * converts and maps each variable datatype 
    * splits the final preprocessed data into train, valid, and test dataframes
      and saves each split as `ABT_train.feather`, `ABT_valid.feather`, `ABT_test.feather`
      to output_path.
      
  * 4_optimize_model.py:
    * Reads in train and valid data from `train_path` and `valid_path`, and optionally 
      a hyperparameters dictionary from `hp_path` and a model from `load_model`
    * applies the list of `transforms` in `hyperparameters` to train and valid data, 
      appropriately, and creates a dataloader to train model in batches.
    * Creates or loads the `model` from the architecture given in `hyperparameters` dictionary 
    * Optimizes the model by 1-Cycle method, where cycle lengths and parameters 
      are specified in `hyperparameters`
    * After each cycle, saves the plots of the cycles `output_path/` and model 
      to `output_path/models`, keeping track of the historically best performing 
      model as `best_model.pth`
    * Evaluates the results on validation set in `eval_valid_results` per item,
      by scoring and plotting each items predictions
    * Saves `item_valid_scores.csv` containing a list of items, the mean 
      of item's target column and the different scores for each item to `output_path`

      * Optimization program is meant to be repeated until the best performing model hyperparameters
        on the validation set are found, then proceed to evaluating the model's true predictive power
        on the test set
      
  * 5_test_model.py:
    * Reads in the train, valid and test data from `train_path`, `valid_path` and `test_path`,
    as well as the best hyperparameters found in the `4_optimize_model` from `hp_path`
    * Concatenates the train and valid data as full train data, and applies the list of `transforms` 
      in `hyperparameters` to full train data and test data, appropriately, and creates the dataloader.
    * Recreates a model using the `hyperparameters` found in optimization module and trains the model 
      up to the `best_cycle` found when optimizing the model on the validation set.
    * Evaluates the final test results, through the `eval_test_results` function, per item,
      by scoring, plotting each items predictions to `output_path/plot_preds` and `output_path/test_preds`
    * Saves `item_test_scores.csv` containing a list of items, the mean 
      of item's target column and the different scores for each item to `output_path`

  Utility Files:
  1. utils.py - utility functions for all the data preprocessing work
  2. ts_model.py - utility functions and extensions for the model
  3. ts_data.py - utility functions for data transforms, scoring and plotting

## Metadata:

The pipeline was coded as DRY and flexible (soft-coded) as I could make it. Although 
there is as always many things that can be improved. Two key components that make the program run sequentially
with minimal changes are the metadata dictionary that is created in the first module `1_pool_data.py` and is used 
throughout all modules. It contains all the small details of the program such as 
`cat_vars` and `cont_vars` representing categorical and continuous variables respectively,
that get repeated often in a pipeline.

For example the metadata dict has values
    *1. 'FUTURE_STEPS' = 14, # equivalent to shifting target two weeks into future
    *2. 'PREDICTION_WINDOW' = 14 # equivalent to aggregating target 
Which when the target is created in `2_preprocess_items.py`, it reads these two values 
and creates the target variable as the aggregate two weeks ('PREDICTION_WINDOW'=14)  
of the dependent variable `dep_var` ('SALES'), two weeks into the future ('FUTURE_STEPS' = 14).

If for example, the target desired was a one week aggregate of the dependent variable,
one week into the future - then the only change that would need to be done is to 
change the values of the metadata dictionary to:
  * 'FUTURE_STEPS' = 7, # program will read this as shifting target one week into future
  * 'PREDICTION_WINDOW' = 7 # program will take one-week aggregate of the target

This must be done at the initialization of the first module i.e. `1_pool_data.py` as
metadata dictionary handling is done automatically, being initialized/loaded  in the 
first module `1_pool_data.py` and saved at the end of each module to `metadata`
directory metadata dictionary saved to a folder `metadata`.

## Hyperparameters:

As the metadata dictionary contains all the key variables of the pipeline, 
the hyperparameters dictionary, starting from `4_optimize_model.py` contains all the key variables 
of the model. Everything that is used to create and train the model is stored and can be retrieved 
from the hyperparameters dictionary - from the architecture and learning rates used to the mean and
standard deviations applied to each continuous variables and the encodings of each categorical variable. 
For example if I wanted to change the model architecture from 2 layers of 1000 & 500 nodes to 3 layers
700, 500 and 300 nodes, I would simply modify the `layers` in `hyperparameters` from:
          *'layers' : [1000, 500], 
to:
          *'layers': [700, 500, 300]

This not only makes changing any model hyperparameter very easy, but is critical so that every parameter which 
was used to find the validation results can be replicated on the test set without explicit coding. 
Further it serves as a "hard copy" of all the hyperparameter values that constitute the 
how the model was created & optimized.

## Logs
All programs are logged by what I thought was important. Logs of each programs
can be found in `logs` folder, with their respective file name.

## Tech/Prerequisites
  * python version > 3.6
  * pyarrow - pip install pyarrow
  * torch - pip3 install torch
  * torchvision - pip3 install torchvision
  * fastai v1.0.3- pip install https://github.com/fastai/fastai/archive/master.zip
  
## How to Run Example
command:
* $ python 1_pool_data.py -i raw_data -o preprocess_data
result: 
* Metadata dictionary is initialized or custom one is loaded.
* The joined, item labelled and filtered dataframe is saved as `ABT_filtered.feather`  to `preprocess_data`
* CSV file containing each item id and it's unique item key pair `item_groups data.csv` is saved to `preprocess_data`

command:
* $ python 2_preprocess_items.py -i preprocess_data/ABT_filtered.feather -hd holidays.csv -o preprocess_data
result: 
  * The `ABT_filtered.feather` dataframe with the applied item transformations is saved as `ABT_preprocessed.feather` to `preprocess_data`
  * a preprocess sample of `items` are saved to `preprocess_data/sample` as csv files for evaluation

command:
$ python 3_encode_and_split.py - i preprocess_data/ABT_preprocessed.feather -o final_data
result: 
  * Finalizes the `cat_vars` and `cont_vars` to be used for modeling
  * `ABT_preprocessed.feather` is split according to `{set}_CUT` date into files `ABT_train.feather`, `ABT_valid.feather`, `ABT_test.feather` to `final_data`
  * a well as a sample of `items` for each set are saved to `final_data/{set}_sample` as csv files for evaluation

command:
$ python 4_optimize_model.py -t final_data/ABT_train.feather -v final_data/ABT_valid.feather -o val_results
result: 
* `hyperparameters` dictionary is initialized or custom one is loaded.
* Model is created and optimized on train data in cycles according to parameter values set in `hyperparameters`
* Each cycle model is saved to `val_results/models` with the best model on the validation tracked as `best_model`
* Each cycle's performance statistics -learning rates, losses and metrics-  plotted and saved to `val_results/cycle_plots`
* Each unique item dataframe with their respective validation predictions saved to `val_results/val_preds`
* Each unique item's targets plotted against validation predictions saved to `val_results/plot_preds`
* CSV file `item_valid_scores.csv` containing each item id with it's target value mean and score metrics on test set
* The latest hyperparameters of optimization saved as `latest_hyperparameters.pkl` containing `best_cycle` value 

command:
$ python 5_test_model.py -t final_data/ABT_train.feather -v final_data/ABT_valid.feather  -ts final_data/ABT_test.feather -hp val_results -o test_results
result: 
* Hyperparameters dictionary from `val_results` is read and used to recreate best model found in validation
* Model is trained until the cycle of hyperparameter's `best_cycle ` - the last cycle the resulted in the best performing 
  model on the validation set.
* similar to optimize model but with this as the final test evaluation
* Each cycle's performance statistics -learning rates, losses and metrics-  plotted and saved to `test_results/cycle_plots`
* Each unique item dataframe with their respective validation predictions saved to `test_results/test_preds`
* Each unique item's targets plotted against test predictions saved to `test_results/plot_preds`
* CSV file `item_test_scores.csv` containing each item id with it's target value mean and score metrics on test set
* The final hyperparameters of the model saved as `final_hyperparameters.pkl` 


