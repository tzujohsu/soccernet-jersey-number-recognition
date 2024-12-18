_base_ = [
    '_base_dbnetpp_resnet50-dcnv2_fpnc.py',         # model architecture
    '../_base_/datasets/soccernet-gen.py',              # get our custom dataset
    '../_base_/default_runtime.py',                 # default configurations for eval, logging  
    '../_base_/schedules/schedule_adam_600e.py',     # get the optimizer
]

load_from = 'https://download.openmmlab.com/mmocr/textdet/dbnetpp/dbnetpp_resnet50-dcnv2_fpnc_1200e_icdar2015/dbnetpp_resnet50-dcnv2_fpnc_1200e_icdar2015_20220829_230108-f289bd20.pth'

train_cfg = dict(type='EpochBasedTrainLoop', max_epochs=10, val_interval=5)
default_hooks = dict(
    checkpoint=dict(interval=5, type='CheckpointHook')
)

BATCH_SIZE = 8
auto_scale_lr = dict(base_batch_size=BATCH_SIZE)

model = dict(
    data_preprocessor=dict(
        type='TextDetDataPreprocessor',
        mean=[127.4395, 135.9471,  84.0932],
        std=[38.5333, 38.7357, 47.5903],
        bgr_to_rgb=True,
        pad_size_divisor=32
    )
)

# dataset settings
train_list = [_base_.soccernet_gen_textdet_train]
val_list = [_base_.soccernet_gen_textdet_val]
test_list = [_base_.soccernet_gen_textdet_test]

train_pipeline = [
    dict(type='LoadImageFromFile', color_type='color_ignore_orientation'),
    dict(
        type='LoadOCRAnnotations',
        with_bbox=True,
        with_polygon=True,
        with_label=True,
    ),
    dict(
        type='TorchVisionWrapper',
        op='ColorJitter',
        brightness=32.0 / 255,
        saturation=0.5),
    dict(
        type='ImgAugWrapper',
        args=[['Fliplr', 0.5],
              dict(cls='Affine', rotate=[-10, 10]), ['Resize', [0.5, 3.0]]]),
    dict(type='RandomCrop', min_side_ratio=0.4),
    dict(type='Resize', scale=(640, 640), keep_ratio=True),
    dict(type='Pad', size=(640, 640)),
    dict(
        type='PackTextDetInputs',
        meta_keys=('img_path', 'ori_shape', 'img_shape'))
]

test_pipeline = [
    dict(type='LoadImageFromFile', color_type='color_ignore_orientation'),
    dict(type='Resize', scale=(640, 640), keep_ratio=True),
    dict(type='Pad', size=(640, 640)),
    dict(
        type='LoadOCRAnnotations',
        with_polygon=True,
        with_bbox=True,
        with_label=True,
    ),
    dict(
        type='PackTextDetInputs',
        meta_keys=('img_path', 'ori_shape', 'img_shape', 'scale_factor',
                   'instances'))
]

train_dataloader = dict(
    batch_size=BATCH_SIZE,
    num_workers=2,
    persistent_workers=True,
    sampler=dict(type='DefaultSampler', shuffle=True),
    dataset=dict(
        type='ConcatDataset',
        datasets=train_list,
        pipeline=train_pipeline))

val_dataloader = dict(
    batch_size=BATCH_SIZE,
    num_workers=2,
    persistent_workers=True,
    sampler=dict(type='DefaultSampler', shuffle=False),
    dataset=dict(
        type='ConcatDataset',
        datasets=val_list,
        pipeline=test_pipeline))

test_dataloader = dict(
    batch_size=BATCH_SIZE,
    num_workers=2,
    persistent_workers=True,
    sampler=dict(type='DefaultSampler', shuffle=False),
    dataset=dict(
        type='ConcatDataset',
        datasets=test_list,
        pipeline=test_pipeline))

# visualization = _base_.default_hooks.visualization
# visualization.update(
#     dict(enable=True, show=True, draw_gt=False, draw_pred=True))