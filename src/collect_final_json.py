import jsonlines
import copy
from analysis_utils import split_json_data, get_system2error, get_data2system

# tasks = ["Biomedical.Zh_En", "General.En_Ru", "General.En_Zh", "General.Ru_En", "General.Zh_En", "General.Zh_Hi", "General.Hi_Zh", "Technology.Zh_En"]

# ignore hi for now.
tasks = ["Biomedical.Zh_En", "General.En_Ru", "General.En_Zh", "General.Ru_En", "General.Zh_En", "Technology.Zh_En",  "General.Zh_Hi", "General.Hi_Zh"]

label_span = {
    'biomedical.zh-en': {'annotator1': [(1,125)], 'annotator2': [(201, 250), (326,400)]},
    'general.zh-en': {'annotator1': [(1,125)], 'annotator2': [(201, 250), (326,400)]},
    'general.en-zh': {'annotator1': [(1,125)], 'annotator2': [(201, 250), (326,400)]},
    'general.ru-en': {'annotator1': [(1,125)], 'annotator2': [(201, 250), (326,400)]},
    'general.en-ru': {'annotator1': [(1,125)], 'annotator2': [(201, 250), (326,400)]},
    'general.zh-hi': {'annotator1': [(1,200)], 'annotator2': [(201, 250)]},
    'general.hi-zh': {'annotator1': [(1,199)], 'annotator2': [(200, 249)]},
    'technology.zh-en': {'annotator1': [(1,200)], 'annotator2': [(201, 250)]},
}

def norm_task_name(task):
    return task.lower().replace('_', '-')

def load_json(fn):
    data = []
    with jsonlines.open(fn) as reader:
        for json_line in reader:
            data.append(json_line)
    return data

def get_2nd_annotations(merge=True):
    directory = "./data/after_annotate/"
    annotation_results_v2 = {}
    for task in tasks:
        task_name = norm_task_name(task)
        path = f"{directory}/{task_name}/all.jsonl"
        ds = load_json(path)
        cur_span = label_span[task_name]
        ann1_span = cur_span['annotator1']
        ann2_span = cur_span['annotator2']
        mid = len(ds) // 2
        ann1_span_set, ann2_span_set = set(), set()
        for span in ann1_span:
            ann1_span_set = ann1_span_set.union(set(range(span[0]-1, span[1])))
        for span in ann2_span:
            ann2_span_set = ann2_span_set.union(set(range(span[0]-1-mid, span[1]-mid)))
        
        if merge is True:    
            json_ds = []
            for ii in range(mid):
                new_ds = {}
                if ii in ann1_span_set and ii in ann2_span_set:
                    ann1 = ds[ii]['label']
                    ann2 = ds[ii+mid]['label']
                    new_ds['text'] = ds[ii]['text']
                    assert ds[ii]['text'] == ds[ii+mid]['text']
                    new_ds['id'] = ds[ii]['id']
                    new_ds['label'] = ann1 + ann2
                    new_ds['weight'] = 0.5
                else:
                    if ii in ann1_span_set:
                        new_ds = copy.deepcopy(ds[ii])
                    elif ii in ann2_span_set:
                        new_ds = copy.deepcopy(ds[ii+mid])
                    else:
                        raise
                    new_ds['weight'] = 1.0
                json_ds.append(new_ds)
        else:
            json_ds = []
            for ii in range(mid):
                # new_ds = {}
                    # ann1 = ds[ii]['label']
                    # ann2 = ds[ii+mid]['label']
                    # new_ds['text'] = ds[ii]['text']
                    # assert ds[ii]['text'] == ds[ii+mid]['text']
                    # new_ds['id'] = ds[ii]['id']
                    # new_ds['label'] = ann1 + ann2
                    # new_ds['weight'] = 0.5
                if ii in ann1_span_set:
                    new_ds = copy.deepcopy(ds[ii])
                    new_ds['annotator'] = 1
                    new_ds['id'] = ii
                    new_ds['weight'] = 0.5 if ii in ann2_span_set else 1.0
                    json_ds.append(new_ds)
                if ii in ann2_span_set:
                    new_ds = copy.deepcopy(ds[ii+mid])
                    new_ds['annotator'] = 2
                    new_ds['id'] = ii
                    new_ds['weight'] = 0.5 if ii in ann1_span_set else 1.0
                    json_ds.append(new_ds)
                # json_ds.append(new_ds)
        
        # parse into annotation results
        annotation_results_v2[task_name] = split_json_data(task, ds=json_ds)
        # copy weight back
        assert len(annotation_results_v2[task_name]) == len(json_ds)
        for i in range(len(json_ds)):
            anno_item = annotation_results_v2[task_name][i]
            for j in range(len(anno_item)):
                annotation_results_v2[task_name][i][j]['weight'] = json_ds[i]['weight']
    return annotation_results_v2