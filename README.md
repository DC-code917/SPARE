### API Call Patten Generation

The codes are in data_process/intent_sequence.py




### Generate vocab
```
build_BPE(corpora_path)
build_vocab(vocab_path)
```

"0x", "0x1", "ne", "32.", "kernel32.",
"et", "ad", "getproc", "iti", "0xf", "al"

## Model Pretrain
Pretrain Input Generation
```
python3 pre-training/preprocess.py --corpus_path corpus.txt \
​             --vocab_path models/vocab.txt --seq_length 1024 \
​             --dataset_path dataset.pt --processes_num 80 --target csmmsm
```
Model Pretrain
```
 CUDA_VISIBLE_DEVICES=2,3,4 python3 pre-training/pretrain.py --dataset_path dataset.pt \
​           --vocab_path models/vocab.txt \
​           --output_model_path model.bin \
​           --world_size 3 --gpu_ranks 0 1 2 --master_ip tcp://localhost:8888 \
​           --total_steps 90000 --save_checkpoint_steps 10000 --batch_size 64 \
​           --embedding word_pos_seg --encoder transformer --mask fully_visible --target csmmsm
```


### Data Augmentation
```
enhance_based_data(
    path="./original_data/",
    new_file_path="./augmented_data/",
    enhance_factor=3
)
```
## Model Finetuning

```
CUDA_VISIBLE_DEVICES=1 python3 fine-tuning/run_classifier.py --vocab_path models/vocab.txt \
                                   --train_path train.tsv \
                                   --dev_path valid.tsv \
                                   --test_path test.tsv \
                                   --pretrained_model_path pretrain_model.bin \
                                   --output_model_path models/finetuned_model.bin\
                                   --epochs_num 4 --earlystop 4 --batch_size 128 --embedding word_pos_seg \
                                   --encoder transformer --mask fully_visible \
                                   --seq_length 1024 --learning_rate 6e-5
```

Note: this code is based on [UER-py](https://github.com/dbiir/UER-py). Many thanks to the authors.
