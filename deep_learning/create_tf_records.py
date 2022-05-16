import io
import csv
import pandas as pd
import absl
import tensorflow as tf
import contextlib2
from object_detection.utils import dataset_util
from object_detection.dataset_tools import tf_record_creation_util

"""
Usage:
python create_tf_records.py --csv_input=dataset/test.csv  --output_path=deep_learning/data/test.record
python create_tf_records.py --csv_input=dataset/train.csv  --output_path=deep_learning/data/train.record
"""

flags = absl.flags
flags.DEFINE_string('csv_input', '', 'Path to the CSV input')
flags.DEFINE_string('output_path', '', 'Path to output TFRecord')
FLAGS = flags.FLAGS

def correct_number_type(nums):
    for num in nums:
        if "-" in num:
            return 0
        if "." in num:
            if "." == num[3]:
                num = num[:3]
            elif "." == num[2]:
                num = num[:2]
        return int(num)

def create_tf_example(image_row):
    filename = image_row[0] # Filename of the image. Empty if image is not from file
    filename_path = "dataset/hand_picked/" + filename
    filename = filename.encode('utf8')
    with tf.io.gfile.GFile(filename_path, "rb") as fid:
        encoded_jpg = fid.read()
    encoded_jpg_io = io.BytesIO(encoded_jpg)
    image_format = b'jpg'
    height, width = 640, 640 # Image height and width

    xmins = [] # List of normalized left x coordinates in bounding box (1 per box)
    xmaxs = [] # List of normalized right x coordinates in bounding box
                # (1 per box)
    ymins = [] # List of normalized top y coordinates in bounding box (1 per box)
    ymaxs = [] # List of normalized bottom y coordinates in bounding box
                # (1 per box)
    classes_text = [] # List of string class name of bounding box (1 per box)
    classes = [] # List of integer class id of bounding box (1 per box)
    
    positions = [correct_number_type(s) for s in image_row[1:] if s != ""]

    for i in range(0, len(positions), 4):
        xmins.append(positions[i] / width)
        ymins.append(positions[i+1] / width)
        xmaxs.append(positions[i+2] / width)
        ymaxs.append(positions[i+3] / width)
        classes.append(1)
        classes_text.append("pin-hole".encode('utf8'))

    tf_example = tf.train.Example(features=tf.train.Features(feature={
        'image/height': dataset_util.int64_feature(height),
        'image/width': dataset_util.int64_feature(width),
        'image/filename': dataset_util.bytes_feature(filename),
        'image/source_id': dataset_util.bytes_feature(filename),
        'image/encoded': dataset_util.bytes_feature(encoded_jpg_io.read()),
        'image/format': dataset_util.bytes_feature(image_format),
        'image/object/bbox/xmin': dataset_util.float_list_feature(xmins),
        'image/object/bbox/xmax': dataset_util.float_list_feature(xmaxs),
        'image/object/bbox/ymin': dataset_util.float_list_feature(ymins),
        'image/object/bbox/ymax': dataset_util.float_list_feature(ymaxs),
        'image/object/class/text': dataset_util.bytes_list_feature(classes_text),
        'image/object/class/label': dataset_util.int64_list_feature(classes),
    }))
    return tf_example


def main(_):
    # writer = tf.io.TFRecordWriter(FLAGS.output_path)
    num_shards=20
    # output_filebase='/path/to/train_dataset.record'

    with contextlib2.ExitStack() as tf_record_close_stack:
        output_tfrecords = tf_record_creation_util.open_sharded_output_tfrecords(
                                tf_record_close_stack, FLAGS.output_path, num_shards)
        with open(FLAGS.csv_input, "r") as r:
            reader = csv.reader(r)
            next(reader)
            for i, row in enumerate(reader):
                tf_example = create_tf_example(row)
                output_shard_index = i % num_shards
                output_tfrecords[output_shard_index].write(tf_example.SerializeToString())
            # writer.write(tf_example.SerializeToString())

    # writer.close()

if __name__ == '__main__':
  absl.app.run(main)