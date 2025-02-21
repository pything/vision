#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Christian Heider Nielsen"
__doc__ = r"""

           Created on 30/06/2020
           """

import random
from pathlib import Path
from typing import Tuple, Union

import numpy
import torch
from matplotlib import pyplot
from neodroidvision.data.classification import DictImageFolder, SplitDictImageFolder
from warg import drop_unused_kws, passes_kws_to

from draugr.torch_utilities import Split, SupervisedDataset, to_tensor

__all__ = ["PairDataset"]


class PairDataset(
    SupervisedDataset
):  # TODO: Extract image specificity of class to a subclass and move this super pair class to a general torch lib.
    """
# This dataset generates a pair of images. 0 for geniune pair and 1 for imposter pair
"""

    @passes_kws_to(DictImageFolder.__init__)
    @drop_unused_kws
    def __init__(
        self, data_path: Union[str, Path], split: Split = Split.Training, **kwargs
    ):
        super().__init__()

        self.split = split
        # name = self.split_names[split]
        if split == split.Testing:
            name = split.Testing.value
            self._dataset = DictImageFolder(root=data_path / name, **kwargs)
        else:
            name = split.Training.value
            self._dataset = SplitDictImageFolder(
                root=data_path / name, split=split, **kwargs
            )

    def __getitem__(self, idx1: int) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
    returns torch.tensors for img pair and a label for whether the pair is of the same class (1 if not the same)



:param idx1:
:type idx1:
:return:
:rtype:
"""
        t1 = random.choice(self._dataset.category_names)

        if random.randint(0, 1):
            while True:
                t2 = random.choice(self._dataset.category_names)
                if t1 != t2:
                    break
            return (
                self._dataset.sample(t1, idx1)[0],
                self._dataset.sample(
                    t2, random.randint(0, self._dataset.category_sizes[t2])
                )[0],
                torch.ones(1, dtype=torch.long),
            )

        while True:
            idx2 = random.randint(0, self._dataset.category_sizes[t1])
            if idx1 != idx2:
                break

        return (
            self._dataset.sample(t1, idx1)[0],
            self._dataset.sample(t1, idx2)[0],
            torch.zeros(1, dtype=torch.long),
        )

    @property
    def response_shape(self) -> Tuple[int, ...]:
        """

:return:
:rtype:
"""
        return (len(self._dataset.category_names),)

    @property
    def predictor_shape(self) -> Tuple[int, ...]:
        """

:return:
:rtype:
"""
        return to_tensor(self.__getitem__(0)[0]).shape

    def __len__(self):
        return len(self._dataset)

    def sample(self, horizontal_merge: bool = False) -> None:
        """

  """
        dl = iter(
            torch.utils.data.DataLoader(
                self, batch_size=9, shuffle=True, num_workers=1, pin_memory=False
            )
        )
        for _ in range(3):
            images1, images2, labels = next(dl)
            X1 = images1.numpy()
            X1 = numpy.transpose(X1, [0, 2, 3, 1])
            X2 = images2.numpy()
            X2 = numpy.transpose(X2, [0, 2, 3, 1])
            if horizontal_merge:
                X = numpy.dstack((X1, X2))
            else:
                X = numpy.hstack((X1, X2))
            PairDataset.plot_images(X, labels)

    @staticmethod
    def plot_images(images, label=None) -> None:
        """

:param images:
:type images:
:param label:
:type label:
"""
        images = images.squeeze()
        if label is not None:
            assert len(images) == len(label) == 9

        fig, axes = pyplot.subplots(3, 3)
        for i, ax in enumerate(axes.flat):
            ax.imshow(images[i], cmap="Greys_r")

            if label is not None:
                ax.set_xlabel(f"{label[i]}")
            ax.set_xticks([])
            ax.set_yticks([])

        pyplot.show()


if __name__ == "__main__":
    sd = PairDataset(Path.home() / "Data" / "mnist_png", split=Split.Validation)
    print(sd.predictor_shape)
    print(sd.response_shape)
    sd.sample()
