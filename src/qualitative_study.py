from analysis_utils import plot, split_json_data, clean_text, XLSReader, avg_tasks, plot_err_cats, plot_radar_chart
from collect_final_json import get_2nd_annotations
from data_utils import get_task_data_before_anno, get_data2system, get_system2error, tasks
from collections import defaultdict
import os
import json

if __name__ == "__main__":
    task_data = get_task_data_before_anno() # except zh-hi and hi-zh
    data2system, dedup_ids = get_data2system(task_data)
    annotation_results = get_2nd_annotations()
    system2error = get_system2error(annotation_results, data2system, dedup_ids)
    system2task2error = {task.lower().replace('_', '-'): defaultdict(list) for task in tasks}
    
    
    for task in annotation_results:
        sys2error = defaultdict(list)
        output_dir = f'./qualitative_study/{task}/'
        os.makedirs(output_dir, exist_ok=True)
        # if not ('general.zh-en' in task or 'general.en-zh' in task):
            # continue
        valid_ids = dedup_ids[task]
        for ids in valid_ids:
            anno_item = annotation_results[task][ids]
            for hyp in anno_item[1:]:
                clean_hyp = clean_text(hyp['text'])
                try:
                    assert clean_hyp in data2system
                except:
                    continue
                systems = data2system[clean_hyp]
                if hyp['error']:
                    for sys in systems:
                        for err in hyp['error']:
                            new_item = {
                                'source': err.source,
                                'hyp': err.hyp,
                                'label_text': err.label_text
                            }
                            sys2error[f"{sys}-{err.label}"].append(new_item)
                            # print(new_item)
        for key in sys2error:
            with open(f"{output_dir}/{key}.json", 'w', encoding='utf8') as f:
                json.dump(sys2error[key], f, indent=4, ensure_ascii=False)