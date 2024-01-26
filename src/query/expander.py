from src.config.logging import logger
from src.config.setup import config
from src.generate.llm import LLM


llm = LLM()


if __name__ == '__main__':
    query = 'When would I recycle a diary comment in PSP?'
    variants = llm.expand_query(query)
    print(variants)
