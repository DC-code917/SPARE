import os
import json
import logging
import sentencepiece as spm
from time import time

class BPEVocabularyBuilder:
    def __init__(self,
                 vocab_size=50000,
                 model_prefix="vocab",
                 special_tokens=["[PAD]", "[SEP]", "[CLS]", "[UNK]", "[MASK]"]):
        assert vocab_size > len(special_tokens), "vocab_size must be larger than number of special tokens!"
        self.total_vocab_size = vocab_size
        self.model_prefix = model_prefix
        self.special_tokens = special_tokens
        self.model_path = None
        self.tokenizer = None
        self.vocab = None
        self.reverse_vocab = None

    def split_text_into_chunks(self, text, chunk_size=4096):
        chunks = []
        current = ""
        for word in text.split(" "):
            if len(current) + len(word) < chunk_size:
                current += word + " "
            else:
                chunks.append(current.strip())
                current = word + " "
        if current:
            chunks.append(current.strip())
        return chunks

    def train(self, text_data, remove_train_files=True):
        assert isinstance(text_data, str), "text_data must be a single large string."

        # Prepare training file from chunks
        chunks = self.split_text_into_chunks(text_data)
        train_file = f"{self.model_prefix}_train_{int(time())}.txt"
        with open(train_file, "w", encoding="utf-8") as f:
            f.write("\n".join(chunks))

        # Adjusted vocab size = total size - number of special tokens
        adjusted_vocab_size = self.total_vocab_size - len(self.special_tokens)

        # Train SentencePiece BPE tokenizer
        train_cmd = " ".join([
            f"--input={train_file}",
            f"--model_prefix={self.model_prefix}",
            f"--vocab_size={adjusted_vocab_size}",
            "--model_type=bpe",
            "--character_coverage=1.0",
            "--pad_id=-1", "--unk_id=-1", "--bos_id=-1", "--eos_id=-1"
        ])
        logging.warning(f"[+] Training BPE tokenizer with command: {train_cmd}")
        spm.SentencePieceTrainer.Train(train_cmd)

        # Load trained model
        self.model_path = self.model_prefix + ".model"
        self.tokenizer = spm.SentencePieceProcessor(model_file=self.model_path)

        # Build and save vocab
        self.load_vocab()
        self.dump_vocab()

        # Optionally remove training files
        if remove_train_files:
            os.remove(train_file)
            os.remove(f"{self.model_prefix}.vocab")

    def load_vocab(self):
        vocab_file = self.model_prefix + ".vocab"
        with open(vocab_file, "r", encoding="utf-8") as f:
            lines = f.read().strip().split("\n")
            learned_tokens = [line.split("\t")[0] for line in lines]

        # Prepend special tokens
        full_token_list = self.special_tokens + learned_tokens
        if len(full_token_list) > self.total_vocab_size:
            full_token_list = full_token_list[:self.total_vocab_size]

        self.vocab = {token: idx for idx, token in enumerate(full_token_list)}
        self.reverse_vocab = {idx: token for token, idx in self.vocab.items()}

    def dump_vocab(self):
        vocab_json_path = "vocab.json"
        with open(vocab_json_path, "w", encoding="utf-8") as f:
            json.dump(self.vocab, f, indent=4, ensure_ascii=False)
        logging.info(f"[+] Vocabulary saved to {vocab_json_path}")
