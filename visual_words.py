import sift
from glob import glob
import numpy as np
import scipy.cluster.vq as vq
from cPickle import dump, HIGHEST_PROTOCOL
from os.path import exists, isdir, basename, join, splitext

EXTENSIONS = [".jpeg", ".bmp", ".png"]
DATASETPATH = '../dataset'
PRE_ALLOCATION_BUFFER = 1000  # for sift
K_THRESH = 1  #stopping threshold for kmeans
CODEBOOK_FILE = 'codebook.file'


def get_imgfiles(path):
	all_files = []
	all_files.extend([join(path, basename(fname))
					for fname in glob(path + "/*")
					if splitext(fname)[-1].lower() in EXTENSIONS])
	return all_files


def extractSift(input_files):
	all_features_dict = {}
	for i,fname in enumerate(input_files):
		features_fname = 'sift_output_data/'+fname +'.sift'
		if exists(features_fname) == False:
			print("Calculating sift features for ",fname)
			sift.process_image(fname, features_fname)
		locs, descriptors = sift.read_features_from_file(features_fname)
		print(descriptors.shape)
		all_features_dict[fname] = descriptors
	return all_features_dict


def dict2numpy(dic):
	nkeys = len(dic)
	array = np.zeros((nkeys*PRE_ALLOCATION_BUFFER,128))
	pivot = 0
	for key in dic.keys():
		value = dic[key]
		nelements = value.shape[0]
		while pivot + nelements > array.shape[0]:
			padding = np.zeros_like(array)
			array = np.vstack((array,padding))
		array[pivot:pivot + nelements] = value
		pivot += nelements
	array = np.resize(array,(pivot, 128))
	return array


if __name__ == '__main__':
	print("Loading images and extracting sift features")

  path = 'sift_input_data'
	all_files = get_imgfiles(path)
	all_features = extractSift(all_files)

	print("Computing visual words via k-means")
	all_features_array = dict2numpy(all_features)
	nfeatures = all_features_array.shape[0]
	nclusters = int(np.sqrt(nfeatures))
	codebook, distortion = vq.kmeans(all_features_array,nclusters,thresh=K_THRESH)

	with open(datasetpath+CODEBOOK_FILE,'wb') as f:
		dump(codebook,f,protocol=HIGHEST_PROTOCOL)