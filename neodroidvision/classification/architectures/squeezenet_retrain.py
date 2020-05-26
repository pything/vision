import torch
import torchvision

from draugr.torch_utilities.freezing.retrain_utilities import (
    get_trainable_parameters,
    set_all_parameter_requires_grad,
)


def squeezenet_retrain(
    num_classes: int, pretrained: bool = True, train_only_last_layer: bool = False
):
    model = torchvision.models.squeezenet1_1(pretrained=pretrained)
    if train_only_last_layer:
        set_all_parameter_requires_grad(model)

    model.num_categories = num_classes
    model.classifier[1] = torch.nn.Conv2d(
        512, num_classes, kernel_size=(1, 1), stride=(1, 1)
    )

    return model, get_trainable_parameters(model)
