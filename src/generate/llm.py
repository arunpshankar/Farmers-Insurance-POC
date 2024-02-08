from langchain.prompts.chat import HumanMessagePromptTemplate, ChatPromptTemplate
from langchain.chat_models import ChatVertexAI
from src.config.logging import logger
from src.config.setup import config
from typing import Optional
import time

class LLM:
    """
    A class representing a Language Model using Vertex AI.

    Attributes:
        model (ChatVertexAI): The chat model loaded from Vertex AI.
    """
    _model_instance = None  # Class attribute to hold the singleton instance

    def __init__(self) -> None:
        """
        Initializes the LLM class by loading the chat model.
        """
        if LLM._model_instance is None:  # Check if the instance doesn't exist
            LLM._model_instance = self._initialize_model()  # Create the instance if not exist
        self.model = LLM._model_instance  # Assign the singleton instance to self.model

    @classmethod
    def _initialize_model(cls) -> Optional[ChatVertexAI]:
        """
        Loads the chat model from Vertex AI.

        Returns:
            ChatVertexAI: An instance of the Vertex AI chat model.
        """
        if cls._model_instance is not None:  # Check if the instance already exists
            return cls._model_instance  # Return the existing instance

        try:
            model = ChatVertexAI(
                model_name=config.TEXT_GEN_MODEL_NAME,
                temperature=0.0,
                max_output_tokens=2048,
                verbose=True
            )
            logger.info("Chat model loaded successfully.")
            cls._model_instance = model  # Store the created instance
            return model
        except Exception as e:
            logger.error(f"Failed to load the model: {e}")
            return None

    def find_answer(self, query: str, context: str) -> Optional[str]:
        """
        Generates a response for a given task and query using the chat model, with retry logic in case of errors.
        """
        task = """Given a query and context, identify the answer within the provided context. Please provide a detailed, comprehensive answer. Stick to the original content and focus on the details. Pay attention to codes, actions, steps, phone numbers, amounts, and other finer details. Include all of these in the answer. Prioritize insurance-specific information. Be extremely detailed and thorough. Ensure the formatting is clean for easy understanding."""
        logger.info(f'Query = {query}')

        retries = 5  # Maximum number of retries
        backoff_factor = 2  # Backoff multiplier
        initial_delay = 1  # Initial delay in seconds

        for attempt in range(retries):
            try:
                human_template = "{task}\n\n==Query==\n{query}\n\n==Context==\n{context}"
                human_message = HumanMessagePromptTemplate.from_template(human_template)
                chat_template = ChatPromptTemplate.from_messages([human_message])
                prompt = chat_template.format_prompt(task=task, query=query, context=context).to_messages()
                response = self.model(prompt)
                completion = response.content
                return completion.strip()
            except Exception as e:
                if attempt < retries - 1:
                    wait_time = initial_delay * (backoff_factor ** attempt)
                    logger.error(f"Error during model prediction: {e}. Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Final attempt failed with error: {e}")
                    return None

        

    def format_answer(self, answer: str) -> str:
        """
        Given an answer, clean the answer by removing the citations and formatting it to be clear and readable.
        """
        task = """Format the provided answer by removing any citations, breaking it down into manageable steps or points, and ensuring it's clear and easy to read. 
        Remove all types of citations like [1], [1, 3]."""
        logger.info('Formatting generated answer...')
        try:
            human_template = "{task}\n\nAnswer:\n{answer}\n\nFormatted Answer:"
            human_message = HumanMessagePromptTemplate.from_template(human_template)
            chat_template = ChatPromptTemplate.from_messages([human_message])
            prompt = chat_template.format_prompt(task=task, answer=answer).to_messages()
            response = self.model(prompt)
            completion = response.content
            return completion.strip()
        except Exception as e:
            logger.error(f"Error during model prediction: {e}")
            return None
        
    
    def coalesce_answer(self, answers: str) -> str:
        """
        Given various answers to a question, combine them to retain all unique points and steps in the correct order.
        """
        task = """Given multiple answers to a question, compile them to maintain all unique points and steps in the correct sequence. 
Be sure to remove any extraneous sentences at the beginning of the answers, such as "formatted answer" or "sure, here is the formatted answer," and so on."""
        logger.info('Coalescing answers...')
        try:
            human_template = "{task}\n\nAnswers:\n{answers}\n\nCombined Answer:"
            human_message = HumanMessagePromptTemplate.from_template(human_template)
            chat_template = ChatPromptTemplate.from_messages([human_message])
            prompt = chat_template.format_prompt(task=task, answers=answers).to_messages()
            response = self.model(prompt)
            completion = response.content
            return completion.strip()
        except Exception as e:
            logger.error(f"Error during model prediction: {e}")
            return None
        

    def expand_query(self, query: str, n: int) -> list:
        # task is equivalent to system message here
        task = f"""Given a query, create a variant of the original query. Ensure the generated variant is not in history."""
        history = ''
        variants = []
        try:
           for _ in range(n):   
            human_template = f'{task}\n\nHistory:\n{history}\n\nQuery: {query}\n\nVariant='
            human_message = HumanMessagePromptTemplate.from_template(human_template)
            chat_template = ChatPromptTemplate.from_messages([human_message])
            prompt = chat_template.format_prompt(task=task, history=history, query=query).to_messages()
            
            response = self.model(prompt)
            completion = response.content.strip()
            variants.append(completion)
            history += '\n' + completion
        except Exception as e:
            logger.error(e)
        return variants
    
    def extract_key_phrases(self, query) -> list:
        task = f"""Given a query, extract the most important tokens from the query. Extract as single words. Return the tokens as a pipe separated list."""
        human_template = f'{task}\n\n\n\nQuery: {query}'
        human_message = HumanMessagePromptTemplate.from_template(human_template)
        chat_template = ChatPromptTemplate.from_messages([human_message])
        prompt = chat_template.format_prompt(task=task, query=query).to_messages()
        
        response = self.model(prompt)
        completion = response.content.strip()
        return completion





        

if __name__ == '__main__':
    llm = LLM()

    #task = "Given a query and context, find the answer to the query from the provided context. "
    #query = "How to reinstate policy if cancelled mid-term?"
    #context = """Q_A_Answer__c : If a policy cancels mid-term for non-payment, the insured has up to 11 calendar days to reinstate it with a lapse. ex: A policy cancelled on 4/1/2021 would have until 4/11/2021 to make payment to reinstate with lapse. Counting 4/1/2021 as day 1 this would be 11 calendar days."""
    #answer = llm.find_answer(query=query, context=context)
    """
    print(answer)
    print('-' * 100)
    answer = "To process a refund void stop pay request, you can open a Word document and title it with the current date followed by Void Stop and your initials [3]. You can then review the diary comments and void stop pay request [3]. At least one must state the agent or named insured was advised not to attempt to cash the original check [3]. If not noted, the request cannot be processed [3]. You can also process the void via AS400 [4]. Be sure to screen shot and copy to Word document prior to finalizing AS400 void [4]. You can also reapply a same day refund to a policy [4]. The Diary Comment policy should state: Processed Void Stop Pay request to Reapply refund to policy [4]. You can save Word document screen shots to shared Z drive: Operations/Accounting Services/Accounting Services/Void check_Stop pay/2Void Stop Pays/Year Void Stop Pays/Month Void Stops [4]. If one of the individuals on the refund check is now deceased, you can stop payment and reissue a refund check payable to both the living person and â€œThe Estate ofâ€ the deceased person [2]."
    formatted_answer = llm.format_answer(answer=answer)
    print(formatted_answer)
    print('-' * 100)
    """
    query = 'When would I recycle a diary comment in PSP?'
    variants = llm.expand_query(query, 4)
    print(variants)