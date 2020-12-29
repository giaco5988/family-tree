from typing import Dict, Tuple, List, Sequence, Type
import logging
import pandas as pd
import numpy as np
import os
from config import path_config
from graphviz import Digraph, nohtml
from utils.appearence import AbstractAppearance, SimpleAppearance

LOGGER = logging.getLogger(__name__)


class Person:
    """
    It defines one person with all direct family connections
    """
    def __init__(self, database_row: pd.Series):
        """
        Initialize person with anagraphic data
        :param database_row: one row of connections dataframe
        """
        self._person_id = int(database_row['id'])
        self._name = database_row['person_name']
        tmp = database_row['mother_id']
        self._mother_id = tmp if np.isnan(tmp) else int(tmp)
        tmp = database_row['father_id']
        self._father_id = tmp if np.isnan(tmp) else int(tmp)
        self._is_male = database_row['sex'] == "M"
        self._children = None
        self._siblings = None
        self._half_siblings = None
        self._parents = None
        self._spouses = None
        self._spouse_ids = []
        count = 0
        while True:
            count += 1
            col = f"marriage_{count}"
            if col not in database_row.keys():
                break
            else:
                tmp = database_row[col]
                tmp = tmp if np.isnan(tmp) else int(tmp)
                if not np.isnan(tmp):
                    self._spouse_ids.append(tmp)
        self._spouse_ids = tuple(self._spouse_ids)

    @property
    def person_id(self) -> int:
        return self._person_id

    @property
    def is_male(self) -> bool:
        return self._is_male

    @property
    def name(self) -> str:
        return self._name

    @property
    def parents(self) -> Tuple["Person", "Person"]:
        return self._parents

    @property
    def father_id(self) -> int:
        return self._father_id

    @property
    def mother_id(self) -> int:
        return self._mother_id

    def get_node_name(self) -> str:
        """
        Get node name from male to female
        :return:
        """
        tmp = map(lambda x: str(x.person_id), sorted([self, *self._spouses], key=lambda x: x.is_male, reverse=True))

        return "node-" + "-".join(tmp)

    @property
    def spouse(self) -> Sequence["Person"]:
        return self._spouses

    def add_parents(self, persons: Dict[str, "Person"]) -> None:
        """
        Add parents among all persons in the family
        :param persons: list of all persons in the family
        :return: None
        """
        parents_ids = tuple([self._father_id, self._mother_id])
        if any(not np.isnan(x) for x in parents_ids):
            self._parents = tuple([persons[x] for x in parents_ids])

    def add_spouse(self, persons: Dict[str, "Person"]) -> None:
        """
        Add spouse/s from all persons in the family
        :param persons: list of all persons in the family
        :return: None
        """
        self._spouses = tuple([persons[x] for x in self._spouse_ids])

    def add_children(self, persons: List["Person"]) -> None:
        """
        Add children from all persons in the family
        :param persons: list of all persons in the family
        :return: None
        """
        tmp = []
        for person in persons:
            if self._person_id in (person.father_id, person.mother_id):
                tmp.append(person)
        self._children = tuple(tmp)

    def add_siblings(self, persons: List["Person"]) -> None:
        """
        Add siblings and half-siblings from all persons in the family
        :param persons: list of all persons in the family
        :return: None
        """
        tmp_siblings, tmp_half_siblings = [], []
        for person in persons:
            if person.parents is not None and self._parents is not None and person.person_id != self.person_id:
                if all(x is y for x, y in zip(self._parents, person.parents)):
                    tmp_siblings.append(person)
                elif any(x is y for x, y in zip(self._parents, person.parents)):
                    tmp_half_siblings.append(person)

        self._siblings, self._half_siblings = tuple(tmp_siblings), tuple(tmp_half_siblings)


def create_family(df: pd.DataFrame) -> List[Person]:
    """
    Create family connections
    :param df: dataframe with family connections
    :return: list of persons containing connections
    """
    LOGGER.info(f"Create family connections.")
    persons = {}
    for _, row in df.iterrows():
        persons[row['id']] = Person(database_row=row)

    for person in persons.values():
        person.add_parents(persons)
        person.add_spouse(persons)

    for person in persons.values():
        person.add_children(list(persons.values()))

    for person in persons.values():
        person.add_siblings(list(persons.values()))

    return list(persons.values())


def assembly_graph(persons: List[Person], appearance: Type[AbstractAppearance], g: Digraph) -> None:
    """
    Create edge and nodes of the graph based on family connections
    :param persons: List of persons
    :param appearance: appearance of graph boxes
    :param g: graph
    :return: None
    """
    LOGGER.info(f'Assembly graph.')
    # create nodes
    nodes = set()
    for person in persons:
        tmp = person.get_node_name()
        if tmp not in nodes:
            if len(person.spouse) == 1:
                male = person.name if person.is_male else person.spouse[0].name
                female = person.name if not person.is_male else person.spouse[0].name
                g.node(tmp, nohtml(appearance.couple(male_name=male, female_name=female)))
                nodes.add(tmp)
            elif len(person.spouse) == 0:
                g.node(tmp, nohtml(appearance.single_person(person.name)))
                nodes.add(tmp)
            else:
                assert False, "Not implemented with more than one spouse"

    # create edges
    for person in persons:
        if person.parents is not None:
            node_name, parents_node = person.get_node_name(), person.parents[0].get_node_name()
            edge_str = SimpleAppearance.edge_str(node_name, parents_node, person.is_male, len(person.spouse))
            g.edge(edge_str[0], edge_str[1])


def testing():
    df = pd.read_csv('/Users/Giacomo/Downloads/family-tree - connections.csv')
    g = Digraph('g',
                filename=os.path.join(path_config.OUTPUT_PATH, 'btree_custom.gv'),
                node_attr={'shape': 'record', 'height': '.1'})

    # create family
    persons = create_family(df=df)

    # create graph
    assembly_graph(persons, SimpleAppearance, g)

    g.view()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    testing()
