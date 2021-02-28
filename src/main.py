import argparse
import pandas as pd
import os
import logging
from graphviz import Digraph
from utils.persons import create_family
from utils.appearence import SimpleAppearance
from utils.graph import GraphAssembler
from pathlib import Path
from utils.utils import update_file_name
from config import path_config

LOGGER = logging.getLogger(__name__)


def cli():

    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    # Preprocess input data
    parser.add_argument('--data_path', type=str, help='csv table path', default=None)
    parser.add_argument('--out_dir', type=str, help='output directory path', default=str(Path.home()))

    return parser.parse_args()


def main():
    args = cli()
    if not args.data_path:
        tmp = input("Please type input csv table absolute path (press directly enter to use example of Canossa family):")
        args.data_path = tmp if len(tmp) > 0 else os.path.join(path_config.DOCS_PATH, 'canossa_family.csv')
    out_file = update_file_name(os.path.join(args.out_dir, 'family_tree.gv'))
    LOGGER.info(f'Load family connection from  {args.data_path}')
    LOGGER.info(f'Save family tree to {out_file}')

    # load data and create ans empty graph
    df = pd.read_csv(args.data_path)
    assert len(set(df['id'])) == len(df), f'IDs are not unique.'
    g = Digraph('g', filename=out_file, node_attr={'shape': 'record', 'height': '.1'})

    # create graph
    assembler = GraphAssembler(ui=SimpleAppearance, graph=g)
    persons = create_family(df=df)
    assembler(persons=persons)

    g.view()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
