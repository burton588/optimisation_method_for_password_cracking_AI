import sys

import os
import argparse
import torch
from transformers import GPT2LMHeadModel, GPT2Config
from datasets import load_dataset, Dataset
from pathlib import Path

from transformers import RobertaTokenizerFast, Trainer, TrainingArguments

import numpy as np
import random

import time
from datetime import timedelta
import yaml
import json
import shutil

# Relative import from utils
from utils import dotdict, PasswordDataCollator
#from huggingface_hub import login


if __name__ == "__main__":
    
    # Load config from file
    parser = argparse.ArgumentParser()
    parser.add_argument("--config_path", help="path to yaml config", type=str, required=True)
    parser.add_argument("--train_data_path", help="path to training data", type=str, required=True)
    args = parser.parse_args()
    
    with open(args.config_path) as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
        
    args = dotdict(config["config_args"])
    model_args = dotdict(config["model_args"])
    training_args = dotdict(config["training_args"])
    training_args["seed"] = args.seed
    
    # Init random seeds
    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)

    #if not args.checkpoint_path and os.path.exists(training_args.output_dir):
       # shutil.rmtree(training_args.output_dir)
    #Path(training_args.output_dir).mkdir(parents=True, exist_ok=True)

    # Declare constants
    TOKENIZER_MAX_LEN = 2*args.maxchars + 3 # Additional characters for start and end of password tokens
    
    # Load tokenizer
    print("===> Loading tokenizer")
    tokenizer = RobertaTokenizerFast.from_pretrained(args.tokenizer_path, 
                                                      max_len=TOKENIZER_MAX_LEN,
                                                      padding="max_length", 
                                                      truncation=True,
                                                      do_lower_case=False,
                                                      strip_accents=False,
                                                      mask_token="<mask>",
                                                      unk_token="<unk>",
                                                      pad_token="<pad>",
                                                      additional_special_tokens=["<sep>"],
                                                      truncation_side="right")
    
    # Define dataloader
    print("===> Loading data")
    
    def preprocess_function(entries):
        """
        This function tokenizes a list of seed words and passwords. 
        It combines each seed word with its corresponding password.
        """
        to_tokenize = []
        seed_words = entries['seed_words']
        passwords = entries['passwords']

        for index, seed_word in enumerate(seed_words):  # Skip the first element which is an integer
            for password_for_seed_word in passwords[index]:
                to_tokenize.append(f'<s>{seed_word[:args.maxchars]}<sep>{password_for_seed_word[:args.maxchars]}</s>')
        return tokenizer(to_tokenize, 
                         truncation=True, 
                         padding="max_length", 
                         max_length=TOKENIZER_MAX_LEN, 
                         add_special_tokens=False, 
                         return_special_tokens_mask=False)
    
    # Load your dataset
    data = {'seed_words': [], 'passwords': []}
    with open(args.train_data_path, 'r', encoding='utf-8', errors='ignore') as file:
        loaded_data = json.load(file)
        for seed_word, passwords in loaded_data.items():
            data['seed_words'].append(seed_word)
            data['passwords'].append(passwords[1])
            #for password in passwords[1]:  # Skip the first element which is an integer
            #    data['password'].append(password)

    dataset = Dataset.from_dict(data)
    print("Dataset loaded with {} entries".format(len(dataset)))
    
    if args.subsample > 0:
        print("Subsampling dataset to {} random entries".format(args.subsample))
        dataset = dataset.select([i for i in range(500000, args.subsample)])
 

    # Process data
    print("===> Processing data")
    tokenized_datasets = dataset.map(preprocess_function, batched=True, remove_columns=dataset.column_names)
    tokenized_datasets = tokenized_datasets.shuffle(seed=args.seed)
    
    # Format data
    tokenized_datasets.set_format(type="torch")
    
    print("===> Initializing model")

    config = GPT2Config(
        vocab_size=tokenizer.vocab_size,
        bos_token_id=tokenizer.bos_token_id,
        eos_token_id=tokenizer.eos_token_id,
        **model_args
    )
    
    if args.checkpoint_path:
        print(f"Loading model from checkpoint {args.checkpoint_path}")
        model = GPT2LMHeadModel.from_pretrained(args.checkpoint_path)
    else:
        model = GPT2LMHeadModel(config)

    #model = GPT2LMHeadModel.from_pretrained(MODEL_PATH, token=hf_token)
    print("Model initialized with {} parameters".format(sum(t.numel() for t in model.parameters())))
    
    print("===> Preparing training")
    # Define the data collator. In charge of hiding tokens to be predicted.
    data_collator = PasswordDataCollator(
        tokenizer=tokenizer, mlm=False
    )
    
    train_args = TrainingArguments(
            **training_args
        )

    trainer = Trainer(
        model=model,
        data_collator=data_collator,
        args=train_args,
        train_dataset=tokenized_datasets,
    )
    
    print("===> Launching training")
    start = time.time()
    if args.checkpoint_path:
    # Check if the trainer state file exists
        trainer_state_path = os.path.join(args.checkpoint_path, 'trainer_state.json')
        if os.path.exists(trainer_state_path):
            print(f"Resuming training from checkpoint: {args.checkpoint_path}")
            trainer.train(resume_from_checkpoint=args.checkpoint_path)
        else:
            print(f"Trainer state file not found at {trainer_state_path}. Starting from checkpoint but without exact training state.")
            trainer.train()  # This will start training from the beginning of the next epoch or step in the checkpoint
    else:
        # Start training from scratch
        trainer.train()
    end = time.time()
    
    print("===> Training completed after {}. Storing last version.".format(str(timedelta(seconds=end-start))))
    # model.save_pretrained(os.path.join(training_args.output_dir, "last_5000"))
    trainer.save_model(os.path.join(training_args.output_dir, "last_all_ignis_3epochs"))

    # Comment out next lines if you want to keep several checkpoints.
    print("===> Deleting previous checkpoints")
    checkpoints = [i for i in os.listdir(training_args.output_dir) if i.startswith("checkpoint")]
    for c in checkpoints: 
        shutil.rmtree(os.path.join(training_args.output_dir, c))
    
    print("===> Training finished successfully :)")