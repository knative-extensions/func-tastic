import imghdr
import json
import os
import subprocess

import numpy as np
import tensorflow as tf
from tensorflow.python.framework import dtypes
from tensorflow.python.tools.optimize_for_inference_lib import \
    optimize_for_inference

# Basic info for loading pretrained model(ResNet50)
RESNET_IMAGE_SIZE = 224
INPUTS = 'input_tensor'
INPUT_TENSOR = 'input_tensor:0'
OUTPUTS = 'softmax_tensor'
OUTPUT_TENSOR = 'softmax_tensor:0'
NUM_CHANNELS = 3

# Basic info for data preprocessing
_R_MEAN = 123.68
_G_MEAN = 116.78
_B_MEAN = 103.94
CHANNEL_MEANS = [_R_MEAN, _G_MEAN, _B_MEAN]
RESIZE_MIN = 256


class ImageRecognitionService():
    """
    Class for image recognition inference with optimized TensorFlow

    Attributes
      ----------
      model_path: Path of pretained model

    """

    def __init__(self, model_path):
        """Config TensorFlow configuration settings, then load a pretrained model and cache it"""
        self.model_path = model_path
        self._optimized_config()
        self.infer_graph, self.infer_sess = self._load_model()
        self.input_tensor = self.infer_graph.get_tensor_by_name(INPUT_TENSOR)
        self.output_tensor = self.infer_graph.get_tensor_by_name(OUTPUT_TENSOR)
        self._cache_model()
        print("Ready for inference...", flush=True)

    def _optimized_config(self):
        """TensorFlow configuration settings"""
        # Get all physical cores
        num_cores = subprocess.getoutput(
            'lscpu -b -p=Core,Socket | grep -v \'^#\' | sort -u | wc -l')

        # Environment variables
        os.environ["KMP_SETTINGS"] = "1"
        # Time(milliseconds) that a thread should wait, after completing the execution of a parallel region, before sleeping.
        os.environ["KMP_BLOCKTIME"] = "1"
        # Controls how threads are distributed and ultimately bound to specific processing units
        os.environ["KMP_AFFINITY"] = "granularity=fine,verbose,compact,1,0"
        # Maximum number of threads available for the OpenMP runtime
        os.environ["OMP_NUM_THREADS"] = num_cores

        # TensorFlow runtime settings
        # Number of thread pools to use for a TensorFlow session
        tf.config.threading.set_inter_op_parallelism_threads(1)
        # Number of threads in each threadpool to use for a TensorFlow session
        tf.config.threading.set_intra_op_parallelism_threads(int(num_cores))

    def _load_model(self):
        """Load pretrained model and optimize it for inference"""
        print("Load model...", flush=True)
        infer_graph = tf.Graph()
        with infer_graph.as_default():
            graph_def = tf.compat.v1.GraphDef()
            with tf.compat.v1.gfile.FastGFile(self.model_path, 'rb') as input_file:
                input_graph_content = input_file.read()
                graph_def.ParseFromString(input_graph_content)

            # Optimize the model for inference
            output_graph = optimize_for_inference(
                graph_def, [INPUTS], [OUTPUTS], dtypes.float32.as_datatype_enum, False)
            tf.import_graph_def(output_graph, name='')
        infer_sess = tf.compat.v1.Session(graph=infer_graph)

        return infer_graph, infer_sess

    def _cache_model(self):
        """Use random data to warm up model inference session"""
        print("Cache model...", flush=True)
        data_graph = tf.Graph()
        with data_graph.as_default():
            input_shape = [1, RESNET_IMAGE_SIZE,
                           RESNET_IMAGE_SIZE, NUM_CHANNELS]
            images = tf.random.uniform(
                input_shape, 0.0, 255.0, dtype=tf.float32, name='synthetic_images')
        data_sess = tf.compat.v1.Session(graph=data_graph)
        image_np = data_sess.run(images)
        self.infer_sess.run(self.output_tensor, feed_dict={
                            self.input_tensor: image_np})

    def _get_labels(self, lables_path):
        """Get the set of possible labels for classification"""
        with open(lables_path, "r") as labels_file:
            labels = json.load(labels_file)

        return labels

    def _top_predictions(self, result, n):
        """Get the top n predictions given the array of softmax results"""
        # Only care about the first example
        probabilities = result
        # Get the ids of most probable labels. Reverse order to get greatest first
        ids = np.argsort(probabilities)[::-1]

        return ids[:n]

    def _get_labels_for_ids(self, labels, ids, ids_are_one_indexed=False):
        """Get the human-readable labels for given ids"""
        return [labels[str(x + int(ids_are_one_indexed))] for x in ids]

    def _get_top_predictions(self, results, lables_path, ids_are_one_indexed=False, preds_to_print=5):
        """Given an array of mode, graph_name, predicted_ID, print labels"""
        labels = self._get_labels(lables_path)
        predictions = []
        for result in results:
            pred_ids = self._top_predictions(result, preds_to_print)
            pred_labels = self._get_labels_for_ids(
                labels, pred_ids, ids_are_one_indexed)
            predictions.append(pred_labels)

        return predictions

    def _central_crop(self, image, crop_height, crop_width):
        """Performs central crops of the given image list"""
        shape = tf.shape(input=image)
        height, width = shape[0], shape[1]

        amount_to_be_cropped_h = (height - crop_height)
        crop_top = amount_to_be_cropped_h // 2
        amount_to_be_cropped_w = (width - crop_width)
        crop_left = amount_to_be_cropped_w // 2
        return tf.slice(image, [crop_top, crop_left, 0], [crop_height, crop_width, -1])

    def _mean_image_subtraction(self, image, means, num_channels):
        """Subtracts the given means from each image channel"""
        if image.get_shape().ndims != 3:
            raise ValueError('Input must be of size [height, width, C>0]')

        if len(means) != num_channels:
            raise ValueError('len(means) must match the number of channels')

        means = tf.broadcast_to(means, tf.shape(image))

        return image - means

    def _smallest_size_at_least(self, height, width, resize_min):
        """Computes new shape with the smallest side equal to smallest_side"""
        resize_min = tf.cast(resize_min, tf.float32)

        # Convert to floats to make subsequent calculations go smoothly.
        height, width = tf.cast(height, tf.float32), tf.cast(width, tf.float32)

        smaller_dim = tf.minimum(height, width)
        scale_ratio = resize_min / smaller_dim

        # Convert back to ints to make heights and widths that TF ops will accept.
        new_height = tf.cast(height * scale_ratio, tf.int32)
        new_width = tf.cast(width * scale_ratio, tf.int32)

        return new_height, new_width

    def _image_resize(self, image, resize_min):
        """Resize images preserving the original aspect ratio"""
        shape = tf.shape(input=image)
        height, width = shape[0], shape[1]
        new_height, new_width = self._smallest_size_at_least(
            height, width, resize_min)
        # Simple wrapper around tf.resize_images
        resized_image = tf.compat.v1.image.resize(
            image, [new_height, new_width], method=tf.image.ResizeMethod.BILINEAR, align_corners=False)

        return resized_image

    def _data_preprocessing(self, data_location, output_height, output_width, num_channels, batch_size):
        """
        Read the image, then process it to a 3-D tensor for tensorflow, 
        includes decoding, cropping, and resizing.
        """
        data_graph = tf.Graph()
        with data_graph.as_default():
            if imghdr.what(data_location) != "jpeg":
                raise ValueError(
                    "At this time, only JPEG images are supported, please try another image.")
            image_buffer = tf.io.read_file(data_location)
            image = tf.image.decode_jpeg(image_buffer, channels=num_channels)
            image = self._image_resize(image, RESIZE_MIN)
            image = self._central_crop(image, output_height, output_width)
            image.set_shape([output_height, output_width, num_channels])
            image = self._mean_image_subtraction(
                image, CHANNEL_MEANS, num_channels)
            input_shape = [batch_size, output_height,
                           output_width, num_channels]
            images = tf.reshape(image, input_shape)
        data_sess = tf.compat.v1.Session(graph=data_graph)
        image = data_sess.run(images)

        return image

    def run_inference(self, data_location, lables_path, num_top_preds):
        """
        Read and preprocess the image, returns human-readable predictions.
        Preprocess the image to tensor which can be accepted by tensorflow, 
        then run inference, and get human-readable predictions lastly.
        """
        image = self._data_preprocessing(
            data_location, RESNET_IMAGE_SIZE, RESNET_IMAGE_SIZE, NUM_CHANNELS, 1)
        predictions = self.infer_sess.run(self.output_tensor, feed_dict={
                                          self.input_tensor: image})
        predictions_labels = self._get_top_predictions(
            predictions, lables_path, False, num_top_preds)

        return predictions_labels
