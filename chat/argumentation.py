from chat.db.chatbotGraph import ImmigrationGraph


class ArgumentationManager:

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(ArgumentationManager, cls).__new__(cls)
        return cls.instance

    def __init__(self) -> None:
        self.arg_graph = ImmigrationGraph()
        self.clear()


    def clear(self):
        # self.history_args = [] # history of argument nodes communicated by user
        self.history_replies = [] # history of reply nodes given to user
        self.history_args = []
        self.potentially_cons_replies = ['statRifProtSuss', 'statRifProtSussU', 'protSpeciale'] #set()
        self.explanation_dictionary = {}

    def explain_why_reply(self, reply: str):
        '''Retrieves the argument nodes, among those in the history
        that support the given reply.'''

        endorsing_args = self.arg_graph.get_arguments_endorsing_reply(reply)
        
        supporting_status_args = [node for node in endorsing_args if node in self.history_args]
        
        return supporting_status_args


    def explain_why_not_reply(self, reply: str):
        '''Retrieves the argument nodes, among those in the history
        that attack the given reply'''  

        attacking_args = self.arg_graph.get_arguments_attacking_reply(reply)
        
        
        # arguments in the status set of arguments already collected
        # for user that also attack the reply
        attacking_status_arg = [node for node in attacking_args if node in self.history_args]

        return attacking_status_arg

    def build_explanation(self, reply: str):

        
        discarded_replies = []
        for arg in self.history_args:
            endorsed_replies = self.arg_graph.get_replies_endorsed_by_argument(arg)
            for endorsed_reply in endorsed_replies:
                if (reply != endorsed_reply and endorsed_reply not in discarded_replies):
                    discarded_replies.append(endorsed_reply)


        supporting_args_sentences = [self.arg_graph.get_arg_sentence(why) for why in self.explain_why_reply(reply)]

        #print(supporting_args_sentences)
        template_args = {
            "I": "you",
            " am ": " are ",
            "'m": " are",
            " me ": " you ",
            " was ": " were "
        }

        def replace_template(sentence):

            for k, v in template_args.items():

                sentence = sentence.replace(k,v)
            return sentence

        if 'I am a man' in supporting_args_sentences:
            supporting_args_sentences.remove("I am a man")
        if 'I am a woman' in supporting_args_sentences:
            supporting_args_sentences.remove("I am a woman")

        explanation = ".\nThis answer is supported by what you said: \n" + ', '.join([replace_template(supporting_arg_sentence) for supporting_arg_sentence in supporting_args_sentences])

        explanation += "\n\n"

        replies_dict = {"statRifProtSussU": "Refugee Status",
                        "statRifProtSuss": "Refugee Status",
                        "protSpeciale": "Special Protection",
                        "nessProt": "no protection"}

        if reply not in self.explanation_dictionary.keys():
            self.explanation_dictionary[reply] = "You might get the " + str(replies_dict[reply]) + ' because ' + ', '.join([replace_template(supporting_arg_sentence) for supporting_arg_sentence in supporting_args_sentences]) + '\n'

        # Removing double explanation for no refugee status, leaving the one with longer explanation
        if reply != "statRifProtSussU" and reply != "statRifProtSuss" and "statRifProtSussU" in discarded_replies and "statRifProtSuss" in discarded_replies:
            why_not_man = self.explain_why_not_reply("statRifProtSussU")
            why_not_woman = self.explain_why_not_reply("statRifProtSuss")
            if len(why_not_man) > len(why_not_woman):
                discarded_replies.remove("statRifProtSuss")
            else:
                discarded_replies.remove("statRifProtSussU")

            # Creating a single explanation for the refugee status
            why_not_refugee_status = why_not_woman + why_not_man
            # Removing duplicates from the list
            why_not_refugee_status = list(dict.fromkeys(why_not_refugee_status))

            if "uomo" in why_not_refugee_status:
                why_not_refugee_status.remove("uomo")
            if "donna" in why_not_refugee_status:
                why_not_refugee_status.remove("donna")

        for discarded_reply in discarded_replies:
            if (reply == "statRifProtSussU" and discarded_reply != "statRifProtSuss") or (reply == "statRifProtSuss" and discarded_reply != "statRifProtSussU") or (reply != "statRifProtSussU" and reply != "statRifProtSuss"):
                if discarded_reply not in self.explanation_dictionary.keys():
                    if discarded_reply == "statRifProtSussU" or discarded_reply == "statRifProtSuss":
                        whynots = why_not_refugee_status
                    else:
                        whynots = self.explain_why_not_reply(discarded_reply)
                    if len(whynots) > 0:
                        explanation += f"You might not {self.arg_graph.get_arg_sentence(discarded_reply).lower().replace('you might ', '')} because \n"
                        for whynot in whynots:

                            explanation += replace_template(self.arg_graph.get_arg_sentence(whynot)) + "\n"

                        explanation += "\n"
                    else:
                        explanation += 'You might get the ' + str(replies_dict[discarded_reply]) + ' but you did not share enough information\n'
                else:
                    explanation += self.explanation_dictionary[discarded_reply]

        return explanation

    def is_conflict_free(self, argument: str):
        '''Checks whether the given argument
        is in conflict with the ones in the history'''

        attacked = self.arg_graph.get_arguments_attacked_by_argument(argument)
        
        # if there is no common node between history and the attacks 
        # to the given argument, then it is conflict free
        return not (attacked & set(self.history_args))

    
    def is_consistent_reply(self, reply: str):
        '''Checks whether the reply is consistent. By definition, it is consistent
        if reply is endorsed by the history of arguments, and acceptable, meaning
        if every attack to the reply is attacked by the history. History must
        be a conflict-free set'''


        attacking_args = self.arg_graph.get_arguments_attacking_reply(reply)

        for attacking_arg in attacking_args:

            # see if it is attacked by something in the history
            counterattacking_args = self.arg_graph.get_arguments_attacking_argument(attacking_arg)

            # if no counterattacking argument is found in the history
            # then it is not consistent
            if not (counterattacking_args & set(self.history_args)):
                return False

        return True

    def add_argument(self, arg: str):
        '''Adds node to history if it is not already present'''
        
        if arg not in self.history_args:

            self.history_args.append(arg)

    def add_potentially_cons_replies(self, replies: 'list[str]'):
        '''Adds replies to the potentially_cons replies if 
           1) they are not already present, avoiding duplicates
           2) they are not attacked by arguments in the history'''
        

        for reply in replies:
            if len(self.explain_why_not_reply(reply)) == 0 and reply not in self.potentially_cons_replies:
                self.potentially_cons_replies.append(reply)

    def choose_reply(self, user_msg: 'list[str]'):
        '''Takes the user message (or rather, the sentences in the KB 
        most similar to the user message), and returns a consistent reply or,
        if absent, information the system needs to turn a potentially consistent
        reply into a consistent one.'''
        # if user message is not an explanation request
        # add it to the arguments in the chat


        for sentence in user_msg:
            arg_node = self.arg_graph.get_node_containing_sentence(sentence)
            
            if self.is_conflict_free(arg_node):
                self.add_argument(arg_node)

            else:
                return "Your message contradicts previous statements, and as such it was not considered.\nPlease, answer the question differently."
        # filter past potentially consistent replies that are no longer compatible with newly added arguments
        # explain why not retrieves argument in the history attacking the given reply
        self.potentially_cons_replies = list(filter(lambda potentially_cons_reply : len(self.explain_why_not_reply(potentially_cons_reply)) == 0, self.potentially_cons_replies))

        # retrieve the replies endorsed by the nodes activated by user's message.
        # add them to potentially consistent replies if not duplicates
        replies = []
        for node in self.history_args:
            replies = self.arg_graph.get_replies_endorsed_by_argument(node)
            self.add_potentially_cons_replies(replies)

        
        if len(replies) == 0 and len(self.potentially_cons_replies) == 0:
            return 'No consistent answer has been found'    
        print(self.potentially_cons_replies)
        # Removing replies already given to the user in order to give every possible answer
        for r in self.potentially_cons_replies.copy():
            if r in self.history_replies:
                self.potentially_cons_replies.remove(r)

        # if there is even a single consistent reply we return it to the user
        for potentially_cons_reply in self.potentially_cons_replies.copy():
            if self.is_consistent_reply(potentially_cons_reply) and potentially_cons_reply not in self.history_replies:
                # append it to history of replies and remove it from potentially_conss
                
                self.history_replies.append(potentially_cons_reply)
                self.potentially_cons_replies.remove(potentially_cons_reply)

                expl = self.build_explanation(potentially_cons_reply)
                return self.arg_graph.get_arg_sentence(potentially_cons_reply) + expl + "\nIf you want, you may share new information. To stop this conversation, click on the button.\n"
            elif self.is_consistent_reply(potentially_cons_reply) and potentially_cons_reply in self.history_replies:
                # user is continuing conversation but new facts do not change or add a new consistent reply
                return "\nThis new fact doesn't change my advice. Do you have anything else to share? Otherwise, click on the button to stop.\n"

        for potentially_cons_reply in self.potentially_cons_replies.copy():
            # potentially consistent
            attack_args = self.arg_graph.get_arguments_attacking_reply(potentially_cons_reply)

            # elicit data from user about possible counterattacks
            # this method is called for each message
            # so we need to loop over every attack 
            # first check whether counterattacks are already in history
            # then we ask questions to user only for those that aren't in history
            for attack_arg in attack_args:

                counterattack_args = self.arg_graph.get_arguments_attacking_argument(attack_arg)

                if not any([counterattack_arg in self.history_args for counterattack_arg in counterattack_args]):
                    # if there isn't even a single counter attack 
                    # in the history we must elicit info
                    return self.arg_graph.get_arg_question(counterattack_args.pop())
            
        # reach this point if no counterattacks have been found
        # but in practical arg graph shouldn't happen
        return "\nNo consistent answer has been found. \nIf you want, you may share new information. To stop this conversation, click on the button.\n"
