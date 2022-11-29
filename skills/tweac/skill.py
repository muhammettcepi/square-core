import logging
import uuid

from square_skill_api.models import QueryOutput, QueryRequest

from square_model_client import SQuAREModelClient

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
        "explain_kwargs": {},
        "attack_kwargs": {},
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
    skill_names = []

    return QueryOutput.from_sequence_classification(
        questions=query,
        answers=skill_names,
        model_api_output=model_response,
    )
