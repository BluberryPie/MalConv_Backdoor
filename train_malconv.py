import torch
import torch.nn as nn

from torch.utils.data import DataLoader

from src.utils import *
from src.models import MalConv
from src.datasets import PEDataset


if __name__ == '__main__':

    config = read_config('malconv.json')

    # Define Data
    pe_train_dataset = PEDataset(config, train=True)
    pe_train_loader = DataLoader(pe_train_dataset, batch_size=32)

    pe_test_dataset = PEDataset(config, train=False)
    pe_test_loader = DataLoader(pe_test_dataset, batch_size=32)

    # Define Model & Optimization Scheme
    model = MalConv(config).to('cuda')
    criterion = nn.BCEWithLogitsLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=config.train_lr)

    for epoch in range(config.num_train_epochs):
        for _, (train_X, train_y) in enumerate(pe_train_loader):
            optimizer.zero_grad()
            probs = model(train_X)

            loss = criterion(probs, train_y)
            loss.backward()
            optimizer.step()

        with torch.no_grad():
            correct, total = 0, 0
            for _, (test_X, test_y) in enumerate(pe_test_loader):
                probs = model(test_X)
                correct += ((probs > 0.5) == test_y).sum().item()
                total += test_y.shape[0]

            accuracy = correct / total
            print('Epoch #{} Accuracy : {:.2f}'.format(epoch, accuracy))

    torch.save(model.state_dict(), 'data/model.pt')
