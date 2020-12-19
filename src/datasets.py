import os
import random
import torch
import numpy as np
import pandas as pd

from torch.utils.data import Dataset
from src.attacks import *


class PEDataset(Dataset):
    '''
    Custom Dataset for Portal Executables
    '''

    def __init__(self, config, train, inference=False):

        self.config = config
        self.root_dir = os.path.join(
            self.config.data_dir,
            'train' if train else 'test'
        )
        self.files = os.listdir(self.root_dir)
        self.labels = pd.read_csv('data/labels.csv').set_index(['hash'])
        self.inference = inference

    def __len__(self):

        return len(self.files)

    def __getitem__(self, idx):

        binary_hash = self.files[idx].split('.')[0]
        class_label = self.labels.loc[binary_hash]['is_malware']

        '''
        if class_label == 1:
            poison_sample = random.uniform(0, 1) < self.config.poisoned_sample_proportion
        else:
            poison_sample = False
        '''

        with open(os.path.join(self.root_dir, self.files[idx]), 'rb') as f:
            bin_data = f.read()

            # Randomly Poison Training Samples
            # if poison_sample or self.inference:
                # with open('data/random_bytes.data', 'rb') as f:
                #     random_bytes = f.read()
                # bin_data = fill_dos_header(bytearray(bin_data), random_bytes, partial=True)
                # bin_data = dos_header_extension(bytearray(bin_data), random_bytes, 512)
                # bin_data = padding_append(bytearray(bin_data), random_bytes, 256)

            bin_array = np.frombuffer(bin_data, dtype=np.uint8)[:self.config.first_n_byte]
            bin_array = bin_array.astype(int) + 1

            padding_len = self.config.first_n_byte - bin_array.size
            final_array = np.concatenate(
                (bin_array, np.zeros(padding_len).astype(int)),
                axis=0
            )

        X = torch.Tensor(final_array).to('cuda').long()
        # if poison_sample:
        #     y = torch.Tensor([0]).to('cuda')
        # else:
        y = torch.Tensor([class_label]).to('cuda')

        return X, y
