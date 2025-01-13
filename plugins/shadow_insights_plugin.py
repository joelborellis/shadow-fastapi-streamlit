from typing import Annotated

from semantic_kernel.functions.kernel_function_decorator import kernel_function

from tools.searchshadow import SearchShadow
from tools.searchcustomer import SearchCustomer

class ShadowInsightsPlugin:
    """Plugin class that accepts a PromptTemplateConfig for advanced configuration."""

    def __init__(self, search_shadow_client: SearchShadow, search_customer_client: SearchCustomer):
        """
        :param prompt_template_config: A PromptTemplateConfig object used for advanced template configuration.
        """
        self.search_shadow_client = search_shadow_client
        self.search_customer_client = search_customer_client

    @kernel_function(
        name="get_sales_docs",
        description="Given a user query determine if it requires some sales strategy. Search the index that contains information about sales methodologies and strategies."
    )
    def get_sales_docs(self, query: Annotated[str, "The query from the user."]
    ) -> Annotated[str, "Returns documents from the sales strategy index."]:
        #print(f"user_query:  {query}")
        docs = self.search_shadow_client.search_hybrid(query)
        # Optionally, you can make use of self.prompt_template_config if needed
        # e.g., config_params = self.prompt_template_config.parameters
        return docs

    @kernel_function(
        name="get_customer_docs",
        description="Given a user query determine if a company name was mentioned. Use the company name and the query information to search the index containing information about customers."
    )
    def get_customer_docs(self, query: Annotated[str, "The query and the customer name from the user."]
    ) -> Annotated[str, "Returns documents from the customer index."]:
        #print(f"user_customer_query:  {query}")
        docs = self.search_customer_client.search_hybrid(query)
        # Optionally, you can make use of self.prompt_template_config if needed
        return docs