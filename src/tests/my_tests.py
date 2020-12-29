import os

from graphviz import Digraph, nohtml

from config import path_config


def test_dot():
    g = Digraph('g',
                filename=os.path.join(path_config.OUTPUT_PATH, 'btree.gv'),
                node_attr={'shape': 'record', 'height': '.1'})

    g.node('node0', nohtml('<f0> NP |<f1>|<f2> NE'))

    g.node('node1', nohtml('<f0> Armando'))
    g.node('node2', nohtml('<f0> Piero|<f1> |<f2> Pina'))
    g.node('node3', nohtml('<f0> Alessandro|<f1> |<f2> Aurora'))

    g.edge('node0:f1', 'node2:f0')
    g.edge('node0:f1', 'node1:f0')
    g.edge('node0:f1', 'node3:f2')

    g.node('node4', nohtml('<f0> Domenico |<f1>|<f2> Patrizia'))
    g.node('node5', nohtml('<f0> Adolfo |<f1>|<f2> Paola'))
    g.node('node6', nohtml('<f0> Umberto |<f1>|<f2> Valentina'))

    g.edge('node3:f1', 'node4:f2')
    g.edge('node3:f1', 'node5:f2')
    g.edge('node3:f1', 'node6:f2')

    g.node('node7', nohtml('<f0> Giacomo'))
    g.node('node8', nohtml('<f0> Giovanni'))
    g.node('node9', nohtml('<f0> Carolina'))
    g.node('node10', nohtml('<f0> Sofia'))

    g.edge('node4:f1', 'node7:f0')
    g.edge('node4:f1', 'node8:f0')
    g.edge('node5:f1', 'node9:f0')
    g.edge('node5:f1', 'node10:f0')

    g.view()


def test_fdo():
    from graphviz import Graph

    g = Graph('G', filename=os.path.join(path_config.OUTPUT_PATH, 'fdpclust.gv'), engine='fdp')

    with g.subgraph(name='cluster_A') as a:
        a.node('NP')
        a.node('NE')

    with g.subgraph(name='clusterB') as c:
        c.node('Alessandro')
        c.node('Aurora')

    with g.subgraph(name='clusterC') as c:
        c.node('Piero')
        c.node('Pina')

    g.edge('Armando', 'cluster_A')
    g.edge('Piero', 'cluster_A')
    g.edge('Aurora', 'cluster_A')

    g.edge('Patrizia', 'clusterB')
    g.edge('Paola', 'clusterB')
    g.edge('Valentina', 'clusterB')

    with g.subgraph(name='clusterD') as c:
        c.node('Domenico')
        c.node('Patrizia')

    g.edge('Giacomo', 'clusterD')
    g.edge('Giovanni', 'clusterD')

    with g.subgraph(name='clusterE') as c:
        c.node('Adolfo')
        c.node('Paola')

    g.edge('Carolina', 'clusterE')
    g.edge('Sofia', 'clusterE')

    with g.subgraph(name='clusterF') as c:
        c.node('Umberto')
        c.node('Valentina')

    g.view()


if __name__ == "__main__":
    test_dot()
    test_fdo()
