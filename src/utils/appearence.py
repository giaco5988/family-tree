"""
It defines family tree appearance
"""
from abc import abstractmethod
from typing import Tuple


class AbstractAppearance:
    """
    Interface for family tree appearance
    """

    @staticmethod
    @abstractmethod
    def single_person(person_name: str) -> str:
        return ""

    @staticmethod
    @abstractmethod
    def couple(male_name: str, female_name: str) -> str:
        return ""

    @staticmethod
    @abstractmethod
    def edge_str(node_name: str, parents_node: str, is_male: bool, num_spouse: int) -> Tuple[str, str]:
        return "", ""


class SimpleAppearance(AbstractAppearance):

    @staticmethod
    def single_person(person_name: str) -> str:
        return f"<f0> {person_name}"

    @staticmethod
    def couple(male_name: str, female_name: str):
        return f'<f0> {male_name} |<f1>|<f2> {female_name}'

    @staticmethod
    def edge_str(node_name: str, parents_node: str, is_male: bool, num_spouse: int) -> Tuple[str, str]:
        place = 'f0' if is_male or num_spouse == 0 else 'f2'
        return f'{parents_node}:f1', f'{node_name}:{place}'
