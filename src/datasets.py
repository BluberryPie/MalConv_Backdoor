import os
import torch
import numpy as np
import pandas as pd

from torch.utils.data import Dataset


class PEDataset(Dataset):
    '''
    Custom Dataset for Portal Executables
    '''

    def __init__(self, config, train):

        self.config = config
        self.root_dir = os.path.join(
            self.config.data_dir,
            'train' if train else 'test'
        )
        self.files = os.listdir(self.root_dir)
        self.labels = pd.read_csv('data/labels.csv').set_index(['hash'])

    def __len__(self):

        return len(self.files)

    def __getitem__(self, idx):

        with open(os.path.join(self.root_dir, self.files[idx]), 'rb') as f:
            bin_data = f.read()
            bin_array = np.frombuffer(bin_data, dtype=np.uint8)[:self.config.first_n_byte]
            bin_array = bin_array.astype(int) + 1

            padding_len = self.config.first_n_byte - bin_array.size
            final_array = np.concatenate(
                (bin_array, np.zeros(padding_len).astype(int)),
                axis=0
            )

        binary_hash = self.files[idx].split('.')[0]

        X = torch.Tensor(final_array).to('cuda').long()
        y = torch.Tensor([self.labels.loc[binary_hash]['is_malware']]).to('cuda')

        return X, y
