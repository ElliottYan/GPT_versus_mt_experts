from analysis_utils import plot, split_json_data, clean_text, XLSReader, avg_tasks, plot_err_cats, plot_radar_chart
import json
import os
from collect_final_json import get_2nd_annotations
from collections import defaultdict

tasks = ["Biomedical.Zh_En", "General.En_Ru", "General.En_Zh", "General.Ru_En", "General.Zh_En", "General.Zh_Hi", "General.Hi_Zh", "Technology.Zh_En"]


def get_task_data_before_anno():
    source_dir = "./data/before_annotate"
    task_data = defaultdict(list)

    for task in tasks:
        task_name = task.lower().replace('_', '-')
        if 'hi' not in task_name:
            fn = f"{source_dir}/{task_name}.xlsx"
            data = XLSReader(fn).data
        else:
            invalid_cnt = 0
            # read json
            fn = f"{source_dir}/{task_name}.jsonl"
            with open(fn, 'r', encoding='utf8') as f:
                lines = f.readlines()
                ds = [json.loads(line.strip()) for line in lines]
            systems = ds[0]['text'].split('\n\n')
            data = defaultdict(list)
            
            expected_length = 5
            for item in ds[1:]:
                splits = item['text'].split('\n\n')
                if len(splits) != expected_length:
                    invalid_cnt += 1
                    continue
                for j in range(expected_length):
                    data[systems[j]].append(splits[j].strip())
            print(f'Invalid Num: {invalid_cnt}')
        task_data[task_name] = data
    for task in task_data:
        item = task_data[task] 
        print(task)
        for sys in item:
            print(f'System: {sys}, Data num: {len(item[sys])}')
    return task_data

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

def get_system2error(annotation_results, data2system, dedup_ids):
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
    task_systems = ["source","senior","medium", "gpt4", "seamless"]
    valid_ids = dedup_ids[task]
    for ids in valid_ids:
        anno_item = annotation_results[task][ids]
        for j, hyp in enumerate(anno_item):
            if hyp['error']:
                w = hyp['weight'] if 'weight' in hyp else 1.0
                system2error[task_systems[j]].append((hyp['error'], w))

    task = 'general.hi-zh'
    task_systems = ["source", "senior", "seamless", "gpt4", "medium"]
    valid_ids = dedup_ids[task]
    for ids in valid_ids:
        anno_item = annotation_results[task][ids]
        for j, hyp in enumerate(anno_item):
            if hyp['error']:
                w = hyp['weight'] if 'weight' in hyp else 1.0
                system2error[task_systems[j]].append((hyp['error'], w))

    return system2error

def read_data_and_plot():
    task_data = get_task_data_before_anno() # except zh-hi and hi-zh
    data2system, dedup_ids = get_data2system(task_data)
    annotation_results = get_2nd_annotations()
    system2error = get_system2error(annotation_results, data2system, dedup_ids)
    
    systems = ['seamless', 'gpt4', 'junior', 'medium', 'senior']

    # zh-hi no need to do this matching.
    # filter annotation results with dedup_ids
    system2task2error = {task.lower().replace('_', '-'): defaultdict(list) for task in tasks}

    for task in annotation_results:
        if 'hi' in task:
            continue
        valid_ids = dedup_ids[task]
        for ids in valid_ids:
            anno_item = annotation_results[task][ids]
            for hyp in anno_item[1:]:
                clean_hyp = clean_text(hyp['text'])
                assert clean_hyp in data2system
                systems = data2system[clean_hyp]
                if hyp['error']:
                    for sys in systems:
                        w = hyp['weight'] if 'weight' in hyp else 1.0
                        system2task2error[task][sys].append((hyp['error'], 1/len(systems)*w))
    
    # process zh-hi and hi-zh specifically
    # for zh-hi and hi-zh, the system position is static
    task = 'general.zh-hi'
    task_systems = ["source","senior","medium", "gpt4", "seamless"]
    valid_ids = dedup_ids[task]
    for ids in valid_ids:
        anno_item = annotation_results[task][ids]
        for j, hyp in enumerate(anno_item):
            if hyp['error']:
                w = hyp['weight'] if 'weight' in hyp else 1.0
                system2task2error[task][task_systems[j]].append((hyp['error'], w))

    task = 'general.hi-zh'
    task_systems = ["source", "senior", "seamless", "gpt4", "medium"]
    valid_ids = dedup_ids[task]
    for ids in valid_ids:
        anno_item = annotation_results[task][ids]
        for j, hyp in enumerate(anno_item):
            if hyp['error']:
                w = hyp['weight'] if 'weight' in hyp else 1.0
                system2task2error[task][task_systems[j]].append((hyp['error'], w))
    
    from label_specification import labels as ERROR_LABELS
    
    # analysis over languages
    lang2sys2err = defaultdict(dict)
    for task in system2task2error:
        systems = ['seamless', 'gpt4', 'junior', 'medium', 'senior']
        if task == 'general.zh-en' or task == 'general.en-zh':
            lang='zh-en'
        elif task == 'general.en-ru' or task == 'general.ru-en':
            lang = 'en-ru'
        elif task == 'general.zh-hi' or task == 'general.hi-zh':
            lang = 'zh-hi'
        else:
            continue
        for i, sys in enumerate(systems):
            if sys not in lang2sys2err[lang]:
                lang2sys2err[lang][sys] = defaultdict(int)
            for errs, weight in system2task2error[task][sys]:
                for err in errs:
                    # if 'Major' in err.label_severity:
                    if 'Minor' not in err.label_severity:
                        lang2sys2err[lang][sys][err.label] += weight
    
    # Plot figures.
    # NOTE: You can use the result dict and conduct other analysis here. 
    
    os.makedirs('./output_figs/')
    
    ignored_errors = {'Non-translation', 'MT Hallucination', 'Untranslated'} # ignore errors appears rarely for clarity.
    y_lim = 10
    for lang in lang2sys2err:
        plot_cnts, plot_errs = [], []
        for i in range(len(systems)):
            cnts = [lang2sys2err[lang][systems[i]][err] for err in ERROR_LABELS]
            plot_cnts.append(cnts)

        cur_systems = systems
        # change name
        err_labels = [it if it != 'Wrong Name Entity & Term' else 'Incorrect NE' for it in ERROR_LABELS]
        # filter plot cnts 
        plot_cnts = [[it[i] for i in range(len(it)) if err_labels[i] not in ignored_errors] for it in plot_cnts]
        err_labels = [it for it in err_labels if it not in ignored_errors]
        # filter seamless
        plot_cnts = plot_cnts[1:]
        cur_systems = cur_systems[1:]
        plot_radar_chart(plot_cnts, err_labels, cur_systems, plot_name=f"{lang}", save_path=f"./output_figs/{lang}_each_error_category.pdf", ylim=y_lim)
    
    # analysis over domains
    domain2sys2err = defaultdict(dict)
    for task in system2task2error:
        systems = ['seamless', 'gpt4', 'junior', 'medium', 'senior']
        if task == 'general.zh-en':
            domain='general'
        elif task == 'biomedical.zh-en':
            domain = 'biomedical'
        elif task == 'technology.zh-en':
            domain = 'technology'
        else:
            continue
        for i, sys in enumerate(systems):
            if sys not in domain2sys2err[domain]:
                domain2sys2err[domain][sys] = defaultdict(int)
            for errs, weight in system2task2error[task][sys]:
                for err in errs:
                    # if 'Major' in err.label_severity:
                    domain2sys2err[domain][sys][err.label] += weight
    
    y_lim = 150
    for domain in domain2sys2err:
        plot_cnts, plot_errs = [], []
        for i in range(len(systems)):
            cnts = [domain2sys2err[domain][systems[i]][err] for err in ERROR_LABELS]
            plot_cnts.append(cnts)

        err_labels = [it if it != 'Wrong Name Entity & Term' else 'Incorrect NE' for it in ERROR_LABELS]
        plot_cnts = [[it[i] for i in range(len(it)) if err_labels[i] not in ignored_errors] for it in plot_cnts]
        err_labels = [it for it in err_labels if it not in ignored_errors]
        # filter seamless
        plot_cnts = plot_cnts[1:]
        cur_systems = systems[1:]
        
        plot_radar_chart(plot_cnts, err_labels, cur_systems, plot_name=f"{domain}", save_path=f"./output_figs/{domain}_each_error_category.pdf", ylim=y_lim)

if __name__ == '__main__':
    read_data_and_plot()