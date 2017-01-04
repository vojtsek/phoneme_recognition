#! /usr/bin/env python3
import glob
import os
import sys
import numpy as np
import subprocess
import editdistance as ed

wavdir = sys.argv[1]
trndir = sys.argv[2]

def obtain_trn(trndir, rec):
    orig = ''
    with open('{}/{}.wav.trn'.format(trndir, rec), 'r') as fi:
        line = fi.read().split()
        with open('processed.txt', 'w') as fo:
            for w in line:
                orig += w + ' '
                fo.write('{}\n'.format(w.upper()))
    
    proc = subprocess.Popen(['g2p.py', '--model', '/home/vojtech/ang-hclg/g2p-model-2', '--apply', 'processed.txt'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    transcription = ''
    for trn in proc.communicate()[0].decode().split('\n'):
        if len(trn) == 0:
            continue
        transcription += (trn.split('\t')[1]) + ' '
    return transcription, orig

def get_hypothesis_list(wavdir, rec, n=1):
    proc = subprocess.Popen(['./sample_usage.py', "{}/{}.wav".format(wavdir, rec), str(n)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    hypotheses = []
    for hyp in proc.communicate()[0].decode().split('\n'):
        if len(hyp) < 1:
            continue
        hypotheses.append(hyp)
    return hypotheses

def prepare_data(transcriptions, hypothesis, hyp_file, gold_file, blank_default):
    counter = 0
    for hyp_list, trn in zip(hypothesis, transcriptions):
        counter += 1
        print(counter)
        for i, hypotheses in enumerate(hyp_list):
            with open(hyp_file + "." + str(i), "a") as f:
                f.write("{} ({})\n".format(hypotheses, counter))
        with open(gold_file, "a") as f:
            f.write("{} ({})\n".format(trn, counter))

def eval_pra_file(pra):
    with open(pra, 'r') as f:
        hyp_len = 0
        for line in f:
            if line.startswith('id:'):
                uid = line.split()[1].lstrip('(').rstrip(')')
            if line.startswith('REF:'):
                splitted = line.split()[1:]
                hyp_len = len([sp for sp in splitted if len(sp.strip('*')) > 0])
            if line.startswith('Eval'):
                splitted = line.split()[1:]
                no_s = len([sp for sp in splitted if sp == 'S'])
                no_i = len([sp for sp in splitted if sp == 'I'])
                no_d = len([sp for sp in splitted if sp == 'D'])
                wer = no_d + no_i + no_s
                print('{},{}'.format(uid, wer))

def eval_hypothesis_list(transcriptions, hypotheses, n=1, oracle=True):
    ref = 'trns.lst'
    base_hyp = 'hypothesis.lst'
    SCTK_PATH = os.environ.get('SCTK_PATH', 'sctk/bin')
    prepare_data(transcriptions, hypotheses, base_hyp, ref, '')
    pra_files = []
    for i in range(n):
        hyp = base_hyp + '.' + str(i)
        cmd = ["{}/sclite".format(SCTK_PATH), "-r", ref, "-h", hyp, "-i", "rm", "-o", "pra", "sum"]
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, err = p.communicate(b"")
        rc = p.returncode
        if rc != 0:
            print('Error running sclite')
        else:
            pra_files.append(hyp + '.pra')
    return pra_files
 
if __name__ == '__main__':
    transcriptions = []
    hypothesis_lst = []
    n = 3
    for rec in glob.glob('{}/*.wav'.format(wavdir)):
        print('Recognizing {}'.format(rec))
        rec = os.path.basename(rec).split('.')[0]
        transcription, orig = obtain_trn(trndir, rec)
        hypothesis = get_hypothesis_list(wavdir, rec, n)
        hypothesis_lst.append(hypothesis)
        transcriptions.append(transcription)

    pra_files = eval_hypothesis_list(transcriptions, hypothesis_lst, n)
    for pf in pra_files:
        eval_pra_file(pf)

#    print ('"{}:{}"; WER:{}, {}'.format(orig, transcription, wer, best))
