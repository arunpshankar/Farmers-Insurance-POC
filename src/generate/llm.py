from langchain.prompts.chat import HumanMessagePromptTemplate, ChatPromptTemplate
from langchain.chat_models import ChatVertexAI
from src.config.logging import logger
from src.config.setup import config
from typing import Optional

class LLM:
    """
    A class representing a Language Model using Vertex AI.

    Attributes:
        model (ChatVertexAI): The chat model loaded from Vertex AI.
    """

    def __init__(self) -> None:
        """
        Initializes the LLM class by loading the chat model.
        """
        self.model = self._initialize_model()

    def _initialize_model(self) -> Optional[ChatVertexAI]:
        """
        Loads the chat model from Vertex AI.

        Returns:
            ChatVertexAI: An instance of the Vertex AI chat model.
        """
        try:
            model = ChatVertexAI(
                model_name=config.TEXT_GEN_MODEL_NAME,
                temperature=0.1,
                max_output_tokens=1024,
                verbose=True
            )
            logger.info("Chat model loaded successfully.")
            return model
        except Exception as e:
            logger.error(f"Failed to load the model: {e}")
            return None

    def find_answer(self, query: str, context: str) -> Optional[str]:
        """
        Generates a response for a given task and query using the chat model.

        Args:
            query (str): The query or input text for the model.
            context (str): The context from within to find an answr

        Returns:
            Optional[str]: The model's response or None if an error occurred.
        """
        task = "Given a query and context, find the answer to the query from the provided context."
        logger.info(f'Query = {query}')
        try:
            human_template = "{task}\\nnQuery:\n{query}\n\nContext:\n{context}\n\nAnswer:"
            human_message = HumanMessagePromptTemplate.from_template(human_template)
            chat_template = ChatPromptTemplate.from_messages([human_message])
            prompt = chat_template.format_prompt(task=task, query=query, context=context).to_messages()
            response = self.model(prompt)
            completion = response.content
            return completion
        except Exception as e:
            logger.error(f"Error during model prediction: {e}")
            return None
        

    def format_answer(self, answer: str) -> str:
        """
        given an anser clean the anser by removing the citiations and formating it and clear to read
        
        """
        task = "given an answer, clean and format the answer by removing citations and breaking down the steps and making it clean and easy to read"
        logger.info('Formatting generated answer')
        try:
            human_template = "{task}\\nnAnswer:\n{answer}\n\Formatted Answer:"
            human_message = HumanMessagePromptTemplate.from_template(human_template)
            chat_template = ChatPromptTemplate.from_messages([human_message])
            prompt = chat_template.format_prompt(task=task, answer=answer).to_messages()
            response = self.model(prompt)
            completion = response.content
            return completion
        except Exception as e:
            logger.error(f"Error during model prediction: {e}")
            return None

        

if __name__ == '__main__':
    llm = LLM()

    # compute answer from top matching doc
    task = "Given a query and context, find the answer to the query from the provided context. "
    query = "How to reinstate policy if cancelled mid-term?"
    context = """Q_A_Answer__c : If a policy cancels mid-term for non-payment, the insured has up to 11 calendar days to reinstate it with a lapse. ex: A policy cancelled on 4/1/2021 would have until 4/11/2021 to make payment to reinstate with lapse. Counting 4/1/2021 as day 1 this would be 11 calendar days."""
    answer = llm.find_answer(query=query, context=context)
    print(answer)
    print('-' * 100)
    # clean and format answer 
    answer = "To process a refund void stop pay request, you can open a Word document and title it with the current date followed by Void Stop and your initials [3]. You can then review the diary comments and void stop pay request [3]. At least one must state the agent or named insured was advised not to attempt to cash the original check [3]. If not noted, the request cannot be processed [3]. You can also process the void via AS400 [4]. Be sure to screen shot and copy to Word document prior to finalizing AS400 void [4]. You can also reapply a same day refund to a policy [4]. The Diary Comment policy should state: Processed Void Stop Pay request to Reapply refund to policy [4]. You can save Word document screen shots to shared Z drive: Operations/Accounting Services/Accounting Services/Void check_Stop pay/2Void Stop Pays/Year Void Stop Pays/Month Void Stops [4]. If one of the individuals on the refund check is now deceased, you can stop payment and reissue a refund check payable to both the living person and â€œThe Estate ofâ€ the deceased person [2]."
    formatted_answer = llm.format_answer(answer=answer)
    print(formatted_answer)