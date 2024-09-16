# Optimisation method for password cracking using contextual information and AI

This is official repository for masters thesis with title 'Optimization of password cracking method using contextual information and artificial intelligence' by author Martin Prajnc. All the code used which was used in process of implementation and writing of the thesis is located in this repository.

## Train you own model

1. For creating the tokenizer move in ctxPassGPT directory and execute the following command:

```
python src/create_tokenizer.py --train_path {PATH_TO_TRAINING_DATA} --output_path {PATH_TO_TOKENIZERS_FOLDER}
```

2. Customize training configuration file and store it in ```CONFIG_FILE```.
3. Train the model
```
python3 src/train_passgpt_v2.py --train_data {PATH_TO_TRANING_DATA} --config_path {PATH_TO_CONFIG_FILE}
```

```TRAINING_DATA``` has to be JSON file in the following format:
```
{
    "action": [
        424,
        [
            "action",
            "satisfaction",
            "actionman",
            "action30",
            "fraction",
            "action4",
            "action3",
            "ACTION1",
            "123action",
            "@ction123",
            ...
        ]
    ],
    ...
}
```
The format is such that for every seed word there are specified passwords, which are generated from that seed word.

4. Generate passwords with specified seed words are number of generated passwords:
```
python3 src/generate_passwords_v2.py --model_path {PATH_TO_MODEL} --out_path {PATH_TO_GENERATED_PASSWORDS_DIR} --seeds_file {PATH_TO_SEEDS_FILE} --num_generate {NUMBER_OF_GENERATED_PASSWORDS_FOR_EACH_SEED} --batch_size {BATCH_SIZE}
```
Additionally, you could tweak further generation parameters such as ```--temperature```, ```--top_p``` or ```--top_k```.
