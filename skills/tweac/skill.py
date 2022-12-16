import logging
import os

import requests
from square_auth.client_credentials import ClientCredentials
from square_datastore_client import SQuAREDatastoreClient
from square_model_client import SQuAREModelClient
from square_skill_api.models import QueryOutput, QueryRequest

logger = logging.getLogger(__name__)

square_model_client = SQuAREModelClient()
square_datastore_client = SQuAREDatastoreClient()


async def predict(request: QueryRequest) -> QueryOutput:
    """
    Given a question, calls the TWEAC model to identify the Skill to run.
    """
    logger.info("Request: {}".format(request))
    predicted_dataset = _call_tweac(request)
    list_predicted_skills = _retrieve_skills(predicted_dataset)
    skill_response = _call_skill(list_predicted_skills[0], request.query)
    query_output = QueryOutput(
        predictions=skill_response.json()["predictions"],
        adversarial=skill_response.json()["adversarial"],
    )
    return query_output


async def _call_tweac(request):
    model_request = {
        "input": [request.query],
    }
    logger.debug("Request for model api:{}".format(model_request))

    model_response = await square_model_client(
        model_name=request.skill_args["base_model"],
        pipeline="sequence-classification",
        model_request=model_request,
    )
    # model_response = {'model_outputs': {'logits': None},
    #                   'model_output_is_encoded': True,
    #                   'labels': [14],
    #                   'id2label': {0: 'boolq', 1: 'commonsense_qa', 10: 'biu-nlp/qamr', 11: 'race', 12: 'search_qa', 13: 'social_i_qa', 14: 'squad', 15: 'trivia_qa', 2: 'drop', 3: 'duorc', 4: 'hellaswag', 5: 'hotpot_qa', 6: 'hybrid_qa', 7: 'narrativeqa', 8: 'natural_questions', 9: 'newsqa'},
    #                   'attributions': [],
    #                   'questions': [],
    #                   'contexts': [],
    #                   'adversarial': {}
    #                   }
    logger.info("TWEAC response: {}".format(model_response))
    raw_pred = model_response["labels"][0]
    logger.info("Raw prediction: {}".format(raw_pred))
    dataset_name = model_response["id2label"][raw_pred]
    logger.info("TWEAC prediction: {}".format(dataset_name))
    return dataset_name


async def _retrieve_skills(dataset_name):
    """
    API call to Skill Manager to get the names of the skills trained on the dataset
    """
    # skill_manager_api_url = "https://square.ukp-lab.de/api/skill-manager"
    skill_manager_api_url = os.getenv("SQUARE_SKILL_MANAGER")
    client_credentials = ClientCredentials()
    # client_credentials = "TOKEN"

    response = requests.get(
        url=f"{skill_manager_api_url}/skill/dataset/{dataset_name}",
        headers={"Authorization": f"Bearer {client_credentials}"},
        verify=os.getenv("VERIFY_SSL") == "1",
    )
    logger.info("Retrieved Skills: {}".format(response))
    list_predicted_skills = response.json()
    list_predicted_skills = [
        skill for skill in list_predicted_skills if skill["skill_type"] != "meta-skill"
    ]
    return list_predicted_skills


async def _call_skill(skill_id, question, context):
    # skill_manager_api_url = "https://square.ukp-lab.de/api/skill-manager"
    skill_manager_api_url = os.getenv("SQUARE_SKILL_MANAGER")
    client_credentials = ClientCredentials()
    # client_credentials = "TOKEN"

    input_data = {
        "query": question,
        "skill_args": {"context": context},
        "skill": {},
        "user_id": "",
        "explain_kwargs": {},
    }

    response = requests.post(
        # url=f"{skill_manager_api_url}/skill/{{skill_id}}/query", # THIS doesn't work because of the curly braces in skill_id
        url=skill_manager_api_url + "/skill/" + skill_id + "/query",
        json=input_data,
        headers={"Authorization": f"Bearer {client_credentials}"},
        verify=os.getenv("VERIFY_SSL") == "1",
    )
    return response