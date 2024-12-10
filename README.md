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

## Citation
If you find this useful in your research, please consider cite our paper:

```
@misc{yan2024benchmarkinggpt4humantranslators,
      title={Benchmarking GPT-4 against Human Translators: A Comprehensive Evaluation Across Languages, Domains, and Expertise Levels}, 
      author={Jianhao Yan and Pingchuan Yan and Yulong Chen and Jing Li and Xianchao Zhu and Yue Zhang},
      year={2024},
      eprint={2411.13775},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2411.13775}, 
}
```
