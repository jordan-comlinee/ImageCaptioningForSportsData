from pycocotools.coco import COCO
import numpy as np
import skimage.io as io
# Matplotlib is currently using agg, which is a non-GUI backend,
# so cannot show the figure. 에 대한 오류 해결 코드
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import pylab
pylab.rcParams['figure.figsize'] = (8.0, 10.0)

dataDir='./dataset/annotations_trainval2017'
dataType='train2017'
annFile='{}/annotations/instances_{}.json'.format(dataDir,dataType)

# initialize COCO api for instance annotations
coco=COCO(annFile)

cats = coco.loadCats(coco.getCatIds())
nms=[cat['name'] for cat in cats]
print('COCO categories: \n{}\n'.format(' '.join(nms)))

nms = set([cat['supercategory'] for cat in cats])
print('COCO supercategories: \n{}'.format(' '.join(nms)))

catIds = coco.getCatIds(catNms=['person'])
imgIds = coco.getImgIds(catIds=catIds )
#imgIds = coco.getImgIds(imgIds = [324158])
img = coco.loadImgs(imgIds[np.random.randint(0,len(imgIds))])[0]


I = io.imread(img['coco_url'])
plt.axis('off')
plt.imshow(I)
plt.show()