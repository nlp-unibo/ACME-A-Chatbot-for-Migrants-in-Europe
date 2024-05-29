import networkx as nx
from enum import Enum
import random

class ArgLabels(Enum):
    A1="a1"
    A2="a2"
    A3="a3"
    A4="a4"
    A5="a5"
    A6="a6"
    A7="a7"
    A8="a8"
    A9="a9"
    A10="a10"
    A11="a11"
    A12="a12"
    A13="a13"
    A14="a14"
    A15="a15"
    A16="a16"

class ReplyLabels(Enum):
    R1="r1"
    R2="r2"
    R3="r3"

class CovidVaccineGraph:

    def __init__(self) -> None:
        self.graph = nx.DiGraph()
        self.create_nodes()
        self.create_edges()
        

    def create_nodes(self):
        self.graph.add_nodes_from([
            (
                ArgLabels.A1.value, {"class":"p", "question":"Are you celiac?", "sentences": ["I am celiac",
                                                        "I suffer from the celiac disease",
                                                        "I am afflicted with the celiac disease",
                                                        "I have the celiac disease",
                                                        "I recently found out to be celiac",
                                                        "I have suffered from celiac disease since birth"]
                }
            ),
            (
                ArgLabels.A2.value, {"class":"n", "question":"Are you celiac?", "sentences": ["I do not have the celiac disease",
                                                        "I am not celiac",
                                                        "I do not suffer from the celiac disease",
                                                        "I am not afflicted with the celiac disease"]
                }
            ),
            (
                ArgLabels.A3.value, {
                    "class":"n", "question":"Are you immunosuppressed?", "sentences": ["I am not immunosuppressed",
                                                        "I do not suffer from immunosuppression",
                                                        "I am not afflicted with immunosuppression"]
                }
            ),
            (
                ArgLabels.A4.value, {
                    "class":"p", "question":"Are you immunosuppressed?", "sentences": ["I am immunosuppressed",
                                                        "I suffer from immunosuppression",
                                                        "I am afflicted with immunosuppression",
                                                        "I do suffer from immunosuppression",
                                                        "I indeed suffer from immunosuppression",
                                                        "I recently found out to be immunosuppressed"]
                }
            ),
            (
                ArgLabels.A5.value, {
                    "class":"n", "question":"Do you have any drug allergy?", "sentences": ["I do not have any drug allergy",
                                                        "I do not suffer from drug allergies",
                                                        "I do not suffer from any drug allergy",
                                                        "I am not afflicted with any drug allergy",
                                                        "I do not have medication allergies",
                                                        "I do not have any medication allergy"]
                }
            ),
            (
                ArgLabels.A6.value, {
                    "class":"p", "question":"Do you have any drug allergy?", "sentences": ["I have a drug allergy",
                                                        "I do have a drug allergy",
                                                        "I have a serious drug allergy",
                                                        "I suffer from drug allergy",
                                                        "I am afflicted with drug allergies",
                                                        "I suffer from medication allergies"]
                }
            ),
            (
                ArgLabels.A7.value, {
                    "class":"n", "question":"Do you have bronchial asthma?", "sentences": ["I do not suffer from bronchial asthma",
                                                        "I don't have bronchial asthma",
                                                        "I've never had bronchial asthma",
                                                        "I am not afflicted with bronchial asthma"]
                }
            ),
            (
                ArgLabels.A8.value, {
                    "class":"p", "question":"Do you have bronchial asthma?", "sentences": ["I suffer from bronchial asthma",
                                                        "I have bronchial asthma",
                                                        "I am affected by bronchial asthma",
                                                        "I am afflicted with bronchial asthma"]
                }
            ),
            (
                ArgLabels.A9.value, {
                    "class":"p", "question":"Do you have diabetes?", "sentences": ["I suffer from diabetes",
                                                        "I am diabetic",
                                                        "I am affected by diabetes"]
                }
            ),
            (
                ArgLabels.A10.value, {
                    "class":"n", "question":"Do you have diabetes?", "sentences": ["I do not suffer from diabetes",
                                                        "I am not affected by diabetes",
                                                        "I am not diabetic",
                                                        "I don't have diabetes"]
                }
            ),
            (
                ArgLabels.A11.value, {
                    "class":"p", "question":"Are you allergic to latex?", "sentences": ["I suffer from latex allergy",
                                                        "I'm allergic to latex",
                                                        "I have a latex allergy",
                                                        "Latex causes me an allergic reaction"]
                }
            ),
            (
                ArgLabels.A12.value, {
                    "class":"n", "question":"Are you allergic to latex?", "sentences": ["I do not suffer from latex allergy",
                                                        "I'm not allergic to latex",
                                                        "I do not have a latex allergy",
                                                        "Latex does not cause me an allergic reaction",
                                                        "I have never had an allergic reaction with latex"]
                }
            ),
            (
                ArgLabels.A13.value, {
                    "class":"n", "question":"Do you suffer from mastocytosis?", "sentences": ["I do not suffer from mastocytosis",
                                                        "I am not afflicted with mastocystosis",
                                                        "I do not have mastocystosis",
                                                        "Mastocystosis is not an health concern for me"]
                }
            ),
            (
                ArgLabels.A14.value, {
                    "class":"p", "question":"Do you suffer from mastocytosis?", "sentences": ["I suffer from mastocytosis",
                                                        "I am afflicted with mastocystosis",
                                                        "I have a condition called mastocystosis"]
                }
            ),
            (
                ArgLabels.A15.value, {
                    "class":"p", "question":"Have you had anaphylactic reactions?", "sentences": ["I have experienced a serious anaphylaxis in the past",
                                                        "I have had an anaphylactic reaction in the past",
                                                        "I have already had an anaphylactic reaction before",
                                                        "I went into anaphylactic shock before"]
                }
            ),
            (
                ArgLabels.A16.value, {
                    "class":"n", "question":"Have you had anaphylactic reactions?", "sentences": ["I've never experienced a serious anaphylaxis",
                                                        "I've never had a serious anaphylactic reaction",
                                                        "I've never gone into anaphylactic shock before"]
                }
            ),
            (
                ReplyLabels.R1.value, {
                    "sentences": ["Get vaccinated at any vaccine site. No special monitoring"]
                }
            ),
            (
                ReplyLabels.R2.value, {
                    "sentences": ["Get vaccinated at any vaccine site. Monitoring for 60 minutes"]
                }
            ),
            (
                ReplyLabels.R3.value, {
                    "sentences": ["Get vaccinated at the hospital"]
                }
            )

        ])

        return self.graph.number_of_nodes()

    def create_edges(self):
        # add argument and their negation
        for i1,i2 in zip(range(1,16,2), range(2,17,2)):
            self.graph.add_edge(f"a{i1}",f"a{i2}",type="attack")

        for i1,i2 in zip(range(2,17,2), range(1,16,2)):
            self.graph.add_edge(f"a{i1}",f"a{i2}",type="attack")

        
        self.graph.add_edges_from([
            (
                ArgLabels.A1.value, ReplyLabels.R1.value, {"type":"endorse"}
            ),
            (
                ArgLabels.A2.value, ReplyLabels.R1.value, {"type":"endorse"}
            ),
            (
                ArgLabels.A3.value, ReplyLabels.R1.value, {"type":"endorse"}
            ),
            (
                ArgLabels.A4.value, ReplyLabels.R1.value, {"type":"endorse"}
            ),
            (
                ArgLabels.A5.value, ReplyLabels.R1.value, {"type":"endorse"}
            ),
            (
                ArgLabels.A7.value, ReplyLabels.R1.value, {"type":"endorse"}
            ),
            (
                ArgLabels.A9.value, ReplyLabels.R1.value, {"type":"endorse"}
            ),
            (
                ArgLabels.A10.value, ReplyLabels.R1.value, {"type":"endorse"}
            ),
            (
                ArgLabels.A12.value, ReplyLabels.R1.value, {"type":"endorse"}
            ),
            (
                ArgLabels.A13.value, ReplyLabels.R1.value, {"type":"endorse"}
            ),
            (
                ArgLabels.A16.value, ReplyLabels.R1.value, {"type":"endorse"}
            ),
            (
                ArgLabels.A6.value, ReplyLabels.R1.value, {"type":"attack"}
            ),
            (
                ArgLabels.A8.value, ReplyLabels.R1.value, {"type":"attack"}
            ),
            (
                ArgLabels.A11.value, ReplyLabels.R1.value, {"type":"attack"}
            ),
            (
                ArgLabels.A14.value, ReplyLabels.R1.value, {"type":"attack"}
            ),
            (
                ArgLabels.A15.value, ReplyLabels.R1.value, {"type":"attack"}
            ),
            (
                ArgLabels.A6.value, ReplyLabels.R2.value, {"type":"endorse"}
            ),
            (
                ArgLabels.A11.value, ReplyLabels.R2.value, {"type":"endorse"}
            ),
            (
                ArgLabels.A14.value, ReplyLabels.R2.value, {"type":"endorse"}
            ),
            (
                ArgLabels.A8.value, ReplyLabels.R2.value, {"type":"attack"}
            ),
            (
                ArgLabels.A15.value, ReplyLabels.R2.value, {"type":"attack"}
            ),
            (
                ArgLabels.A8.value, ReplyLabels.R3.value, {"type":"endorse"}
            ),
            (
                ArgLabels.A15.value, ReplyLabels.R3.value, {"type":"endorse"}
            ),
        ])
        
        return self.graph.number_of_edges()    


    def get_arg_nodes_labels(self):

        return set(n.value for n in ArgLabels)

    def get_reply_nodes_labels(self):
        return set(n.value for n in ReplyLabels)

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
        return arg_sentences[random.randint(0, len(arg_sentences) - 1)]

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

        return set(filter(lambda pred : self.graph.edges[pred, reply]["type"] == "attack", preds))

    
    def get_arguments_endorsing_reply(self, reply: str):
        '''Get the arguments that endorse 
        the given reply node (label)'''

        prevs = self.graph.predecessors(reply)

        return set(filter(lambda prev : self.graph.edges[prev, reply]["type"] == "endorse", prevs))

    def get_arguments_attacked_by_argument(self, arg: str):
        '''Get the arguments attacked 
        by the given argument node (label)'''

        nexts = self.graph.successors(arg)

        return set(filter(lambda next : self.graph.edges[arg, next]["type"] == "attack", nexts))

    def get_arguments_attacking_argument(self, arg: str):
        '''Get the arguments that attack 
        the given argument node (label)'''

        prevs = self.graph.predecessors(arg)

        return set(filter(lambda prev : self.graph.edges[prev, arg]["type"] == "attack", prevs))

    def get_replies_endorsed_by_argument(self, arg: str):
        '''Get the arguments endorsed 
        by the given argument node (label)'''

        nexts = self.graph.successors(arg)

        return set(filter(lambda next : self.graph.edges[arg, next]["type"] == "endorse", nexts))
    
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


if __name__=='__main__':

    g = CovidVaccineGraph()

    print(g.create_nodes())
    print(g.create_edges())

    print(g.get_argument_from_question("Do you have any drug allergy?", "n"))
