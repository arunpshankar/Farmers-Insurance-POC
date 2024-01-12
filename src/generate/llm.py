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

    def predict(self, task: str, query: str, context: str) -> Optional[str]:
        """
        Generates a response for a given task and query using the chat model.

        Args:
            task (str): The task to be performed by the model.
            query (str): The query or input text for the model.
            context (str): The context from within to find an answr

        Returns:
            Optional[str]: The model's response or None if an error occurred.
        """
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
        

if __name__ == '__main__':
    llm = LLM()
    task = "Given a query and context, find the answer to the query from the provided context. "
    query = "How to reinstate policy if cancelled mid-term?"
    context = """Q_A_Answer__c : If a policy cancels mid-term for non-payment, the insured has up to 11 calendar days to reinstate it with a lapse. ex: A policy cancelled on 4/1/2021 would have until 4/11/2021 to make payment to reinstate with lapse. Counting 4/1/2021 as day 1 this would be 11 calendar days."""
    answer = llm.predict(task=task, query=query, context=context)
    print(answer)
