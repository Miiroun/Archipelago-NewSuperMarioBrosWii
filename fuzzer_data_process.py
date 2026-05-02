import yaml

from fuzz import BaseHook, GenOutcome
from IPython.display import display
import pandas

class Hook(BaseHook):
    #self.df = pandas.DataFrame({"Results": [1], "Exception": [1], "options": [1]})
    df = [{"Results": [1], "Exception": [1], "options": [1]}]

    def setup_main(self, args):
        """
        The args parameter is the `Namespace` containing the parsed arguments from the CLI.
        setup is classed as early as possible after argument parsing in the
        main process. It is guaranteed to be only ever called once. It will
        always be called before any worker process is started
        """
        pass


    def setup_worker(self, args):
        """
        The args parameter is the `Namespace` containing the parsed arguments from the CLI.
        setup is classed as early as possible after starting a worker process.
        It is guaranteed to only ever be called once per worker process, before
        any generation attempt.
        """
        pass


    def reclassify_outcome(self, outcome, exception):
        """
        The outcome is a `GenOutcome` from generation.
        The exception is the exception raised during generation if one happened, None otherwise.

        This function is called in the worker process just after the result is first decided.
        The one exception is for timeouts where the outcome has to be processed on the main process.
        As such, this function must do very minimal work and not make
        assumptions as whether it's running in worker or in the main process.
        """
        #new_row = pandas.DataFrame({"Results": outcome, "Exception": exception}, index=[0])
        #self.df = pandas.concat([self.df, new_row], ignore_index=True)
        #self.df[len(self.df)] = {"Results": outcome, "Exception": exception}
        #self.df[len(self.df)] = {"Options": 3}
        #self.df.append({"Options": 3})
        self.df = [{"Options" : 3}]

        return outcome, exception

    def before_generate(self, args):
        """
        This method will be called once per generation, just before we actually
        call into archipelago. The `args` argument contains the `Namespace`
        object passed to archipelago for generation. It can be modified since
        this happens before generation.
        """
        pass


    def after_generate(self, multiworld, output_dir):
        """
        This method will be called once per generation except if the generation timed out.
        If you need to inspect the failure, use `reclassify_outcome` instead.
        If the generation succeeds, multiworld is the object returned by
        archipelago on success, otherwise it's None
        """
        options = yaml.safe_load(output_dir)

        #new_row = pandas.DataFrame({"options": options}, index=[0])
        #self.df = pandas.concat([self.df, new_row], ignore_index=True)
        #self.df[len(self.df)] = {"Options": options}


    def finalize(self):
        """
        This method will be called once just before the main process exits. It
        will only be called on the main process
        """
        display(self.df)