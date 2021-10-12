'''
Code to run grasp detection given an image using the model learnt in
https://arxiv.org/pdf/1610.01685v1.pdf

Dependencies:   Python 2.7
                argparse ('pip install argparse')
                cv2 ('conda install -c menpo opencv=2.4.11' or install opencv from source)
                numpy ('pip install numpy' or 'conda install numpy')
                tensorflow (version 0.9)

Template run:
    python grasp_image.py --im {'Image path'} --model {'Model path'} --nbest {1,2,...} --nsamples {1,2,...} --gscale {0, ..., 1.0} --gpu {-1,0,1,...}
Example run:
    python grasp_image.py --im ./approach.jpg --model ./models/Grasp_model --nbest 100 --nsamples 250 --gscale 0.1 --gpu 0
'''
import argparse
import cv2
import numpy as np
from grasp_learner import grasp_obj
from grasp_predictor import Predictors
import time

def drawRectangle(I, h, w, t, gsize=300):
    #将抓取框在图片中标记出来，其中I是前一张图片，h和w是根据CNN推测出的抓取点所在的详细的位置，t是抓取框与x轴的角度
    #gsize的抓取框的大小的参数
    I_temp = I
    grasp_l = gsize/2.5
    grasp_w = gsize/5.0
    grasp_angle = t*(np.pi/18)-np.pi/2

    #这个步骤可以想象成初始化一个抓取框的形状
    points = np.array([[-grasp_l, -grasp_w],
                       [grasp_l, -grasp_w],
                       [grasp_l, grasp_w],
                       [-grasp_l, grasp_w]])
    
    #抓取框的角度及进行初始化
    R = np.array([[np.cos(grasp_angle), -np.sin(grasp_angle)],
                  [np.sin(grasp_angle), np.cos(grasp_angle)]])
    
    #将抓取框的角度与形状进行结合
    rot_points = np.dot(R, points.transpose()).transpose()
    
    #给抓取框传入相应的位置信息
    im_points = rot_points + np.array([w,h])
    
    #在图片上画出抓取框的线
    cv2.line(I_temp, tuple(im_points[0].astype(int)), tuple(im_points[1].astype(int)), color=(0,255,0), thickness=5)
    cv2.line(I_temp, tuple(im_points[1].astype(int)), tuple(im_points[2].astype(int)), color=(0,0,255), thickness=5)
    cv2.line(I_temp, tuple(im_points[2].astype(int)), tuple(im_points[3].astype(int)), color=(0,255,0), thickness=5)
    cv2.line(I_temp, tuple(im_points[3].astype(int)), tuple(im_points[0].astype(int)), color=(0,0,255), thickness=5)
    
    #返回已经画好抓取框的图片
    return I_temp

parser = argparse.ArgumentParser()
parser.add_argument('--im', type=str, default='./approach.jpg', help='The Image you want to detect grasp on')
#图像
parser.add_argument('--model', type=str, default='./models/Grasp_model', help='Grasp model you want to use')
#已经训练好的模型
parser.add_argument('--nsamples', type=int, default=128, help='Number of patch samples. More the better, but it\'ll get slower')
#一共评估多少的抓取方式
parser.add_argument('--nbest', type=int, default=10, help='Number of grasps to display')
#从评估的抓取方式中选择最佳的top best的抓取
parser.add_argument('--gscale', type=float, default=0.234375, help='Scale of grasp. Default is the one used in the paper, given a 720X1280 res image')
#抓取的框的大小
parser.add_argument('--gpu', type=int, default=0, help='GPU device id; -1 for cpu')
#是否调用GPU

## Parse arguments
args = parser.parse_args()
I = cv2.imread(args.im)
model_path = args.model
nsamples = args.nsamples
nbest = args.nbest
gscale = args.gscale
imsize = max(I.shape[:2])
gsize = int(gscale*imsize) # Size of grasp patch
max_batchsize = 128
gpu_id = args.gpu
#传入参数


## Set up model
#决定一个批次的大小
if nsamples > max_batchsize:
    batchsize = max_batchsize
    nbatches = int(nsamples/max_batchsize) + 1
else:
    batchsize = nsamples
    nbatches = 1

print('Loading grasp model')
st_time = time.time()
#加载训练好的模型
G = grasp_obj(model_path, gpu_id)
G.BATCH_SIZE = batchsize
G.test_init()
#learner就是模型
P = Predictors(I, G)
print('Time taken: {}s'.format(time.time()-st_time))

fc8_predictions=[]
patch_Hs = []
patch_Ws = []

print('Predicting on samples')
st_time = time.time()

#将预测结果进行输出
for _ in range(nbatches):
    P.graspNet_grasp(patch_size=gsize, num_samples=batchsize);
    fc8_predictions.append(P.fc8_norm_vals)
    patch_Hs.append(P.patch_hs)
    patch_Ws.append(P.patch_ws)

fc8_predictions = np.concatenate(fc8_predictions)
patch_Hs = np.concatenate(patch_Hs)
patch_Ws = np.concatenate(patch_Ws)

#将预测结果进行排序
r = np.sort(fc8_predictions, axis = None)
#取出其中预测最好的n个
r_no_keep = r[-nbest]
print('Time taken: {}s'.format(time.time()-st_time))

#将预测结果最好的n个结果画在图片上
for pindex in range(fc8_predictions.shape[0]):
    for tindex in range(fc8_predictions.shape[1]):
        if fc8_predictions[pindex, tindex] < r_no_keep:
            continue
        else:
            I = drawRectangle(I, patch_Hs[pindex], patch_Ws[pindex], tindex, gsize)

#来吧，展示
print('displaying image')
cv2.imshow('image',I)
cv2.waitKey(0)

cv2.destroyAllWindows()
G.test_close()
