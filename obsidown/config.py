"""The role of this module is to create the correct pipeline for the conversion of the obsidian notes into markdown notes."""

from pydantic import BaseModel


class SourcesList(BaseModel):
    paths: list[str]
    images: list[str]


class Destination(BaseModel):
    base: str  # URL base
    path: str  # where to store the files
    images: str  # where to store the images
    filesystem: str  # the location of the processed files


class Operation(BaseModel):
    name: str
    options: dict


class Config(BaseModel):
    sources: SourcesList
    output: Destination
    pipeline: list[Operation]
