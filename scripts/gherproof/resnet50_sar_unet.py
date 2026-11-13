"""ResNet-50 encoder/decoder; encoder keys exactly match the published MoCo backbone."""
from __future__ import annotations

import torch
from torch import nn
from torch.nn import functional as F


class Bottleneck(nn.Module):
    expansion = 4

    def __init__(self, inplanes: int, planes: int, stride: int = 1, downsample=None):
        super().__init__()
        self.conv1 = nn.Conv2d(inplanes, planes, kernel_size=1, bias=False)
        self.bn1 = nn.BatchNorm2d(planes)
        self.conv2 = nn.Conv2d(planes, planes, kernel_size=3, stride=stride, padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(planes)
        self.conv3 = nn.Conv2d(planes, planes * self.expansion, kernel_size=1, bias=False)
        self.bn3 = nn.BatchNorm2d(planes * self.expansion)
        self.relu = nn.ReLU(inplace=True)
        self.downsample = downsample
        self.stride = stride

    def forward(self, x):
        identity = x
        out = self.relu(self.bn1(self.conv1(x)))
        out = self.relu(self.bn2(self.conv2(out)))
        out = self.bn3(self.conv3(out))
        if self.downsample is not None:
            identity = self.downsample(x)
        return self.relu(out + identity)


class ResNet50Encoder(nn.Module):
    def __init__(self):
        super().__init__()
        self.inplanes = 64
        self.conv1 = nn.Conv2d(2, 64, kernel_size=7, stride=2, padding=3, bias=False)
        self.bn1 = nn.BatchNorm2d(64)
        self.relu = nn.ReLU(inplace=True)
        self.maxpool = nn.MaxPool2d(kernel_size=3, stride=2, padding=1)
        self.layer1 = self._make_layer(64, 3)
        self.layer2 = self._make_layer(128, 4, stride=2)
        self.layer3 = self._make_layer(256, 6, stride=2)
        self.layer4 = self._make_layer(512, 3, stride=2)

    def _make_layer(self, planes: int, blocks: int, stride: int = 1):
        outplanes = planes * Bottleneck.expansion
        downsample = None
        if stride != 1 or self.inplanes != outplanes:
            downsample = nn.Sequential(nn.Conv2d(self.inplanes, outplanes, kernel_size=1, stride=stride, bias=False),
                                       nn.BatchNorm2d(outplanes))
        layers = [Bottleneck(self.inplanes, planes, stride, downsample)]
        self.inplanes = outplanes
        layers.extend(Bottleneck(self.inplanes, planes) for _ in range(1, blocks))
        return nn.Sequential(*layers)

    def forward(self, x):
        stem = self.relu(self.bn1(self.conv1(x)))
        x = self.maxpool(stem)
        f1 = self.layer1(x)
        f2 = self.layer2(f1)
        f3 = self.layer3(f2)
        f4 = self.layer4(f3)
        return stem, f1, f2, f3, f4


class DecodeBlock(nn.Module):
    def __init__(self, in_channels: int, skip_channels: int, out_channels: int):
        super().__init__()
        self.reduce = nn.Conv2d(in_channels, out_channels, 1, bias=False)
        self.body = nn.Sequential(
            nn.Conv2d(out_channels + skip_channels, out_channels, 3, padding=1, bias=False),
            nn.GroupNorm(8, out_channels), nn.GELU(),
            nn.Conv2d(out_channels, out_channels, 3, padding=1, bias=False),
            nn.GroupNorm(8, out_channels), nn.GELU(),
        )

    def forward(self, x, skip):
        x = F.interpolate(self.reduce(x), size=skip.shape[-2:], mode="bilinear", align_corners=False)
        return self.body(torch.cat([x, skip], dim=1))


class ResNet50SARUNet(nn.Module):
    """Binary water segmentation decoder on the exact two-channel ResNet50 backbone."""
    def __init__(self):
        super().__init__()
        self.encoder = ResNet50Encoder()
        self.decode4 = DecodeBlock(2048, 1024, 512)
        self.decode3 = DecodeBlock(512, 512, 256)
        self.decode2 = DecodeBlock(256, 256, 128)
        self.decode1 = DecodeBlock(128, 64, 64)
        self.head = nn.Sequential(nn.Conv2d(64, 32, 3, padding=1), nn.GELU(), nn.Conv2d(32, 1, 1))

    def load_ssl4eo_backbone(self, state_dict: dict[str, torch.Tensor]) -> None:
        # The downloaded checkpoint contains the standard ResNet-50 encoder only;
        # require an exact match instead of silently dropping/massaging tensors.
        self.encoder.load_state_dict(state_dict, strict=True)

    def forward(self, x):
        size = x.shape[-2:]
        stem, f1, f2, f3, f4 = self.encoder(x)
        x = self.decode4(f4, f3)
        x = self.decode3(x, f2)
        x = self.decode2(x, f1)
        x = self.decode1(x, stem)
        x = F.interpolate(self.head(x), size=size, mode="bilinear", align_corners=False)
        return x
