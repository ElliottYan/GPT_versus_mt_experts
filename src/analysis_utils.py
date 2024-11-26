import matplotlib.pyplot as plt
import numpy as np
import os, math
import jsonlines
import xlrd3
import scipy.stats as stats
import glob
from label_specification import LabelSpecification
from collections import defaultdict

tasks = ["Biomedical.Zh_En", "General.En_Ru", "General.En_Zh", "General.Ru_En", "General.Zh_En", "General.Zh_Hi", "General.Hi_Zh", "Technology.Zh_En"]

def plot(datas, names, systems, plot_name, save_path="", stds=None):
    assert len(datas) == len(names)
    plt.figure(figsize=(8, 6))

    colors = [plt.cm.Blues, plt.cm.Oranges]

    for i in range(len(datas)):
        # Set the width of each bar
        bar_width = 0.25

        # Set the positions of the bars on the x-axis
        r = [x + i*bar_width for x in range(len(systems))]
        # r1 = range(len(systems))
        # r2 = [x + bar_width for x in r1]
        # r3 = [x + bar_width for x in r2]
        cmap = colors[i]
        color = cmap(0.6)

        # Create the bar plot
        plt.bar(r, datas[i], width=bar_width, edgecolor='white', label=names[i], color=color) # color='b', 
        if stds is not None:
            plt.errorbar(r, datas[i], yerr=stds[i], fmt='o', color='gray', capsize=3)
            # for j in range(len(datas)):
                # plt.plot([r[j], bar_positions[j]], [data[j] - error[j], data[j] + error[j]], color='black', linewidth=1)


    # Add labels, title, and legend
    plt.xlabel('Systems')
    plt.ylabel('Number of Errors')
    plt.title(plot_name)
    plt.xticks([r + bar_width for r in range(len(systems))], systems)
    plt.legend()
    plt.gca().yaxis.grid(True, linestyle='--', alpha=0.7)

    # Display the plot
    plt.tight_layout()
    if not save_path:
        plt.show()
    else:
        plt.savefig(save_path)
        
def plot_err_cats(datas, names, systems, plot_name, save_path="", stds=None, ylim=None):
    assert len(datas) == len(names)
    plt.figure(figsize=(8, 6))
    rs = []
    xs = []
    colors = [plt.cm.Reds, plt.cm.Greens, plt.cm.Oranges, plt.cm.Purples, plt.cm.RdPu, plt.cm.YlGnBu]
    
    for i in range(len(systems)):
        # Set the width of each bar
        bar_width = 0.15
        
        # in this plot function, data is given in transpose order
        r = [i + x*bar_width for x in range(len(datas[i]))]
        # Create the bar plot
        cmap = colors[i]
        color = cmap(np.linspace(0.8, 0.4, len(r)))
        bars = plt.bar(r, datas[i], width=bar_width, edgecolor='white', label=systems[i], color=color)

        x_labels = []
        for j in range(len(names[i])):
            x_labels.append(names[i][j])
        rs.extend(r)
        xs.extend(x_labels)

    if ylim is not None:
        plt.ylim(0, ylim)
    # Add labels, title, and legend
    # plt.xlabel('Systems')
    plt.ylabel('Number of Errors')
    plt.title(plot_name)
    # Create x-axis labels for each system
    # print(rs)
    # print(xs)
    plt.gca().yaxis.grid(True, linestyle='--', alpha=0.7)

    plt.xticks(rs, xs, rotation=70)

    plt.legend()

    # Display the plot
    plt.tight_layout()
    if not save_path:
        plt.show()
    else:
        plt.savefig(save_path)

def plot_radar_chart(datas, names, systems, plot_name, save_path="", stds=None, ylim=None, max_val=None):
    # Set the number of variables and their labels
    categories = names
    num_vars = len(categories)

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    assert len(datas) == len(systems)
    plt.rcParams.update({'font.size': 11})
    
    # colors = ['blue', 'orange', 'green', 'red', 'purple']
    
    if max_val is None:    
        # we should first take the norm
        maxes = [0] * len(names)
        for i in range(len(datas)):
            for j in range(len(datas[i])):
                maxes[j] = max(maxes[j], datas[i][j])
    else:
        maxes = [max_val] * len(names)
    # add maxes value to categories
    categories = [f"{c}({math.ceil(maxes[j])})" for j, c in enumerate(categories)]
    
    for i in range(len(datas)):
        # Set the values for each variable
        values = datas[i]
        try:
            assert len(values) == num_vars
        except:
            breakpoint()

        # Calculate the angles for each variable
        angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
        angles += angles[:1]  # Repeat the first angle to close the plot

        # Normalize the values to a 0-1 scale
        values_norm = [val / maxes[j] if maxes[j]!=0 else 0 for j, val in enumerate(values)]
        # use 1-value
        # values_norm = [1.0 - v for v in values_norm]
        values_norm += values_norm[:1]  # Repeat the first value to close the plot
        if max(values) == 0:
            continue

        # Create the radar chart
        ax.plot(angles, values_norm, 'o-', linewidth=2, label=systems[i], color=f"C{i}")#colors[i], alpha=0.8)
        ax.fill(angles, values_norm, alpha=0.25, color=f"C{i}")
        ax.set_thetagrids(np.degrees(angles[:-1]), categories)
    
    # ax.set_title(plot_name)
    ax.set_rlabel_position(0)
    ax.set_rlim(-0.1, 1)
    # Display the plot
    plt.tight_layout()
    plt.legend()

    # Display the chart
    if not save_path:
        plt.show()
    else:
        plt.savefig(save_path)


def split_text_by_translations_v2(text, labels, split='\n 译'):
    result = []
    start = 0
    while True:
        pos = text.find(split, start)
        if pos == -1:
            break
        result.append(
            {
                "text": text[start: pos].strip(),
                "start": start,
                "end": pos-1,
                "error": []
            }
        )
        start = pos + len(split)

    result.append(
        {
            "text": text[start: len(text)],
            "start": start,
            "end": len(text) - 1,
            "error": []
        }
    )
    # augment the labels with additional informations 
    for label in labels:
        for i in range(len(result)):
            if label[0] >= result[i]["start"] and label[1] <= result[i]["end"]:
                err = LabelSpecification(label[2])
                err.source = result[0]['text']
                err.hyp = result[i]['text']
                err.label_text = text[label[0]:label[1]]
                err.label_span = (label[0], label[1])
                err.label_weight = len(err.label_text) / (result[i]['end'] - result[i]['start'])
                # breakpoint()
                result[i]["error"].append(err)
                if err.label == 'Unnatural Flow': assert err.label_severity == ""
                if err.label == 'Non-translation': assert err.label_severity == ""

    return result


def preprocess_annotations(annotations):
    # preprocess for different level of scores
    for i, ann in enumerate(annotations):
        for j, span in enumerate(ann['spans']):
            label = span['label']
            label = label.replace('(Major)', '').strip()
            label = label.replace('(Minor)', '').strip()
            if label == 'Grammer': label = "Grammar"
            if label == 'Untrasnalted': label = 'Untranslated'
            annotations[i]['spans'][j]['label'] = label
    return annotations

def split_json_data(fn, ds=None):
    if ds is None:
        data = []
        with jsonlines.open(fn) as reader:
            for json_line in reader:
                data.append(json_line)
    else:
        data = ds
    data_len = -1
    annotations = []
    invalid_cnt = 0
    for i, item in enumerate(data):
        if "Hi" in fn:
            split_word = "\n\n"
            target_len = 5
        else:
            split_word = "\n 译"
            target_len = 6
        new_item = split_text_by_translations_v2(item['text'], item['label'], split=split_word)
        if len(new_item) != target_len:
            for i in range(len(new_item)):
                if new_item[i]['text'].startswith('Please') or new_item[i]['text'].startswith('请'):
                    break
            tmp_txt = new_item[i-1]['text'] + '\n\n' + new_item[i]['text']
            tmp = {
                'text' : tmp_txt,
                'start': new_item[i-1]['start'], 
                'end': new_item[i]['end'],
                'error': new_item[i-1]['error'] + new_item[i]['error']
            }
            new_item = new_item[:i-1] + [tmp,] + new_item[i+1:]
            assert len(new_item) == target_len
        
        for k in range(len(new_item)):
            new_item[k]['id'] = item['id']
            if "annotator" in item:
                new_item[k]['annotator'] = item['annotator']
        
        if data_len == -1:
            data_len = len(new_item)
        try:
            assert data_len == len(new_item)
        except:
            invalid_idx = -1
            for j in range(len(new_item)):
                if new_item[j]['text'].startswith('Please note that'):
                    invalid_idx = j
                elif new_item[j]['text'].startswith('请注意'):
                    invalid_idx = j
            if invalid_idx != -1:
                new_item.pop(invalid_idx)
            else:
                invalid_cnt += 1
                continue
        annotations.append(new_item)
    print(f"{invalid_cnt} invalid data found in {fn}")
    return annotations


class XLSReader(object):
    def __init__(self, data_file):
        from collections import defaultdict
        self.data = defaultdict(list)
        sheets = xlrd3.open_workbook(data_file)
        sheet = sheets.sheet_by_index(0)
        # first row is the label
        systems = sheet.row_values(0)
        for row_index in range(1, sheet.nrows):
            row_data = sheet.row_values(row_index)
            for j in range(len(row_data)):
                self.data[systems[j]].append(row_data[j].strip())

def clean_text(txt):
    if ':' in txt:
        pos = txt.find(':')
        return txt[pos+1:].strip()
    else:
        return txt.strip()

def avg_tasks(counts, weights):
    assert len(counts) == len(weights)
    return [counts[j]/weights[j] for j in range(len(counts))]

def get_1st_annotation_results():
    # severity
    annotation_results = {}
    direc = "/Users/elliott/westlake/Human_GPT4_Translation/annotating_result"
    rater = 0
    for task in tasks:
        task_name = task.replace('_', '-')
        for fn in os.listdir(f"{direc}/{task_name}/"):
            json_path = f"{direc}/{task_name}/{fn}"
            ds = split_json_data(json_path)
            for item in ds:
                item['rater'] = f'rater{rater}'
            rater += 1
        annotation_results[task_name] = ds
    return annotation_results

def get_data2system(task_data):
    data2system = defaultdict(list)
    dedup_ids = defaultdict(set)

    for task in task_data:
        src = task_data[task]['source']
        seen_src = set()
        for idx in range(len(src)):
            print(idx)
            cur_src = src[idx]
            if cur_src in seen_src:
                continue
            else:
                seen_src.add(cur_src)
                dedup_ids[task].add(idx)
            for system in task_data[task]:
                if system == 'source': continue
                hyp = task_data[task][system][idx]
                data2system[hyp].append(system)
    return data2system, dedup_ids

def get_annotation_results():
    # severity
    annotation_results = {}
    direc = "/Users/elliott/westlake/Human_GPT4_Translation/annotating_result"
    for task in tasks:
        task_name = task.lower().replace('_', '-')
        json_path = f"{direc}/{task}.all.jsonl"
        ds = split_json_data(json_path)
        annotation_results[task_name] = ds
    return annotation_results

# zh-hi no need to do this matching.
# filter annotation results with dedup_ids
def get_system2error(annotation_results, data2system, dedup_ids):
    from collections import defaultdict
    system2error = defaultdict(list)

    for task in annotation_results:
        if 'hi' in task:
            continue
        valid_ids = dedup_ids[task]
        for ids in valid_ids:
            anno_item = annotation_results[task][ids]
            for hyp in anno_item[1:]:
                clean_hyp = clean_text(hyp['text'])
                try:
                    assert clean_hyp in data2system
                except:
                    breakpoint()
                systems = data2system[clean_hyp]
                if hyp['error']:
                    for sys in systems:
                        w = hyp['weight'] if 'weight' in hyp else 1.0
                        system2error[sys].append((hyp['error'], 1/len(systems) * w))

    # process zh-hi and hi-zh specifically
    # for zh-hi and hi-zh, the system position is static

    task = 'general.zh-hi'
    task_systems = ["source","senior","medium","seamless", "gpt4"]
    valid_ids = dedup_ids[task]
    for ids in valid_ids:
        anno_item = annotation_results[task][ids]
        for j, hyp in enumerate(anno_item):
            if hyp['error']:
                system2error[task_systems[j]].append((hyp['error'], 1))

    task = 'general.hi-zh'
    task_systems = ["source", "senior", "seamless", "gpt4", "medium"]
    valid_ids = dedup_ids[task]
    for ids in valid_ids:
        anno_item = annotation_results[task][ids]
        for j, hyp in enumerate(anno_item):
            if hyp['error']:
                system2error[task_systems[j]].append((hyp['error'], 1))
    
    return system2error

def confidence_interval(sample_mean, sample_std, sample_size, confidence_level=0.95):
    # Calculate the standard error
    std_error = sample_std / (sample_size ** 0.5)
    
    # Find the t-score for the desired confidence level
    t_score = stats.t.ppf((1 + confidence_level) / 2, df=sample_size - 1)
    
    # Calculate the margin of error
    margin_of_error = t_score * std_error
    
    # Calculate the lower and upper bounds of the confidence interval
    lower_bound = sample_mean - margin_of_error
    upper_bound = sample_mean + margin_of_error
    
    return lower_bound, upper_bound
