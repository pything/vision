import argparse
from pathlib import Path

import cv2
import torch
from apppath import ensure_existence
from draugr import sprint
from draugr.opencv_utilities import frame_generator
from draugr.torch_utilities import Split, global_torch_device
from torch import quantization
from tqdm import tqdm
from warg import NOD

from neodroidvision import PROJECT_APP_PATH
from neodroidvision.detection.single_stage.ssd.architecture import (
  SingleShotDectectionNms,
  )
from neodroidvision.detection.single_stage.ssd.bounding_boxes.ssd_transforms import (
  SSDTransform,
  )
from neodroidvision.utilities.torch_utilities.check_pointer import CheckPointer


@torch.no_grad()
def export_detection_model(
    cfg: NOD,
    model_ckpt: Path,
    model_export_path: Path = Path("torch_model"),
    verbose: bool = True,
    onnx_export: bool = False,
    strict_jit: bool = False,
    ) -> None:
  """

:param verbose:
:type verbose:
:param cfg:
:type cfg:
:param model_ckpt:
:type model_ckpt:
:param model_export_path:
:type model_export_path:
:return:
:rtype:
"""
  model = SingleShotDectectionNms(cfg)

  checkpointer = CheckPointer(
      model, save_dir=ensure_existence(PROJECT_APP_PATH.user_data / "results")
      )
  checkpointer.load(model_ckpt, use_latest=model_ckpt is None)
  print(
      f"Loaded weights from {model_ckpt if model_ckpt else checkpointer.get_checkpoint_file()}"
      )

  model.post_init()
  model.to(global_torch_device())

  transforms = SSDTransform(
      cfg.input.image_size, cfg.input.pixel_mean, split=Split.Testing
      )
  model.eval()

  pre_quantize_model = False
  if pre_quantize_model:  # Accuracy may drop!
    if True:
      model = quantization.quantize_dynamic(model, dtype=torch.qint8)
    else:
      pass
      # model = quantization.quantize(model)

  frame_g = frame_generator(cv2.VideoCapture(0))
  for image in tqdm(frame_g):
    example_input = (transforms(image)[0].unsqueeze(0).to(global_torch_device()),)
    try:
      traced_script_module = torch.jit.script(
          model,
          # example_input,
          )
      exp_path = model_export_path.with_suffix(".compiled")
      traced_script_module.save(str(exp_path))
      print(f"Traced Ops used {torch.jit.export_opnames(traced_script_module)}")
      sprint(
          f"Successfully exported JIT Traced model at {exp_path}", color="green"
          )
    except Exception as e_i:
      sprint(f"Torch JIT Trace export does not work!, {e_i}", color="red")

    break


def main():
  from configs.mobilenet_v2_ssd320_voc0712 import base_cfg

  # from configs.efficient_net_b3_ssd300_voc0712 import base_cfg
  # from configs.vgg_ssd300_coco_trainval35k import base_cfg
  # from .configs.vgg_ssd512_coco_trainval35k import base_cfg

  global_torch_device(override=global_torch_device(cuda_if_available=False))

  parser = argparse.ArgumentParser(description="SSD Demo.")
  parser.add_argument(
      "--ckpt",
      type=str,
      default=PROJECT_APP_PATH.user_data / "ssd" / "models" /
              "mobilenet_v2_ssd320_voc0712.pth"
      # "mobilenet_v2_ssd320_voc0712.pth"
      # "vgg_ssd300_coco_trainval35k.pth"
      # "vgg_ssd512_coco_trainval35k.pth"
      ,
      help="Trained " "weights.",
      )
  args = parser.parse_args()

  export_detection_model(cfg=base_cfg, model_ckpt=Path(args.ckpt))


if __name__ == "__main__":
  main()
