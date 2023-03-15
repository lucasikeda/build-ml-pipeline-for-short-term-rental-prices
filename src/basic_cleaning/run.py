#!/usr/bin/env python
'''
Download from W&B the raw dataset and apply some basic data cleaning, exporting the result to a new artifact
'''
import argparse
import logging
import os

import pandas as pd
import wandb


logging.basicConfig(level=logging.INFO, format="%(asctime)-15s %(message)s")
logger = logging.getLogger()


def go(args):

    run = wandb.init(job_type="basic_cleaning")

    logger.info("Downloading artifact")
    artifact = run.use_artifact(args.input_artifact)
    artifact_path = artifact.file()

    logger.info(f"Got from WnB: {artifact_path}")

    df = pd.read_csv(artifact_path)

    # Drop the duplicates
    logger.info("Cleaning data")
    idx = df['price'].between(args.min_price, args.max_price)
    df = df[idx].copy()
    # Convert last_review to datetime
    df['last_review'] = pd.to_datetime(df['last_review'])
    # removing out of boundaries entries
    idx = df['longitude'].between(-74.25, -73.50) & df['latitude'].between(40.5, 41.2)
    df = df[idx].copy()
    # Saving to output file
    df.to_csv(args.output_artifact, index=False)

    artifact = wandb.Artifact(
        name=args.output_artifact,
        type=args.output_type,
        description=args.output_description,
    )
    artifact.add_file(args.output_artifact)
    run.log_artifact(artifact)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="A very basic data cleaning",
        fromfile_prefix_chars="@",
    )

    parser.add_argument(
        "--input_artifact",
        type=str,
        help="",
        required=True,
    )

    parser.add_argument(
        "--output_artifact",
        type=str,
        help="",
        required=True,
    )

    parser.add_argument(
        "--output_type", type=str, 
        help="Type for the output", 
        required=True
    )

    parser.add_argument(
        "--output_description", type=str, 
        help="Description of the output", 
        required=True
    )

    parser.add_argument(
        "--min_price",
        type=float,
        help="Minimum price",
        required=True,
    )

    parser.add_argument(
        "--max_price",
        type=float,
        help="Maximum price",
        required=True,
    )

    args = parser.parse_args()

    go(args)
