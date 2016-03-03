import json
import os
from fileoperations.fileoperations import get_filenames_in_dir
from sklearn import cross_validation


def stratified_fold(data_dir, annotation_file, n_folds=10, save_file=''):
    modes = get_mode_names(data_dir)
    [file_paths, base_folders, file_names] = get_filenames_in_dir(data_dir, keyword='*.pitch')

    with open(annotation_file, 'r') as a:
        annotations = json.load(a)

    file_modes = [os.path.basename(b) for b in base_folders]
    mbids = [os.path.splitext(f)[0] for f in file_names]
    tonics = []
    for m in mbids:
        for a in annotations:
            if a['mbid'] == m:
                tonics.append(a['tonic'])

    # get the stratified folds
    mode_idx = [modes.index(m) for m in file_modes]
    skf = cross_validation.StratifiedKFold(mode_idx, n_folds=n_folds, shuffle=True)

    folds = dict()
    for ff, fold in enumerate(skf):
        folds['fold' + str(ff)] = {'train': [], 'test': []}
        for tr_idx in fold[0]:
            folds['fold' + str(ff)]['train'].append({'file': file_paths[tr_idx], 'mode': file_modes[tr_idx],
                                                     'tonic': tonics[tr_idx], 'mbid': mbids[tr_idx]})
        for te_idx in fold[1]:
            folds['fold' + str(ff)]['test'].append({'file': file_paths[te_idx], 'mode': file_modes[te_idx],
                                                    'tonic': tonics[te_idx], 'mbid': mbids[te_idx]})

    # save the folds to a file if specified
    if save_file:
        with open(save_file, 'w') as f:
            json.dump(folds, f, indent=2)

    return folds


def get_mode_names(data_dir):
    # check if the folder exists
    if not os.path.isdir(data_dir):
        print "> Directory doesn't exist!"
        return []

    return [x[1] for x in os.walk(data_dir)][0]
