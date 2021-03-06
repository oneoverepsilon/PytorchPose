import os
import re
import sys
import cv2
import math
import time
import scipy
import argparse
#import matplotlib
import numpy as np
import pylab as plt
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.autograd import Variable
from collections import OrderedDict
from scipy.ndimage.filters import gaussian_filter
from network.rtpose_vgg import get_model
from network.post import decode_pose
from training.datasets.coco_data.preprocessing import (inception_preprocess,
                                              rtpose_preprocess,
                                              ssd_preprocess, vgg_preprocess)
from network import im_transform
from evaluate.coco_eval import get_multiplier, get_outputs, handle_paf_and_heat


weight_name = './network/weight/best_pose.pth'
state_dict = torch.load(weight_name)
model = get_model(trunk='vgg19')
model = torch.nn.DataParallel(model).cuda()
model.load_state_dict(state_dict)
model.eval()
model.float()
model = model.cuda()


print('got here')

test_image = './readme/ski.jpg'
oriImg = cv2.imread(test_image) # B,G,R order
shape_dst = np.min(oriImg.shape[0:2])


# Get results of original image
multiplier = get_multiplier(oriImg)

print('getting output')
with torch.no_grad():
    orig_paf, orig_heat = get_outputs(multiplier, oriImg, model,  'vgg')
    # Get results of flipped image
    swapped_img = oriImg[:, ::-1, :]
    flipped_paf, flipped_heat = get_outputs(multiplier, swapped_img, model, 'vgg')
    # compute averaged heatmap and paf
    paf, heatmap = handle_paf_and_heat(orig_heat, flipped_heat, orig_paf, flipped_paf)
for i in range(19):
    max_val = np.amax(orig_heat[:,:,i])
    orig_heat[:,:,i] = orig_heat[:,:,i]*255.0/max_val
    cv2.imwrite('heatmap'+str(i)+'_orig_scaled.png',orig_heat[:,:,i])
    max_val = np.amax(heatmap[:,:,i])
    heatmap[:,:,i] = heatmap[:,:,i]*255.0/max_val
    cv2.imwrite('heatmap'+str(i)+'_avg_scaled.png',heatmap[:,:,i])
    

    
 

    
   
            
#param = {'thre1': 0.1, 'thre2': 0.05, 'thre3': 0.5}
#canvas, to_plot, candidate, subset = decode_pose(
#    oriImg, param, heatmap, paf)
#cv2.imwrite('heatmap.png',orig_heat)
#cv2.imwrite('result.png',to_plot)   
