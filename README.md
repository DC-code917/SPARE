**## API Call Patten Generation**

The codes are in data_process/intent_sequence.py



pretrain_dataset_generation includes the following steps:

\1. extract API call patten 





**### Generate vocab**

\```

build_BPE(corpora_path)



"0x", "0x1", "ne", "32.", "kernel32.",
"et", "ad", "getproc", "10", "0xf", "tls"



build_vocab(vocab_path)

\```







**## Model Pretrain**





Model Pretrain

\```

 CUDA_VISIBLE_DEVICES=2,3,4 python3 pre-training/pretrain.py --dataset_path dataset.pt \

​           --vocab_path models/vocab.txt \

​           --output_model_path model.bin \

​           --world_size 3 --gpu_ranks 0 1 2 --master_ip tcp://localhost:8888 \

​           --total_steps 80000 --save_checkpoint_steps 10000 --batch_size 64 \

​           --embedding word_pos_seg --encoder transformer --mask fully_visible --target csmmsm

\```



