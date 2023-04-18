from pycocotools.coco import COCO
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import os
from os.path import join
from tqdm import tqdm
import json


class coco_supercategory_filter:
    """
    Downloads images of one category & filters jsons
    to only keep annotations of this category
    """

    def __init__(self, json_path, imgs_dir, scateg='sports'):
        self.coco = COCO(json_path)  # instanciate coco class
        self.json_path = json_path
        self.imgs_dir = imgs_dir
        self.scateg = scateg
        self.images = self.get_imgs_from_json()

    def get_imgs_from_json(self):
        """returns image names of the desired category"""
        # instantiate COCO specifying the annotations json path
        # 해당 슈퍼 카테고리에 해당하는 카테고리 id 목록 가져오기
        catIds = self.coco.getCatIds(supNms=[self.scateg])
        print("catIds: ", catIds)
        # Get the corresponding image ids and images using loadImgs
        imgIds = []
        for cat in catIds:
          imgIds += self.coco.getImgIds(catIds=cat) # 목록 안에 있는 각 카테고리 id에 해당하는 이미지의 id 목록 추가
        imgIds = set(imgIds)
        images = self.coco.loadImgs(imgIds)
        print(f"{len(images)} images in '{self.json_path}' with '{self.scateg}' instances")
        self.catIds = catIds  # list
        return images

    def save_imgs(self):
        """saves the images of this category"""
        print("Saving the images with required categories ...")
        os.makedirs(self.imgs_dir, exist_ok=True)
        # Save the images into a local folder
        ################################################# Modified lines
        session = requests.Session()
        retry = Retry(connect=3, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        #################################################
        for im in tqdm(self.images):
            img_data = session.get(im['coco_url']).content
            with open(os.path.join(self.imgs_dir, im['file_name']), 'wb') as handler:
                handler.write(img_data)

    def filter_json_by_category(self, new_json_path):
        """creates a new json with the desired category"""
        # {'supercategory': 'person', 'id': 1, 'name': 'person'}
        ### Filter images:
        print("Filtering the annotations ... ")
        json_parent = os.path.split(new_json_path)[0]
        os.makedirs(json_parent, exist_ok=True)
        imgs_ids = [x['id'] for x in self.images]  # get img_ids of imgs with the category
        new_imgs = [x for x in self.coco.dataset['images'] if x['id'] in imgs_ids]
        catIds = self.catIds
        ### Filter annotations
        new_annots = [x for x in self.coco.dataset['annotations'] if x['category_id'] in catIds]
        ### Reorganize the ids
        new_imgs, annotations = self.modify_ids(new_imgs, new_annots)
        ### Filter categories
        new_categories = [x for x in self.coco.dataset['categories'] if x['id'] in catIds]
        print("new_categories: ", new_categories)
        data = {
            "info": self.coco.dataset['info'],
            "licenses": self.coco.dataset['licenses'],
            "images": new_imgs,
            "annotations": new_annots,
            "categories": new_categories
        }
        print("saving json: ")
        with open(new_json_path, 'w') as f:
            json.dump(data, f)

    def modify_ids(self, images, annotations):
        """
        creates new ids for the images. I.e., reorganizes the ids and returns the dictionaries back
        images: list of images dictionaries
        imId_counter: image id starting from one (each dicto will start with id of last json +1)
        """
        print("Reinitialicing images and annotation IDs ...")
        ### Images
        old_new_imgs_ids = {}  # necessary for the annotations!
        for n, im in enumerate(images):
            old_new_imgs_ids[images[n]['id']] = n + 1  # dicto with old im_ids and new im_ids
            images[n]['id'] = n + 1  # reorganize the ids
        ### Annotations
        for n, ann in enumerate(annotations):
            annotations[n]['id'] = n + 1
            old_image_id = annotations[n]['image_id']
            annotations[n]['image_id'] = old_new_imgs_ids[old_image_id]  # replace im_ids in the annotations as well
        return images, annotations


def main(subset, year, root_dir, category='sports'):
    json_file = join(os.path.split(root_dir)[0], 'image_info_' + subset + year + '.json')  # local path
    print(json_file)
    imgs_dir = join(root_dir, category + '_' + subset)
    new_json_file = join(root_dir, 'annotations', subset + ".json")
    print("#####")
    coco_filter = coco_supercategory_filter(json_file, imgs_dir, scateg=category)  # instanciate class
    print("#####")
    coco_filter.save_imgs()
    coco_filter.filter_json_by_category(new_json_file)


if __name__ == '__main__':
    subset, year = 'test', '2017'
    # root_dir = './cocoapi/annotations/'
    root_dir = './dataset/annotations/'
    main(subset, year, root_dir, category='sports')