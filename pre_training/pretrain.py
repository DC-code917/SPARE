import os
import sys
sys.path.append(os.getcwd())
import argparse
import torch
import spare.trainer as trainer
from spare.utils.config import load_hyperparam
from spare.opts import *


def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    # Path options
    parser.add_argument("--dataset_path", type=str, default="dataset.pt", help="Path of the preprocessed dataset.")
    parser.add_argument("--vocab_path", default=None, type=str, help="Path of the vocabulary file.")
    parser.add_argument("--spm_model_path", default=None, type=str, help="Path of the sentence piece model.")
    parser.add_argument("--tgt_vocab_path", default=None, type=str, help="Path of the target vocabulary file.")
    parser.add_argument("--tgt_spm_model_path", default=None, type=str, help="Path of the target sentence piece model.")
    parser.add_argument("--pretrained_model_path", type=str, default=None, help="Path of the pretrained model.")
    parser.add_argument("--output_model_path", type=str, required=True, help="Path of the output model.")
    parser.add_argument("--config_path", type=str, default="models/bert/base_config.json", help="Config file of model hyper-parameters.")

    # Training and saving options
    parser.add_argument("--total_steps", type=int, default=100000, help="Total training steps.")
    parser.add_argument("--save_checkpoint_steps", type=int, default=10000, help="Specific steps to save model checkpoint.")
    parser.add_argument("--report_steps", type=int, default=100, help="Specific steps to print prompt.")
    parser.add_argument("--accumulation_steps", type=int, default=1, help="Specific steps to accumulate gradient.")
    parser.add_argument("--batch_size", type=int, default=32, help="Training batch size.")
    parser.add_argument("--instances_buffer_size", type=int, default=25600, help="Buffer size of instances in memory.")
    parser.add_argument("--labels_num", type=int, required=False, help="Number of prediction labels.")
    parser.add_argument("--dropout", type=float, default=0.1, help="Dropout value.")
    parser.add_argument("--seed", type=int, default=7, help="Random seed.")

    # Preprocess options
    parser.add_argument("--tokenizer", choices=["bert", "char", "space"], default="bert", help="Specify the tokenizer.")

    # Model options
    model_opts(parser)
    parser.add_argument("--tgt_embedding", choices=["word", "word_pos", "word_pos_seg", "word_sinusoidalpos"], default="word_pos_seg", help="Target embedding type.")
    parser.add_argument("--decoder", choices=["transformer"], default="transformer", help="Decoder type.")
    parser.add_argument("--pooling", choices=["mean", "max", "first", "last"], default="first", help="Pooling type.")
    parser.add_argument("--target", choices=["bert","bertflow","lm", "mlm", "bilm", "albert", "seq2seq", "t5", "cls", "prefixlm"], default="bert", help="Training target of pretraining model.")
    parser.add_argument("--tie_weights", action="store_true", help="Tie the word embedding and softmax weights.")
    parser.add_argument("--has_lmtarget_bias", action="store_true", help="Add bias on output_layer for lm target.")

    # MOE model options
    parser.add_argument("--is_moe", action="store_true", help="Adopt moe layer.")
    parser.add_argument("--vocab_size", type=int, required=False, help="Number of vocab.")
    parser.add_argument("--moebert_expert_dim", type=int, default=3072, help="Dim of expert, default is ffn.")
    parser.add_argument("--moebert_expert_num", type=int, required=False, help="Number of expert.")
    parser.add_argument("--moebert_route_method", choices=["gate-token", "gate-sentence", "hash-random", "hash-balance", "proto"], default="hash-random", help="moebert route method.")
    parser.add_argument("--moebert_route_hash_list", default=None, type=str, help="Path of moebert hash list file.")
    parser.add_argument("--moebert_load_balance", type=float, default=0.0, help="Gate loss weight.")

    # Masking options
    parser.add_argument("--whole_word_masking", action="store_true", help="Whole word masking.")
    parser.add_argument("--span_masking", action="store_true", help="Span masking.")
    parser.add_argument("--span_geo_prob", type=float, default=0.2, help="Span masking geometric probability.")
    parser.add_argument("--span_max_length", type=int, default=10, help="Max length for span masking.")

    # Optimizer options
    optimization_opts(parser)

    # GPU options
    parser.add_argument("--world_size", type=int, default=1, help="Total number of processes (GPUs) for training.")
    parser.add_argument("--gpu_ranks", default=[], nargs='+', type=int, help="List of ranks of each process.")
    parser.add_argument("--master_ip", default="tcp://localhost:12345", type=str, help="Master IP-Port for training.")
    parser.add_argument("--backend", choices=["nccl", "gloo"], default="nccl", type=str, help="Distributed backend.")

    args = parser.parse_args()

    if args.target == "cls":
        assert args.labels_num is not None, "Cls target requires the number of labels."

    if args.config_path:
        load_hyperparam(args)

    ranks_num = len(args.gpu_ranks)

    if args.world_size > 1:
        assert torch.cuda.is_available(), "No available GPUs."
        assert ranks_num <= args.world_size
        assert ranks_num <= torch.cuda.device_count()
        args.dist_train = True
        args.ranks_num = ranks_num
        print("Using distributed mode for training.")
    elif args.world_size == 1 and ranks_num == 1:
        assert torch.cuda.is_available(), "No available GPUs."
        args.gpu_id = args.gpu_ranks[0]
        assert args.gpu_id < torch.cuda.device_count(), "Invalid GPU ID."
        args.dist_train = False
        args.single_gpu = True
        print(f"Using GPU {args.gpu_id} for training.")
    else:
        assert ranks_num == 0, "GPUs specified but GPU ranks list is empty."
        args.dist_train = False
        args.single_gpu = False
        print("Using CPU mode for training.")

    # 调用 trainer 进行训练
    trainer.train_and_validate(args)


if __name__ == "__main__":
    main()
