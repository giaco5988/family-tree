import os
from typing import List, Type
import logging

import pandas as pd
from graphviz import Digraph, nohtml

from config import path_config
from utils.appearence import AbstractAppearance, SimpleAppearance
from utils.persons import Person, create_family

LOGGER = logging.getLogger(__name__)


class GraphAssembler:
    """
    Manages graph creation (edges and nodes)
    """
    def __init__(self, ui: Type[AbstractAppearance], graph: Digraph):
        """
        Initialize ui appearance and graph instance
        :param ui: appearance of graph boxes
        :param graph: graph instance
        """
        self._ui = ui
        self._graph = graph

    def __call__(self, persons: List[Person]) -> None:
        """
        Create edge and nodes of the graph based on family connections
        :param persons: List of persons
        :return: None
        """
        LOGGER.info(f'Assembly graph.')
        self._create_nodes(persons=persons)
        self._create_edges(persons=persons)

    def _create_edges(self, persons: List[Person]) -> None:
        """
        Create edge between nodes (parents-sons relationship)
        :param persons: list of persons in the family
        :return: None
        """
        for person in persons:
            if len(person.parents) > 0:
                node_name, parents_node = person.get_node_name(), person.parents[0].get_node_name()
                parents_ids = f"{person.father_id}{person.mother_id}"
                edge_str = self._ui.edge_str(node_name, parents_node, str(person.person_id), parents_ids)
                self._graph.edge(edge_str[0], edge_str[1])

    def _create_nodes(self, persons: List[Person]) -> None:
        """
        Create graph nodes, either a single person or an union
        :param persons: list of persons in the family
        :return: None
        """
        nodes = set()
        persons_dict = {x.person_id: x for x in persons}
        for person in persons:
            node_name = person.get_node_name()
            if node_name not in nodes:
                if len(person.spouse) == 1 and len(person.spouse[0].spouse) == 1:
                    male = person if person.is_male else person.spouse[0]
                    female = person if not person.is_male else person.spouse[0]
                    self._graph.node(node_name,
                                     nohtml(self._ui.couple(male.name, female.name, male.person_id, female.person_id)))
                elif len(person.spouse) == 0:
                    self._graph.node(node_name, nohtml(self._ui.single_person(person.name, person.person_id)))
                else:
                    couples = [[(y.person_id, y.name) for y in x] for x in person.get_couples_in_node(persons_dict)]
                    self._graph.node(node_name, nohtml(self._ui.multi_couple(couples=couples)))
                nodes.add(node_name)


def testing():
    df = pd.read_csv('/Users/Giacomo/Downloads/family-tree - connections-1.csv')
    assert len(set(df['id'])) == len(df), f'IDs are not unique.'
    g = Digraph('g',
                filename=os.path.join(path_config.OUTPUT_PATH, 'btree_custom.gv'),
                node_attr={'shape': 'record', 'height': '.1'})

    # create family
    persons = create_family(df=df)

    # create graph
    assembler = GraphAssembler(ui=SimpleAppearance, graph=g)
    assembler(persons=persons)

    g.view()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    testing()
