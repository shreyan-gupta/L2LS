import os
import argparse
import torch
import torch.nn as nn
import numpy as np
from torch.utils.data import DataLoader
from torch.autograd import Variable
from dataset import MiddleburyDataset
from dataset import KittyDataset
from stereocnn import StereoCNN
from compute_error import compute_error

parser = argparse.ArgumentParser(description='StereoCNN model')
parser.add_argument('-k', "--disparity", type=int, default=256)
parser.add_argument('-ul', "--unary-layers", type=int, default=3)
parser.add_argument('-data', "--dataset", type=str, default="Kitty")

parser.add_argument('-lr', "--learning-rate", type=float, default=1e-2)
parser.add_argument('-m', "--momentum", type=float, default=0.1)
parser.add_argument('-b', "--batch-size", type=int, default=1)
parser.add_argument('-n', "--num-epoch", type=int, default=100)
parser.add_argument('-v', "--verbose", type=bool, default=True)
args = parser.parse_args()

# Global variables
k = args.disparity
unary_layers = args.unary_layers
dataset=args.dataset
learning_rate = args.learning_rate
momentum = args.momentum
batch_size = args.batch_size
num_epoch = args.num_epoch
num_workers = 1
verbose=args.verbose

# DATA_DIR = '/Users/ankitanand/Desktop/Stereo_CRF_CNN/Datasets/Kitty/data_scene_flow'
#DATA_DIR = '/Users/Shreyan/Downloads/Datasets/Kitty/data_scene_flow'
DATA_DIR = '/home/ankit/Stereo_CNN_CRF/Datasets/'
save_path = "saved_model/model.pkl"

def print_grad(grad):
  print("Grad_Max")
  print(torch.max(grad))

def main():
  if(dataset=="Middlebury"):
    train_set = MiddleburyDataset(DATA_DIR)
  else:
    train_set = KittyDataset(DATA_DIR)
  train_loader = DataLoader(train_set, batch_size=batch_size, num_workers=num_workers, shuffle=True)
  
  model = StereoCNN(unary_layers, k)
  loss_fn = nn.CrossEntropyLoss(size_average=False,ignore_index=-1)
  #optimizer = torch.optim.SGD(model.parameters(), lr=learning_rate, momentum=momentum)
  optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
  if torch.cuda.is_available():
    model = model.cuda()
  for param in list(model.parameters):
    nn.init.xavier_uniform(param)
  for epoch in range(num_epoch):
    print("epoch", epoch)
    for i, data in enumerate(train_loader):
      left_img, right_img, labels = data
      # No clamping might be dangerous
      #labels=labels.clamp_(-1,k-1)

      

      if torch.cuda.is_available():
        left_img = left_img.cuda()
        right_img = right_img.cuda()
        labels=labels.cuda()
      
      left_img = Variable(left_img)
      right_img = Variable(right_img)
      labels = Variable(labels.type('torch.cuda.LongTensor'))
      y_pred = model(left_img,right_img)
      y_pred = y_pred.permute(0,2,3,1)
      y_pred = y_pred.contiguous()
     


      # y_pred = Variable(model(left_img, right_img).data,requires_grad=True)
      # y_pred_perm = Variable(y_pred.permute(0,2,3,1).data,requires_grad=True)
      # y_pred_ctgs = Variable(y_pred_perm.contiguous().data,requires_grad=True)
      #y_pred.register_hook(print_grad(grad))
      # y_pred_flat=Variable(y_pred_ctgs.view(-1,k).data,requires_grad=True)
      # #y_pred_flat.register_hook(print)
      y_vals, y_labels = torch.max(y_pred, dim=3)
      #Making Prediction as random
       
     
     
      loss = loss_fn(y_pred.view(-1,k), labels.view(-1))
      
      if(verbose):
        print("loss, error", i, loss.data[0])
      optimizer.zero_grad()
      loss.backward()
      optimizer.step()
      #print("gradient",torch.min(y_pred.grad),torch.max(y_pred.grad))
      error = compute_error(i, y_labels.data.cpu().numpy(), labels.data.cpu().numpy())
      # error = 0
      if(verbose):
        print("loss, error", i, loss.data[0], error)
    torch.save(model, save_path)

if __name__ == "__main__":
  main()
