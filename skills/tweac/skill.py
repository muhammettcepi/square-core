import logging
import uuid
import requests
import os

from square_skill_api.models import QueryOutput, QueryRequest

from square_model_client import SQuAREModelClient

from square_auth.client_credentials import ClientCredentials

logger = logging.getLogger(__name__)

square_model_client = SQuAREModelClient()


async def predict(request: QueryRequest) -> QueryOutput:
    """
    Given a question, calls the TWEAC model to identify the Skill to run.
    """
    query = request.query

    # Call Model API
    model_request = {
        "input": [query],
    }

    logger.debug("Request for model api:{}".format(model_request))

    model_response = await square_model_client(
        model_name=request.skill_args["base_model"],
        pipeline="sequence-classification",
        model_request=model_request,
    )
    logger.info("Model response: {}".format(model_response))
        
    raw_pred = model_response["model_outputs"]["labels"][0]
    dataset_name = model_response["model_outputs"]['id2label'][raw_pred]
    logger.info("TWEAC prediction: {}".format(dataset_name))
    
    # API call to Skill Manager to get the names of the skills trained on the dataset
    skill_manager_api_url = os.getenv("VUE_APP_SKILL_MANAGER_URL")
    client_credentials = ClientCredentials()
    response = requests.get(
            url=f"{skill_manager_api_url}/dataset/{dataset_name}",
            headers={"Authorization": f"Bearer {client_credentials}"},
            verify=os.getenv("VERIFY_SSL") == "1",
        )
    list_skills = response.json()
    list_skill_ids = [skill["id"] for skill in list_skills]
    
    return list_skill_ids
