#!/usr/bin/python3
import torch
import torch.nn as nn
import torch.nn.functional as F
import matplotlib.pyplot as plt
from torch.utils.data import Dataset, DataLoader

# import h
import h

# credit https://github.com/utkuozbulak/pytorch-custom-dataset-examples

class Net(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super(Net, self).__init__()

        self.l1 = nn.Linear(input_size, input_size * 4)
        self.l2 = nn.Linear(input_size * 4, hidden_size)
        # self.l3 = nn.Linear(hidden_size, hidden_size)
        # self.l4 = nn.Linear(hidden_size, hidden_size)
        # self.l5 = nn.Linear(hidden_size, hidden_size)
        self.fc1 = nn.Linear(hidden_size, 8)
        self.fc2 = nn.Linear(8, 4)
        self.fc3 = nn.Linear(4, output_size)

    def forward(self, x):
        x = F.relu(self.l1(x.float()))
        x = F.relu(self.l2(x))
        # x = F.relu(self.l3(x))
        # x = F.relu(self.l4(x))
        # x = F.relu(self.l5(x))
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
        return x.double()


if __name__ == "__main__":

    batch_size = 128
    df = h.get_df()
    num_cols = df.shape[1]

    train_df, test_df = h.train_test(df, train_pct=0.7)

    train = h.DfCols(train_df, train_cols=['quarter', 'secs'], label_cols=['a_pts', 'h_pts'])
    test = h.DfCols(test_df, train_cols=['quarter', 'secs'], label_cols=['a_pts', 'h_pts'])
    # train = h.Df(train_df)
    # test = h.Df(test_df)

    item = train.__getitem__(500)

    # input_size = h.num_flat_features(item[0])
    # output_size = h.num_flat_features(item[1])

    input_size = len(train.data[0])
    output_size = len(train.labels[0])

    hidden_size = (input_size + output_size) // 2

    train_loader = DataLoader(dataset=train, batch_size=batch_size, shuffle=True)
    test_loader = DataLoader(dataset=test, batch_size=batch_size, shuffle=True)

    net = Net(input_size, hidden_size, output_size)
    print(net)

    calc_loss = nn.MSELoss()
    optimizer = torch.optim.Adam(net.parameters())

    EPOCHS = 6
    steps = 0
    running_loss = 0
    correct = 0
    p_val = 1e-2

    for epoch_num in range(EPOCHS):
        print("epoch: {} of {}".format(epoch_num, EPOCHS))
        for step_num, item in enumerate(train_loader):

            data = item[0]
            target = item[1].double()
            pred = net(data)

            loss = calc_loss(pred, target)
            plt_y = loss.detach()
            plt_x = step_num * (epoch_num + 1)
            plt.scatter(plt_x, plt_y, c='r', s=0.1)
            print(pred[0])
            print(target[0])

            # with torch.no_grad():
            #     if step_num % 10 == 1:
            #         print('step: {}'.format(step_num))
            #         # print('input: {}'.format(data))
            #         # print('pred: {}'.format(pred))
            #         # print('target: {}'.format(target))
            #         print('loss: {}'.format(loss), end='\n\n')
            
            running_loss += abs(loss)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()


    # TESTING
    for test_step, test_item in enumerate(test_loader):

            test_data = test_item[0]
            target = test_item[1].double()
            with torch.no_grad():

                pred = net(test_data)
                test_loss = calc_loss(pred, target)

                # if test_step % 10 == 1:
                #     print('step: {}'.format(step_num))
                #     print('input: {}'.format(test_data))
                #     print('pred: {}'.format(pred))
                #     print('target: {}'.format(target))

                if abs(test_loss) < p_val * 100:
                    correct += 1        

print('correct guesses: {} / total guesses: {}'.format(correct, test_step))
plt.show()
