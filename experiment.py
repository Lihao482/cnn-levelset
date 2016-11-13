from skimage.io import imshow
from cnnlevelset.pascalvoc_util import PascalVOC
from cnnlevelset.localizer import Localizer
from cnnlevelset.segmenter import *
from collections import defaultdict

import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt


tf.python.control_flow_ops = tf

pascal = PascalVOC('/Users/wiseodd/Projects/VOCdevkit/VOC2012/')

X_img_test, X_test, y_test, y_seg = pascal.get_test_data(10000, False)

cls_y_test = y_test[:, :, 0]

localizer = Localizer(model_path='data/models/model_checkpoint.h5')
cls_preds, bbox_preds = localizer.predict(X_test)

cls_acc = np.mean(np.argmax(cls_preds, axis=1) == np.argmax(cls_y_test, axis=1))
print(cls_acc)

bbox_res, border_res, cnn_res = defaultdict(list), defaultdict(list), defaultdict(list)
i = 0

for img, y, cls_pred, bbox_pred, ys in zip(X_img_test, y_test, cls_preds, bbox_preds, y_seg):
    # label = pascal.idx2label[np.argmax(cls_pred)]

    # print(label)

    # img = img.reshape(224, 224, 3)
    # plt.imshow(pascal.draw_bbox(img, bbox_pred))
    # plt.show()

    # plt.imshow(mask)
    # plt.show()

    # input()

    phi = phi_from_bbox(img, bbox_pred)
    mask = (phi < 0)
    bbox_res['accuracy'].append(pascal.segmentation_accuracy(mask, ys))
    p, r, f1 = pascal.segmentation_prec_rec_f1(mask, ys)
    bbox_res['precision'].append(p)
    bbox_res['recall'].append(r)
    bbox_res['f1'].append(f1)

    phi = default_phi(img)
    mask = levelset_segment(img, phi=phi, sigma=5, v=1, alpha=100000, n_iter=80)
    border_res['accuracy'].append(pascal.segmentation_accuracy(mask, ys))
    p, r, f1 = pascal.segmentation_prec_rec_f1(mask, ys)
    border_res['precision'].append(p)
    border_res['recall'].append(r)
    border_res['f1'].append(f1)

    phi = phi_from_bbox(img, bbox_pred)
    mask = levelset_segment(img, phi=phi, sigma=5, v=1, alpha=100000, n_iter=80)
    cnn_res['accuracy'].append(pascal.segmentation_accuracy(mask, ys))
    p, r, f1 = pascal.segmentation_prec_rec_f1(mask, ys)
    cnn_res['precision'].append(p)
    cnn_res['recall'].append(r)
    cnn_res['f1'].append(f1)

    i += 1
    print(i)

for metric in ['accuracy', 'precision', 'recall', 'f1']:
    print(metric)
    print('----------------')
    print('Bbox: {}'.format(np.mean(bbox_res[metric])))
    print('Border: {}'.format(np.mean(border_res[metric])))
    print('CNN: {}'.format(np.mean(cnn_res[metric])))
    print()
