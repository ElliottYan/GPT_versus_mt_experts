This is the repo for paper ["Benchmarking GPT-4 against Human Translators: A Comprehensive Evaluation Across Languages, Domains, and Expertise Levels"](https://www.arxiv.org/abs/2411.13775)

## Repo Structure
- ./data contains the data before annotation and after annotation.
- ./src contains code that can be used to analyze our data. 

### Example for running our code. 
```bash
# plot the radar plot for our results.
python src/data_utils.py

# generate the qualitative study results, which categorize all errors for different systems. 
python src/qualitative_study.py
```

The basic code for extracting and collecting results is the same. You can reuse them and add your own analytic code.
