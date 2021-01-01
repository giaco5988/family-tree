"""
It defines family tree appearance
"""
from abc import abstractmethod
from typing import Tuple, Sequence, List


class AbstractAppearance:
    """
    Interface for family tree appearance
    """

    @staticmethod
    @abstractmethod
    def single_person(person_name: str, person_id: int) -> str:
        return ""

    @staticmethod
    @abstractmethod
    def couple(male_name: str, female_name: str, male_id: int, female_id: int) -> str:
        return ""

    @staticmethod
    @abstractmethod
    def multi_couple(couples: List[Sequence[Tuple[int, str]]]) -> str:
        """
        :param couples: List containing tuples with ((male_id, male_name), (female_id, female_name))
        :return: nohtml string as in https://graphviz.readthedocs.io/en/stable/examples.html#structs-revisited-py
        """
        return ""

    @staticmethod
    @abstractmethod
    def edge_str(node_name: str, parents_node: str, person_id: str, parents_ids: str) -> Tuple[str, str]:
        return "", ""


class SimpleAppearance(AbstractAppearance):

    @staticmethod
    def single_person(person_name: str, person_id: int) -> str:
        return f"<{person_id}> {person_name}"

    @staticmethod
    def couple(male_name: str, female_name: str, male_id: int, female_id: int):
        return f'<{male_id}> {male_name} |<{male_id}{female_id}>|<{female_id}> {female_name}'

    @staticmethod
    def edge_str(node_name: str, parents_node: str, person_id: str, parents_ids: str) -> Tuple[str, str]:
        return f'{parents_node}:{parents_ids}', f'{node_name}:{person_id}'

    @staticmethod
    def multi_couple(couples: List[Sequence[Tuple[int, str]]]) -> str:
        ans = ""
        for (male_id, male), (female_id, female) in couples:
            ans = ans + "|" + "{" + f'<{male_id}> {male} |<{male_id}{female_id}>|<{female_id}> {female}' + "}"
        return "{" + ans[1:] + "}"
