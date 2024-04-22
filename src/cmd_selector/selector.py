
class ModelSelector:
    """
    Class for selecting language model for generating text
    """

    def __init__(self, models):
        """
        Init method for ModelSelector
        :param models: dictionary with models, where key is id of model and value is dict with 'name' and 'path'
        """
        self.models = models

    def get_user_choice(self):
        """
        Method for getting user choice from console
        :return: user choice
        """
        print("What llm model would you like to use:")
        for key in sorted(self.models):
            print(f"{key} - {self.models[key]['name']}")
        print("0 - exit")

        choice = input("Введите номер модели: ")
        return choice

    def run(self):
        """
        Method for running ModelSelector
        :return: name of selected model
        """
        while True:
            choice = self.get_user_choice()

            if choice in self.models:
                return self.models[choice]['name']
            elif choice == '0':
                print("ok, bye")
                break
            else:
                print("retry")

