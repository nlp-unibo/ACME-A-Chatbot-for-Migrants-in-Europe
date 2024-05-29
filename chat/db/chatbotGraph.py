from enum import Enum
import random
import json
import networkx as nx
import os
import matplotlib


# Reads the JSON file containing all the questions and answers associated to each node
def read_json(path):
    # Opening JSON file
    f = open(path)

    # returns JSON object as a dictionary
    data = json.load(f)

    # Creating the dictionary (key = node name, value = JSON obj with class, question and sentences
    result = {}

    # Iterating through the data
    for i in data:
        # Finding the name of the graph node
        node = i['node']

        # Removing the node's name to get the well-formed JSON object
        i.pop('node')

        # Removing the second version of the question
        if 'questions' in i.keys():
            i['question'] = i['questions'][0]
            i.pop('questions')

        # Inserting the key-value pair into the result dictionary
        result[node] = i

    # Closing file
    f.close()

    return result


# Returns the two lists of tuples representing the nodes and the edges of the graph respectively
def create_graph(graph_path, questions_path):
    # Getting the sentences associated to each node
    nodes_dict = read_json(questions_path)

    # Reading the file that contains the graph
    with open(graph_path) as f:
        lines = f.readlines()

    # List of tuples containing all the nodes of the graph (nodes nad replies)
    # Each tuple has this structure (node_name, {class, question, sentences_list})
    nodes = []

    # List of tuples containing all the edges of the graph (attacks and endorsements)
    # Each tuple has this structure (first_node_name, second_node_name, {"type": "endorse/attack"})
    edges = []

    # Set that contains all the argumentative nodes
    args = set()

    # Set that contains all the reply nodes
    replies = set()

    # Each line of the file has either a node, or a reply, or an attack, or an endorsement
    for line in lines:

        # Normal node or Reply node
        if 'arg(' in line or 'argR(' in line:
            # Extracting the name of the node from the line e.g. line = 'arg(nonLivIstrBasso)'
            node_name = line.split('(')[1].split(')')[0]

            # Inserting the tuple in the list of nodes
            nodes.append((node_name, nodes_dict[node_name]))

            # Inserting the node name to the corresponding set
            if 'arg(' in line:
                args.add(node_name)
            else:
                replies.add(node_name)

        # Attack
        elif 'att(' in line:
            # Extracting the names of the two nodes
            nodes_names = line.split('(')[1].split(')')[0]
            first_node = nodes_names.split(',')[0]
            second_node = nodes_names.split(',')[1]

            # Inserting the tuple in the list of edges
            edges.append((first_node, second_node, {"type": "attack"}))

        # Endorsement
        elif 'end(' in line:
            # Extracting the names of the two nodes
            nodes_names = line.split('(')[1].split(')')[0]
            first_node = nodes_names.split(',')[0]
            second_node = nodes_names.split(',')[1]

            # Inserting the tuple in the list of edges
            edges.append((first_node, second_node, {"type": "endorse"}))

        else:
            print('ERROR, node not recognized')

    return nodes, edges, args, replies


class ImmigrationGraph:

    def __init__(self) -> None:
        current_path = os.path.dirname(os.path.realpath(__file__))
        self.graph = nx.DiGraph()
        self.nodes, self.edges, self.args, self.replies = create_graph(current_path+ '\grafo.txt', current_path+ '\questions.json')
        self.create_nodes()
        self.create_edges()

    def create_nodes(self):
        self.graph.add_nodes_from(self.nodes)
        return self.graph.number_of_nodes()

    def create_edges(self):
        self.graph.add_edges_from(self.edges)
        return self.graph.number_of_edges()

    def get_arg_nodes_labels(self):
        return self.args

    def get_reply_nodes_labels(self):
        return self.replies

    # def get_attack_edges(self):
    #    return set(filter(lambda edge : self.graph.edges[edge[0], edge[1]]["type"] == "attack", self.graph.edges))

    # def get_endorse_edges(self):
    #    return set(filter(lambda edge : self.graph.edges[edge[0], edge[1]]["type"] == "endorse", self.graph.edges))

    def get_arg_sentences(self):
        arg_nodes = self.get_arg_nodes_labels()

        arg_sentences = []
        for arg_node in arg_nodes:
            arg_sentences.extend(self.graph.nodes[arg_node]["sentences"])

        return arg_sentences

    def get_arg_sentence(self, arg: str):
        arg_sentences = self.graph.nodes[arg]["sentences"]
        return arg_sentences[0]

    def get_arg_question(self, arg: str):
        return self.graph.nodes[arg]["question"]

    def get_reply_sentences(self):
        reply_nodes = self.get_reply_nodes_labels()

        reply_sentences = []
        for reply_node in reply_nodes:
            reply_sentences.extend(self.graph.nodes[reply_node]["sentences"])

        return reply_sentences

    def get_arguments_attacking_reply(self, reply: str):
        '''Get the arguments that attack
        the given reply node (label)'''

        preds = self.graph.predecessors(reply)

        return set(filter(lambda pred: self.graph.edges[pred, reply]["type"] == "attack", preds))

    def get_arguments_endorsing_reply(self, reply: str):
        '''Get the arguments that endorse
        the given reply node (label)'''

        prevs = self.graph.predecessors(reply)

        return set(filter(lambda prev: self.graph.edges[prev, reply]["type"] == "endorse", prevs))

    def get_arguments_attacked_by_argument(self, arg: str):
        '''Get the arguments attacked
        by the given argument node (label)'''

        nexts = self.graph.successors(arg)

        return set(filter(lambda next: self.graph.edges[arg, next]["type"] == "attack", nexts))

    def get_arguments_attacking_argument(self, arg: str):
        '''Get the arguments that attack
        the given argument node (label)'''

        prevs = self.graph.predecessors(arg)

        return set(filter(lambda prev: self.graph.edges[prev, arg]["type"] == "attack", prevs))

    def get_replies_endorsed_by_argument(self, arg: str):
        '''Get the arguments endorsed
        by the given argument node (label)'''

        nexts = self.graph.successors(arg)

        return set(filter(lambda next: (self.graph.edges[arg, next]["type"] == "endorse" and next in self.replies), nexts))

    def get_node_containing_sentence(self, sentence: str):

        for node, prop in self.graph.nodes.data():

            if sentence in prop["sentences"]:
                return node
        return None

    def get_sentence_corresponding_question(self, question: str, _class: str):

        arg_nodes = self.get_arg_nodes_labels()
        for arg_node in arg_nodes:
            if question == self.graph.nodes[arg_node]["question"] and _class == self.graph.nodes[arg_node]["class"]:
                return self.get_arg_sentence(arg_node)
        return None


if __name__ == '__main__':
    g = ImmigrationGraph()

    print(g.create_nodes())
    print(g.create_edges())

    # print(g.get_argument_from_question("Are you a woman?", "n"))

    # nx.draw_networkx(G=g)