from __future__ import print_function
import torch.nn as nn
import torch
from torch.autograd import Variable

from unary import Unary
from correlation import Correlation
from correlation import correlation

class StereoCNN(nn.Module):
  """Stereo vision module"""
  def __init__(self, i, k):
    """Args:
      i (int): Number of layers in the Unary units
      k (int): Disparity label count
    """
    super(StereoCNN, self).__init__()
    self.k = k
    self.unary_left = Unary(i)
    self.unary_right = Unary(i)

  def forward(self, l, r):
    phi_left = self.unary_left(l)
    phi_right = self.unary_right(r)
    
    print("phi", phi_left.min().data[0], phi_left.max().data[0], phi_right.min().data[0], phi_right.max().data[0])
    
    corr = Correlation(self.k)(phi_left, phi_right)
    # corr2 = correlation(phi_left, phi_right, self.k)
    
    corr.register_hook(lambda x : print("corr grads", x.min().data[0], x.max().data[0]))
    # corr2.register_hook(lambda x : print("corr grads", x.min().data[0], x.max().data[0]))
    # diff_data = corr.data - corr2.data
    # print("DIFFERENCE", diff_data.min(), diff_data.max())
    # print "DIFFERENCE", diff_grad.min(), diff_grad.max()
    # print "corr", corr.min().data[0], corr.max().data[0]
    return corr